# 11. コマンド早見表

> **この章でわかること**
> - シェルから使う CLI コマンドとフラグ
> - セッション内で使うスラッシュコマンドの全一覧
> - キーボードショートカット
> - 設定ファイルの置き場所

利用できるコマンドはプラットフォーム・プラン・環境によって異なります。手元で使えるものは `/help` または `/` で確認してください。

---

## 11-1. シェルコマンド

### 起動・再開

| コマンド | 説明 |
| --- | --- |
| `claude` | 対話セッションを開始 |
| `claude "タスク"` | 最初のプロンプトを渡して開始 |
| `claude -p "質問"` | 非対話で実行して終了 |
| `cat file \| claude -p "質問"` | パイプ入力を処理 |
| `claude -c` | 直近の会話を再開 |
| `claude -r "<セッション>" "質問"` | ID か名前でセッションを再開 |
| `claude --teleport` | クラウドセッションをターミナルに引き継ぐ |
| `claude --cloud "タスク"` | クラウドセッションを新規作成 |
| `claude --bg "タスク"` | バックグラウンドエージェントとして開始 |

### 管理・診断

| コマンド | 説明 |
| --- | --- |
| `claude --version` | バージョン確認 |
| `claude update` | 最新版に更新 |
| `claude doctor` | インストール・設定を診断 |
| `claude auth login` / `logout` / `status` | 認証の操作・確認 |
| `claude mcp` | MCP サーバーを設定 |
| `claude mcp list` | MCP サーバーの一覧と接続状態 |
| `claude mcp login <名前>` / `logout <名前>` | MCP の OAuth |
| `claude plugin install <名前>` | プラグインをインストール |
| `claude agents` | エージェントビューを開く |
| `claude attach <id>` / `logs <id>` / `stop <id>` / `rm <id>` | バックグラウンドセッションの操作 |
| `claude auto-mode defaults` | auto モードの分類ルールを JSON で出力 |
| `claude setup-token` | 長期有効な OAuth トークンを生成 |
| `claude self-hosted-runner setup` | セルフホスト環境のランナーを構築（Team / Enterprise） |

### よく使うフラグ

**セッション**

| フラグ | 説明 |
| --- | --- |
| `-p`, `--print` | 非対話モード |
| `-c`, `--continue` | 直近の会話を再開 |
| `-r`, `--resume` | セッションを指定して再開 |
| `-n`, `--name` | セッションに表示名を付ける |
| `--fork-session` | 再開時に新しいセッション ID を作る |
| `--no-session-persistence` | セッションを保存しない |

**モデル・思考**

| フラグ | 説明 |
| --- | --- |
| `--model` | モデルを指定（`sonnet` / `opus` / `haiku` / `fable`） |
| `--effort` | 努力度（`low` / `medium` / `high` / `xhigh` / `max` / `ultracode`） |
| `--fallback-model` | フォールバック先のモデル |

**権限**

| フラグ | 説明 |
| --- | --- |
| `--permission-mode` | `default` / `acceptEdits` / `plan` / `auto` / `dontAsk` / `bypassPermissions` |
| `--allowedTools` | 確認なしで使えるツール |
| `--disallowedTools` | 使わせないツール |
| `--tools` | 使える組み込みツールを制限 |
| `--dangerously-skip-permissions` | すべての確認をスキップ（**隔離環境のみ**） |

**ファイル・ディレクトリ**

| フラグ | 説明 |
| --- | --- |
| `--add-dir` | 作業ディレクトリを追加 |
| `-w`, `--worktree` | git worktree を作ってそこで作業。PR / マージリクエストの URL を渡すとそのブランチから開始 |
| `--tmux` | worktree 用の tmux セッションを作る |

**出力**

| フラグ | 説明 |
| --- | --- |
| `--output-format` | `text` / `json` / `stream-json` |
| `--json-schema` | スキーマに沿った JSON 出力 |
| `--verbose` | 詳細ログ |

**制限**

| フラグ | 説明 |
| --- | --- |
| `--max-turns` | エージェントのターン数上限 |
| `--max-budget-usd` | API 呼び出しの上限金額 |

**その他**

| フラグ | 説明 |
| --- | --- |
| `--append-system-prompt` | システムプロンプトに追記 |
| `--mcp-config` | MCP サーバー定義を JSON から読み込む |
| `--settings` | 設定 JSON のパス、またはインライン JSON |
| `--safe-mode` | すべてのカスタマイズを無効化（切り分け用） |
| `--debug` | デバッグモード（`--debug "api,mcp"` のように絞り込み可） |
| `--ide` | IDE に自動接続 |
| `--agents` | サブエージェントを JSON で動的に定義 |

---

## 11-2. スラッシュコマンド

### セッション・コンテキスト

| コマンド | 説明 |
| --- | --- |
| `/clear`（`/reset`, `/new`） | 会話をリセット |
| `/compact [指示]` | 会話を要約してコンテキストを空ける |
| `/context [all]` | コンテキストの使用状況を可視化 |
| `/rewind [checkpoint]` | コードと会話をチェックポイントに巻き戻す |
| `/resume [名前]` | 過去の会話に戻る |
| `/branch [名前]` | 現在の会話を分岐させる |
| `/fork [プロンプト]` | 会話をコピーして新しいバックグラウンドセッションへ |
| `/rename` | セッションに名前を付ける |
| `/export [ファイル名]` | 会話をテキストで書き出す |
| `/copy [N]` | 直前の応答をクリップボードへ |
| `/btw [質問]` | 会話履歴に残さず質問する |
| `/status` | セッションの状態を表示 |
| `/exit`（`/quit`） | 終了 |

### 設定・メモリ

| コマンド | 説明 |
| --- | --- |
| `/init` | プロジェクト用の `CLAUDE.md` を生成 |
| `/memory` | `CLAUDE.md` とオートメモリを編集 |
| `/config`（`/settings`） | 設定画面を開く |
| `/permissions` | 承認ルールを設定 |
| `/model [モデル]` | モデルを切り替え |
| `/effort [レベル]` | 努力度を設定 |
| `/fast [on\|off]` | 高速モードの切り替え |
| `/keybindings` | キーバインド設定ファイルを開く |
| `/add-dir <パス>` | 作業ディレクトリを追加 |
| `/cd <パス>` | 作業ディレクトリを移動 |

### 拡張機能

| コマンド | 説明 |
| --- | --- |
| `/agents` | サブエージェントの設定を管理 |
| `/skills` | カスタムスキルを管理 |
| `/hooks` | 設定されているフックを閲覧 |
| `/mcp` | MCP サーバーの接続を管理 |
| `/plugins` | プラグインを管理 |
| `/subtask <指示>` | 会話を引き継いだサブエージェント（fork）に脇道タスクを渡す |
| `/tasks` | バックグラウンド作業の一覧 |
| `/list-agents`（`/peers`） | メッセージを送れる他のセッションを一覧表示 |
| `/reload-plugins` | プラグインを再読み込み |

### 開発ワークフロー

| コマンド | 説明 |
| --- | --- |
| `/plan` | プランモードに切り替え |
| `/diff` | 未コミットの変更を差分ビューアで表示 |
| `/code-review [レベル] [--fix]`（`/review`） | 差分をバグ観点でレビュー。バックグラウンドで実行され、レベル省略時は前回の指定を再利用 |
| `/design [指示]` | UI の設計案を編集可能なアートボードとして描く（リサーチプレビュー） |
| `/claude-security` | 複数エージェントによる脆弱性スキャン（プラグインの導入が必要） |
| `/security-review` | 差分をセキュリティ観点でチェック |
| `/simplify` | コードの簡素化を提案・適用 |
| `/test [ファイル]` | テストを実行して失敗をデバッグ |
| `/verify` | 変更が要件を満たすか検証 |
| `/pr-feedback` | オープン中の PR のフィードバックを取得 |
| `/pr-summary` | オープン中の PR の変更を要約 |
| `/autofix-pr` | PR を監視して CI 失敗時に修正をプッシュ |
| `/batch <指示>` | 大規模変更をコードベース全体に並列適用 |
| `/goal [条件]` | 達成すべきゴールを設定し、満たすまで作業させる |

### 連携・移動

| コマンド | 説明 |
| --- | --- |
| `/desktop`（`/app`） | デスクトップアプリで継続 |
| `/web` | ブラウザで開く |
| `/teleport`（`/tp`） | クラウドセッションをターミナルに引き継ぐ |
| `/remote-control` | 他のデバイスから操作できるようにする |
| `/mobile`（`/ios`, `/android`） | モバイルアプリの QR コードを表示 |
| `/background`（`/bg`） | セッションをバックグラウンドエージェントに切り離す |
| `/install-github-app` | Claude GitHub App をインストール |
| `/install-slack-app` | Claude Slack アプリをインストール |
| `/chrome` | Chrome 連携の設定 |

### 診断・サポート

| コマンド | 説明 |
| --- | --- |
| `/help` | ヘルプとコマンド一覧 |
| `/doctor`（`/checkup`） | 環境チェックと修正提案 |
| `/debug [説明]` | デバッグログを有効化して問題を切り分け |
| `/usage`（`/cost`） | トークン使用量とコスト |
| `/insights` | セッションの分析レポート |
| `/feedback [内容]` | 製品フィードバックを送る |
| `/bug`（`/share`） | バグ報告・会話の共有 |
| `/fewer-permission-prompts` | 承認プロンプトを減らす許可リストを提案 |
| `/login` / `/logout` | サインイン / サインアウト |

### その他

| コマンド | 説明 |
| --- | --- |
| `/loop [間隔] [プロンプト]` | プロンプトを一定間隔で繰り返す |
| `/deep-research <質問>` | Web 検索を並列展開して出典付きレポートを作る |
| `/advisor [モデル\|off]` | 難しい判断で第2のモデルに相談する機能の切り替え |
| `/focus` | フォーカス表示（要約のみ）の切り替え |
| `/color [色]` | プロンプトバーの色を変える |

---

## 11-3. キーボードショートカット

### 最重要

| キー | 動作 |
| --- | --- |
| `Esc` | Claude を中断（作業は保持される） |
| `Esc` `Esc` | 巻き戻しメニュー（入力が空のとき）／入力クリア |
| `Shift+Tab` | 権限モードを切り替え |
| `Ctrl+G` | プロンプト・プランを外部エディタで開く |

### 全般

| キー | 動作 |
| --- | --- |
| `Ctrl+C` | 中断／入力クリア（2回で終了） |
| `Ctrl+D` | 終了（2回押し） |
| `Ctrl+L` | 画面を再描画 |
| `Ctrl+O` | トランスクリプトビューアの切り替え |
| `Ctrl+R` | コマンド履歴の逆順検索 |
| `Ctrl+B` | 実行中のタスクをバックグラウンドへ |
| `Ctrl+T` | TODO チェックリストの表示切り替え |
| `Ctrl+S` | 入力の一時退避／復元 |
| `Ctrl+Z` | プロセスを一時停止（Unix のみ。`fg` で復帰） |
| `Alt+P` / `Option+P` | モデルを切り替え |
| `Alt+T` / `Option+T` | 拡張思考の切り替え |
| `Alt+O` / `Option+O` | 高速モードの切り替え |
| `?`（入力が空のとき） | ショートカットのヘルプパネル |

### 入力

| キー | 動作 |
| --- | --- |
| `/` | コマンド・スキルの一覧 |
| `@` | ファイルパスの補完 |
| `!` | シェルモード（コマンドを実行して結果を渡す） |
| `Ctrl+V` / `Cmd+V` / `Alt+V` | クリップボードから画像を貼り付け |
| `\` + `Enter` / `Ctrl+J` / `Shift+Enter` | 改行（複数行入力） |
| `↑` / `↓` | カーソル移動／コマンド履歴 |

### テキスト編集

| キー | 動作 |
| --- | --- |
| `Ctrl+A` / `Ctrl+E` | 行頭 / 行末へ |
| `Ctrl+K` / `Ctrl+U` | カーソル以降 / 以前を削除 |
| `Ctrl+W` | 直前の単語を削除 |
| `Ctrl+Y` | 削除したテキストを貼り付け |
| `Alt+B` / `Alt+F` | 単語単位で移動 |

---

## 11-4. 主なファイルの置き場所

### プロジェクト内

```
your-project/
├── CLAUDE.md                    # プロジェクトの指示（git 管理）
├── CLAUDE.local.md              # 個人のメモ（.gitignore へ）
├── .mcp.json                    # プロジェクト共有の MCP サーバー（git 管理）
└── .claude/
    ├── CLAUDE.md                # CLAUDE.md の別の置き場所
    ├── settings.json            # プロジェクト設定（git 管理）
    ├── settings.local.json      # 個人のプロジェクト設定（.gitignore へ）
    ├── rules/
    │   ├── testing.md           # トピック別ルール
    │   └── api-design.md        # paths フロントマターでスコープ可
    ├── skills/
    │   └── deploy/SKILL.md      # → /deploy
    ├── agents/
    │   └── security-reviewer.md # カスタムサブエージェント
    └── commands/                # 旧形式のカスタムコマンド（今も動く）
```

### ユーザー単位

```
~/.claude/
├── CLAUDE.md                    # 全プロジェクト共通の個人設定
├── settings.json                # ユーザー設定
├── keybindings.json             # キーバインド
├── rules/                       # 個人のルール
├── skills/                      # 個人のスキル
├── agents/                      # 個人のサブエージェント
└── projects/<project>/memory/   # オートメモリ
    ├── MEMORY.md
    └── ...
~/.claude.json                   # MCP サーバー（local / user スコープ）
```

### 組織（管理者）

| OS | パス |
| --- | --- |
| macOS | `/Library/Application Support/ClaudeCode/CLAUDE.md` |
| Linux / WSL | `/etc/claude-code/CLAUDE.md` |
| Windows | `C:\Program Files\ClaudeCode\CLAUDE.md` |

---

## 11-5. 主な設定キー

`~/.claude/settings.json` や `.claude/settings.json` に書きます。

| キー | 内容 |
| --- | --- |
| `permissions.defaultMode` | 既定の権限モード（`auto` はユーザー設定にのみ書ける） |
| `permissions.allow` / `ask` / `deny` | ツールごとの許可・確認・拒否ルール |
| `outputStyle` | 出力スタイル（`Concise` / `Proactive` / `Explanatory` / `Learning`） |
| `model` | 使用するモデル |
| `crossSessionInbound` | 他セッションからのメッセージの扱い（`accept` / `hold` / `refuse`） |
| `isolatePeerMachines` | 別マシンへのメッセージ送信に承認を要求する |
| `keybindingFlavor` | `"readline"` にすると `Ctrl+W` が空白まで削除する |
| `spellcheck` | 入力中の綴り誤りに下線を引く |
| `emojiCompletionEnabled` | 絵文字ショートコードの補完 |
| `autoMemoryEnabled` | オートメモリの有効・無効 |
| `sandbox.filesystem.disabled` | ファイルシステム隔離だけを外す |
| `claudeMdExcludes` | 読み込まない CLAUDE.md をパターンで指定 |
| `hooks` | フックの定義 |

## 11-6. 主な環境変数

| 変数 | 内容 |
| --- | --- |
| `ANTHROPIC_DEFAULT_MODEL` | 新規セッションが開始するモデル（v2.1.236 以降） |
| `ANTHROPIC_MODEL` | 使用するモデル（設定より優先） |
| `ANTHROPIC_API_KEY` | API キー認証 |
| `CLAUDE_CODE_FORK_SUBAGENT` | `0` で fork モードを無効化 |
| `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` | サブエージェントの同時実行数（既定 20） |
| `CLAUDE_CODE_ENABLE_TODO_TOOLS` | `1` で TODO 管理ツールを再有効化 |
| `CLAUDE_CODE_TOOL_MEMORY_LIMIT` | Bash / PowerShell ツールのメモリ上限（Linux / WSL） |
| `CLAUDE_CODE_GOAL_CHECKIN_MINUTES` | `/goal` の待機中の確認間隔（`0` で無効） |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` でエージェントチームを有効化 |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 自動圧縮を始める使用率 |
| `USE_BUILTIN_RIPGREP` | `0` でシステムの ripgrep を使う |
| `MAX_THINKING_TOKENS` | 思考トークンの上限（固定budget のモデルのみ） |

## 11-7. 権限モード早見

| モード | 確認なしで実行 | 切り替え |
| --- | --- | --- |
| `default`（Manual） | 読み取りのみ | `Shift+Tab` |
| **既定** | **2026年8月14日以降、Pro / Max / Team では `auto` が新規セッションの既定** | — |
| `acceptEdits` | 読み取り＋編集＋基本ファイル操作 | `Shift+Tab` |
| `plan` | 読み取りのみ（編集ブロック） | `Shift+Tab` / `/plan` |
| `auto` | ほぼすべて（分類モデルが監視） | `Shift+Tab`（条件を満たす場合） |
| `dontAsk` | 事前承認したもののみ | `--permission-mode dontAsk` |
| `bypassPermissions` | すべて | `--dangerously-skip-permissions` |

---

**公式ドキュメント**: https://code.claude.com/docs/en/cli-reference / https://code.claude.com/docs/en/commands / https://code.claude.com/docs/en/interactive-mode
