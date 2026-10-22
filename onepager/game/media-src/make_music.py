"""게임 배경 음악(16초 반복용 칩튠)을 WAV로 만들어요. Python 표준 라이브러리만 써요.

사용법
  python3 make_music.py music.wav
  ffmpeg -y -i music.wav -codec:a libmp3lame -b:a 96k media/music.mp3

120 BPM, 8마디(16초)짜리 짧은 반복 음악이에요. 처음과 끝의 박자가 같아서 반복해도 끊기지 않게 들려요.
"""
import math
import random
import struct
import sys
import wave

RATE = 22050
BPM = 120
EIGHTH = 60 / BPM / 2  # 8분음표 길이(초)

NOTE = {}
for octave in range(2, 7):
    for i, name in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']):
        midi = 12 * (octave + 1) + i
        NOTE[f'{name}{octave}'] = 440 * 2 ** ((midi - 69) / 12)

# 마디마다 8분음표 8개. 코드 진행은 C - G - Am - F를 두 번이에요.
LEAD = [
    'E5 G5 C6 G5 E5 G5 C6 G5', 'D5 G5 B5 G5 D5 G5 B5 D6',
    'C5 E5 A5 E5 C5 E5 A5 C6', 'C5 F5 A5 F5 C5 F5 A5 C6',
    'G5 E5 C6 E6 D6 C6 G5 E5', 'D6 B5 G5 B5 D6 B5 G5 D5',
    'E5 A5 C6 A5 E5 A5 C6 B5', 'A5 F5 C6 A5 G5 F5 E5 D5',
]
BASS = ['C3', 'G2', 'A2', 'F2'] * 2


def square(phase, duty=0.25):
    return 1.0 if (phase % 1.0) < duty else -1.0


def triangle(phase):
    p = phase % 1.0
    return 4 * p - 1 if p < 0.5 else 3 - 4 * p


def envelope(t, length, attack=0.005, release=0.04):
    if t < attack:
        return t / attack
    if t > length - release:
        return max(0.0, (length - t) / release)
    return 1.0


def render():
    total = int(RATE * EIGHTH * 8 * len(LEAD))
    out = [0.0] * total
    rng = random.Random(7)
    step = int(RATE * EIGHTH)
    for bar, line in enumerate(LEAD):
        for k, name in enumerate(line.split()):
            start = (bar * 8 + k) * step
            freq = NOTE[name]
            length = step / RATE * 0.9
            for n in range(int(length * RATE)):
                t = n / RATE
                out[start + n] += 0.16 * square(freq * t) * envelope(t, length)
        root = NOTE[BASS[bar]]
        for beat in range(4):  # 4분음표마다 근음과 5도를 번갈아
            start = (bar * 8 + beat * 2) * step
            freq = root if beat % 2 == 0 else root * 1.5
            length = step * 2 / RATE * 0.95
            for n in range(int(length * RATE)):
                t = n / RATE
                out[start + n] += 0.22 * triangle(freq * t) * envelope(t, length, release=0.06)
            # 북: 박마다 낮게 떨어지는 소리
            for n in range(int(0.12 * RATE)):
                t = n / RATE
                out[start + n] += 0.28 * math.sin(2 * math.pi * (120 - 400 * t) * t) * (1 - t / 0.12)
            # 하이햇: 엇박에 짧은 잡음
            hat = start + step
            for n in range(int(0.03 * RATE)):
                out[hat + n] += 0.05 * (rng.random() * 2 - 1) * (1 - n / (0.03 * RATE))
    peak = max(abs(v) for v in out) or 1.0
    return [v / peak * 0.85 for v in out]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'music.wav'
    samples = render()
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b''.join(struct.pack('<h', int(v * 32767)) for v in samples))
    print(f'{path}: {len(samples) / RATE:.1f}초, {RATE}Hz')


if __name__ == '__main__':
    main()
