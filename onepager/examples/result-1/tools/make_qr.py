#!/usr/bin/env python3
"""주소를 QR 코드 PNG로 만든다. 사용법: make_qr.py <주소> [출력.png]
파이썬 표준 라이브러리만 쓴다. 바이트 모드, 오류 정정 M, 버전 1~6(최대 106바이트)."""
import struct
import sys
import zlib

# 버전: (데이터 코드워드 수, 블록당 ECC 코드워드 수, 블록 수)
VERSIONS = {1: (16, 10, 1), 2: (28, 16, 1), 3: (44, 26, 1), 4: (64, 18, 2), 5: (86, 24, 2), 6: (108, 16, 4)}
ALIGN = {2: 18, 3: 22, 4: 26, 5: 30, 6: 34}

# GF(256) 계산표
EXP, LOG = [0] * 512, [0] * 256
_x = 1
for _i in range(255):
    EXP[_i] = _x
    LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x11d
for _i in range(255, 512):
    EXP[_i] = EXP[_i - 255]


def rs_ecc(data, n):
    gen = [1]
    for i in range(n):
        nxt = [0] * (len(gen) + 1)
        for j, g in enumerate(gen):
            nxt[j] ^= g
            if g:
                nxt[j + 1] ^= EXP[LOG[g] + i]
        gen = nxt
    rem = [0] * n
    for b in data:
        f = b ^ rem[0]
        rem = rem[1:] + [0]
        if f:
            for i in range(n):
                if gen[i + 1]:
                    rem[i] ^= EXP[LOG[gen[i + 1]] + LOG[f]]
    return rem


def build_codewords(payload, version):
    total, ecc_len, blocks = VERSIONS[version]
    bits = '0100' + format(len(payload), '08b') + ''.join(format(b, '08b') for b in payload)
    bits += '0' * min(4, total * 8 - len(bits))
    bits += '0' * (-len(bits) % 8)
    data = [int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)]
    pad = [0xEC, 0x11]
    while len(data) < total:
        data.append(pad[(len(data) - len(bits) // 8) % 2])
    per = total // blocks
    chunks = [data[i * per:(i + 1) * per] for i in range(blocks)]
    eccs = [rs_ecc(c, ecc_len) for c in chunks]
    out = [chunks[b][i] for i in range(per) for b in range(blocks)]
    out += [eccs[b][i] for i in range(ecc_len) for b in range(blocks)]
    return out


def bch(value, poly, bits_total, shift):
    v = value << shift
    for i in range(bits_total - 1, shift - 1, -1):
        if v >> i & 1:
            v ^= poly << (i - shift)
    return (value << shift) | v


def make_matrix(payload):
    version = next((v for v in VERSIONS if VERSIONS[v][0] - 2 >= len(payload)), None)
    if version is None:
        raise SystemExit('주소가 너무 길어요 (최대 106바이트)')
    n = 17 + 4 * version
    cw = build_codewords(payload, version)
    bits = ''.join(format(b, '08b') for b in cw)

    base = [[None] * n for _ in range(n)]  # None = 비어 있음, 0/1 = 고정 모듈

    def setm(x, y, v):
        if 0 <= x < n and 0 <= y < n:
            base[y][x] = v

    def finder(cx, cy):
        for dy in range(-1, 8):
            for dx in range(-1, 8):
                d = max(abs(dx - 3), abs(dy - 3))
                setm(cx + dx, cy + dy, 1 if d in (0, 1, 3) and 0 <= dx <= 6 and 0 <= dy <= 6 and d != 2 else 0)

    finder(0, 0); finder(n - 7, 0); finder(0, n - 7)
    for i in range(8, n - 8):
        setm(i, 6, 1 - i % 2); setm(6, i, 1 - i % 2)
    if version in ALIGN:
        c = ALIGN[version]
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                setm(c + dx, c + dy, 1 if max(abs(dx), abs(dy)) != 1 else 0)
    setm(8, n - 8, 1)  # 항상 검은 모듈
    reserved = [[base[y][x] is not None for x in range(n)] for y in range(n)]
    for i in range(9):
        reserved[8][i] = reserved[i][8] = True
    for i in range(8):
        reserved[8][n - 1 - i] = reserved[n - 1 - i][8] = True

    def place(mask):
        m = [row[:] for row in base]
        i = 0
        x, up = n - 1, True
        while x > 0:
            if x == 6:
                x -= 1
            for k in range(n):
                y = n - 1 - k if up else k
                for xx in (x, x - 1):
                    if not reserved[y][xx]:
                        bit = int(bits[i]) if i < len(bits) else 0
                        i += 1
                        m[y][xx] = bit ^ MASKS[mask](xx, y)
            x -= 2
            up = not up
        fmt = bch((0b00 << 3) | mask, 0b10100110111, 15, 10) ^ 0b101010000010010  # ECC M = 00
        for k in range(15):
            b = fmt >> k & 1
            # 첫 번째 사본: 왼쪽 위 finder 주변
            if k < 6: m[k][8] = b
            elif k == 6: m[7][8] = b
            elif k == 7: m[8][8] = b
            elif k == 8: m[8][7] = b
            else: m[8][14 - k] = b
            # 두 번째 사본: 오른쪽 위 가로줄, 왼쪽 아래 세로줄
            if k < 8: m[8][n - 1 - k] = b
            else: m[n - 15 + k][8] = b
        return m

    best = min((place(mk) for mk in range(8)), key=penalty)
    return best


MASKS = [
    lambda x, y: (x + y) % 2 == 0, lambda x, y: y % 2 == 0, lambda x, y: x % 3 == 0,
    lambda x, y: (x + y) % 3 == 0, lambda x, y: (y // 2 + x // 3) % 2 == 0,
    lambda x, y: (x * y) % 2 + (x * y) % 3 == 0, lambda x, y: ((x * y) % 2 + (x * y) % 3) % 2 == 0,
    lambda x, y: ((x + y) % 2 + (x * y) % 3) % 2 == 0,
]
MASKS = [(lambda f: (lambda x, y: int(f(x, y))))(f) for f in MASKS]


def penalty(m):
    n = len(m)
    p = 0
    for grid in (m, [list(c) for c in zip(*m)]):
        for row in grid:
            run = 1
            for i in range(1, n):
                if row[i] == row[i - 1]:
                    run += 1
                else:
                    if run >= 5: p += run - 2
                    run = 1
            if run >= 5: p += run - 2
            s = ''.join(map(str, row))
            p += 40 * (s.count('10111010000') + s.count('00001011101'))
    for y in range(n - 1):
        for x in range(n - 1):
            if m[y][x] == m[y][x + 1] == m[y + 1][x] == m[y + 1][x + 1]:
                p += 3
    dark = sum(map(sum, m)) * 100 // (n * n)
    p += abs(dark - 50) // 5 * 10
    return p


def write_png(path, m, box=12, quiet=4):
    n = len(m) + quiet * 2
    rows = []
    for y in range(n):
        line = bytearray()
        for x in range(n):
            yy, xx = y - quiet, x - quiet
            dark = 0 <= yy < len(m) and 0 <= xx < len(m) and m[yy][xx]
            line += (b'\x00' if dark else b'\xff') * box
        rows += [b'\x00' + bytes(line)] * box

    def chunk(tag, data):
        body = tag + data
        return struct.pack('>I', len(data)) + body + struct.pack('>I', zlib.crc32(body) & 0xffffffff)

    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', n * box, n * box, 8, 0, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(b''.join(rows), 9)) + chunk(b'IEND', b''))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit('사용법: make_qr.py <주소> [출력.png]')
    url = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else 'qr.png'
    write_png(out, make_matrix(url.encode('utf-8')))
    print('만들었어요:', out, '->', url)
