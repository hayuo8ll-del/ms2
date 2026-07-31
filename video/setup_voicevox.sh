#!/usr/bin/env bash
#
# VOICEVOX（高品質な日本語音声合成）をセットアップする。
#
# 既定の OpenJTalk より自然な声で読み上げたいときに実行する。
# 実行後、デッキの meta に engine: voicevox を書けば使われる。
#
#   bash video/setup_voicevox.sh
#
# 公式のダウンローダ（download-linux-x64）は使っていない。あれは
# api.github.com からリリース情報を引くうえ、Rust 製で CA ストアを
# 埋め込んでいるため、企業プロキシ配下では証明書エラーで止まってしまう。
# ここでは必要な 3 つの資産を URL 直指定で取得している。
#
# 取得するもの:
#   1. Python バインディング（音声モデル同梱、約 1.2GB）
#   2. ONNX Runtime の共有ライブラリ（約 6MB）
#   3. Open JTalk の辞書（約 24MB）
#
# ※ VOICEVOX で生成した音声を公開する場合、キャラクターごとの利用規約に従い
#    クレジット表記が必要です（例: 「VOICEVOX:No.7」）。
#    詳細は https://voicevox.hiroshiba.jp/term/ を確認してください。

set -euo pipefail

VERSION="0.15.7"
ONNX_VERSION="1.13.1"
DICT_VERSION="1.11"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HERE/.voicevox"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$DEST"

echo "==> Python バインディングを取得（約 1.2GB、音声モデル同梱）"
WHEEL="voicevox_core-${VERSION}+cpu-cp38-abi3-linux_x86_64.whl"
curl -fsSL --retry 3 -o "$TMP/$WHEEL" \
  "https://github.com/VOICEVOX/voicevox_core/releases/download/${VERSION}/voicevox_core-${VERSION}%2Bcpu-cp38-abi3-linux_x86_64.whl"

echo "==> ONNX Runtime を取得"
curl -fsSL --retry 3 -o "$TMP/onnx.tgz" \
  "https://github.com/microsoft/onnxruntime/releases/download/v${ONNX_VERSION}/onnxruntime-linux-x64-${ONNX_VERSION}.tgz"

echo "==> Open JTalk 辞書を取得"
curl -fsSL --retry 3 -o "$TMP/dict.tar.gz" \
  "https://github.com/r9y9/open_jtalk/releases/download/v1.11.1/open_jtalk_dic_utf_8-${DICT_VERSION}.tar.gz"

echo "==> 展開・配置"
tar xzf "$TMP/dict.tar.gz" -C "$DEST"
tar xzf "$TMP/onnx.tgz" -C "$TMP"

# 共有ライブラリはローダから見える場所に置く。root で無い場合は
# LD_LIBRARY_PATH で参照させる。
LIB="$TMP/onnxruntime-linux-x64-${ONNX_VERSION}/lib/libonnxruntime.so.${ONNX_VERSION}"
if [ -w /usr/local/lib ]; then
  cp "$LIB" /usr/local/lib/
  ldconfig 2>/dev/null || true
  echo "    /usr/local/lib に配置しました"
else
  mkdir -p "$DEST/lib"
  cp "$LIB" "$DEST/lib/"
  echo "    $DEST/lib に配置しました"
  echo "    実行前に次を設定してください: export LD_LIBRARY_PATH=$DEST/lib:\$LD_LIBRARY_PATH"
fi

echo "==> Python バインディングをインストール"
pip3 install --quiet --break-system-packages "$TMP/$WHEEL"

echo
echo "==> 動作確認"
python3 - <<'PY'
from voicevox_core import METAS
print(f"    話者 {len(METAS)} 名を読み込みました")
for m in METAS:
    if m.name == "No.7":
        print("    既定の話者:", m.name, [f"{s.name}={s.id}" for s in m.styles][:3])
PY

echo
echo "完了しました。デッキの meta に次を書くと VOICEVOX が使われます:"
echo
echo "  meta:"
echo "    engine: voicevox"
echo "    speaker: 30      # No.7 アナウンス"
echo
