#!/usr/bin/env python3
"""8비트 포스터(assets/poster.png)를 만든다. 파이썬 표준 라이브러리만 쓴다."""
import struct
import sys
import zlib
from pathlib import Path

GW, GH, SCALE = 96, 128, 8  # 도트 96x128, 8배 확대 -> 768x1024

PAL = {
    'S': (94, 200, 255), 'T': (150, 224, 255), 'W': (255, 255, 255), 'Y': (255, 224, 51),
    'y': (255, 170, 0), 'G': (60, 207, 90), 'g': (36, 168, 74), 'D': (139, 90, 43),
    'd': (107, 66, 28), 'O': (255, 122, 26), 'o': (200, 80, 0), 'P': (255, 150, 170),
    'K': (31, 36, 48), 'N': (255, 111, 15), 'L': (45, 190, 80), 'R': (255, 80, 110),
}

RABBIT = [
    "..WW....WW..",
    ".WPW....WPW.",
    ".WPW....WPW.",
    ".WPW....WPW.",
    ".WWWWWWWWWW.",
    "WWWWWWWWWWWW",
    "WWKWWWWWWKWW",
    "WWWWWWWWWWWW",
    "WPPWWNNWWPPW",
    ".WWWWWWWWWW.",
    "..WWWWWWWW..",
    ".WWWWWWWWWW.",
    "WWWWWWWWWWWW",
    "WWWWWWWWWWWW",
    ".WWW....WWW.",
]
CARROT = [
    ".L.L.L.",
    "..LLL..",
    ".OOOOO.",
    ".OOOOO.",
    ".OOoOO.",
    "..OOO..",
    "..OoO..",
    "...O...",
    "...O...",
]
FONT = {
    'C': ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'G': ["01111", "10000", "10000", "10011", "10001", "10001", "01111"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
}

grid = [['S'] * GW for _ in range(GH)]


def put(x, y, c):
    if 0 <= x < GW and 0 <= y < GH:
        grid[y][x] = c


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            put(xx, yy, c)


def sprite(art, x, y, k=1):
    for j, row in enumerate(art):
        for i, ch in enumerate(row):
            if ch != '.':
                rect(x + i * k, y + j * k, k, k, ch)


def text(s, x, y, k, color, shadow):
    for pass_color, off in ((shadow, 1), (color, 0)):
        cx = x
        for ch in s:
            for j, row in enumerate(FONT[ch]):
                for i, bit in enumerate(row):
                    if bit == '1':
                        rect(cx + i * k + off, y + j * k + off, k, k, pass_color)
            cx += 6 * k


# 하늘: 위쪽을 조금 더 진하게, 아래쪽은 밝게 (띠 모양으로 끊어서 8비트 느낌)
for y in range(GH):
    band = 'S' if y < 40 else 'T'
    for x in range(GW):
        grid[y][x] = band

# 해
for dy in range(-7, 8):
    for dx in range(-7, 8):
        if dx * dx + dy * dy <= 49:
            put(80 + dx, 54 + dy, 'Y' if dx * dx + dy * dy <= 30 else 'y')

# 구름
for cx, cy in ((6, 46), (66, 68)):
    rect(cx, cy + 2, 18, 4, 'W')
    rect(cx + 3, cy, 10, 3, 'W')
    rect(cx + 6, cy - 2, 5, 3, 'W')

# 언덕(계단식)과 땅
for x in range(GW):
    h1 = 78 + abs((x * 7) % 40 - 20) // 4
    for y in range(h1, GH):
        grid[y][x] = 'g'
    h2 = 88 + abs(((x + 20) * 5) % 30 - 15) // 5
    for y in range(h2, GH):
        grid[y][x] = 'G'
rect(0, 106, GW, 22, 'D')
rect(0, 106, GW, 2, 'G')
for x in range(0, GW, 8):
    rect(x, 112, 4, 2, 'd')
    rect(x + 4, 118, 4, 2, 'd')

# 떨어지는 당근들
for cx, cy in ((6, 66), (40, 42), (76, 82), (10, 90)):
    sprite(CARROT, cx, cy, 2)

# 주인공 토끼 (크게)
sprite(RABBIT, 33, 58, 2)
rect(33, 89, 24, 2, 'g')

# 제목
text("CARROT", 14, 6, 2, 'W', 'K')
text("DODGE", 20, 24, 2, 'Y', 'K')

# 반짝이
for x, y in ((5, 30), (90, 70), (44, 50), (74, 96)):
    put(x, y, 'W'); put(x - 1, y, 'W'); put(x + 1, y, 'W'); put(x, y - 1, 'W'); put(x, y + 1, 'W')


def write_png(path, rows):
    raw = bytearray()
    for row in rows:
        line = bytearray()
        for ch in row:
            line += bytes(PAL[ch]) * SCALE
        for _ in range(SCALE):
            raw += b'\x00' + line

    def chunk(tag, data):
        body = tag + data
        return struct.pack('>I', len(data)) + body + struct.pack('>I', zlib.crc32(body) & 0xffffffff)

    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', GW * SCALE, GH * SCALE, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    Path(path).write_bytes(png)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'assets/poster.png'
    write_png(out, grid)
    print('만들었어요:', out)
