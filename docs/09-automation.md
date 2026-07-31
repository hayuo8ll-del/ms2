# 09. 自動化とチーム利用

> **この章でわかること**
> - 非対話モード（`claude -p`）でスクリプト・CI に組み込む方法
> - 複数セッションを並列で動かす方法
> - GitHub Actions / GitLab CI との連携
> - 定期実行（Routines / `/loop`）
> - Web 版・モバイル・Slack との連携

---

## 9-1. 非対話モード（`claude -p`）

対話プロンプトを出さずに実行し、結果を出力して終了するモードです。**CI パイプライン、pre-commit フック、スクリプトへの組み込みはすべてこれを使います。**

```bash
# 一問一答
claude -p "このプロジェクトの概要を説明して"

# パイプで入力
cat error.log | claude -p "このログの異常を教えて"

# 構造化出力（スクリプトで処理する場合）
claude -p "すべての API エンドポイントを列挙して" --output-format json

# ストリーミング（リアルタイム処理）
claude -p "このログファイルを分析して" --output-format stream-json --verbose
```

### 出力フォーマット

| フォーマット | 内容 |
| --- | --- |
| `text`（デフォルト） | プレーンテキスト |
| `json` | `result` フィールドを持つ 1 個の JSON オブジェクト |
| `stream-json` | 1 行 1 JSON オブジェクト。init イベントから始まる |

### 自動化で使うと安全なフラグ

```bash
claude -p "lint エラーを直して" \
  --allowedTools "Edit" "Bash(npm run lint)" \
  --max-turns 10 \
  --max-budget-usd 5.00
```

| フラグ | 説明 |
| --- | --- |
| `--allowedTools` | 確認なしで使えるツールを明示。**無人実行では必須級** |
| `--disallowedTools` | 禁止するツール |
| `--max-turns` | エージェントのターン数上限 |
| `--max-budget-usd` | API 呼び出しの上限金額 |
| `--permission-mode dontAsk` | 事前承認したもの以外は自動拒否（CI 向け） |
| `--no-session-persistence` | セッションを保存しない |

> `-p` での実行も、デフォルトでは再開可能なセッションを作ります。

---

## 9-2. 多数のファイルに一括適用する（ファンアウト）

大規模なマイグレーションや解析は、並列に分散できます。

**ステップ 1: 対象リストを作る**

```text
移行が必要な Python ファイルをすべて列挙して files.txt に書き出して
```

**ステップ 2: ループで回す**

```bash
for file in $(cat files.txt); do
  claude -p "$file を React から Vue に移行して。OK か FAIL だけ返して" \
    --allowedTools "Edit,Bash(git commit *)"
done
```

**ステップ 3: まず数件で試してから全件に流す**

最初の 2〜3 件で何がうまくいかないかを見てプロンプトを調整してから、全件に適用してください。

既存のデータ処理パイプラインに組み込むこともできます。

```bash
claude -p "<プロンプト>" --output-format json | your_command
```

> `/batch` スキルを使うと、同様の大規模変更を Claude 側で並列オーケストレーションさせることもできます。

---

## 9-3. 複数セッションを並列で動かす

| 方法 | 説明 | 向いている場面 |
| --- | --- | --- |
| **git worktree** | `claude -w feature-auth` で隔離されたチェックアウトを作る | ローカルで複数の変更を同時進行させたい |
| **デスクトップアプリ** | 複数のローカルセッションを視覚的に管理 | 進捗を一覧で見ながら並行作業 |
| **Web 版** | Anthropic 管理のクラウド VM 上で実行 | マシンの負荷をかけずに長時間タスクを回す |
| **エージェントチーム** | 複数セッションが共有タスクリストとメッセージで自動連携 | 議論・分担が必要な複雑な作業（実験的機能） |
| **バックグラウンドエージェント** | `claude --bg "..."` で切り離して実行 | 別作業をしながら裏で走らせる |

### git worktree での並列作業

```bash
claude -w feature-auth          # worktree を作ってそこでセッション開始
claude -w feature-auth --tmux   # tmux セッションも作る
```

worktree ごとに独立したチェックアウトなので、**編集が衝突しません。**

### バックグラウンドで走らせて後で確認する

```bash
claude --bg "flaky なテストの原因を調査して"
```

```text
/tasks     # 実行中のバックグラウンド作業を一覧
```

```bash
claude attach 7c5dcf5d   # バックグラウンドセッションに接続
claude logs 7c5dcf5d     # 出力を表示
claude stop 7c5dcf5d     # 停止
```

### エージェントチーム（実験的）

複数の独立した Claude Code セッションが、共有タスクリストとメッセージで自律的に連携します。

```bash
# 有効化（settings.json または環境変数）
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

> **コストに注意**
> チームメイトはそれぞれ独立したコンテキストウィンドウを持つため、**トークン消費はチームの人数にほぼ比例します。** プランモードで動かす場合、標準的なセッションの約 7 倍のトークンを使うという目安があります。
> チームは小さく保ち、チームメイトには Sonnet を使い、作業が終わったら終了させてください。

---

## 9-4. CI / CD 連携

### GitHub Actions

PR の自動レビュー、Issue のトリアージなどを自動化できます。

```text
/install-github-app
```

このコマンドでリポジトリに Claude GitHub App をインストールできます。

主な用途:

- **PR の自動レビュー** — 変更内容をレビューしてコメント
- **Issue のトリアージ** — ラベル付け、重複チェック、対応方針の提案
- **`@claude` メンションでの実装依頼** — Issue や PR のコメントから作業を依頼

### GitLab CI/CD

GitLab のパイプラインにも組み込めます。詳細は [公式ドキュメント](https://code.claude.com/docs/en/gitlab-ci-cd) を参照してください。

### PR の自動修正（Auto-fix）

CI の失敗やレビューコメントに Claude が自動で対応する機能です。

```text
/autofix-pr
```

PR のブランチ上でこのコマンドを実行すると、Claude Code が `gh` で対象 PR を検出し、Web セッションを起動して監視を開始します。

有効化の方法は他にもあります。

- Web 版で PR を作った場合: CI ステータスバーから **Auto-fix** を選択
- モバイルアプリから: 「この PR を監視して CI の失敗やレビューコメントに対応して」と指示
- 既存の PR: PR の URL をセッションに貼って、自動修正を依頼

**動作**

| 状況 | Claude の動き |
| --- | --- |
| 明確に直せる | 修正してプッシュし、セッションで説明する |
| 曖昧・設計に関わる | 実行前にあなたに確認する |
| 重複・対応不要 | 記録して次に進む |

> ⚠️ **注意**
> リポジトリが Atlantis、Terraform Cloud、`issue_comment` で動く GitHub Actions などのコメント駆動の自動化を使っている場合、**Claude のコメントがそれらのワークフローを起動する可能性があります。** 有効化する前に自動化の内容を確認してください。
> また、GitHub はベースブランチが進んでコンフリクトが生じたときに webhook を出さないため、Auto-fix はコンフリクトに自動では反応できません。セッションを開いて rebase を依頼してください。

---

## 9-5. Web 版とモバイル

### Web 版（Claude Code on the web）

[claude.ai/code](https://claude.ai/code) で、Anthropic 管理のクラウド VM 上にセッションを作れます。

- ローカル環境の準備が不要
- ブラウザを閉じてもセッションは動き続ける
- 手元に無いリポジトリでも作業できる
- 複数タスクを並列で回せる
- スマホアプリから進捗を確認・操作できる

**GitHub の接続方法は 2 通り**

| 方法 | 内容 | 向いている人 |
| --- | --- | --- |
| **GitHub App** | オンボーディング時に Claude GitHub App を認可 | ブラウザから始める人、Auto-fix を使いたいチーム |
| **`/web-setup`** | ターミナルで実行し、ローカルの `gh` トークンを同期 | すでに `gh` を使っている個人開発者 |

### ターミナル → Web

```bash
claude --cloud "src/auth/login.ts の認証バグを直して"
```

現在のディレクトリの GitHub リモートを、現在のブランチでクローンしたクラウドセッションが作られます。
**VM は GitHub からクローンするので、ローカルのコミットは先にプッシュしてください。**

複数を同時に投げられます。

```bash
claude --cloud "auth.spec.ts の flaky なテストを直して"
claude --cloud "API ドキュメントを更新して"
claude --cloud "logger を構造化ログに書き換えて"
```

進捗は `/tasks` で確認できます。

> **おすすめの型: ローカルで計画 → クラウドで実行**
> ```bash
> claude --permission-mode plan     # ローカルで方針を詰める
> # 計画をリポジトリに保存してコミット・プッシュ
> claude --cloud "docs/migration-plan.md の計画を実行して"
> ```

### Web → ターミナル

```bash
claude --teleport                # セッションを選んで引き継ぐ
claude --teleport <session-id>   # 特定のセッションを指定
```

セッション内からは `/teleport`（`/tp`）でも同じことができます。`/tasks` から `t` キーでも可能です。

**引き継ぎの条件**

| 条件 | 内容 |
| --- | --- |
| git がクリーン | 未コミットの変更があると stash を促される |
| 同じリポジトリ | fork ではなく同一リポジトリのチェックアウトである必要がある |
| ブランチがプッシュ済み | クラウドセッションのブランチがリモートにある必要がある |
| 同じアカウント | クラウドセッションと同じ claude.ai アカウントで認証されている必要がある |

> `--teleport` と `--resume` は別物です。`--resume` はこのマシンのローカル履歴、`--teleport` はクラウドセッションとそのブランチを引っ張ってきます。

### その他のサーフェス間移動

| コマンド | 動作 |
| --- | --- |
| `/desktop`（`/app`） | ターミナルのセッションをデスクトップアプリで継続 |
| `/remote-control` | ローカルのセッションをスマホ・ブラウザから操作可能にする |
| `/web` | セッションをブラウザで開く |
| `/mobile` | モバイルアプリのダウンロード用 QR コードを表示 |

### Slack

`@Claude` にメンションしてタスクを依頼できます。バグ報告を投げて PR を返してもらう、といった使い方ができます。

```text
/install-slack-app
```

---

## 9-6. 定期実行

| 方法 | 実行場所 | 特徴 |
| --- | --- | --- |
| **Routines** | Anthropic 管理のインフラ | **PC の電源が切れていても動く**。API 呼び出しや GitHub イベントでも起動できる |
| **デスクトップの定期タスク** | 自分のマシン | ローカルのファイル・ツールに直接アクセスできる |
| **`/loop`** | 現在の CLI セッション内 | 簡易的なポーリング用 |

**Routines の作成**: Web、デスクトップアプリ、または CLI で `/schedule` を実行。

**`/loop` の例**:

```text
/loop 5m /pr-feedback
```

使いどころの例:

- 朝の PR レビュー
- 夜間の CI 失敗分析
- 週次の依存パッケージ監査
- PR マージ後のドキュメント同期

> `/loop` は現在のセッションのコンテキストを毎回送るため、**アイドル中でもトークンを消費します。** 長時間放置する用途には Routines のほうが適しています。

---

## 9-7. チーム導入のすすめ方

### 1. まず `CLAUDE.md` を整える

`/init` で雛形を作り、チームで育てて git にコミットします。これが最も費用対効果の高い最初の一歩です。
→ [06 CLAUDE.md とメモリ](06-claude-md.md)

### 2. 権限方針を決める

「どこまで自動承認するか」をチームで揃えておくと混乱がありません。
`.claude/settings.json` に許可リストを書いてコミットします。
→ [07 権限とセキュリティ](07-permissions-security.md)

### 3. 定型作業をスキル化する

デプロイ手順、リリース手順、レビューチェックリストなどを `.claude/skills/` に置いて共有します。
→ [08 拡張機能](08-extensions.md)

### 4. 必ず守らせたいことはフックにする

「コミット前に Lint」「migrations フォルダは編集禁止」など。
→ [08-3 フック](08-extensions.md#hooks)

### 5. CI に組み込む

PR の自動レビューから始めるのが導入しやすいです。

### 6. 使用状況を把握する

- Team / Enterprise: 組織アナリティクスの spend report、[analytics ダッシュボード](https://claude.ai/analytics/claude-code)
- Console（API）: Console の usage ページ、ワークスペースの上限設定
- クラウドプロバイダ経由: 各クラウドの請求コンソール、または OpenTelemetry エクスポート

→ コスト管理の詳細は [10 トラブルシューティング](10-troubleshooting.md#10-5-コストとトークンを節約する)

---

## 次に読む

- 困ったときの対処 → [10 トラブルシューティング](10-troubleshooting.md)

**公式ドキュメント**: https://code.claude.com/docs/en/headless / https://code.claude.com/docs/en/claude-code-on-the-web / https://code.claude.com/docs/en/github-actions / https://code.claude.com/docs/en/routines
