# 動画生成パイプライン

[ガイド本編](../README.md)の内容を、**音声と字幕が付いた MP4** にするための一式です。
デッキ（YAML）にスライドとナレーションを書くと、`build.py` が動画と字幕ファイルを出力します。

```bash
pip install -r requirements.txt
bash setup_voicevox.sh          # 高品質な音声を使う場合（推奨・任意）
python3 build.py decks/sample.yaml
# → out/sample.mp4, out/sample.srt, out/sample.segments.json
```

---

## 仕組み

処理の最小単位は **セグメント**で、**ナレーション 1 文がちょうど 1 セグメント**です。

```
1 セグメント = ① 字幕を焼き込んだスライド画像 1 枚（1920x1080 PNG）
             + ② その 1 文を読み上げた音声 1 本（WAV）
```

セグメントを順に連結すれば動画になります。この作りにしている理由は 2 つあります。

- **字幕を ffmpeg のフィルタに頼らない。** `subtitles`（libass）や `drawtext` は ffmpeg のビルドオプション次第で使えないことがあります。字幕を最初から画像に描いてしまえば、ffmpeg には「画像の連結」「音声の連結」「エンコード」しか要求しません。
- **字幕のタイムコードが正確になる。** 各文の音声長が確定しているので、累積するだけで誤差なく `.srt` を作れます。

処理の流れは次の通りです。

| 段階 | 使うもの |
| --- | --- |
| 1. スライドを PNG に | Chromium（`--headless --screenshot`）＋ `theme.css` |
| 2. ナレーションを WAV に | VOICEVOX または OpenJTalk（下記「音声エンジン」） |
| 3. 連結してエンコード | `imageio-ffmpeg` 同梱の ffmpeg（H.264 + AAC、ラウドネス正規化あり） |

---

## 音声エンジン

デッキの `meta.engine` で選びます。

| `engine` | 音質 | 準備 |
| --- | --- | --- |
| `voicevox` | かなり自然。**推奨** | `bash setup_voicevox.sh`（約 1.3GB のダウンロード） |
| `openjtalk` | 明らかに合成音声とわかる | 不要（`requirements.txt` だけで動く） |

```yaml
meta:
  engine: voicevox
  speaker: 30 # No.7 アナウンス
  speed: 1.0
  loudness: -16.0 # 統合ラウドネスの目標値（LUFS）
```

### 話者の選び方

`speaker` は VOICEVOX のスタイル ID です。一覧はこう出せます。

```bash
python3 -c "
from voicevox_core import METAS
for m in METAS:
    print(m.name, [(s.name, s.id) for s in m.styles])
"
```

技術解説の動画には、**ナレーション用のスタイルを持つ話者**が向いています。既定にしている「No.7」には `アナウンス(30)` と `読み聞かせ(31)` があり、落ち着いた読み上げになります。

> ⚠ **クレジット表記が必要です。**
> VOICEVOX で生成した音声を公開する場合、キャラクターごとの利用規約に従ってクレジットを表示してください（例:「VOICEVOX:No.7」）。規約はキャラクターごとに異なります。
> https://voicevox.hiroshiba.jp/term/

---

## デッキの書き方

`decks/` 配下の YAML がスライドとナレーションの定義です。**このファイルがそのままナレーション原稿**になります。

```yaml
meta:
  title: "動画のタイトル"
  width: 1920
  height: 1080
  fps: 30
  gap: 0.35      # セグメント間に入れる無音（秒）
  speed: 1.0     # 読み上げ速度

slides:
  - layout: bullets
    chapter: "01. Claude Code とは"   # 左上に出る小見出し
    title: "チャット版 Claude との違い"
    reveal: true                       # ナレーションに合わせて 1 行ずつ強調する
    bullets:
      - "自分でファイルを探して読む"
      - "実際にコードを書き換える"
    narration:
      - "1 つ目の文。これが 1 セグメントになります。"
      - text: "Claude Code は違います。"
        read: "クロードコードは違います。"
```

### ⚠ 英語表記には必ず `read` を添える

OpenJTalk は**英単語をアルファベット 1 文字ずつ読みます**。`Claude Code` はそのままだと「シーエルエーユーディーイー…」になってしまいます。

```yaml
narration:
  - text: "Claude Code は違います。"      # 画面に出る文字列
    read: "クロードコードは違います。"     # 読み上げに渡す文字列
```

文字列だけを書いた場合は、表示と読み上げが同じテキストになります。日本語だけの文ならそれで構いません。

### レイアウト

| `layout` | 使うキー | 用途 |
| --- | --- | --- |
| `title` | `title`, `subtitle` | 章の扉、まとめ |
| `bullets` | `title`, `bullets`, `reveal` | 箇条書き。`reveal: true` でナレーションに同期して強調が移動する |
| `code` | `title`, `code` | コマンドやコード。`#` 始まりはコメント色、`$` 始まりはコマンド色 |
| `compare` | `title`, `before`, `after` | Before / After の対比（それぞれ `label` と `text`） |

`reveal: true` を使うときは、**`bullets` の項目数と `narration` の文数を揃えて**ください。N 番目の文を読んでいる間、N 番目の項目が強調されます。

---

## 出力されるもの

| ファイル | 内容 |
| --- | --- |
| `out/<名前>.mp4` | 動画本体（H.264 + AAC、字幕焼き込み済み） |
| `out/<名前>.srt` | 字幕ファイル。YouTube 等に別途読み込ませる用 |
| `out/<名前>.segments.json` | 各セグメントの表示文・読み・長さ。音声を差し替えるときの手がかり |

`out/` は `.gitignore` で除外しているのでコミットされません。

---

## オプション

```bash
python3 build.py decks/sample.yaml --keep     # 中間ファイル（PNG/WAV/HTML）を残す
python3 build.py decks/sample.yaml --limit 3  # 先頭 3 セグメントだけ作る（確認用）
python3 build.py decks/sample.yaml --out /tmp/v   # 出力先を変える
```

レイアウト崩れを疑ったときは `--keep` を付けて、`out/<名前>.work/seg0000.png` を直接開いて確認するのが早いです。

---

## さらに別の音声に差し替える

**方法 1: `build.py` に合成関数を足す**

`synth_voicevox()` / `synth_openjtalk()` はどちらも「1 文を受け取って WAV を書き、長さを返す」だけの関数です。同じ形の関数を書いて `synthesize()` の分岐に足せば、他の処理はそのまま使えます。

**方法 2: 自分で録音して差し替える**

`out/<名前>.segments.json` に、各文の表示テキスト・読み・長さが並んでいます。これを台本にして録音し、`--keep` で残した `seg0000.wav` … を差し替えてから連結し直してください。

### この環境で使えなかった選択肢

参考までに、調べた結果を残しておきます。

| 配布元 | 状態 |
| --- | --- |
| PyPI | 到達可（プロキシ除外） |
| GitHub リリース / raw | 到達可 → **VOICEVOX はここから取得している** |
| GitHub API | このセッションのリポジトリのみ |
| huggingface.co | 遮断 → piper や Style-Bert-VITS2 のモデルは取得できない |
| Google / Microsoft の TTS | 遮断 |

`setup_voicevox.sh` が公式ダウンローダを使わず URL 直指定なのはこのためです。公式ダウンローダは `api.github.com` からリリース情報を引くうえ、Rust 製で CA ストアを埋め込んでいるため、プロキシ配下では証明書エラーで止まります。

---

## 動作環境について

- **Chromium**: `/opt/pw-browsers/` 配下のものを自動で探します。`headless_shell` を優先します。通常の `chrome` を `--headless=new` で使うと、ウィンドウ装飾のぶんビューポートが縦に縮み、**下端 90px ほどが描画されず字幕が切れます**。`build.py` は 1 枚目を撮った時点でこれを検査し、問題があれば止まります。
- **フォント**: `IPAPGothic` / `IPAGothic` を使います。この環境には **Bold フェイスが無い**ため、`theme.css` では強調を「色」と「サイズ」で表現し、`font-weight` に頼らない作りにしています。
- **生成時間**: 66 秒の動画で約 40 秒。10 分程度の動画なら 6〜10 分が目安です。
