# 02. インストールとセットアップ

> **この章でわかること**
> - OS 別のインストール手順と確認方法
> - ログインのやり方と、アカウント種別ごとの違い
> - VS Code / JetBrains / デスクトップ / Web 版のはじめ方
> - アップデートとアンインストール

---

## 2-1. 事前に必要なもの

- ターミナル（コマンドプロンプト、PowerShell、iTerm2、Windows Terminal など）
- 作業対象のコードプロジェクト（git リポジトリだとより便利）
- Claude のアカウント（[01-4 必要なアカウントとプラン](01-overview.md#1-4-必要なアカウントとプラン) を参照）

---

## 2-2. インストール

### ネイティブインストール（推奨）

**バックグラウンドで自動更新される**ため、この方法が最も手間がかかりません。

**macOS / Linux / WSL**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell**

```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows コマンドプロンプト（CMD）**

```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

> **PowerShell と CMD を間違えたときのエラー**
> - `The token '&&' is not a valid statement separator` → PowerShell にいます。PowerShell 用のコマンドを使ってください
> - `'irm' is not recognized as an internal or external command` → CMD にいます。CMD 用のコマンドを使ってください
> - 見分け方: プロンプトが `PS C:\` なら PowerShell、`C:\` だけなら CMD

> **Windows ネイティブで使う場合**
> [Git for Windows](https://git-scm.com/downloads/win) を入れておくことを推奨します。入っていれば Claude Code が Bash ツールを使えます。無い場合は PowerShell がシェルツールとして使われます。WSL を使う場合は不要です。

### パッケージマネージャを使う場合

**Homebrew（macOS / Linux）**

```bash
brew install --cask claude-code
```

Homebrew には 2 つの cask があります。

| cask | 説明 |
| --- | --- |
| `claude-code` | 安定版チャンネル。おおむね 1 週間遅れ。大きな不具合のあるリリースはスキップされる |
| `claude-code@latest` | 最新版チャンネル。リリースされ次第すぐ届く |

**Homebrew 版は自動更新されません。** 定期的に `brew upgrade claude-code`（または `claude-code@latest`）を実行してください。

**WinGet（Windows）**

```powershell
winget install Anthropic.ClaudeCode
```

こちらも自動更新されないので、`winget upgrade Anthropic.ClaudeCode` を定期的に実行します。

**Linux パッケージマネージャ**

Debian / Ubuntu（apt）、Fedora / RHEL（dnf）、Alpine（apk）でもインストールできます。詳しくは公式の [Advanced setup](https://code.claude.com/docs/en/setup) を参照してください。

### インストールできたか確認する

```bash
claude --version
```

`2.1.234 (Claude Code)` のようにバージョン番号と `(Claude Code)` が表示されれば成功です。

`command not found` が出る場合は PATH が通っていない可能性があります。ターミナルを開き直す、それでもダメなら [10 トラブルシューティング](10-troubleshooting.md) を参照してください。

---

## 2-3. ログイン

インストール直後、プロジェクトディレクトリで `claude` を実行するとログインを求められます。

```bash
cd ~/path/to/your-project
claude
```

画面の指示に従ってブラウザで認証を完了させます。**一度ログインすれば認証情報が保存される**ので、次回以降は不要です。

### セッション中にログインし直す / アカウントを切り替える

```text
/login
```

ログアウトは `/logout`、状態確認は `claude auth status`（シェルから実行）です。

### 環境変数 `ANTHROPIC_API_KEY` を設定している場合

ログイン画面はスキップされ、「そのキーを使ってよいか」の確認だけが表示されます。

### 選べるアカウント種別

- Claude Pro / Max / Team / Enterprise（推奨）
- Claude Console（API・プリペイドクレジット）
- Amazon Bedrock / Google Cloud の Agent Platform / Microsoft Foundry（企業向けクラウド）
- 組織が運用する Claude apps gateway（企業 SSO でログイン）

---

## 2-4. 最初のセッションを起動する

```bash
cd /path/to/your/project
claude
```

起動すると、プロンプトの上にバージョン・使用中のモデル・作業ディレクトリが表示されます。

まずはこれを試してください。

| 入力 | 何が起きるか |
| --- | --- |
| `/help` | 使えるコマンドの一覧が出る |
| `このプロジェクトは何をするもの？` | ファイルを読んで要約してくれる |
| `/status` | 現在のセッションの状態を表示 |
| `/exit` | 終了（`Ctrl+D` を2回でも可） |

> **ポイント**
> Claude Code は必要に応じて自分でファイルを読みます。事前にコンテキストとしてファイルを渡す必要はありません。

---

## 2-5. IDE・デスクトップ・Web 版のはじめ方

### VS Code / Cursor 拡張

エディタ内で差分表示、`@` メンション、プランのレビュー、会話履歴の閲覧ができます。

1. 拡張機能ビュー（`Cmd+Shift+X` / `Ctrl+Shift+X`）を開く
2. 「Claude Code」を検索してインストール
3. コマンドパレット（`Cmd+Shift+P` / `Ctrl+Shift+P`）で「Claude Code」と入力し、**Open in New Tab** を選択

### JetBrains（IntelliJ IDEA / PyCharm / WebStorm など）

1. JetBrains Marketplace から Claude Code プラグインをインストール
2. IDE を再起動

**JetBrains プラグインは Claude Code CLI を別途必要とします。** 先に CLI をインストールしておいてください。

### デスクトップアプリ

差分の視覚的なレビュー、複数セッションの並行実行、定期タスクのスケジュール、クラウドセッションの起動ができます。

- macOS（Intel / Apple Silicon）、Windows（x64 / ARM64）向けに配布
- インストール後、サインインして **Code** タブから開始
- **有料サブスクリプションが必要**です

ダウンロードリンクは [公式 Overview ページ](https://code.claude.com/docs/en/overview) を参照してください。

### Web 版（ブラウザ）

ローカル環境のセットアップ無しで使えます。[claude.ai/code](https://claude.ai/code) にアクセスするだけです。

- GitHub アカウントの接続が必要（Claude GitHub App を認可、または `/web-setup` でローカルの `gh` トークンを同期）
- Anthropic 管理の隔離された VM 上で動作
- ブラウザを閉じてもセッションは動き続ける
- 詳しくは [09 自動化とチーム利用](09-automation.md#9-5-web-版とモバイル) を参照

---

## 2-6. アップデート

| インストール方法 | アップデート方法 |
| --- | --- |
| ネイティブインストール | **自動**（バックグラウンドで更新） |
| Homebrew | `brew upgrade claude-code` または `brew upgrade claude-code@latest` |
| WinGet | `winget upgrade Anthropic.ClaudeCode` |
| 手動 | `claude update` |

**Claude Code は更新が速いプロダクトです。** 「ドキュメントに書いてある機能が見当たらない」ときは、まずバージョンを確認してください。

```bash
claude --version
```

---

## 2-7. 最初にやっておくと良い設定

必須ではありませんが、早い段階でやっておくと体験が大きく変わります。

### 1. `/init` でプロジェクトのルールファイルを作る

セッション内で実行します。

```text
/init
```

Claude がコードベースを解析して、ビルドコマンド・テストコマンド・コーディング規約などをまとめた `CLAUDE.md` を作ってくれます。これは**毎回のセッション開始時に自動で読み込まれる**ファイルです。
→ 詳しくは [06 CLAUDE.md とメモリ](06-claude-md.md)

### 2. `gh` などの CLI ツールを入れる

GitHub を使うなら `gh` CLI を入れておくと、Issue の作成・PR のオープン・コメントの読み取りを Claude が直接できるようになります。API 経由より効率的です。

```bash
# 例: macOS
brew install gh && gh auth login
```

### 3. 使うモデルを決めておく

`/model` で選ぶと、その選択は次回以降のセッションにも引き継がれます。環境変数で既定を決めることもできます。

```bash
export ANTHROPIC_DEFAULT_MODEL=sonnet   # 新規セッションが開始するモデル（v2.1.236 以降）
```

この変数は、`--model`・`ANTHROPIC_MODEL`・設定ファイルの `model` のいずれも指定が無いときにだけ効きます。

### 4. ターミナルの設定（改行を打ちやすくする）

複数行入力をしたいとき、`Shift+Enter` が効かない環境があります。VS Code、Cursor、Alacritty、Zed を使っている場合は、セッション内で以下を実行するとキーバインドが設定されます。

```text
/terminal-setup
```

---

## つまずいたら

- インストール・ログインが失敗する → [10 トラブルシューティング](10-troubleshooting.md)
- セッション内で `/doctor` を実行すると、環境をチェックして修正を提案してくれます
- `claude` が起動すらしない場合は、シェルから `claude doctor` を実行します

---

## 次に読む

- 操作方法を覚える → [03 基本操作](03-basics.md)

**公式ドキュメント**: https://code.claude.com/docs/en/quickstart / https://code.claude.com/docs/en/setup
