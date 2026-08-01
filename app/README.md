# Claude Code 設定ジェネレータ

質問に答えていくと、Claude Code の設定ファイル一式を生成する Web アプリです。

**公開 URL**: https://hayuo8ll-del.github.io/ms2/

```
CLAUDE.md
.claude/settings.json      # 権限（allow / ask / deny）とフックを統合したもの
.claude/agents/<name>.md   # サブエージェント
.claude/skills/<name>/SKILL.md
.claude/rules/<name>.md    # パススコープルール
.mcp.json                  # MCP サーバー
mcp-add.sh                 # .mcp.json と等価な claude mcp add コマンド
```

生成物はファイルごとにコピー・保存できるほか、**一括 ZIP** を押すと `.claude/` の
ディレクトリ構造のまま固めてダウンロードできます。プロジェクトのルートで展開すればそのまま使えます。

---

## なぜ作ったか

[ガイド本編](../README.md)の 06〜08 章には、`CLAUDE.md` に何を書くか、`permissions` の書式、
フックの JSON 構造、フロントマターのフィールドが載っています。ただ、実際に設定を作ろうとすると
**章をまたいで書式を探し、JSON を手書きし、キー名のタイプミスで動かない**という詰まり方をします。

このアプリは、その知識をフォームに落として、**構造が壊れない形で出力する**ためのものです。
書式を思い出す作業をゼロにするのが目的なので、単なるテンプレート集ではなく、
ガイドの判断基準をそのままチェックとして持っています。

| チェック | 根拠 |
| --- | --- |
| `CLAUDE.md` が 200 行を超えたら警告し、`.claude/rules/` への分割を促す | [06-4](../docs/06-claude-md.md) |
| API キー・トークンらしき文字列を検出して赤字で止める（これらは git にコミットされる） | [07-6](../docs/07-permissions-security.md) |
| `Bash(*)` のような広すぎる allow に警告する（auto モードで無効化されるため） | [07-3](../docs/07-permissions-security.md) |
| `bypassPermissions` を選ぶと隔離環境専用である旨を警告する | [07-2](../docs/07-permissions-security.md) |
| スキル・サブエージェントの `description` 未記入を警告する（無いと呼ばれない） | [08-2](../docs/08-extensions.md) |
| 名前がケバブケースでない・重複している場合に警告する | [08-2](../docs/08-extensions.md) |
| フックを複数足しても、イベント名を兄弟キーとして正しく並べる | [08-3](../docs/08-extensions.md) |

---

## 使い方

1. ページを開く（またはこのファイルを `open app/index.html` で直接開く）
2. 上部の「プリセットを選ぶ…」から近いものを選ぶと、一通りの雛形が入ります
3. 各タブを埋める。右側に生成結果が即座に反映されます
4. 「一括 ZIP」でダウンロードし、プロジェクトのルートで展開する

```bash
unzip claude-config.zip -d /path/to/your-project
```

`CLAUDE.md` と `.claude/settings.json` は **git にコミットしてチームで共有**するファイルです。
個人用の設定は `.claude/settings.local.json` や `CLAUDE.local.md` に分けてください。

### 入力内容の保存

- 入力はブラウザの localStorage に自動保存されます。**外部には一切送信されません**
- 「設定を保存」で JSON として書き出し、別のマシンで「設定を読込」から復元できます

### URL パラメータ

| パラメータ | 動作 |
| --- | --- |
| `?preset=node` | その雛形を入れた状態で開く（`node` / `python` / `go` / `monorepo`） |
| `?selftest=1` | 生成ロジックのセルフテストを実行し、結果をページ先頭に表示する |

---

## 仕組み

`index.html` の 1 ファイルだけで完結しています。ビルド不要、依存パッケージなし、オフラインで動作します。

- **`state` が唯一の真実**。フォームは `state` を書き換えるだけ
- 生成は **state → 文字列 の純粋関数**（`buildClaudeMd` / `buildSettings` / `buildAgentMd` /
  `buildSkillMd` / `buildRuleMd` / `buildMcpJson`）。副作用がないのでテストしやすい
- ZIP は外部ライブラリを使わず、無圧縮（store 形式）のアーカイブを組み立てている

### テスト

生成関数と警告ロジックのテストがページ自体に入っています。ブラウザで
`index.html?selftest=1` を開くと結果が出ます。ヘッドレスでも実行できます。

```bash
# ローカル（このリポジトリの開発環境）
/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell \
  --disable-gpu --no-sandbox --virtual-time-budget=3000 \
  --dump-dom "file://$PWD/app/index.html?selftest=1" | grep -o 'SELFTEST: .*failed'
```

CI（`.github/workflows/pages.yml`）でも同じテストが走り、**1 件でも失敗するとデプロイされません。**

---

## 公開の設定

GitHub Pages はワークフローからデプロイしています。初回だけリポジトリ側の設定が必要です。

**Settings > Pages > Build and deployment > Source** を **GitHub Actions** に変更してください。

以降は `main` の `app/` に変更が入るたびに自動でデプロイされます。
