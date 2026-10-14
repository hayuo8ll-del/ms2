# 14. 新機能まとめ（2026年6月〜10月）

> **この章でわかること**
> - 前回版（2026-08-26）以降に入った主な変更
> - 特に**挙動が変わった**もの（古い記述を直す必要があるもの）
> - どの機能がどの章で解説されているか

すでにガイドを読んだ方が、**差分だけ追える**ようにまとめた章です。はじめての方は [01 Claude Code とは](01-overview.md) から読んでください。

対象: Claude Code v2.1.195 〜 **v2.1.299**（2026年10月14日時点）

> **情報源について**
> 公式の週次ダイジェスト（What's new）は **2026年9月11日の週（v2.1.269）まで**です。それ以降の v2.1.270〜299 は公式の[変更履歴](https://code.claude.com/docs/en/changelog)から、主なものを整理しています。細かな修正は載せていません。

---

<a id="corrections"></a>

## 14-0. 前回版（8/26）からの訂正

前回までの記述で、**その後の変更により正しくなくなったもの**です。古い版を読んだ方は、ここを確認してください。

| 項目 | 前回の記述 | 現在 |
| --- | --- | --- |
| **auto モードの既定** | 8月14日から Pro / Max / Team の既定 | **v2.1.283 以降、ターミナルと VS Code の対話セッションは全プランで既定**（`claude -p` を除く） |
| **auto モードと使用量** | 分類モデルの呼び出しは使用量にカウントされない | Pro / Max / Team では従来どおりだが、**Enterprise と API・クラウドプロバイダでは加算される**。サーバー側審査が効く場合は別呼び出し自体が無い |
| **`keybindingFlavor`** | `"readline"` で `Ctrl+W` が空白まで削除 | **設定は効果なし。** 全員が readline 挙動になった（`Ctrl+W` は空白まで、`Alt+B` / `Alt+F` / `Alt+D` は `/` や `.` を区切りとする） |
| **`/agents`** | サブエージェントの設定を管理する画面 | **案内を表示するだけ**。作成・管理は Claude に頼むか、`.claude/agents/` を直接編集 |
| **AGENTS.md** | Claude Code は読まない | **`CLAUDE.md` が無いプロジェクトでは `AGENTS.md` を読む**（v2.1.277〜） |
| **既定の Opus** | Opus 5 | **Opus 5.5**。Pro / Team Standard の既定も Sonnet から Opus に（v2.1.280〜） |
| **`/output-style`** | 廃止済み（`/config` を使う） | **コマンドが復活**（`/output-style concise` のように使える） |
| **セッション間メッセージング** | Bedrock・Vertex・Foundry では不可 | **同じマシン上のセッション同士なら可**（v2.1.240〜250 の間に対応） |

---

## 14-1. まず知っておくべき「挙動が変わった」もの

新機能より先に、**これまでと動きが変わった点**を押さえてください。

### ⚠ auto モードが既定の権限モードになった（対象が拡大）

| 時期 | 内容 |
| --- | --- |
| 2026-08-14 | Pro / Max / Team の新規セッションの既定が `auto` に |
| v2.1.283（9月下旬） | **ターミナルと VS Code の対話セッションは、全プラン・全プロバイダで `auto`** |
| v2.1.285 | `claude -p` と Python の Agent SDK も、**機能フラグを取得しないセッション**（サードパーティプロバイダ、テレメトリ無効）では `auto` で始まる |

- 自分でデフォルトを設定している場合は**そのまま維持**されます（一度だけ切り替えの確認が出ますが、断れば変わりません）
- 組織が管理設定で指定したデフォルトも変わりません。**HIPAA 構成の組織は `default` のまま**です
- 慎重に進めたい作業では `Shift+Tab` で Manual に切り替えてください
- `auto` を既定にできるのは**ユーザー設定と管理設定だけ**です。**プロジェクトの `.claude/settings.json` に書いた `auto` と `bypassPermissions` は無視**され、Manual で始まります（`bypassPermissions` は v2.1.251〜261 の間に、`auto` はそれ以前から）

→ [07 権限とセキュリティ](07-permissions-security.md)

### ⚠ Ultraplan が廃止された

`/ultraplan` コマンドと `ultraplan` キーワードは削除されました。プランモード、または Claude Code on the web を使ってください。

### ⚠ サブエージェントが既定でバックグラウンド実行になった

対話セッションで Claude が起動するサブエージェントは、**既定でバックグラウンド実行**です。`context: fork` を持つスキルも同様です（フロントマターの `background: false` で同じターンで結果を待ちます）。

### ⚠ ツールの削除・変更

| 変更 | 内容 |
| --- | --- |
| TODO 管理ツール | `TaskCreate` / `TaskUpdate` / `TodoWrite` は、Opus 4.8・Sonnet 5 以降・Fable 5 以降などでは**提供されません**。戻すには `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` |
| **`TaskOutput` ツール** | **削除**（v2.1.277）。バックグラウンドタスクの出力は、そのファイルを Read で読みます。`taskOutputMaxChars` と `TASK_MAX_OUTPUT_LENGTH` は効果がなくなりました |
| `PermissionRequest` フック | **`agent` 型は動かなくなりました。** `command` か `http` 型を使います |
| MCP の許可ルール | `mcp__a` は **`a__b` に一致しなくなりました**（v2.1.299）。サーバー全体は `mcp__<サーバー名>__*` |
| `claude project purge` | **`claude purge` に改名**（旧名も動く） |
| `/pr-comments` / `/vim` | 削除済み（Claude に頼む／`/config` → Editor mode） |

---

<a id="model"></a>

## 14-2. モデルまわり

### 現在のラインナップ

| エイリアス | 解決先（Anthropic API） | 用途 |
| --- | --- | --- |
| `opus` | **Opus 5.5** | 複雑な推論。**多くのプラン・プロバイダの既定** |
| `sonnet` | **Sonnet 5.5** | 日常のコーディング |
| `haiku` | **Haiku 5.5** | 高速・低コスト。単純な作業・サブエージェント |
| `fable` | **Fable 5.1**（ゲートウェイ経由では Fable 5） | 最も難しく長い作業。**既定にはならない** |
| `best` | Fable が使えればそれ、なければ `opus` | — |
| `default` | （エイリアスではなく特殊値）アカウントの既定に戻す | — |
| `opusplan` | **計画は Opus、実行は Sonnet** | 計画の質を保ちつつコストを抑える。`opusplan[1m]` も可 |
| `opus[1m]` / `sonnet[1m]` | 100万トークン版 | 新しいモデルは `[1m]` 不要（下記） |

```text
/model claude-opus-5-5      # 名前を指定
/model fable                # エイリアス
```

**プロバイダによって解決先が違います。**

| プロバイダ | opus | sonnet | haiku |
| --- | --- | --- | --- |
| Anthropic API | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
| Claude Platform on AWS | Opus 5.5 | Sonnet 4.6 | Haiku 4.5 |
| Bedrock・Google Cloud の Agent Platform | Opus 5.5 | Sonnet 4.5 | Haiku 4.5 |
| Microsoft Foundry | Opus 4.6 | Sonnet 4.5 | Haiku 4.5 |

### 既定のモデルとコンテキスト

- **既定**: Pro・Max・Team・Enterprise・Anthropic API・Claude Platform on AWS・Bedrock・Agent Platform は **Opus 5.5**、Microsoft Foundry は Sonnet 4.5。**Fable はどのアカウントでも既定になりません**（選んだときだけ使われ、`/model` で選ぶと保存されます）
- **100万トークンが標準**: Fable 5.1・Sonnet 5 以降・Haiku 5.5・Opus 4.7 以降は `[1m]` 不要です。Bedrock・Vertex・Foundry・ゲートウェイでも同様です。200K に戻すには `CLAUDE_CODE_DISABLE_1M_CONTEXT=1`、ゲートウェイの上限が低いなら `/autocompact 200k`
- 自動圧縮は、100万トークン級のモデルでは**約 96.7 万トークン**あたりから始まります

### 料金の目安（各リリースの変更履歴の記載）

| モデル | 入力 / 出力（100万トークンあたり） | キャッシュ読み出し |
| --- | --- | --- |
| Opus 5.5 | $4 / $20 | $0.20 |
| Sonnet 5.5 | $2 / $10 | $0.10（v2.1.296 で $0.20 から引き下げ） |
| Haiku 5.5 | $0.10 / $0.50（10万トークン超は $0.50 / $2.50） | — |

> 料金は変わります。**最新は公式の料金ページで確認してください。**

### 努力度（effort）

| 項目 | 内容 |
| --- | --- |
| レベル | `low` / `medium` / `high` / `xhigh` / `max`（Opus 4.6・Sonnet 4.6 は `xhigh` なし） |
| 既定 | 多くのモデルで `high`。**Opus 5.5・Sonnet 5.5・Haiku 5.5 は `medium`**、Opus 4.7 は `xhigh` |
| **モデルごとに保存** | `/effort` や `/model` で `Enter` を押すと、**そのモデルの既定として保存**。`s` なら今回のセッションのみ |
| `max` | 今回のセッションのみ（`CLAUDE_CODE_EFFORT_LEVEL` で指定した場合を除く） |
| **ultracode** | **努力度ではなく別のトグル。** 動的ワークフローを計画させる。`/effort ultracode [on\|off]`、または `Tab`。`xhigh` を強制しなくなった（v2.1.284〜） |
| 上限を決める | `maxEffortLevel`（全プロバイダ。モデル別も可）。組織の上限があれば低いほうが適用 |
| 確認 | `/effort status` |

### モデル選択まわりの設定

```json
{
  "fallbackModel": ["claude-sonnet-5", "claude-haiku-4-5"]
}
```

- **`fallbackModel`**: サーバーエラー・過負荷のときに**順に試すモデル**（最大 3 つ、現在のターンのみ。認証・課金・レート制限では発動しない）。`--fallback-model sonnet,haiku` でも指定
- **`modelPicker`**: `/model` の一覧に**自分のエントリを追加・置換**します（Bedrock・Agent Platform の ID も指定可）
- **`ANTHROPIC_DEFAULT_MODEL`**: 新規セッションが開始するモデル（v2.1.236〜）。`--model`・`ANTHROPIC_MODEL`・設定ファイルの `model` が無いときだけ効きます
- 管理者向け: `availableModelsMatch: "exact"`（バージョンまで厳密に許可）、`deniedModels`（許可リストより優先して拒否）、`allowedProviders`（使える API プロバイダを制限）

---

## 14-3. セッション間メッセージング（新機能）

**あなたの複数の Claude Code セッションが、互いにメッセージを送れるようになりました。**

片方のセッションで見つけたことを、もう片方に伝え直す手間がなくなります。

```text
決済 API を触っているセッションに、users.name が users.display_name に変わったと伝えて
```

`@` を入力すると、他のセッションを名前で指定できます。

```text
@api-worker にスキーマ移行が終わったと伝えて
```

到達できるセッションの一覧はこれで確認します。

```text
/list-agents      （/peers も同じ）
```

**重要な性質**

- 送られるのは **Claude が書いたテキストだけ**。会話履歴やファイルは渡りません
- 受信側の**権限は変わりません**。メッセージが承認の代わりになることはなく、設定を変えさせることもできません
- メッセージ内の `/compact` などのコマンドは**ただのテキストとして届き、実行されません**
- 同一マシン内はソケット経由で、**Anthropic のサーバーを経由しません**
- 別マシンや Web のセッションへは、Remote Control 接続を通じて届きます

**対応環境**: macOS / Linux / WSL 2 は v2.1.224 以降、ネイティブ Windows は v2.1.234 以降。**Bedrock・Agent Platform・Foundry でも、同じマシン上のセッション同士なら使えます。** Claude Platform on AWS は公式ドキュメントの Availability を確認してください。

**受信の制御**

```json
{
  "crossSessionInbound": "accept"   // accept / hold / refuse
}
```

`/config` の **Messages from your other sessions** からも選べます。組織全体で止めるなら管理設定で `SendMessage` と `ListAgents` を `deny` に入れ、`crossSessionInbound` を `refuse` にします。

**別マシンへの送信に承認を挟む**

```json
{ "isolatePeerMachines": true }
```

---

## 14-4. fork（会話を引き継ぐサブエージェント）

**fork モードが既定で有効**になりました。`fork` 型のサブエージェントは、**それまでの会話全体とプロンプトキャッシュを引き継ぎます。**

通常のサブエージェントは白紙から始まるため、背景を説明し直す必要がありました。fork ならその手間がありません。

```text
/subtask ここまでのパーサー変更に対するユニットテストを書いて
```

無効にするには `CLAUDE_CODE_FORK_SUBAGENT=0` を設定します。

**関連する変更**

- 1 セッションあたりのサブエージェント総数の上限（200）が撤廃されました
- 同時実行は既定で 20。`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` で変更できます
- `/fork` でコピーしたセッションは、**自分専用の worktree** でコードを変更するようになりました

→ [08-5 サブエージェント](08-extensions.md#subagents)

---

## 14-5. 出力スタイル「Concise」

**Claude の返答から前置きと実況を省き、結果から書き始めさせる**組み込みスタイルです。作業の丁寧さは Default と変わりません。

```json
{ "outputStyle": "Concise" }
```

`/config` の **Output style** からも選べます。反映には `/clear` か新しいセッションが必要です。

**説明を求めれば通常どおり詳しく答えます。** また、エラー報告・セキュリティ警告・破壊的操作の確認は、常に完全な内容が保たれます。

組み込みスタイルは全部で 5 つです。

| スタイル | 内容 |
| --- | --- |
| **Default** | 標準 |
| **Concise** | 結果から書き始め、前置きを省く（v2.1.237 以降） |
| **Proactive** | 確認を挟まず即実行する。auto モードより強い自律実行の指示 |
| **Explanatory** | 作業しながら解説を挟む |
| **Learning** | `TODO(human)` を置いて、一部をあなたに実装させる |

---

## 14-6. `/design`（リサーチプレビュー）

UI の設計案を**編集可能なアートボード**として複数枚描き、気に入ったものを実装させられます。

```text
/design 申請フォームを、実際の利用状況に合わせて設計し直して
```

公開されたキャンバスへのリンクが表示されるので、開いて 1 つ選び、実装を指示します。
Pro / Max / Team / Enterprise で利用可能。v2.1.233 以降が必要です。

---

## 14-7. Claude Security プラグイン

**複数のエージェントによる脆弱性スキャン**をセッション内で実行します。アーキテクチャの把握 → 脅威モデル作成 → 脆弱性探索 → 各指摘の独立レビュー、という流れで、結果を `CLAUDE-SECURITY-<timestamp>/` に書き出します。

```text
/plugin install claude-security@claude-plugins-official
/reload-plugins
/claude-security
```

リポジトリ全体でも、ブランチの差分・PR・単一コミットだけでもスキャンできます。選んだ指摘を**レビュー済みのパッチ**に変換でき、適用は自分で行います。

---

## 14-8. GitLab 対応の強化

| 機能 | 内容 |
| --- | --- |
| worktree | `claude --worktree <マージリクエストURL>` で MR のブランチから作業を開始 |
| エージェントビュー | MR に紐づくセッションを `!N` として表示 |
| フッター表示 | `glab auth login` 済みなら `MR !N` バッジを表示（ドラフト・オープン・マージ可能で色分け） |
| マーケットプレイス | `gitlab.com` の URL をそのままクローン（ネストしたサブグループも可） |
| セキュリティ | `glpat-` / `glrt-` などの GitLab トークンを秘匿し、`glab` の設定を `gh` と同様に保護 |

```bash
claude --worktree https://gitlab.com/group/project/-/merge_requests/42
```

---

## 14-9. セルフホスト環境（Team / Enterprise パブリックベータ）

**クラウドセッションを自社のインフラで動かせます。** 社内ネットワーク内のサービスにアクセスできるため、業務システムの開発と相性が良い機能です。

```bash
claude self-hosted-runner setup
```

Owner が管理設定で **Allow self-hosted environments** を有効にしたうえで、自社のマシンやコンテナでランナーを起動します。claude.ai・モバイル・デスクトップ・`claude --cloud` からその環境を選ぶと、そのセッションは自社ネットワーク内で動きます。

---

## 14-10. その他の変更

### 使い勝手

| 変更 | 内容 |
| --- | --- |
| 使用上限の自動継続 | 上限に達しても、リセット後に中断したターンを自動で再開。`/config` の **Continue automatically at usage limit** で無効化可。デスクトップではセッション上限のカードに **Auto-continue when limits reset** が出る |
| 自分のプロンプトも Markdown 表示 | コードブロックやリストが返答と同じように整形される |
| 絵文字ショートコード | `:heart:` のように入力して絵文字を挿入。`emojiCompletionEnabled` で無効化可 |
| スペルチェック | `spellcheck` 設定で、入力中の綴り誤りに下線（`aspell` / `hunspell` / `ispell` を使用） |
| `Ctrl+W` の挙動 | **全員が readline 挙動に**なりました。`Ctrl+W` は直前の空白まで削除し、`Alt+B` / `Alt+F` / `Alt+D` は `/` や `.` を単語の区切りとして扱います（`keybindingFlavor` は効果なし） |
| 作業中の設定変更 | Claude が作業中でも `/permissions` を開いたり `/add-dir` を実行できる。権限ルールの変更はそのターンの残りから有効 |
| `/review` | `/code-review` のエイリアスに。効果レベルを省略すると前回指定した値を再利用 |
| `/goal` の待機 | バックグラウンド作業を待つとき、30 分ごとに確認を入れる。`CLAUDE_CODE_GOAL_CHECKIN_MINUTES=0` で無効化 |

### モバイル・Remote Control

- **Remote Control がリサーチプレビューを卒業**しました
- `claude remote-control` を実行しているマシンが、**スマホの Code タブに「デバイスカード」として表示**されます。タップしてディレクトリを選べば、その場でセッションを開始できます
- スマホや claude.ai/code から努力度（effort）を変えると、手元のマシンのセッションに反映されます

### 安全性

| 変更 | 内容 |
| --- | --- |
| worktree の隔離強化 | ファイル編集だけでなく、**メインのチェックアウトに届く Bash コマンドや git のリダイレクトもブロック** |
| Bash の権限チェック | コマンドの一部を隠して権限チェックを回避することができなくなった。タブや不可視 Unicode による偽装も無効 |
| PreToolUse フック | 自動承認フックが、要約や圧縮などの内部処理でツール制限を迂回できなくなった |
| Remote Control の自動接続 | リポジトリにコミットされた設定からは有効化できなくなった（無効化のみ可能） |
| サンドボックス | `sandbox.filesystem.disabled` でファイルシステム隔離だけを外し、ネットワーク制御は維持できる。Linux / WSL2 では認証情報ファイルの `mode: "mask"` に対応 |

### 開発・運用

| 変更 | 内容 |
| --- | --- |
| メモリ上限 | Linux / WSL で `CLAUDE_CODE_TOOL_MEMORY_LIMIT=4G` のように、Bash / PowerShell ツールのメモリを制限できる |
| `--max-budget-usd` | サブエージェントにも上限が効くようになった。到達すると新規起動が止まり、実行中のものも停止する |
| バックグラウンドセッション | worktree で変更したらコミット・プッシュしてから終了し、必要なときだけドラフト PR を作る。`CLAUDE.md` の git ルールにも従う |
| プラグイン配布 | zip アーカイブ（`archive` ソース、SHA-256 のピン留め可）と `command` ソースに対応。`/plugin install` はマーケットプレイスを自動更新してから実行 |
| 設定エイリアス | `additionalMarketplaces` / `allowedMarketplaces` が `extraKnownMarketplaces` / `strictKnownMarketplaces` の別名として使える |
| Write ツール | 新しいモデルでは、そのセッションで読んでいないファイルも上書きできるようになった（Edit と同じ規則） |
| VS Code 拡張 | **Focus view**（ツール実行をターンごとに 1 行に畳む。`Ctrl+Alt+F`）と、**セッションのグループ分け**に対応 |
| デスクトップ | macOS で **iOS シミュレータのペイン**（Pro / Max / Team のパブリックベータ）。Claude がアプリを操作する様子を見ながら確認できる |

---

## 14-11. 8月下旬〜10月の新機能（v2.1.240〜v2.1.299）

### 開発体験

| 機能 | 内容 |
| --- | --- |
| **`/diff` のライブパネル** | フルスクリーン表示（幅 110 桁以上・git リポジトリ内）で、**会話の横にパネル**が開き、Claude の編集のたびに更新されます。変更ファイルの追加・削除行数が並び、行をマウスで選んで次のプロンプトに添付できます（v2.1.260〜） |
| **`/skill-doctor`** | スキルごとの**コンテキスト消費と使用頻度**を表示。外すべきスキルの判断材料に（v2.1.252〜）→ [08](08-extensions.md#skills) |
| **今すぐ送信** | `Ctrl+Enter`（または `Ctrl+X` `Ctrl+S`）で、実行中のターンを中断して溜まったメッセージをまとめて送る。実行中のツールは**中断されずバックグラウンドへ**（v2.1.275/281） |
| **AGENTS.md** | `CLAUDE.md` が無いプロジェクトでは `AGENTS.md` を読む。`/config` の Project instructions で変更可 |
| **`/import`** | **OpenAI Codex・Google Gemini CLI・Cursor** の設定を取り込む（`--dry-run` で確認のみ） |
| **Claude が下書きするフィードバック** | ツールが失敗し続けたり、あなたが誤りを指摘したりすると、Claude が**報告の下書き**を作ってプロンプトの上にカード表示。**送信するまで何も送られません**。`/feedback` で下書きの一覧を開く。`/config` の **Claude-drafted feedback** で無効化（v2.1.238〜） |
| **`/code-review` の強化** | レベルに `ultra`、`--max-findings <n\|all>` を追加。調整済みでないモデルでは、多数のサブエージェントを起こさず軽量なプロンプトで動く |
| **`/rate-limit-options`** | 使用上限に当たったときの選択肢（待つ・自動継続・クレジット）を表示 |
| **`/doctor prompt-audit`** | `CLAUDE.md`・スキル・エージェント・コマンドを、**古いモデル向けの書き方**がないか診断 |
| **`/recap`** | セッションの要約を 1 行で出す |
| **`/mcp reconnect all`** | 失敗または認証待ちの MCP サーバーをまとめて再接続 |
| **`attribution: false`** | コミット・PR の帰属表記を非表示にする設定（v2.1.281〜）。古い CLI と共有するファイルではオブジェクト形式のまま |
| **WebFetch** | 5 分で取得が終わらないと**期限切れで失敗**（`CLAUDE_CODE_WEBFETCH_DEADLINE_MS`。`0` で無制限）。`CLAUDE_CODE_DISABLE_WEB_FETCH` でツールごと無効化 |
| Read ツール | `allow_large` で、通常の上限を超えるファイルを全文読める（v2.1.296） |
| **デスクトップ** | `/resume` で**CLI のセッションを引き継げる**。macOS では**バックグラウンドの computer use**（Pro / Max ベータ）。ペインを**別ウィンドウに切り出せる**。`claude --desktop` で CLI から開く |
| **VS Code** | モデル名のクリックでピッカー、**Output styles / Hooks / Permissions** をコマンドメニューから編集、エージェントマップ（サブエージェントのトランスクリプト閲覧・停止）、メッセージのタイムスタンプ（既定で表示）、「Run in background」 |

### 安全性・権限

| 変更 | 内容 |
| --- | --- |
| **サーバー側の分類審査** | 分類を通常のモデル呼び出しの一部として**サーバー側**で行う。直接の API 接続、クラウドプロバイダ、ゲートウェイで既定。審査結果が返らない操作は**実行されず拒否**（v2.1.271〜278） |
| **「Yes, and switch to auto mode」** | Manual / acceptEdits の Bash 確認に、承認と同時に auto へ切り替える選択肢（v2.1.247〜） |
| **作業ディレクトリ外の初回読み取り** | auto モードでは**確認が出る**。「ask again next time」で都度確認も選べる |
| **`/permissions` の Auto mode タブ** | 分類ルールを設定ファイルなしで編集 |
| **ブロック理由にルール名** | 拒否時に `[Data Exfiltration]` のように**一致したルール名**が Claude に伝わる |
| **新たに既定でブロック** | インスタンスメタデータ（`169.254.169.254`）への認証情報要求、Claude が起動していないコンテナ・Pod・VM への接続 |
| **危険な `rm`** | auto / `--dangerously-skip-permissions` で **2 分待って許可されなければ拒否**（`CLAUDE_CODE_DISABLE_DANGEROUS_RM_TIMEOUT=1` で無効） |
| **シンボリックリンク** | リポジトリにコミットされたシンボリックリンク経由で、機微なファイルや作業ツリーの外へ書く操作は、**書き込み先を示して人の承認を待つ** |
| **フックの失敗時** | `onFailure: "block"` で、失敗・タイムアウト時にアクションをブロック（v2.1.295〜） |
| **サブエージェントの結果** | 「サブエージェントの出力」と分かるヘッダー付きで届き、指示と取り違えられにくい |
| **設定の信頼境界** | プロジェクト設定から、Claude in Chrome の有効化・テレメトリ変数・`sandbox` の緩和・`CLAUDE_CODE_DISABLE_ATTACHMENTS` を**変更できない**ように |
| **`gh api`** | `GH_HOST` / `GH_REPO` で github.com 以外を指す場合は拒否 |

### プラグイン・拡張

| 変更 | 内容 |
| --- | --- |
| **`claude plugin eval`** | プラグインを**テストケースで採点**し、プラグインなしと比較（v2.1.269〜）→ [08-6](08-extensions.md) |
| **Mods** | プラグインが Claude Code の**挙動をより深く変える**仕組み（v2.1.287〜）。`/plugin-authoring` で作る |
| **インストールの安全性** | npm ソースは `npm pack --ignore-scripts`＋整合性検証。`--accept-command <sha256>`。`--marketplace` でマーケットプレイスの追加も同時に |
| **claude.ai との同期** | claude.ai で有効にしたスキル・プラグインがターミナルにも同期される（`syncClaudeAiSkills` / `syncClaudeAiPlugins` で無効化） |
| **サブエージェント** | フロントマターに `omitClaudeMd`・`autoCompactWindow`。Agent ツールに `effort`。プリロードできるスキルは最大 32 個 |
| **MCP** | プロトコル 2026-07-28 を既定で交渉（`MCP_PROTOCOL_NEGOTIATION=legacy` で旧方式）。`alwaysLoad: false` はそのサーバーの全ツールを tool search の後ろに遅延。ツール説明の上限は 2,048 → 4,096 文字 |
| **Monitor** | 監視には**必ず期限**がある（最大 30 分、`-p` の単発では 10 分） |

### 管理者・運用

| 設定・機能 | 内容 |
| --- | --- |
| **`--restricted`** | コマンド実行ツールなしで起動（共有マシンの評価ハーネス向け）→ [09-1](09-automation.md) |
| `managedMcpServers` | HTTP / SSE の MCP サーバーを**全ユーザーに配布** |
| `modelPricing` | 契約単価で `/usage`・ステータスライン・OpenTelemetry の金額を表示 |
| `allowedProviders` | 使える API プロバイダを制限 |
| `deniedModels` / `availableModelsMatch` | モデルの拒否と、バージョンまで厳密な許可 |
| `maxEffortLevel` | 努力度の上限（全プロバイダ） |
| セルフホストランナー | `--drain-marker-file`、`--defer-shutdown-max-min`、`--proxy-authorization-command` など。システムプロンプトは**ファイル渡し**（`--system-prompt-file`）に |
| `/login` | **Console アカウントでのサインイン**（API キーを許可しない Console 組織向け） |

### コスト・性能

| 変更 | 内容 |
| --- | --- |
| **アイドル圧縮** | 20 万トークン超が約 54 分アイドルなら、キャッシュ切れの前に自動圧縮（`idleCompaction: false` で無効）→ [10-5](10-troubleshooting.md) |
| **`/cost` のキャッシュ行** | `Prompt cache (main)`。ヒット率・ミス・直近のミスの推定原因 |
| **`/usage` の Loops 内訳** | `/loop` と定期タスクのトークン消費 |
| **インストーラが軽量に** | zstd 圧縮で Linux x64 は約 340 MB → 約 75 MB。必要なときにコードを読み込むため、**1 セッションあたり 40〜70 MB メモリ減** |
| **`bashOutputMaxChars`** | 成功したコマンドの出力を、より多く Claude に渡せる（最大 128,000 文字） |
| **リトライの上限** | 失敗した API リトライは 1 回の呼び出しあたり最大 14 リクエスト。無人実行は `CLAUDE_CODE_RETRY_WATCHDOG_MAX_WAIT_MS` で待ち時間に上限 |

---

## 14-12. 章別の参照先

| 新機能 | 解説している章 |
| --- | --- |
| auto モードの既定化、サーバー側審査、権限モード | [07 権限とセキュリティ](07-permissions-security.md) |
| fork、サブエージェント、プラグイン | [08 拡張機能](08-extensions.md) |
| セッション間メッセージング、セルフホスト環境、GitLab | [09 自動化とチーム利用](09-automation.md) |
| モデル選択、コスト | [10 トラブルシューティング](10-troubleshooting.md) |
| 出力スタイル、新コマンド、新設定 | [11 コマンド早見表](11-cheatsheet.md) |
| 自動化の進め方 | [12 業務自動化ロードマップ](12-automation-roadmap.md) |
| 業務での使いどころ | [13 活用事例](13-use-cases.md) |

---

**公式の更新情報**: https://code.claude.com/docs/en/whats-new/index
**変更履歴（全件）**: https://code.claude.com/docs/en/changelog
