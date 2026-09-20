#!/usr/bin/env python3
"""Hand-authored pixel art for Treat Time. Writes PNGs under public/sprites/."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "sprites"
OUT.mkdir(parents=True, exist_ok=True)

PALETTE = {
    ".": None,
    "k": (42, 24, 16, 255),  # outline
    "w": (255, 248, 238, 255),  # white fluff
    "s": (232, 208, 176, 255),  # cream shade
    "c": (212, 146, 74, 255),  # caramel
    "d": (154, 94, 40, 255),  # dark caramel
    "n": (26, 14, 10, 255),  # nose / eye
    "p": (244, 160, 176, 255),  # pink
    "h": (255, 255, 255, 255),  # highlight
    "g": (196, 172, 140, 255),  # deep shade
    "b": (196, 224, 120, 255),  # tennis
    "t": (232, 93, 117, 255),  # heart
    "m": (216, 188, 232, 255),  # soap
    "l": (168, 132, 196, 255),  # soap dark
    "v": (92, 96, 108, 255),  # vacuum
    "u": (140, 148, 164, 255),  # vacuum light
    "y": (248, 236, 196, 255),  # bone
    "o": (184, 140, 72, 255),  # wood
    "r": (122, 82, 40, 255),  # wood dark
    "f": (124, 176, 72, 255),  # grass
    "e": (90, 138, 52, 255),  # grass dark
    "a": (168, 206, 88, 255),  # grass light
    "i": (126, 186, 214, 255),  # sky
    "q": (186, 222, 236, 255),  # sky light
    "x": (214, 236, 196, 255),  # horizon
    "z": (74, 122, 58, 255),  # leaves
    "j": (56, 96, 44, 255),  # leaves dark
}


def write_png(path: Path, width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> None:
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(pixels[y * width + x])

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    png = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)),
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
            chunk(b"IEND", b""),
        ]
    )
    path.write_bytes(png)


def canvas(width: int, height: int, fill: tuple[int, int, int, int] | None = None) -> list[tuple[int, int, int, int]]:
    px = fill if fill is not None else (0, 0, 0, 0)
    return [px] * (width * height)


def put(
    pixels: list[tuple[int, int, int, int]],
    width: int,
    x: int,
    y: int,
    color: tuple[int, int, int, int] | None,
) -> None:
    if color is None:
        return
    height = len(pixels) // width
    if 0 <= x < width and 0 <= y < height:
        pixels[y * width + x] = color


def pad_row(row: str, width: int) -> str:
    if len(row) < width:
        return row + "." * (width - len(row))
    return row[:width]


def blit_map(
    pixels: list[tuple[int, int, int, int]],
    width: int,
    ox: int,
    oy: int,
    rows: list[str],
    palette: dict[str, tuple[int, int, int, int] | None] = None,
    row_width: int | None = None,
) -> None:
    pal = palette or PALETTE
    expected = row_width if row_width is not None else max(len(r) for r in rows)
    for y, row in enumerate(rows):
        for x, ch in enumerate(pad_row(row, expected)):
            put(pixels, width, ox + x, oy + y, pal.get(ch))


def shift_rows(rows: list[str], dy: int, fill: str = ".") -> list[str]:
    width = len(rows[0])
    empty = fill * width
    if dy > 0:
        return [empty] * dy + rows[:-dy]
    if dy < 0:
        return rows[-dy:] + [empty] * (-dy)
    return list(rows)


DOG_IDLE = [
    "................................",
    ".....dddd..............dddd.....",
    "....dccccd............dccccd....",
    "...dccccccd..........dccccccd...",
    "...dccccccckkkkkkkkkkcccccccd...",
    "..kccccccccswwwwwwscccccccck....",
    "..kcccccwwwwwwwwwwwwwwwwcccck...",
    ".kccccwwwwwwwwwwwwwwwwwwwwccck..",
    ".kcccwwwwwwwwwwwwwwwwwwwwwwcck..",
    ".kccwwwhhnwwwwwwwwwwwnhhwwwcck..",
    ".kccwwwwnnwwwwwwwwwwwwnnwwwwck..",
    ".kcwwwwwwwwwsssssswwwwwwwwwwck..",
    ".kcwwwwwwwwssnnnnsswwwwwwwwwck..",
    ".kwwwwwwwwwwspnnpswwwwwwwwwwwk..",
    ".kwwwwwwwwwwwsssswwwwwwwwwwwwk..",
    ".kwwwwwwwwwwwwwwwwwwwwwwwwwwwk..",
    "..ksswwwwwwwwwwwwwwwwwwwwwwsk...",
    "..kksswwwwwwwwwwwwwwwwwwwwsskk..",
    ".kwwkksssswwwwwwwwwwwwsssskkwwk.",
    ".kwwwwkwwwwwwwwwwwwwwwwwwkwwwwk.",
    ".kwwwwkwwwwwwwwwwwwwwwwwwkwwwwk.",
    ".ksswwkwwwwwwwwwwwwwwwwwwkwwssk.",
    "..kwwwksswwwwwwwwwwwwwwsskwwwk..",
    "..kwwwkksssskkwwkksssskkkwwwk...",
    "..ksswwkwwkk......kkwwkwwssk....",
    "...kwwwkwwk........kwwkwwwk.....",
    "...ksskkssk........ksskkssk.....",
    "....kkwwkk..........kkwwkk......",
    ".....kssk............kssk.......",
    "......kk..............kk........",
    "................................",
    "................................",
]

DOG_BOB = shift_rows(DOG_IDLE, 1)

DOG_HOP = [
    ".....dddd..............dddd.....",
    "....dccccd............dccccd....",
    "...dccccccd..........dccccccd...",
    "...dccccccckkkkkkkkkkcccccccd...",
    "..kccccccccswwwwwwscccccccck....",
    "..kcccccwwwwwwwwwwwwwwwwcccck...",
    ".kccccwwwwwwwwwwwwwwwwwwwwccck..",
    ".kcccwwwwwwwwwwwwwwwwwwwwwwcck..",
    ".kccwwwhhnwwwwwwwwwwwnhhwwwcck..",
    ".kccwwwwnnwwwwwwwwwwwwnnwwwwck..",
    ".kcwwwwwwwwwss....sswwwwwwwwck..",
    ".kcwwwwwwwws.pppp.swwwwwwwwwck..",
    ".kwwwwwwwwwwwssnnsswwwwwwwwwwk..",
    ".kwwwwwwwwwwwwsssswwwwwwwwwwwk..",
    ".kwwwwwwwwwwwwwwwwwwwwwwwwwwwk..",
    "..ksswwwwwwwwwwwwwwwwwwwwwwsk...",
    "..kksswwwwwwwwwwwwwwwwwwwwsskk..",
    ".kwwkksssswwwwwwwwwwwwsssskkwwk.",
    ".kwwwwkwwwwwwwwwwwwwwwwwwkwwwwk.",
    ".kwwwwkwwwwwwwwwwwwwwwwwwkwwwwk.",
    ".ksswwkwwwwwwwwwwwwwwwwwwkwwssk.",
    "..kwwwksswwwwwwwwwwwwwwsskwwwk..",
    "..kwwwkksssskkwwkksssskkkwwwk...",
    "...kss..kwwk......kwwk..ssk.....",
    "....kk..kssk......kssk..kk......",
    ".........kk........kk...........",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
]

DOG_HIT = [
    "................................",
    "................................",
    "......dddd............dddd......",
    ".....dccccd..........dccccd.....",
    "....dccccccdkkkkkkkkdccccccd....",
    "...kcccccccswwwwwwscccccccck....",
    "...kccccwwwwwwwwwwwwwwwwccck....",
    "..kcccwwwwwwwwwwwwwwwwwwwwcck...",
    "..kccwwwwwwwwwwwwwwwwwwwwwwck...",
    "..kcwwwnnnwwwwwwwwwwwnnnwwwck...",
    "..kcwwwnnnwwwwwwwwwwwnnnwwwwk...",
    "..kwwwwwwwwwsssssswwwwwwwwwwk...",
    "..kwwwwwwwwss....sswwwwwwwwwk...",
    "..kwwwwwwwwwspnnpswwwwwwwwwwk...",
    "..kwwwwwwwwwwsssswwwwwwwwwwwk...",
    "..kwwwwwwwwwwwwwwwwwwwwwwwwwk...",
    "...ksswwwwwwwwwwwwwwwwwwwwsk....",
    "...kksswwwwwwwwwwwwwwwwwwssk....",
    "..kwwkksssswwwwwwwwwwsssskkwwk..",
    "..kwwwwkwwwwwwwwwwwwwwwwkwwwwk..",
    "..ksswwkwwwwwwwwwwwwwwwwkwwssk..",
    "...kwwwksswwwwwwwwwwwwsskwwwk...",
    "...kwwwkksssskkwwkksssskkwwwk...",
    "...ksswwkwwkk......kkwwkwwssk...",
    "....kwwwkwwk........kwwkwwwk....",
    "....ksskkssk........ksskkssk....",
    ".....kkwwkk..........kkwwkk.....",
    "......kssk............kssk......",
    ".......kk..............kk.......",
    "................................",
    "................................",
    "................................",
]

BONE = [
    "................",
    "................",
    "..yy......yy....",
    ".ywwy....ywwy...",
    ".ywwwyyyywwwy...",
    "kywwwwwwwwwwyk..",
    "kywwwwwwwwwwyk..",
    ".ywwwyyyywwwy...",
    ".ywwy....ywwy...",
    "..yy......yy....",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
]

HEART = [
    "................",
    "................",
    "...tt....tt.....",
    "..twwt..twtt....",
    ".twwwwttwwwwt...",
    ".twwwwwwwwwt....",
    "ktwwwwwwwwwtk...",
    ".twwwwwwwwt.....",
    "..twwwwwwt......",
    "...twwwwt.......",
    "....twwt........",
    ".....tt.........",
    "................",
    "................",
    "................",
    "................",
]

BALL = [
    "................",
    "................",
    ".....kkkk.......",
    "....kbbbhk......",
    "...kbbhbbbk.....",
    "...kbbbbbbk.....",
    "..khbbbbbbbk....",
    "..kbbbwwbbbk....",
    "..kbbwwwwbbk....",
    "..kbbbwwbbbk....",
    "...kbbbbbbk.....",
    "...kbbbbbk......",
    "....kkkk........",
    "................",
    "................",
    "................",
]

SOAP = [
    "................",
    "..........hh....",
    ".........h..h...",
    "..........hh....",
    "....kkkkkk......",
    "...kmmmmmmk.....",
    "..kmmhhhhmmk....",
    "..kmmmmmmmlk....",
    "..kmmmmmmmmlk...",
    "..klmmmmmmmk....",
    "...kllllllk.....",
    "....kkkkkk......",
    "................",
    "................",
    "................",
    "................",
]

VACUUM = [
    "................",
    "................",
    "....u..u..u.....",
    "...u.vv.u.v.....",
    "..uv.vvv.vu.....",
    "..uvvvvvvvu.....",
    ".kuvvvvvvvuk....",
    ".kvvuuuvvvk.....",
    "..kvvvvvvk......",
    "...kvvuvk.......",
    "....kvvk........",
    ".....kk.........",
    "................",
    "................",
    "................",
    "................",
]

HEART_UI = [
    "................",
    "...tt....tt.....",
    "..twwt..twtt....",
    ".twwwwttwwwwt...",
    ".twwwwwwwwwt....",
    "ktwwwwwwwwwtk...",
    ".twwwwwwwwt.....",
    "..twwwwwwt......",
    "...twwwwt.......",
    "....twwt........",
    ".....tt.........",
    "................",
    "................",
    "................",
    "................",
    "................",
]

HEART_EMPTY = [
    "................",
    "...kk....kk.....",
    "..k..k..k..k....",
    ".k....kk....k...",
    ".k..........k...",
    "kk..........kk..",
    ".k..........k...",
    "..k........k....",
    "...k......k.....",
    "....k....k......",
    ".....k..k.......",
    "......kk........",
    "................",
    "................",
    "................",
    "................",
]

MUTE_OFF = [
    "................",
    "................",
    "....kk..........",
    "...kwwk.kk......",
    "..kwwwk.k.k.....",
    "kkwwwwkkk.k.....",
    "kwwwwwwk..k.....",
    "kwwwwwwk..k.....",
    "kkwwwwkkk.k.....",
    "..kwwwk.k.k.....",
    "...kwwk.kk......",
    "....kk..........",
    "................",
    "................",
    "................",
    "................",
]

MUTE_ON = [
    "................",
    "................",
    "....kk.....k.k..",
    "...kwwk.kk..k...",
    "..kwwwk.k.k.k...",
    "kkwwwwkkk.kk.k..",
    "kwwwwwwk..k.....",
    "kwwwwwwk..k.....",
    "kkwwwwkkk.kk.k..",
    "..kwwwk.k.k.k...",
    "...kwwk.kk..k...",
    "....kk.....k.k..",
    "................",
    "................",
    "................",
    "................",
]


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def draw_background() -> list[tuple[int, int, int, int]]:
    w, h = 180, 320
    sky_top = (126, 186, 214, 255)
    sky_mid = (186, 222, 236, 255)
    horizon = (214, 236, 196, 255)
    pixels = canvas(w, h, sky_mid)

    for y in range(168):
        t = y / 167
        if t < 0.65:
            u = t / 0.65
            col = (
                lerp(sky_top[0], sky_mid[0], u),
                lerp(sky_top[1], sky_mid[1], u),
                lerp(sky_top[2], sky_mid[2], u),
                255,
            )
        else:
            u = (t - 0.65) / 0.35
            col = (
                lerp(sky_mid[0], horizon[0], u),
                lerp(sky_mid[1], horizon[1], u),
                lerp(sky_mid[2], horizon[2], u),
                255,
            )
        # chunky bands
        if y % 6 == 5:
            col = (max(0, col[0] - 8), max(0, col[1] - 4), max(0, col[2] - 4), 255)
        for x in range(w):
            put(pixels, w, x, y, col)

    def cloud(cx: int, cy: int, scale: int = 1) -> None:
        puffs = [
            (0, 1, 6, 3),
            (2, 0, 7, 4),
            (6, 1, 6, 3),
        ]
        white = (255, 255, 255, 255)
        shade = (232, 244, 248, 255)
        for ox, oy, pw, ph in puffs:
            for yy in range(ph * scale):
                for xx in range(pw * scale):
                    col = shade if yy > ph * scale - 2 else white
                    put(pixels, w, cx + ox * scale + xx, cy + oy * scale + yy, col)

    cloud(12, 18, 2)
    cloud(110, 10, 2)
    cloud(70, 36, 1)
    cloud(148, 42, 1)

    def hill(base_y: int, peak_x: int, radius: int, col: tuple[int, int, int, int]) -> None:
        for y in range(base_y - radius, base_y + 1):
            for x in range(peak_x - radius, peak_x + radius + 1):
                dx = x - peak_x
                dy = y - base_y
                if dx * dx + dy * dy * 2 <= radius * radius:
                    put(pixels, w, x, y, col)

    hill(168, 30, 34, (106, 160, 70, 255))
    hill(170, 90, 28, (90, 142, 58, 255))
    hill(168, 150, 36, (118, 168, 76, 255))

    def tree(tx: int, ty: int, big: bool = False) -> None:
        trunk = (122, 82, 40, 255)
        trunk_d = (90, 58, 28, 255)
        leaf = (74, 122, 58, 255)
        leaf_d = (56, 96, 44, 255)
        leaf_l = (108, 156, 72, 255)
        th = 18 if big else 12
        tw = 3 if big else 2
        for y in range(th):
            for x in range(tw):
                put(pixels, w, tx + x, ty + y, trunk_d if x == 0 else trunk)
        r = 11 if big else 8
        cx, cy = tx + tw // 2, ty + 2
        for y in range(cy - r, cy + r - 1):
            for x in range(cx - r, cx + r + 1):
                dx, dy = x - cx, y - cy
                if dx * dx + dy * dy <= r * r:
                    if dx * dx + dy * dy <= (r - 3) * (r - 3) and dy < 0:
                        put(pixels, w, x, y, leaf_l)
                    elif dx + dy > r // 2:
                        put(pixels, w, x, y, leaf_d)
                    else:
                        put(pixels, w, x, y, leaf)

    tree(22, 132, True)
    tree(54, 140, False)
    tree(128, 128, True)
    tree(158, 138, False)

    # fence
    wood = (184, 140, 72, 255)
    wood_d = (122, 82, 40, 255)
    for x in range(0, w, 2):
        put(pixels, w, x, 172, wood_d)
        put(pixels, w, x + 1, 172, wood)
        put(pixels, w, x, 182, wood_d)
        put(pixels, w, x + 1, 182, wood)
    for x in range(6, w, 16):
        for y in range(166, 190):
            put(pixels, w, x, y, wood_d)
            put(pixels, w, x + 1, y, wood)
            put(pixels, w, x + 2, y, wood)

    # grass field
    for y in range(188, h):
        t = (y - 188) / (h - 188)
        col = (
            lerp(124, 90, t),
            lerp(176, 138, t),
            lerp(72, 52, t),
            255,
        )
        stripe = (y % 8 == 0)
        for x in range(w):
            pixel = col
            n = (x * 17 + y * 31) % 11
            if n == 0:
                pixel = (min(255, col[0] + 18), min(255, col[1] + 16), min(255, col[2] + 8), 255)
            elif n == 1:
                pixel = (max(0, col[0] - 16), max(0, col[1] - 14), max(0, col[2] - 8), 255)
            if stripe and x % 3 == 0:
                pixel = (max(0, pixel[0] - 10), max(0, pixel[1] - 8), max(0, pixel[2] - 4), 255)
            put(pixels, w, x, y, pixel)

    # dirt path
    dirt = (196, 156, 96, 255)
    dirt_d = (168, 124, 72, 255)
    for y in range(210, h):
        half = 18 + (y - 210) // 8
        cx = 90
        for x in range(cx - half, cx + half):
            n = (x * 13 + y * 7) % 9
            put(pixels, w, x, y, dirt_d if n == 0 else dirt)

    # flowers
    flowers = [(18, 206, (244, 160, 176)), (40, 248, (255, 248, 238)), (152, 220, (244, 160, 176)), (168, 260, (232, 93, 117)), (28, 280, (255, 248, 238)), (160, 292, (244, 160, 176))]
    for fx, fy, col in flowers:
        put(pixels, w, fx, fy, (90, 138, 52, 255))
        put(pixels, w, fx, fy - 1, col + (255,))
        put(pixels, w, fx - 1, fy, col + (255,))
        put(pixels, w, fx + 1, fy, col + (255,))
        put(pixels, w, fx, fy + 1, (255, 248, 238, 255))

    return pixels


def tile_grass() -> list[str]:
    return [
        "aaaaaaaaaaaaaaaa",
        "afafafafafafafaf",
        "aaaaaaaaaaaaaaaa",
        "aafaafaafaafaafe",
        "aaaaaaaaaaaaaaaa",
        "afafafafafafafaf",
        "aaaaaaaaaaaaaaaa",
        "faefaefaefaefaef",
        "aaaaaaaaaaaaaaaa",
        "afafafafafafafaf",
        "aaaaaaaaaaaaaaaa",
        "aafaafaafaafaafe",
        "aaaaaaaaaaaaaaaa",
        "afafafafafafafaf",
        "aaaaaaaaaaaaaaaa",
        "faefaefaefaefaef",
    ]


def tile_dirt() -> list[str]:
    return [
        "yyyyyyyyyyyyyyyy",
        "ysyyyyysyyyyysyy",
        "yyyyyyyyyyyyyyyy",
        "yyyysyyyyysyyyyy",
        "yyyyyyyyyyyyyyyy",
        "ysyyyyyyyyyyyysy",
        "yyyyyyyyyyyyyyyy",
        "yyyyysyyyyysyyyy",
        "yyyyyyyyyyyyyyyy",
        "ysyyyyysyyyyysyy",
        "yyyyyyyyyyyyyyyy",
        "yyyysyyyyysyyyyy",
        "yyyyyyyyyyyyyyyy",
        "ysyyyyyyyyyyyysy",
        "yyyyyyyyyyyyyyyy",
        "yyyyysyyyyysyyyy",
    ]


def tile_fence() -> list[str]:
    return [
        "................",
        "...rorr.........",
        "...rorr.........",
        "rrrrrrrrrrrrrrrr",
        "oooooooooooooooo",
        "...rorr.........",
        "...rorr.........",
        "...rorr.........",
        "rrrrrrrrrrrrrrrr",
        "oooooooooooooooo",
        "...rorr.........",
        "...rorr.........",
        "...rorr.........",
        "...rorr.........",
        "...rorr.........",
        "...rorr.........",
    ]


def tile_leaves() -> list[str]:
    return [
        "....jjzzzzjj....",
        "..jjzzzzzzzzjj..",
        ".jzzzazzzzzzzzj."
        ".jzzzzzzzzzajj.",
        "jzzzzazzzzzzzzj",
        "jzzzzzzzzzazzzj",
        "jzzazzzzzzzzzzj",
        "jjzzzzzzazzzzzj",
        ".jzzzzzzzzzzjj.",
        ".jjzzazzzzzzj..",
        "..jjzzzzzzjj...",
        "....jjzzjj.....",
        "................",
        "................",
        "................",
        "................",
    ]


def main() -> None:
    dog = canvas(128, 32)
    for i, rows in enumerate((DOG_IDLE, DOG_BOB, DOG_HOP, DOG_HIT)):
        blit_map(dog, 128, i * 32, 0, rows, row_width=32)
    write_png(OUT / "shih-tzu.png", 128, 32, dog)

    items = canvas(80, 16)
    for i, rows in enumerate((BONE, HEART, BALL, SOAP, VACUUM)):
        blit_map(items, 80, i * 16, 0, rows, row_width=16)
    write_png(OUT / "items.png", 80, 16, items)

    ui = canvas(64, 16)
    for i, rows in enumerate((HEART_UI, HEART_EMPTY, MUTE_OFF, MUTE_ON)):
        blit_map(ui, 64, i * 16, 0, rows, row_width=16)
    write_png(OUT / "ui.png", 64, 16, ui)

    tiles = canvas(64, 16)
    for i, rows in enumerate((tile_grass(), tile_dirt(), tile_fence(), tile_leaves())):
        blit_map(tiles, 64, i * 16, 0, rows, row_width=16)
    write_png(OUT / "tiles.png", 64, 16, tiles)

    bg = draw_background()
    write_png(OUT / "background.png", 180, 320, bg)

    # Tiny face favicon
    face = canvas(32, 32)
    blit_map(face, 32, 0, 0, DOG_IDLE)
    write_png(OUT / "favicon.png", 32, 32, face)

    print(f"wrote sprites to {OUT}")


if __name__ == "__main__":
    main()
