# 14. 新機能まとめ（2026年6月〜8月）

> **この章でわかること**
> - 前バージョンのガイド（2026-07-31 時点）以降に入った主な変更
> - 特に挙動が変わったもの（**auto モードの既定化**など）
> - どの機能がどの章で解説されているか

すでにガイドを読んだ方が、**差分だけ追える**ようにまとめた章です。はじめての方は [01 Claude Code とは](01-overview.md) から読んでください。

対象: Claude Code v2.1.195 〜 v2.1.239（2026年8月26日時点）

---

## 14-1. まず知っておくべき「挙動が変わった」もの

新機能より先に、**これまでと動きが変わった点**を押さえてください。

### ⚠ auto モードが既定の権限モードになった

**2026年8月14日以降、Pro / Max / Team プランでは auto モードが新規セッションの既定**です。

| | 変更前 | 変更後 |
| --- | --- | --- |
| 新規セッションの既定 | Manual（読み取り以外は毎回確認） | **auto**（分類モデルが危険な操作だけブロック） |

- 自分でデフォルトを設定している場合は、**そのまま維持されます**（一度だけ出る切り替え確認に応じない限り）
- 組織が管理設定でデフォルトを指定している場合も変わりません
- `Shift+Tab` でいつでも切り替えられます
- **auto モードの分類モデル呼び出しは、使用量にカウントされなくなりました**

慎重に進めたい作業では Manual に切り替えてください。
→ [07 権限とセキュリティ](07-permissions-security.md)

### ⚠ Ultraplan が廃止された

`/ultraplan` コマンドと `ultraplan` キーワードは削除されました。プランモード、または Claude Code on the web を使ってください。
プラン承認時の選択肢からも消えています。

### ⚠ サブエージェントが既定でバックグラウンド実行になった

対話セッションで Claude が起動するサブエージェントは、**既定でバックグラウンド実行**になりました。待たされずに作業を続けられます。
`context: fork` を持つスキルも同様です（フロントマターに `background: false` を書くと同じターンで結果を待ちます）。

### ⚠ TODO 管理ツールが一部モデルで無効に

`TaskCreate` / `TaskUpdate` / `TodoWrite` などのタスク管理ツールは、**Opus 4.8・Sonnet 5・Fable 5・Mythos 5 以降のモデルでは提供されません**。
必要なら `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` で戻せます。

---

## 14-2. モデルまわり

### Claude Opus 5

新しい既定の Opus モデルです。

| 項目 | 内容 |
| --- | --- |
| 既定になるプラン | Max / Team Premium / Enterprise 従量課金 / Anthropic API / Claude Platform on AWS / Amazon Bedrock / Google Cloud の Agent Platform |
| コンテキストウィンドウ | **100万トークン**（API・Max・Team・Enterprise。Bedrock と Agent Platform では 1M 版を選択） |
| 高速モード | Opus 5 に対応（$10 / $50 per MTok） |

```text
/model claude-opus-5
```

**高速モードは Opus 4.7 に非対応になりました。** `/fast` は Opus 5 と Opus 4.8 に適用されます。

### モデルエイリアスの一覧

| エイリアス | 用途 |
| --- | --- |
| `default` | アカウントの既定に戻す（エイリアスではなく特殊値） |
| `best` | Fable 5 が使えるならそれ、なければ最新の Opus |
| `fable` | Claude Fable 5。最も難しく長い作業向け（既定にはならない） |
| `sonnet` | 最新の Sonnet。日常のコーディング |
| `opus` | 最新の Opus。複雑な推論 |
| `haiku` | 高速・低コスト。単純な作業 |
| `sonnet[1m]` / `opus[1m]` | 100万トークンのコンテキストウィンドウ |
| **`opusplan`** | **プランモードでは Opus、実行時は Sonnet に切り替える** |

> `opusplan` は業務でも使いやすい設定です。計画の質は Opus で担保し、実装は Sonnet のコストで回せます。

### 新しい環境変数

```bash
export ANTHROPIC_DEFAULT_MODEL=sonnet   # 新規セッションが開始するモデル（v2.1.236 以降）
```

`--model`、`ANTHROPIC_MODEL`、設定ファイルの `model` のいずれも指定が無いときにだけ効きます。`/model` での選択が優先されます。

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

**対応環境**: macOS / Linux / WSL 2 は v2.1.224 以降、ネイティブ Windows は v2.1.234 以降。Amazon Bedrock、Claude Platform on AWS、Google Cloud の Agent Platform、Microsoft Foundry では利用できません。

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
| `Ctrl+W` の挙動 | `keybindingFlavor: "readline"` にすると、Bash と同じく空白まで削除する |
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

## 14-11. 章別の参照先

| 新機能 | 解説している章 |
| --- | --- |
| auto モードの既定化、権限モード | [07 権限とセキュリティ](07-permissions-security.md) |
| fork、サブエージェント、プラグイン | [08 拡張機能](08-extensions.md) |
| セッション間メッセージング、セルフホスト環境、GitLab | [09 自動化とチーム利用](09-automation.md) |
| モデル選択、コスト | [10 トラブルシューティング](10-troubleshooting.md) |
| 出力スタイル、新コマンド、新設定 | [11 コマンド早見表](11-cheatsheet.md) |
| 自動化の進め方 | [12 業務自動化ロードマップ](12-automation-roadmap.md) |
| 業務での使いどころ | [13 活用事例](13-use-cases.md) |

---

**公式の更新情報**: https://code.claude.com/docs/en/whats-new/index
**変更履歴（全件）**: https://code.claude.com/docs/en/changelog
