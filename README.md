# Claude Code 使い方ガイド（日本語）

**Claude Code（クロードコード）** は、Anthropic が提供する AI コーディングエージェントです。
チャットのように質問に答えるだけでなく、**あなたのコードを読み、ファイルを編集し、コマンドを実行し、テストが通るまで自分で直します**。
ターミナル・VS Code・JetBrains・デスクトップアプリ・ブラウザ・Slack・CI など、さまざまな場所で同じエンジンが動きます。

この資料は、**はじめて触る人から、チームで実務投入する人まで**を対象にした日本語の実践ガイドです。

---

## 5分クイックスタート

```bash
# 1. インストール（macOS / Linux / WSL）
curl -fsSL https://claude.ai/install.sh | bash

# 2. インストールできたか確認
claude --version        # 「2.x.x (Claude Code)」のように表示されればOK

# 3. プロジェクトのディレクトリで起動（初回はブラウザでログイン）
cd ~/path/to/your-project
claude
```

起動したら、まずはこう聞いてみてください。

```text
このプロジェクトは何をするもの？主要なディレクトリ構成も教えて
```

次に、実際に手を動かしてもらいます。

```text
README.md にインストール手順のセクションを追加して
```

Claude Code が変更内容を提示するので、内容を確認して承認します。これが基本のサイクルです。

> **Windows の場合**
> PowerShell: `irm https://claude.ai/install.ps1 | iex`
> コマンドプロンプト: `curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd`
> 詳細は [インストールとセットアップ](docs/02-setup.md) を参照してください。

---

## 目次

| # | ドキュメント | 内容 |
| --- | --- | --- |
| 01 | [Claude Code とは](docs/01-overview.md) | できること、動作する場所、チャット版 Claude との違い、必要なプラン |
| 02 | [インストールとセットアップ](docs/02-setup.md) | OS 別インストール、ログイン、IDE・デスクトップ・Web 版の導入、アップデート |
| 03 | [基本操作](docs/03-basics.md) | 起動・終了、対話の基本、`@` によるファイル参照、スラッシュコマンド、ショートカット、セッション管理 |
| 04 | [はじめての実践](docs/04-first-tasks.md) | コード理解 → バグ修正 → テスト → コミットまでの一連の流れと定番パターン |
| 05 | [効果的な使い方](docs/05-best-practices.md) | 検証手段を与える、探索→計画→実装、指示の書き方、コンテキスト管理、失敗パターン |
| 06 | [CLAUDE.md とメモリ](docs/06-claude-md.md) | プロジェクトのルールを覚えさせる、`/init`、`.claude/rules/`、オートメモリ |
| 07 | [権限とセキュリティ](docs/07-permissions-security.md) | 権限モード、許可リスト、サンドボックス、機密情報とプロンプトインジェクション対策 |
| 08 | [拡張機能](docs/08-extensions.md) | スキル、フック、MCP、サブエージェント、プラグイン。どれを使うかの判断基準 |
| 09 | [自動化とチーム利用](docs/09-automation.md) | 非対話モード、並列実行、GitHub Actions、定期実行、Web・モバイル連携 |
| 10 | [トラブルシューティング](docs/10-troubleshooting.md) | 動かない・重い・思った通りにならない時の対処、コスト削減 |
| 11 | [コマンド早見表](docs/11-cheatsheet.md) | CLI フラグ／スラッシュコマンド／ショートカット／設定ファイルの一覧 |
| 12 | [業務自動化ロードマップ](docs/12-automation-roadmap.md) | 何から自動化するか、手作業→無人実行までの 5 段階、業務別レシピ、90 日チェックリスト |
| — | [用語集](docs/glossary.md) | エージェント的ループ、コンテキストウィンドウ、MCP などの用語解説 |

---

## 設定ジェネレータ（Web アプリ）

**https://hayuo8ll-del.github.io/ms2/**

06〜08 章の内容を、実際に使える設定ファイルとして出力するツールです。
質問に答えていくと、次のファイルが生成されます。

```
CLAUDE.md
.claude/settings.json      # 権限（allow / ask / deny）とフックを統合したもの
.claude/agents/<name>.md   # サブエージェント
.claude/skills/<name>/SKILL.md
.claude/rules/<name>.md    # パススコープルール
.mcp.json                  # MCP サーバー
```

「一括 ZIP」でまとめて落として、プロジェクトのルートで展開すればそのまま動きます。
`CLAUDE.md` が 200 行を超えた、`Bash(*)` のように allow が広すぎる、認証情報が混ざっている、
といったガイド由来のチェックがその場で警告として出ます。

入力内容はブラウザの中だけに保存され、外部には送信されません。
ソースと詳細は [`app/`](app/README.md) を参照してください。

---

## マイクラ建築図面ジェネレータ（Web アプリ）

**https://hayuo8ll-del.github.io/ms2/minecraft/**

ガイド本編とは別に、同じ作り方（単一 HTML・ビルド不要・セルフテストが CI の関門）で作った
もう 1 つのアプリです。立体を**レイヤー（Y 座標）ごとの平面図**と**材料表**にします。

入力は 3 通りで、出力は共通です。

| 入力 | 中身 |
| --- | --- |
| 形から作る | 円・球・ドーム・円錐・切妻／寄棟／片流れ屋根・螺旋階段・アーチ |
| ファイルを読む | 公開されている建築やトラップの `.litematic` / `.schem` / `.nbt` |
| 実際の建物 | 現実の寸法（メートル）とスケールから、基礎・壁・床・窓・玄関・屋根 |

- 平面図と立面図、全レイヤーのコンタクトシート（印刷可）
- **材料表**。ブロックごとの個数とスタック換算、段ごとの内訳
- 向き（`facing`）を矢印で表示。トラップのホッパーやオブザーバーの向きも読める
- テキスト図面のコピーと、相対座標の `setblock` 列（`.mcfunction`）の書き出し

読み込んだファイルはブラウザの中だけで解析し、外部には送信しません。
詳細は [`app/minecraft/`](app/minecraft/README.md) を参照してください。

---

## 読み進め方

### はじめて使う人（所要 30〜60 分）

1. [01 Claude Code とは](docs/01-overview.md) — 何ができるのかを掴む
2. [02 インストールとセットアップ](docs/02-setup.md) — 動く状態にする
3. [03 基本操作](docs/03-basics.md) — 最低限の操作を覚える
4. [04 はじめての実践](docs/04-first-tasks.md) — 実際に 1 つタスクを完了させる
5. [05 効果的な使い方](docs/05-best-practices.md) — ここまで来ると精度が一段上がる

### すでに使っている人

- 結果がブレる・手戻りが多い → [05 効果的な使い方](docs/05-best-practices.md)
- 毎回同じ説明をしている → [06 CLAUDE.md とメモリ](docs/06-claude-md.md)
- 承認ボタンを押し続けるのが辛い → [07 権限とセキュリティ](docs/07-permissions-security.md)
- 定型作業を自動化したい → [08 拡張機能](docs/08-extensions.md) / [09 自動化とチーム利用](docs/09-automation.md)
- 業務自動化を「何から・どの順で」進めるか知りたい → [12 業務自動化ロードマップ](docs/12-automation-roadmap.md)
- コマンドをど忘れした → [11 コマンド早見表](docs/11-cheatsheet.md)

### チームに導入する人

[06 CLAUDE.md とメモリ](docs/06-claude-md.md) でプロジェクトのルールを共有し、
[08 拡張機能](docs/08-extensions.md) でスキル・フックを整備、
[09 自動化とチーム利用](docs/09-automation.md) で CI 連携まで広げる、という順序がおすすめです。
進め方の全体設計（どの業務から、どの順で、どこまで自動化するか）は
[12 業務自動化ロードマップ](docs/12-automation-roadmap.md) にまとめています。

---

## この資料の使い方のコツ

- **Claude Code 自身に聞くのが一番速い場合があります。** Claude Code は自分のドキュメントを参照できるので、セッション内で「カスタムスキルの作り方を教えて」と聞けば答えてくれます。
- **日本語のプロンプトでそのまま使えます。** 本資料の例も日本語中心にしていますが、英語でも同じように動きます。
- **バージョンによって使える機能が違います。** 「あるはずの機能が無い」ときは、まず `claude --version` を確認してアップデートしてください。

---

## この資料について

- **対象バージョン**: Claude Code v2.1 系（2026年7月時点）
- **最終更新日**: 2026-07-31
- **情報源**: 本資料は Anthropic 公式ドキュメント [code.claude.com/docs](https://code.claude.com/docs/en/overview) の内容を基に、日本語で再構成したものです。

Claude Code は更新が非常に速いプロダクトです。細かい仕様や最新機能は、必ず公式ドキュメントおよび [変更履歴](https://code.claude.com/docs/en/changelog) もあわせて確認してください。

| 主な公式ドキュメント | URL |
| --- | --- |
| 概要 | https://code.claude.com/docs/en/overview |
| クイックスタート | https://code.claude.com/docs/en/quickstart |
| ベストプラクティス | https://code.claude.com/docs/en/best-practices |
| CLI リファレンス | https://code.claude.com/docs/en/cli-reference |
| コマンド一覧 | https://code.claude.com/docs/en/commands |
