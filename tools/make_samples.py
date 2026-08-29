#!/usr/bin/env python3
"""図面ジェネレータの同梱サンプルを生成する。

app/minecraft/samples/ に、同じ中身を 3 形式で書き出す。
アプリを開いた直後から「選んで読む」を試せるようにするためのもので、
第三者の作品ではなく、ここで生成した自前のデータ。

    python3 tools/make_samples.py

3 形式が同じ図面になることは、アプリのセルフテスト側でも見ている。
"""

import gzip
import json
import math
import pathlib
import struct

OUT = pathlib.Path(__file__).resolve().parent.parent / "app" / "minecraft" / "samples"

TAG_END, TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG = 0, 1, 2, 3, 4
TAG_FLOAT, TAG_DOUBLE, TAG_BYTE_ARRAY, TAG_STRING = 5, 6, 7, 8
TAG_LIST, TAG_COMPOUND, TAG_INT_ARRAY, TAG_LONG_ARRAY = 9, 10, 11, 12


class Tag:
    def __init__(self, tag, val):
        self.tag, self.val = tag, val


def name_bytes(v):
    b = v.encode("utf-8")
    return struct.pack(">H", len(b)) + b


def B(v): return Tag(TAG_BYTE, v)
def Sh(v): return Tag(TAG_SHORT, v)
def I(v): return Tag(TAG_INT, v)
def S(v): return Tag(TAG_STRING, v)
def C(d): return Tag(TAG_COMPOUND, d)
def L(t, items): return Tag(TAG_LIST, (t, items))
def BA(v): return Tag(TAG_BYTE_ARRAY, v)
def LA(v): return Tag(TAG_LONG_ARRAY, v)


def payload(t):
    tag, val = t.tag, t.val
    if tag == TAG_BYTE:
        return struct.pack(">b", val)
    if tag == TAG_SHORT:
        return struct.pack(">h", val)
    if tag == TAG_INT:
        return struct.pack(">i", val)
    if tag == TAG_LONG:
        return struct.pack(">q", val)
    if tag == TAG_STRING:
        return name_bytes(val)
    if tag == TAG_BYTE_ARRAY:
        return struct.pack(">i", len(val)) + bytes((x & 0xFF) for x in val)
    if tag == TAG_LONG_ARRAY:
        return struct.pack(">i", len(val)) + b"".join(struct.pack(">q", x) for x in val)
    if tag == TAG_LIST:
        item_tag, items = val
        return struct.pack(">Bi", item_tag, len(items)) + b"".join(payload(x) for x in items)
    if tag == TAG_COMPOUND:
        out = b""
        for k, v in val.items():
            out += struct.pack(">B", v.tag) + name_bytes(k) + payload(v)
        return out + b"\x00"
    raise ValueError("知らないタグ: %r" % tag)


def write(root, path):
    data = struct.pack(">B", TAG_COMPOUND) + name_bytes("") + payload(root)
    path.write_bytes(gzip.compress(data))
    return path


# ---------------------------------------------------------------------------
# サンプルの中身: 7 × 5 × 7。トラップの体裁になるよう、向きのあるブロックと水を入れる
# ---------------------------------------------------------------------------

SX, SY, SZ = 7, 5, 7

PALETTE = [
    ("minecraft:air", {}),
    ("minecraft:stone_bricks", {}),
    ("minecraft:oak_stairs", {"facing": "east", "half": "bottom", "shape": "straight"}),
    ("minecraft:hopper", {"facing": "north", "enabled": "true"}),
    ("minecraft:water", {"level": "0"}),
    ("minecraft:redstone_block", {}),
    ("minecraft:glass", {}),
]


def make_grid():
    g = [[[0] * SX for _ in range(SZ)] for _ in range(SY)]
    # 床
    for z in range(SZ):
        for x in range(SX):
            g[0][z][x] = 1
    # 外周の壁（2 段）。角にガラスを入れて種類を増やす
    for y in (1, 2):
        for z in range(SZ):
            for x in range(SX):
                if x in (0, SX - 1) or z in (0, SZ - 1):
                    g[y][z][x] = 6 if (x in (0, SX - 1) and z in (0, SZ - 1)) else 1
    # 中央の水路とホッパー（回収口）
    g[1][3][3] = 3
    for x in (2, 4):
        g[1][3][x] = 4
    # 階段と、その上のレッドストーンブロック
    g[1][1][5] = 2
    g[2][1][5] = 5
    # 天井の一部
    for z in range(2, 5):
        for x in range(2, 5):
            g[3][z][x] = 1
    return g


GRID = make_grid()


def expected():
    out = {}
    for y in range(SY):
        for z in range(SZ):
            for x in range(SX):
                v = GRID[y][z][x]
                if v:
                    out[PALETTE[v][0]] = out.get(PALETTE[v][0], 0) + 1
    return out


def props_compound(props):
    return C({k: S(v) for k, v in props.items()})


def state_name(name, props):
    if not props:
        return name
    return name + "[" + ",".join("%s=%s" % (k, props[k]) for k in sorted(props)) + "]"


def varint(v):
    out = b""
    while True:
        b = v & 0x7F
        v >>= 7
        if v:
            out += bytes([b | 0x80])
        else:
            return out + bytes([b])


def pack_longs(indices, bits):
    """Litematica のビットパック。1 個の値が long の境界をまたぐことがある"""
    longs = [0] * ((len(indices) * bits + 63) // 64)
    for i, v in enumerate(indices):
        start = i * bits
        a, off = start // 64, start % 64
        b = (start + bits - 1) // 64
        longs[a] |= (v << off) & ((1 << 64) - 1)
        if a != b:
            longs[b] |= v >> (64 - off)
    return [x - (1 << 64) if x >= (1 << 63) else x for x in longs]


def build_palette_list():
    out = []
    for name, props in PALETTE:
        d = {"Name": S(name)}
        if props:
            d["Properties"] = props_compound(props)
        out.append(C(d))
    return out


def write_structure_nbt(path):
    blocks = [
        C({"state": I(GRID[y][z][x]), "pos": L(TAG_INT, [I(x), I(y), I(z)])})
        for y in range(SY) for z in range(SZ) for x in range(SX) if GRID[y][z][x]
    ]
    return write(C({
        "DataVersion": I(3465),
        "size": L(TAG_INT, [I(SX), I(SY), I(SZ)]),
        "palette": L(TAG_COMPOUND, build_palette_list()),
        "blocks": L(TAG_COMPOUND, blocks),
        "entities": L(TAG_COMPOUND, []),
    }), path)


def write_sponge_schem(path):
    pal = C({state_name(n, p): I(i) for i, (n, p) in enumerate(PALETTE)})
    data = b"".join(
        varint(GRID[y][z][x]) for y in range(SY) for z in range(SZ) for x in range(SX)
    )
    return write(C({
        "Version": I(2), "DataVersion": I(3465),
        "Width": Sh(SX), "Height": Sh(SY), "Length": Sh(SZ),
        "Palette": pal, "PaletteMax": I(len(PALETTE)),
        "BlockData": BA(list(data)),
    }), path)


def write_litematic(path):
    indices = [GRID[y][z][x] for y in range(SY) for z in range(SZ) for x in range(SX)]
    bits = max(2, math.ceil(math.log2(len(PALETTE))))
    return write(C({
        "Version": I(6), "MinecraftDataVersion": I(3465),
        "Metadata": C({
            "Name": S("サンプル: 小さな回収室"),
            "Author": S("ms2 図面ジェネレータ"),
            "Description": S("読み込みを試すための自前サンプル"),
            "EnclosingSize": C({"x": I(SX), "y": I(SY), "z": I(SZ)}),
        }),
        "Regions": C({"main": C({
            "Position": C({"x": I(0), "y": I(0), "z": I(0)}),
            "Size": C({"x": I(SX), "y": I(SY), "z": I(SZ)}),
            "BlockStatePalette": L(TAG_COMPOUND, build_palette_list()),
            "BlockStates": LA(pack_longs(indices, bits)),
            "TileEntities": L(TAG_COMPOUND, []),
            "Entities": L(TAG_COMPOUND, []),
        })}),
    }), path)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    written = [
        write_litematic(OUT / "sample-collection-room.litematic"),
        write_sponge_schem(OUT / "sample-collection-room.schem"),
        write_structure_nbt(OUT / "sample-collection-room.nbt"),
    ]
    exp = expected()
    (OUT / "README.md").write_text(
        "# 同梱サンプル\n\n"
        "`tools/make_samples.py` が生成した自前のデータです（第三者の作品ではありません）。\n"
        "読み込みを試すためのもので、3 形式とも中身は同じです。\n\n"
        "```\n%d × %d × %d（幅X × 奥行Z × 高さY）  ブロック %d 個\n```\n\n"
        "| ブロック | 個数 |\n| --- | --- |\n%s\n"
        % (SX, SZ, SY, sum(exp.values()),
           "\n".join("| `%s` | %d |" % (k, v) for k, v in sorted(exp.items(), key=lambda kv: -kv[1]))),
        encoding="utf-8")

    print("寸法 %d × %d × %d / 合計 %d 個" % (SX, SZ, SY, sum(exp.values())))
    print("期待する材料:", json.dumps(exp, ensure_ascii=False))
    for p in written:
        print("  %-40s %5d bytes" % (p.name, p.stat().st_size))


if __name__ == "__main__":
    main()
