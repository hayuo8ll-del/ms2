# 10. トラブルシューティング

> **この章でわかること**
> - 症状別のどこを見ればよいかの早見表
> - インストール・起動・動作が重いときの対処
> - 「思った通りに動かない」ときのチェックリスト
> - コストとトークンの節約方法

---

## 10-1. まず試すこと

問題の種類がわからないときは、この 3 つから始めてください。

| コマンド | 実行場所 | 何をするか |
| --- | --- | --- |
| `/doctor` | セッション内 | インストール・設定・拡張機能・コンテキスト使用量を自動チェックし、**修正案を提示して適用してくれる** |
| `claude doctor` | シェル | `claude` が起動しない場合の診断 |
| `/mcp` | セッション内 | MCP サーバーの接続状態を確認 |

---

## 10-2. 症状別の早見表

| 症状 | 対処・参照先 |
| --- | --- |
| `command not found`、インストール失敗、PATH の問題、`EACCES`、TLS エラー | [10-3 インストール・起動の問題](#install-issues) / 公式 [Troubleshoot installation](https://code.claude.com/docs/en/troubleshoot-install) |
| ログインループ、OAuth エラー、`403 Forbidden`、「組織が無効」 | 公式 [Troubleshoot installation and login](https://code.claude.com/docs/en/troubleshoot-install#login-and-authentication) |
| 設定が反映されない、フックが発火しない、MCP が読み込まれない | [10-4 思った通りに動かない](#not-working) / 公式 [Debug your configuration](https://code.claude.com/docs/en/debug-your-config) |
| `API Error: 5xx`、`529 Overloaded`、`429` | 公式 [Error reference](https://code.claude.com/docs/en/errors) |
| `model not found` | 公式 [Error reference](https://code.claude.com/docs/en/errors) |
| VS Code 拡張が繋がらない | 公式 [VS Code integration](https://code.claude.com/docs/en/vs-code#fix-common-issues) |
| JetBrains プラグインが IDE を検出しない | 公式 [JetBrains integration](https://code.claude.com/docs/en/jetbrains#troubleshooting) |
| CPU・メモリ使用量が高い、応答が遅い、固まる | [10-3](#install-issues) |
| `@file` や検索がファイルを見つけられない | [10-3](#install-issues) の「検索がうまくいかない」 |

---

<a id="install-issues"></a>

## 10-3. インストール・起動の問題

### `claude --version` が動かない

1. ターミナルを開き直す（PATH の再読み込み）
2. `claude doctor` を実行して診断
3. 公式の [インストールのトラブルシューティング](https://code.claude.com/docs/en/troubleshoot-install#find-your-error) でエラーメッセージを照合

### Windows でインストールコマンドがエラーになる

| エラー | 原因 |
| --- | --- |
| `The token '&&' is not a valid statement separator` | PowerShell にいるのに CMD 用コマンドを実行している |
| `'irm' is not recognized...` | CMD にいるのに PowerShell 用コマンドを実行している |

プロンプトが `PS C:\` なら PowerShell、`C:\` だけなら CMD です。

### CPU・メモリ使用量が高い

1. `/compact` をこまめに実行してコンテキストを減らす
2. 大きなタスクの区切りで Claude Code を再起動する
3. 大きなビルドディレクトリを `.gitignore` に追加する
4. `claude --safe-mode` で起動する（すべてのカスタマイズを無効化）
   → これで改善するなら、プラグイン・MCP サーバー・フックのどれかが原因です

それでもメモリ使用量が高い場合は `/heapdump` でヒープスナップショットを出力できます。

> ⚠️ `.heapsnapshot` にはプロセス内のすべての文字列が含まれます。**公開の Issue に添付しないでください。** メモリ問題を報告する場合は `-diagnostics.json` のほうだけを添付してください（会話内容や認証情報は含まれません）。

### 固まった・応答しない

1. `Ctrl+C` で現在の処理をキャンセル
2. それでもダメならターミナルを閉じて再起動

**再起動しても会話は失われません。** 同じディレクトリで `claude --resume` を実行すれば続きから再開できます。

### 自動圧縮が「thrashing」エラーで止まる

`Autocompact is thrashing: the context refilled to the limit...` と出る場合、圧縮は成功したものの、直後に大きなファイルやツール出力がコンテキストを埋め戻す状態が繰り返されています。

1. 大きなファイルを「特定の行範囲・特定の関数だけ」読ませる
2. `/compact 計画と差分だけ残して` のように、大きな出力を捨てる指示を付けて圧縮する
3. 大きなファイルを扱う作業をサブエージェントに回す
4. 前の会話が不要なら `/clear`

### 検索がうまくいかない（`@file` やスキルがファイルを見つけられない）

同梱の `ripgrep` がシステム上で動かない可能性があります。OS のパッケージをインストールしてください。

```bash
brew install ripgrep                      # macOS
sudo apt install ripgrep                  # Ubuntu / Debian
apk add ripgrep                           # Alpine
pacman -S ripgrep                         # Arch
winget install BurntSushi.ripgrep.MSVC    # Windows
```

その後、環境変数に `USE_BUILTIN_RIPGREP=0` を設定します。`claude doctor` の Search 行が、`OK (bundled)` ではなくシステムの ripgrep のパスを示せば成功です。

### WSL で検索結果が少ない

Windows ファイルシステム（`/mnt/c/`）への読み取りが遅いことが原因です。

1. 検索範囲を具体的に指定する（「auth-service パッケージ内の JWT 検証ロジックを探して」）
2. プロジェクトを Linux ファイルシステム（`/home/`）に移す
3. WSL ではなく Windows ネイティブで動かす

### エディタの統合ターミナルで文字化けする

VS Code、Cursor、Devin Desktop の統合ターミナルで文字が崩れる場合は、GPU レンダラーが原因のことが多いです。

```text
/terminal-setup
```

これで `terminal.integrated.gpuAcceleration` が `"off"` に設定されます。

### 表が途中で切れる

200 行を超える Markdown テーブルは、最初の 200 行だけ表示されます（`… N more rows not shown`）。
**表示上の制限だけ**で、内容は会話に残っています。`/copy` なら全行コピーできます。読みきれない場合は「ファイルに書き出して」と頼んでください。

---

<a id="not-working"></a>

## 10-4. 「思った通りに動かない」とき

これはバグではなく、多くの場合**設定か指示の問題**です。

### チェックリスト

**1. `CLAUDE.md` は読み込まれているか**

```text
/context
```

**Memory files** の欄に該当ファイルがあるか確認します。無ければ置き場所が違います。
→ [06-3 どこに置くか](06-claude-md.md#6-3-どこに置くか)

**2. 指示は具体的か**

「コードをきれいに」ではなく「インデントは半角スペース 2 つ」。検証できるレベルまで具体化してください。

**3. 矛盾する指示は無いか**

複数の `CLAUDE.md`、`.claude/rules/`、会話中の指示が食い違っていないか確認します。

**4. `CLAUDE.md` が長すぎないか**

200 行を超えていると、重要なルールがノイズに埋もれます。`/doctor` が削減案を出してくれます。

**5. コンテキストが埋まっていないか**

`/context` で確認し、必要なら `/clear` します。長いセッションほど指示が守られにくくなります。

**6. 「必ず」実行してほしいことか**

CLAUDE.md やスキルの指示は**お願い**であって保証ではありません。確実に実行させたいならフックにしてください。
→ [08-3 フック](08-extensions.md#hooks)

### フック・MCP・設定が効かないとき

```text
/hooks     # 設定されているフックを確認
/mcp       # MCP サーバーの接続状態
/context   # 読み込まれているメモリファイル
```

`claude --safe-mode` で起動して問題が消えるなら、カスタマイズのどれかが原因です。1 つずつ戻して切り分けてください。

### `/compact` の後に指示が消えたように見える

プロジェクトルートの `CLAUDE.md` は圧縮後に再読み込みされます。サブディレクトリの `CLAUDE.md` は自動では戻らず、そのディレクトリのファイルを次に読んだときに再読み込みされます。
会話中だけで伝えた指示は消えるので、残したいなら `CLAUDE.md` に書いてください。

---

## 10-5. コストとトークンを節約する

### 現状を把握する

```text
/usage      （/cost も同じ）
```

- **サブスクリプション利用者**: プラン上限に対する使用状況、スキル・サブエージェント・プラグイン・MCP サーバーごとの内訳が見られます。`d` / `w` で 24 時間 / 7 日間を切り替えられます
- **API 利用者**: セッションのトークン数と概算コストが表示されます（標準料金での**ローカル計算**なので、実際の請求とは異なる場合があります）

```text
/context
```

今何がコンテキストを占めているかを可視化します。

### 効果の大きい順に

**1. タスクの区切りで `/clear` する**

最も効果があります。古い文脈はその後のすべてのメッセージでトークンを消費し続けます。
`/rename` で名前を付けてから `/clear` すれば、後で `/resume` で戻れます。

**2. モデルを使い分ける**

Sonnet はほとんどのコーディングタスクを十分こなし、Opus より安価です。Opus は複雑なアーキテクチャ判断や多段の推論が必要なときに使ってください。

```text
/model
```

サブエージェントには `model: haiku` を指定して、単純な作業を安いモデルに回すこともできます。

**3. 具体的なプロンプトを書く**

「このコードベースを改善して」は広範なスキャンを引き起こします。「auth.ts の login 関数に入力バリデーションを追加して」なら最小限のファイル読み込みで済みます。

**4. プランモードを使う**

方針が間違っていた場合の作り直しは高くつきます。複雑なタスクでは、先に計画を確認してから実装させてください。

**5. サブエージェントに回す**

テスト実行、ドキュメント取得、ログ処理などの冗長な出力は、サブエージェント側のコンテキストに閉じ込めて、要約だけ受け取ります。

**6. CLAUDE.md からスキルへ移す**

`CLAUDE.md` はセッション開始時に常に読み込まれます。特定の作業でしか使わない詳細な手順はスキルに移してください。スキルは必要になったときだけ読み込まれます。

**7. MCP のオーバーヘッドを減らす**

- 使っていないサーバーは `/mcp` で無効化する
- CLI ツール（`gh`、`aws`、`gcloud`）で代替できるならそちらを使う

**8. 拡張思考（extended thinking）を調整する**

思考トークンは出力トークンとして課金されます。単純なタスクでは `/effort` で努力度を下げるか、`/config` で無効化できます。

**9. フックで前処理する**

10,000 行のログを読ませる代わりに、フックで `ERROR` 行だけ抽出して返せば、数万トークンが数百トークンになります。
→ [08-3 フック](08-extensions.md#hooks)

**10. 型付き言語ならコードインテリジェンスプラグインを入れる**

grep で候補ファイルを何個も読む代わりに、1 回の定義ジャンプで済みます。

### なぜ長いセッションで消費が増えるのか

| 原因 | 説明 |
| --- | --- |
| **長いコンテキスト** | 毎リクエストで会話全体が送られる。プロンプトキャッシュがあっても、キャッシュ料金は発生する |
| **キャッシュミス** | 一定時間空けた後の最初のメッセージはキャッシュを外し、全コンテキストを再処理する |
| **定期タスク** | アイドル中でも間隔ごとに発火し、毎回コンテキスト全体を送る |
| **エージェントチームメイト** | 終了するまでトークンを消費し続ける |
| **コンパクション** | `/compact` は要約対象の会話を読むので、それ自体が大きなリクエストになる。継続が不要なら `/clear` のほうが安い（コストゼロ） |

### 上限に達したときのメッセージの読み分け

| メッセージ | 意味 |
| --- | --- |
| 「セッション上限に達しました」「週次の上限に達しました」 | サブスクリプションの使用枠。**モデルを切り替えても回復しません**。リセット時刻が表示されます |
| コンテキスト / 自動圧縮の警告 | 使用上限ではありません。会話がモデルの最大入力サイズに近づいたため、古い履歴を要約しています |
| Opus の上限に達しました | モデル固有の上限。`/model` で切り替えれば作業は続けられます |

`/usage-credits` で追加のクレジットをリクエストできる場合があります（claude.ai サブスクリプションでログインしている場合）。

---

## 10-6. それでも解決しないとき

1. `/doctor` で環境チェック、`/mcp` で MCP の状態確認
2. `/feedback` で Anthropic に直接問題を報告
3. [GitHub リポジトリ](https://github.com/anthropics/claude-code) の既知の Issue を確認
4. **Claude 自身に聞く**。Claude Code は自分のドキュメントを参照できます

```text
フックが発火しない原因を調べて。設定は .claude/settings.json にある
```

アカウント・請求・サブスクリプションの問題は Anthropic のサポートへ。[claude.ai](https://claude.ai)（Console 利用者は [platform.claude.com](https://platform.claude.com)）にサインインし、左下のイニシャルをクリックして **Get help** を選択してください。

---

## 次に読む

- コマンドを一覧で確認する → [11 コマンド早見表](11-cheatsheet.md)

**公式ドキュメント**: https://code.claude.com/docs/en/troubleshooting / https://code.claude.com/docs/en/errors / https://code.claude.com/docs/en/costs
