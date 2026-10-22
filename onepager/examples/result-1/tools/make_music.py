#!/usr/bin/env python3
"""밝은 8비트 배경 음악(assets/music.wav)을 만든다. 파이썬 표준 라이브러리만 쓴다."""
import math
import random
import struct
import sys
import wave

RATE = 22050
BPM = 150
EIGHTH = 60 / BPM / 2  # 8분음표 길이(초)

NOTES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def freq(name):
    n = NOTES[name[0]]
    octave = int(name[1])
    return 440.0 * 2 ** ((n + (octave - 4) * 12 - 9) / 12)


MELODY = [
    "E5 . G5 E5 C6 . G5 E5",
    "D5 . G5 D5 B5 . G5 D5",
    "E5 . A5 E5 C6 . A5 E5",
    "F5 . A5 F5 C6 . A5 F5",
    "G5 E5 C5 E5 G5 C6 E6 C6",
    "B5 G5 D5 G5 B5 D6 B5 G5",
    "A5 F5 C5 F5 A5 C6 A5 F5",
    "G5 . B5 . D6 . G5 .",
]
BASS = ['C3', 'G2', 'A2', 'F2', 'C3', 'G2', 'F2', 'G2']


def square(phase, duty):
    return 1.0 if (phase % 1.0) < duty else -1.0


def triangle(phase):
    p = phase % 1.0
    return 4 * abs(p - 0.5) - 1


def render():
    total = int(len(MELODY) * 8 * EIGHTH * RATE)
    buf = [0.0] * total
    rnd = random.Random(8)
    for bar, line in enumerate(MELODY):
        for step, tok in enumerate(line.split()):
            start = int((bar * 8 + step) * EIGHTH * RATE)
            n = int(EIGHTH * RATE)
            if tok != '.':
                f = freq(tok)
                for i in range(n):
                    t = i / RATE
                    env = max(0.0, 1 - i / n) ** 0.6
                    buf[start + i] += 0.22 * env * square(f * t, 0.25)
            # 베이스: 뿌리음과 한 옥타브 위를 번갈아
            bf = freq(BASS[bar]) * (2 if step % 2 else 1)
            for i in range(n):
                t = i / RATE
                env = 1 - 0.3 * i / n
                buf[start + i] += 0.30 * env * triangle(bf * t)
            # 하이햇: 뒷박에 짧은 잡음
            if step % 2 == 1:
                for i in range(int(0.04 * RATE)):
                    buf[start + i] += 0.07 * (1 - i / (0.04 * RATE)) * rnd.uniform(-1, 1)
    peak = max(abs(v) for v in buf)
    return [v / peak * 0.8 for v in buf]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else 'assets/music.wav'
    samples = render()
    with wave.open(out, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b''.join(struct.pack('<h', int(v * 32767)) for v in samples))
    print('만들었어요:', out, f'({len(samples) / RATE:.1f}초)')


if __name__ == '__main__':
    main()
