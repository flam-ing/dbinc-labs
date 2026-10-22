"""PWA와 확장 프로그램 아이콘(PNG)을 Python 표준 라이브러리만으로 다시 만든다.

python3 make_icons.py   → pwa/icons/icon-192.png, icon-512.png, extension/icons/icon-16·48·128.png

주황 바탕에 흰 카드(방명록 한 장)와 기록 세 줄, 오른쪽 위의 알림 점을 그린다.
바탕을 끝까지 칠해서 휴대폰이 아이콘을 둥글게 잘라도 모양이 남는다.
"""
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parent
ORANGE = (255, 111, 15)
WHITE = (255, 252, 248)
LINE = (240, 196, 160)
INK = (43, 41, 38)


def pixel(x, y):
    """0~1 좌표의 한 점이 무슨 색인지 정한다."""
    # 알림 점(오른쪽 위 원)
    if (x - 0.74) ** 2 + (y - 0.26) ** 2 < 0.115 ** 2:
        return INK
    # 흰 카드(둥근 모서리 사각형)
    left, top, right, bottom, radius = 0.22, 0.24, 0.78, 0.80, 0.07
    if left <= x <= right and top <= y <= bottom:
        cx = min(max(x, left + radius), right - radius)
        cy = min(max(y, top + radius), bottom - radius)
        if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
            # 기록 세 줄
            for row, length in [(0.42, 0.62), (0.54, 0.66), (0.66, 0.50)]:
                if 0.31 <= x <= length and abs(y - row) <= 0.025:
                    return LINE
            return WHITE
    return ORANGE


def png(size):
    rows = []
    for j in range(size):
        row = bytearray([0])  # 필터 없음
        for i in range(size):
            row.extend(pixel((i + 0.5) / size, (j + 0.5) / size))
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)  # 8비트 RGB
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def main():
    targets = {
        ROOT / "pwa" / "icons" / "icon-192.png": 192,
        ROOT / "pwa" / "icons" / "icon-512.png": 512,
        ROOT / "extension" / "icons" / "icon-16.png": 16,
        ROOT / "extension" / "icons" / "icon-48.png": 48,
        ROOT / "extension" / "icons" / "icon-128.png": 128,
    }
    for path, size in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(png(size))
        print(f"{path.relative_to(ROOT)} {size}x{size} {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
