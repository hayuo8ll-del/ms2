#!/usr/bin/env python3
"""デッキ YAML から、音声と字幕付きの MP4 を生成する。

処理の単位は「セグメント」で、ナレーション 1 文がちょうど 1 セグメントになる。
各セグメントについて、字幕を焼き込んだスライド画像 1 枚と、その文を読み上げた
音声 1 本を作り、最後にすべてを連結して 1 本の動画にする。

字幕を ffmpeg のフィルタ（subtitles / drawtext）ではなく画像に直接描き込むのは、
それらのフィルタが ffmpeg のビルドオプションに依存して使えないことがあるため。
画像に描いてしまえば、ffmpeg には連結とエンコードしか要求しない。

使い方:
    python3 build.py decks/sample.yaml
    python3 build.py decks/sample.yaml --out out --keep
"""

from __future__ import annotations

import argparse
import glob
import html
import io
import json
import shutil
import struct
import subprocess
import sys
import wave
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent

# 字幕を折り返す目安の文字数。日本語は単語境界が無いので文字数で判断する。
CAPTION_WRAP = 32
# 読点で折り返せる場合はそちらを優先する
CAPTION_BREAK_CHARS = "、。，,"


# --------------------------------------------------------------------------
# 外部ツールの場所
# --------------------------------------------------------------------------


def find_chrome() -> str:
    """スライド描画に使う Chromium を探す。

    headless_shell を優先する。通常の chrome を --headless=new で動かすと
    ウィンドウ装飾のぶんビューポートが縦に縮み、指定した高さで撮っても
    下端 90px ほどが描画されないまま残ってしまう（字幕が切れる）。
    headless_shell はウィンドウを持たないので、指定サイズがそのまま描画される。
    """
    candidates = sorted(
        glob.glob("/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell")
    )
    candidates += sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))
    for name in ("chromium", "chromium-browser", "google-chrome"):
        found = shutil.which(name)
        if found:
            candidates.append(found)
    if not candidates:
        sys.exit(
            "Chromium が見つかりません。PLAYWRIGHT_BROWSERS_PATH 配下を確認してください。"
        )
    return candidates[0]


def find_ffmpeg() -> str:
    """音声を扱えるフル機能の ffmpeg を返す。

    Playwright 同梱の ffmpeg は --disable-everything ビルドで音声コーデックを
    一切持たないため、imageio-ffmpeg のものを優先する。
    """
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    found = shutil.which("ffmpeg")
    if not found:
        sys.exit("ffmpeg が見つかりません。pip install imageio-ffmpeg を実行してください。")
    return found


# --------------------------------------------------------------------------
# デッキの読み込み
# --------------------------------------------------------------------------


@dataclass
class Segment:
    """ナレーション 1 文ぶんの単位。"""

    index: int
    slide: dict
    slide_index: int
    line_index: int  # スライド内で何番目の文か
    caption: str  # 画面に出す文字列
    read: str  # 読み上げに渡す文字列
    duration: float = 0.0
    png: Path = field(default=Path())
    wav: Path = field(default=Path())


def load_deck(path: Path) -> tuple[dict, list[Segment]]:
    deck = yaml.safe_load(path.read_text(encoding="utf-8"))
    meta = deck.get("meta", {})
    segments: list[Segment] = []

    for slide_index, slide in enumerate(deck.get("slides", [])):
        narration = slide.get("narration") or []
        if not narration:
            raise SystemExit(
                f"スライド {slide_index + 1}（{slide.get('title', '')}）に narration がありません"
            )
        for line_index, item in enumerate(narration):
            # 文字列なら表示と読みが同じ。dict なら read で読みを上書きできる。
            # 英単語は OpenJTalk がアルファベットを 1 文字ずつ読むため、
            # "Claude Code" のような表記には read: "クロードコード" を添える。
            if isinstance(item, dict):
                caption = item.get("text", "")
                read = item.get("read") or caption
            else:
                caption = str(item)
                read = caption
            segments.append(
                Segment(
                    index=len(segments),
                    slide=slide,
                    slide_index=slide_index,
                    line_index=line_index,
                    caption=caption,
                    read=read,
                )
            )
    if not segments:
        raise SystemExit("スライドが 1 枚もありません")
    return meta, segments


# --------------------------------------------------------------------------
# スライドの HTML 生成
# --------------------------------------------------------------------------


def wrap_caption(text: str) -> str:
    """字幕を最大 2 行に折り返して HTML を返す。"""
    if len(text) <= CAPTION_WRAP:
        return html.escape(text)

    # 中央付近の読点で切れるならそこで切る
    mid = len(text) // 2
    best = None
    for i, ch in enumerate(text):
        if ch in CAPTION_BREAK_CHARS and 0 < i < len(text) - 1:
            if best is None or abs(i - mid) < abs(best - mid):
                best = i
    cut = best + 1 if best is not None else mid
    head, tail = text[:cut], text[cut:]
    return html.escape(head) + "<br>" + html.escape(tail)


# 見出しと字幕帯を除いた、コードブロックに使える縦幅の目安（px）
CODE_AREA_H = 500
CODE_LINE_RATIO = 1.65
CODE_MAX_SIZE = 38
CODE_MIN_SIZE = 22


def code_font_size(lines: list[str]) -> int:
    """行数からコードの文字サイズを決める。

    固定サイズだと行数が多いスライドで字幕帯に食い込むため、
    入る大きさを計算してしまう。長すぎるコードは警告を出す。
    """
    n = max(len(lines), 1)
    size = int(min(CODE_MAX_SIZE, CODE_AREA_H / (n * CODE_LINE_RATIO)))
    if size < CODE_MIN_SIZE:
        print(
            f"  警告: コードが {n} 行あり、読める大きさに収まりません。"
            f"{int(CODE_AREA_H / (CODE_MIN_SIZE * CODE_LINE_RATIO))} 行以内に分割してください。"
        )
        size = CODE_MIN_SIZE
    return size


def render_body(slide: dict, line_index: int) -> str:
    """レイアウト別に本文の HTML を組み立てる。"""
    layout = slide.get("layout", "bullets")
    title = html.escape(slide.get("title", ""))

    if layout == "title":
        subtitle = slide.get("subtitle", "")
        sub_html = f'<p class="lead">{html.escape(subtitle)}</p>' if subtitle else ""
        return f'<h1>{title}</h1><div class="rule"></div>{sub_html}'

    parts = [f"<h2>{title}</h2>"] if title else []

    if layout == "bullets":
        bullets = slide.get("bullets", [])
        reveal = slide.get("reveal", False)
        items = []
        for i, b in enumerate(bullets):
            if not reveal:
                cls = ""
            elif i == line_index:
                cls = "on"
            elif i < line_index:
                cls = ""
            else:
                cls = "off"
            items.append(f'<li class="{cls}">{html.escape(str(b))}</li>')
        parts.append('<ul class="bullets">' + "".join(items) + "</ul>")

    elif layout == "code":
        raw_lines = str(slide.get("code", "")).rstrip("\n").split("\n")
        lines = []
        for raw in raw_lines:
            escaped = html.escape(raw)
            if raw.strip().startswith("#"):
                lines.append(f'<span class="cmt">{escaped}</span>')
            elif raw.strip().startswith("$"):
                lines.append(f'<span class="cmd">{escaped}</span>')
            else:
                lines.append(escaped)
        size = code_font_size(raw_lines)
        parts.append(
            f'<pre class="code" style="font-size:{size}px">' + "\n".join(lines) + "</pre>"
        )

    elif layout == "compare":
        left = slide.get("before", {})
        right = slide.get("after", {})
        parts.append(
            '<div class="compare">'
            f'<div class="col bad"><div class="label">{html.escape(left.get("label", "惜しい指示"))}</div>'
            f'<div class="text">{html.escape(left.get("text", ""))}</div></div>'
            f'<div class="col good"><div class="label">{html.escape(right.get("label", "良い指示"))}</div>'
            f'<div class="text">{html.escape(right.get("text", ""))}</div></div>'
            "</div>"
        )

    else:
        raise SystemExit(f"未知の layout: {layout}")

    return "".join(parts)


def render_html(seg: Segment, total: int, css: str) -> str:
    layout = seg.slide.get("layout", "bullets")
    chapter = seg.slide.get("chapter", "")
    chapter_html = f'<div class="chapter">{html.escape(chapter)}</div>' if chapter else ""
    progress = (seg.index + 1) / total * 100

    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><style>{css}</style></head>
<body>
  <div class="slide layout-{html.escape(layout)}">
    {chapter_html}
    <div class="body">{render_body(seg.slide, seg.line_index)}</div>
    <div class="caption"><p>{wrap_caption(seg.caption)}</p></div>
    <div class="progress" style="width: {progress:.3f}%"></div>
  </div>
</body></html>
"""


def shoot(chrome: str, html_path: Path, png_path: Path, width: int, height: int) -> None:
    # headless_shell は --headless が既定。通常の chrome には明示が要る。
    headless = "--headless" if "headless_shell" in chrome else "--headless=new"
    cmd = [
        chrome,
        headless,
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        f"--window-size={width},{height}",
        f"--screenshot={png_path}",
        html_path.as_uri(),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if not png_path.exists():
        sys.exit(f"スクリーンショットに失敗しました:\n{result.stderr[-2000:]}")


def verify_canvas(ffmpeg: str, png_path: Path, width: int, height: int) -> None:
    """1 枚目を使って、指定サイズいっぱいに描画できているか確かめる。

    ビューポートが縮んでいると下端が未描画のまま残り、字幕が切れる。
    見落とすと全セグメントを作り直すことになるので、最初に一度だけ検査する。
    """
    png_size = struct.unpack(">II", png_path.read_bytes()[16:24])
    if png_size != (width, height):
        sys.exit(f"画像サイズが {png_size} で、指定した {(width, height)} と違います。")

    # 最下段 4px を 1px に潰して RGBA を取り出す。透明なら未描画。
    result = subprocess.run(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(png_path),
            "-vf", f"crop={width}:4:0:{height - 4},scale=1:1",
            "-f", "rawvideo", "-pix_fmt", "rgba", "-",
        ],
        capture_output=True,
    )
    pixel = result.stdout[:4]
    if len(pixel) == 4 and pixel[3] < 250:
        sys.exit(
            "スライド下端が描画されていません（ビューポートが縦に足りていない）。\n"
            "headless_shell を使うか、--window-size の高さを増やしてください。"
        )


# --------------------------------------------------------------------------
# 音声合成
# --------------------------------------------------------------------------


_VOICEVOX_CORE = None


def voicevox_core(dict_dir: Path):
    """VOICEVOX を初期化して使い回す。モデル読み込みに数秒かかるため 1 回だけ。"""
    global _VOICEVOX_CORE
    if _VOICEVOX_CORE is None:
        try:
            from voicevox_core import AccelerationMode, VoicevoxCore
        except ImportError:
            sys.exit(
                "VOICEVOX が入っていません。setup_voicevox.sh を実行するか、\n"
                "デッキの meta から engine: voicevox を外してください。"
            )
        if not dict_dir.is_dir():
            sys.exit(f"Open JTalk 辞書が見つかりません: {dict_dir}\nsetup_voicevox.sh を実行してください。")
        _VOICEVOX_CORE = VoicevoxCore(
            acceleration_mode=AccelerationMode.CPU, open_jtalk_dict_dir=str(dict_dir)
        )
    return _VOICEVOX_CORE


def write_wav(path: Path, frames: bytes, sr: int, gap: float) -> float:
    """PCM を WAV に書き、末尾に無音を足した長さ（秒）を返す。"""
    silence = b"\x00\x00" * int(sr * gap)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(frames + silence)
    return (len(frames) // 2 + int(sr * gap)) / sr


def synth_voicevox(seg: Segment, wav_path: Path, gap: float, speed: float,
                   speaker: int, dict_dir: Path) -> float:
    core = voicevox_core(dict_dir)
    if not core.is_model_loaded(speaker):
        core.load_model(speaker)

    # audio_query を経由すると読み上げ速度などを調整できる
    query = core.audio_query(seg.read, speaker)
    query.speed_scale = speed
    wav_bytes = core.synthesis(query, speaker)

    # VOICEVOX はヘッダ付きの WAV を返すので、PCM を取り出して詰め直す
    with wave.open(io.BytesIO(wav_bytes)) as r:
        sr = r.getframerate()
        frames = r.readframes(r.getnframes())
        if r.getnchannels() == 2:
            # 念のためモノラルに落とす（通常は 1ch）
            import numpy as np

            stereo = np.frombuffer(frames, dtype="<i2").reshape(-1, 2)
            frames = stereo.mean(axis=1).astype("<i2").tobytes()

    # VOICEVOX の出力は音量が揃っているので、正規化はしない
    return write_wav(wav_path, frames, sr, gap)


def synth_openjtalk(seg: Segment, wav_path: Path, gap: float, speed: float) -> float:
    import numpy as np
    import pyopenjtalk

    wave_data, sr = pyopenjtalk.tts(seg.read, speed=speed)
    audio = np.asarray(wave_data, dtype=np.float64)

    # 文ごとに音量がばらつくので、聞き取りやすい水準に揃える
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 0:
        audio = audio / peak * (0.89 * 32767)

    return write_wav(wav_path, audio.astype("<i2").tobytes(), sr, gap)


def synthesize(seg: Segment, wav_path: Path, gap: float, speed: float,
               engine: str, speaker: int, dict_dir: Path) -> float:
    """1 文を読み上げて WAV に保存し、長さ（秒）を返す。"""
    if engine == "voicevox":
        return synth_voicevox(seg, wav_path, gap, speed, speaker, dict_dir)
    if engine == "openjtalk":
        return synth_openjtalk(seg, wav_path, gap, speed)
    sys.exit(f"未知の engine: {engine}（voicevox / openjtalk のいずれか）")


# --------------------------------------------------------------------------
# 字幕ファイル
# --------------------------------------------------------------------------


def srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(segments: list[Segment], path: Path, gap: float) -> None:
    lines = []
    t = 0.0
    for i, seg in enumerate(segments, start=1):
        # 末尾の無音は字幕を出しっぱなしにしない
        end = t + max(seg.duration - gap * 0.6, 0.4)
        lines.append(str(i))
        lines.append(f"{srt_time(t)} --> {srt_time(end)}")
        lines.append(seg.caption)
        lines.append("")
        t += seg.duration
    path.write_text("\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------
# 連結してエンコード
# --------------------------------------------------------------------------


def encode(ffmpeg: str, segments: list[Segment], out: Path, fps: int, work: Path,
           loudness: float) -> None:
    images = work / "images.txt"
    audios = work / "audio.txt"

    with images.open("w", encoding="utf-8") as f:
        for seg in segments:
            f.write(f"file '{seg.png.resolve()}'\n")
            f.write(f"duration {seg.duration:.4f}\n")
        # concat demuxer は最後の 1 枚を duration 無しで再掲する必要がある
        f.write(f"file '{segments[-1].png.resolve()}'\n")

    with audios.open("w", encoding="utf-8") as f:
        for seg in segments:
            f.write(f"file '{seg.wav.resolve()}'\n")

    cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(images),
        "-f", "concat", "-safe", "0", "-i", str(audios),
        "-map", "0:v", "-map", "1:a",
        # 合成音声はヘッドルームが広く、そのままだと動画として音が小さい。
        # 配信で一般的な水準に揃えておく。
        "-af", f"loudnorm=I={loudness}:TP=-1.5:LRA=11",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", str(fps),
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
        "-movflags", "+faststart",
        "-shortest",
        str(out),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not out.exists():
        sys.exit(f"エンコードに失敗しました:\n{result.stderr[-3000:]}")


# --------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description="デッキ YAML から音声・字幕付き動画を作る")
    ap.add_argument("deck", type=Path, help="デッキ YAML のパス")
    ap.add_argument("--out", type=Path, default=ROOT / "out", help="出力ディレクトリ")
    ap.add_argument("--keep", action="store_true", help="中間ファイルを残す")
    ap.add_argument("--limit", type=int, default=0, help="先頭 N セグメントだけ作る（動作確認用）")
    args = ap.parse_args()

    meta, segments = load_deck(args.deck)
    if args.limit:
        segments = segments[: args.limit]

    width = int(meta.get("width", 1920))
    height = int(meta.get("height", 1080))
    fps = int(meta.get("fps", 30))
    gap = float(meta.get("gap", 0.35))
    speed = float(meta.get("speed", 1.0))
    engine = str(meta.get("engine", "openjtalk"))
    speaker = int(meta.get("speaker", 30))  # No.7 アナウンス
    dict_dir = Path(meta.get("dict_dir") or (ROOT / ".voicevox" / "open_jtalk_dic_utf_8-1.11"))
    loudness = float(meta.get("loudness", -16.0))  # 統合ラウドネスの目標値（LUFS）

    name = args.deck.stem
    out_dir = args.out
    work = out_dir / f"{name}.work"
    out_dir.mkdir(parents=True, exist_ok=True)
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()

    chrome = find_chrome()
    ffmpeg = find_ffmpeg()
    css = (ROOT / "theme.css").read_text(encoding="utf-8")

    total = len(segments)
    print(f"デッキ : {args.deck}")
    print(f"構成   : スライド {len({s.slide_index for s in segments})} 枚 / セグメント {total} 個")
    print(f"Chrome : {chrome}")
    print(f"ffmpeg : {ffmpeg}\n")

    print("[1/3] スライドを描画中...")
    for seg in segments:
        html_path = work / f"seg{seg.index:04d}.html"
        seg.png = work / f"seg{seg.index:04d}.png"
        html_path.write_text(render_html(seg, total, css), encoding="utf-8")
        shoot(chrome, html_path, seg.png, width, height)
        if seg.index == 0:
            verify_canvas(ffmpeg, seg.png, width, height)
        print(f"  {seg.index + 1:>3}/{total}  {seg.caption[:38]}")

    print(f"\n[2/3] 音声を合成中... （engine: {engine}"
          f"{f' / speaker: {speaker}' if engine == 'voicevox' else ''}）")
    for seg in segments:
        seg.wav = work / f"seg{seg.index:04d}.wav"
        seg.duration = synthesize(seg, seg.wav, gap, speed, engine, speaker, dict_dir)
        print(f"  {seg.index + 1:>3}/{total}  {seg.duration:5.2f}s  {seg.read[:34]}")

    total_sec = sum(s.duration for s in segments)
    print(f"\n[3/3] 動画を書き出し中... （尺 {int(total_sec // 60)}分{total_sec % 60:04.1f}秒）")

    mp4 = out_dir / f"{name}.mp4"
    srt = out_dir / f"{name}.srt"
    encode(ffmpeg, segments, mp4, fps, work, loudness)
    write_srt(segments, srt, gap)

    # 後から音声だけ差し替えたい人のために、区間の情報も残しておく
    (out_dir / f"{name}.segments.json").write_text(
        json.dumps(
            [
                {
                    "index": s.index,
                    "slide": s.slide_index,
                    "caption": s.caption,
                    "read": s.read,
                    "duration": round(s.duration, 4),
                }
                for s in segments
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    if not args.keep:
        shutil.rmtree(work)

    size_mb = mp4.stat().st_size / 1024 / 1024
    print(f"\n完成: {mp4}  ({size_mb:.1f} MB)")
    print(f"字幕: {srt}")


if __name__ == "__main__":
    main()
