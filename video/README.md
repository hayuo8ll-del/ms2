# 動画生成パイプライン

[ガイド本編](../README.md)の内容を、**音声と字幕が付いた MP4** にするための一式です。
デッキ（YAML）にスライドとナレーションを書くと、`build.py` が動画と字幕ファイルを出力します。

```bash
pip install -r requirements.txt
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
| 2. ナレーションを WAV に | `pyopenjtalk`（OpenJTalk、完全オフライン） |
| 3. 連結してエンコード | `imageio-ffmpeg` 同梱の ffmpeg（H.264 + AAC） |

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

## 音声を高品質なものに差し替える

同梱している OpenJTalk は完全オフラインで動く代わりに、**いかにも合成音声とわかる声**です。より自然な声にしたい場合は次のいずれかで差し替えられます。

**方法 1: `build.py` の合成部分だけ差し替える**

`synthesize()` が「1 文を受け取って WAV を書き、長さを返す」だけの関数になっています。ここを VOICEVOX や好みの TTS の呼び出しに置き換えれば、他の処理はそのまま使えます。

**方法 2: 自分で録音して差し替える**

`out/<名前>.segments.json` に、各文の表示テキスト・読み・長さが並んでいます。これを台本にして録音し、`--keep` で残した `seg0000.wav` … を差し替えてから、`build.py` の最後の連結処理だけを実行してください。

なお、この環境では neural TTS（piper 等）のモデル配布元（`huggingface.co`）に到達できないため、OpenJTalk を採用しています。ネットワークに制限がない環境なら、より自然な選択肢が使えます。

---

## 動作環境について

- **Chromium**: `/opt/pw-browsers/` 配下のものを自動で探します。`headless_shell` を優先します。通常の `chrome` を `--headless=new` で使うと、ウィンドウ装飾のぶんビューポートが縦に縮み、**下端 90px ほどが描画されず字幕が切れます**。`build.py` は 1 枚目を撮った時点でこれを検査し、問題があれば止まります。
- **フォント**: `IPAPGothic` / `IPAGothic` を使います。この環境には **Bold フェイスが無い**ため、`theme.css` では強調を「色」と「サイズ」で表現し、`font-weight` に頼らない作りにしています。
- **生成時間**: 66 秒の動画で約 40 秒。10 分程度の動画なら 6〜10 分が目安です。
