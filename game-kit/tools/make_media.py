#!/usr/bin/env python3
"""게임 미디어 묶음(배경 음악, 효과음, 엔딩 영상, ZIP)을 다시 만들어요.

1일차 2교시에서 무료 생성 사이트가 막혔을 때 나눠 주는 '미리 만든 파일'이에요.
Python 표준 라이브러리와 ffmpeg만 써요. 생성형 AI 서비스는 쓰지 않아요.

포스터(poster.png)는 이 스크립트가 그리지 않아요. 포스터 세 장은 Codex CLI의
내장 이미지 생성 도구로 따로 만들었고, `poster` 명령은 받은 그림을 1600×900으로
자르고 줄이는 일만 해요. 엔딩 영상은 그 포스터를 배경으로 써요.
포스터가 없으면 단색 배경으로 만들어요.

사용법(저장소 맨 위 폴더에서)
  python3 labs/game-kit/tools/make_media.py                  # 음악, 효과음, 영상, ZIP 전부
  python3 labs/game-kit/tools/make_media.py music sfx        # 고른 것만
  python3 labs/game-kit/tools/make_media.py video --set space
  python3 labs/game-kit/tools/make_media.py zip
  python3 labs/game-kit/tools/make_media.py poster --set bright --src 받은그림.png

필요한 것
  Python 3.9 이상, ffmpeg(libmp3lame, libx264, aac가 들어 있는 빌드)
  영상 글자용 TrueType 글꼴(.ttf). macOS와 Windows의 Arial 계열을 먼저 찾고,
  없으면 DejaVu나 Liberation 글꼴을 찾아요. --font로 직접 줄 수도 있어요.

만드는 파일(labs/game-kit 아래)
  media/<세트>/music.mp3   반복해서 틀 수 있는 배경 음악, 30~45초, 128kbps, 약 -16 LUFS
  media/<세트>/ending.mp4  1280×720, 7초, H.264와 AAC, 짧은 축하 음악이 들어 있어요
  media/sfx/jump.wav, coin.wav, hit.wav  짧은 효과음
  media-pack.zip           세트 셋, 효과음, README를 모두 담은 ZIP
  media-<세트>.zip         그 세트의 파일 세 개만 담은 ZIP(ZIP 맨 위에 바로 있어요)
"""
import argparse
import array
import json
import math
import os
import random
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import wave
import zipfile
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE.parent
MEDIA = KIT / 'media'
SETS = ('bright', 'space', 'forest')

RATE = 44100
W, H, FPS = 1280, 720, 30
DUR = 7.0                     # 엔딩 영상 길이(초)
NF = int(DUR * FPS)           # 엔딩 영상 프레임 수
TAU = 2.0 * math.pi

FONT_CANDIDATES = {
    'heavy': [
        '/System/Library/Fonts/Supplemental/Arial Black.ttf',
        'C:/Windows/Fonts/ariblk.ttf',
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
        'C:/Windows/Fonts/arialbd.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
        '/usr/share/fonts/liberation/LiberationSans-Bold.ttf',
    ],
    'round': [
        '/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf',
        'C:/Windows/Fonts/ARLRDBD.TTF',
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
        'C:/Windows/Fonts/arialbd.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
    ],
}


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# 1. 소리 합성(표준 라이브러리만)
# ---------------------------------------------------------------------------

_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def mtof(m):
    """MIDI 번호를 주파수(Hz)로 바꿔요. 69번이 라(A4, 440Hz)예요."""
    return 440.0 * 2.0 ** ((m - 69) / 12.0)


def pitch_class(name):
    return (_PC[name[0]] + name[1:].count('#') - name[1:].count('b')) % 12


def midi(name):
    """'C#5', 'Bb3' 같은 음 이름을 MIDI 번호로 바꿔요."""
    i = 1
    while i < len(name) and name[i] in '#b':
        i += 1
    return 12 * (int(name[i:]) + 1) + _PC[name[0]] + name[1:i].count('#') - name[1:i].count('b')


def parse(line):
    """'E5:2 G5:2 r:4'를 [(시작 칸, 길이 칸, MIDI 번호 또는 None)]로 바꿔요. 한 칸은 16분음표예요."""
    out, pos = [], 0
    for tok in line.split():
        name, _, ln = tok.partition(':')
        ln = int(ln) if ln else 2
        out.append((pos, ln, None if name == 'r' else midi(name)))
        pos += ln
    return out, pos


CHORDS = {
    'C': 'C E G', 'G': 'G B D', 'Am': 'A C E', 'F': 'F A C', 'Dm': 'D F A', 'Em': 'E G B',
    'G7': 'G B D F', 'Bb': 'Bb D F', 'A': 'A C# E', 'A7': 'A C# E G', 'Gm': 'G Bb D',
    'Bm': 'B D F#', 'D': 'D F# A', 'D/F#': 'D F# A', 'Am7': 'A C E G',
}


def chord_notes(ch, lo):
    """코드 음을 lo(MIDI 번호) 이상에서 시작해 위로 쌓아서 돌려줘요."""
    names = CHORDS[ch].split()
    out = [lo + (pitch_class(names[0]) - lo) % 12]
    for nm in names[1:]:
        out.append(out[-1] + ((pitch_class(nm) - out[-1]) % 12 or 12))
    return out


def bass_root(ch, lo):
    """코드의 베이스 음(슬래시 코드면 슬래시 뒤 음)을 lo 이상 한 옥타브 안에서 골라요."""
    name = ch.split('/')[1] if '/' in ch else CHORDS[ch].split()[0]
    return lo + (pitch_class(name) - lo) % 12


class Mix:
    """스테레오 버퍼예요. 반복 음악은 끝을 넘친 소리(꼬리)를 맨 앞에 더해서 이음새 없이 이어지게 해요."""

    def __init__(self, n, tail):
        self.n = n
        self.size = n + tail
        zeros = bytes(8 * self.size)
        self.L = array.array('d', zeros)
        self.R = array.array('d', zeros)
        self.rev = array.array('d', zeros)   # 잔향으로 보내는 버스

    def put(self, start, x, vol, pan=0.0, rev=0.0):
        if start < 0:
            x = x[-start:]
            start = 0
        end = min(start + len(x), self.size)
        if end <= start:
            return
        x = x[:end - start]
        gl = vol * math.cos((pan + 1.0) * math.pi / 4.0)
        gr = vol * math.sin((pan + 1.0) * math.pi / 4.0)
        L, R = self.L, self.R
        L[start:end] = array.array('d', [a + b * gl for a, b in zip(L[start:end], x)])
        R[start:end] = array.array('d', [a + b * gr for a, b in zip(R[start:end], x)])
        if rev:
            g = vol * rev
            V = self.rev
            V[start:end] = array.array('d', [a + b * g for a, b in zip(V[start:end], x)])

    def reverb(self, room=0.84, damp=0.3, wet=1.0, spread_ms=13.0):
        """잔향 버스를 Schroeder 방식(빗살 필터 4개와 전대역 통과 필터 2개)으로 울려서 섞어요."""
        x = self.rev
        n = self.size
        y = [0.0] * n
        for d in (1557, 1617, 1491, 1422):
            buf = [0.0] * d
            idx = 0
            store = 0.0
            for i in range(n):
                o = buf[idx]
                store = o * (1.0 - damp) + store * damp
                buf[idx] = x[i] + store * room
                y[i] += o
                idx += 1
                if idx == d:
                    idx = 0
        for d in (556, 225):
            buf = [0.0] * d
            idx = 0
            for i in range(n):
                b = buf[idx]
                v = y[i]
                buf[idx] = v + b * 0.5
                y[i] = b - v
                idx += 1
                if idx == d:
                    idx = 0
        off = int(spread_ms / 1000.0 * RATE)
        g = wet * 0.25
        L, R = self.L, self.R
        L[:] = array.array('d', [a + b * g for a, b in zip(L, y)])
        R[off:] = array.array('d', [a + b * g for a, b in zip(R[off:], y[:n - off])])

    def fold(self):
        """반복용: 길이를 넘친 꼬리를 맨 앞에 더해요. 그러면 끝에서 처음으로 끊김 없이 이어져요."""
        n = self.n
        for buf in (self.L, self.R):
            tail = buf[n:]
            m = len(tail)
            buf[0:m] = array.array('d', [a + b for a, b in zip(buf[0:m], tail)])
            del buf[n:]

    def trim(self, fade=0.25):
        """반복하지 않는 소리: 정해진 길이로 자르고 끝을 살짝 줄여요."""
        n = self.n
        f = int(fade * RATE)
        for buf in (self.L, self.R):
            del buf[n:]
            for i in range(f):
                buf[n - f + i] *= 1.0 - i / f


def envelope(n, gate, a, d, s, r_n):
    a_n = max(1, min(gate, int(a * RATE)))
    e = [i / a_n for i in range(a_n)]
    rest = gate - a_n
    if rest > 0:
        if d > 0 and s < 1.0:
            k = -1.0 / (d * RATE)
            e += [s + (1.0 - s) * math.exp(k * i) for i in range(rest)]
        else:
            e += [s] * rest
    last = e[-1] if e else 0.0
    if r_n > 0:
        e += [last * (1.0 - i / r_n) ** 2 for i in range(r_n)]
    return e


def wave_list(kind, n, freq, duty=0.5, vib=0.0, vib_rate=5.5, vib_delay=0.15,
              glide=None, arp=None, arp_rate=1.0 / 60.0):
    """-1~1 사이 파형 샘플 n개를 돌려줘요. pulse와 saw는 PolyBLEP로 거친 잡음을 줄여요."""
    if vib or glide or arp:
        ph = [0.0] * n
        p = 0.0
        for i in range(n):
            t = i / RATE
            f = arp[int(t / arp_rate) % len(arp)] if arp else freq
            if glide and t < glide[1]:
                f = glide[0] * (f / glide[0]) ** (t / glide[1])
            if vib and t > vib_delay:
                f *= 1.0 + vib * min(1.0, (t - vib_delay) / 0.25) * math.sin(TAU * vib_rate * t)
            ph[i] = p
            p += f / RATE
            p -= int(p)
    else:
        inc = freq / RATE
        ph = [(i * inc) % 1.0 for i in range(n)]
    dt = min(0.5, (max(arp) if arp else freq) / RATE)
    if kind == 'pulse':
        out = [0.0] * n
        lo, hi = dt, 1.0 - dt
        for i, p in enumerate(ph):
            v = 1.0 if p < duty else -1.0
            if p < lo:
                x = p / dt
                v += x + x - x * x - 1.0
            elif p > hi:
                x = (p - 1.0) / dt
                v += x * x + x + x + 1.0
            q = p - duty
            if q < 0.0:
                q += 1.0
            if q < lo:
                x = q / dt
                v -= x + x - x * x - 1.0
            elif q > hi:
                x = (q - 1.0) / dt
                v -= x * x + x + x + 1.0
            out[i] = v
        return out
    if kind == 'saw':
        out = [0.0] * n
        lo, hi = dt, 1.0 - dt
        for i, p in enumerate(ph):
            v = 2.0 * p - 1.0
            if p < lo:
                x = p / dt
                v -= x + x - x * x - 1.0
            elif p > hi:
                x = (p - 1.0) / dt
                v -= x * x + x + x + 1.0
            out[i] = v
        return out
    if kind == 'tri':
        return [4.0 * p - 1.0 if p < 0.5 else 3.0 - 4.0 * p for p in ph]
    if kind == 'tri4':   # 옛 게임기 삼각파처럼 16단계로 끊어요
        return [round((4.0 * p - 1.0 if p < 0.5 else 3.0 - 4.0 * p) * 7.5) / 7.5 for p in ph]
    if kind == 'sine':
        return [math.sin(TAU * p) for p in ph]
    raise ValueError(kind)


def lowpass(x, cutoff):
    a = 1.0 - math.exp(-TAU * cutoff / RATE)
    y = 0.0
    out = [0.0] * len(x)
    for i, v in enumerate(x):
        y += a * (v - y)
        out[i] = y
    return out


def tone(mix, start, dur, freq, kind='pulse', vol=0.2, pan=0.0, rev=0.0, duty=0.5,
         a=0.003, d=0.0, s=1.0, r=0.03, cutoff=0.0, poles=1, detune=0.0, **mod):
    """start(샘플 위치)부터 dur초 동안 음 하나를 넣어요."""
    gate = max(1, int(dur * RATE))
    r_n = max(1, int(r * RATE))
    n = gate + r_n
    x = wave_list(kind, n, freq, duty=duty, **mod)
    if detune:   # 살짝 어긋난 소리를 하나 더 겹쳐 두껍게 만들어요
        x2 = wave_list(kind, n, freq * 2.0 ** (detune / 1200.0), duty=duty, **mod)
        x = [(u + v) * 0.5 for u, v in zip(x, x2)]
    for _ in range(poles if cutoff else 0):
        x = lowpass(x, cutoff)
    e = envelope(n, gate, a, d, s, r_n)
    mix.put(start, [u * v for u, v in zip(x, e)], vol, pan, rev)


def noise_burst(rng, dur, decay, hp=True, cutoff=0.0, body=0.0, body_freq=180.0, body_decay=0.05):
    """잡음 한 번(하이햇, 스네어, 심벌)을 만들어요."""
    n = int(dur * RATE)
    out = [0.0] * n
    prev = 0.0
    k = -1.0 / (decay * RATE)
    for i in range(n):
        w = rng.uniform(-1.0, 1.0)
        out[i] = ((w - prev) * 0.6 if hp else w) * math.exp(k * i)
        prev = w
    if cutoff:
        out = lowpass(out, cutoff)
    if body:
        kb = -1.0 / (body_decay * RATE)
        for i in range(n):
            out[i] += body * math.sin(TAU * body_freq * i / RATE) * math.exp(kb * i)
    return out


def kick_wave(f0=160.0, f1=48.0, sweep=0.035, decay=0.16, click=0.25):
    n = int(decay * 5 * RATE)
    out = [0.0] * n
    p = 0.0
    for i in range(n):
        t = i / RATE
        p += (f1 + (f0 - f1) * math.exp(-t / sweep)) / RATE
        out[i] = math.sin(TAU * p) * math.exp(-t / decay)
    c = int(0.003 * RATE)
    for i in range(c):
        out[i] += click * (1.0 - i / c) * (1.0 if (i // 3) % 2 else -1.0)
    return out


def riser(mix, start, dur, vol, f0=300.0, f1=7000.0, pan=0.0, rev=0.0, seed=3):
    """점점 밝아지며 커지는 잡음(긴장감을 올릴 때)이에요."""
    rng = random.Random(seed)
    n = int(dur * RATE)
    out = [0.0] * n
    y = 0.0
    for i in range(n):
        t = i / n
        a = 1.0 - math.exp(-TAU * f0 * (f1 / f0) ** t / RATE)
        y += a * (rng.uniform(-1.0, 1.0) - y)
        out[i] = y * t * t
    mix.put(start, out, vol, pan, rev)


_KS_CACHE = {}


def pluck_wave(freq, dur, bright=0.6, decay=0.996, seed=1):
    """Karplus-Strong 방식의 뜯는 소리(하프, 기타 비슷한 소리)예요."""
    key = (round(freq, 3), dur, bright, decay, seed)
    if key in _KS_CACHE:
        return _KS_CACHE[key]
    rng = random.Random(seed)
    p = RATE / freq - 0.5
    N = max(2, int(p))
    frac = p - N
    C = (1.0 - frac) / (1.0 + frac)
    buf = [rng.uniform(-1.0, 1.0) for _ in range(N)]
    sm = 0.0                                  # 처음 잡음을 조금 부드럽게
    for i in range(N):
        sm += (1.0 - bright * 0.6) * (buf[i] - sm) if bright < 1 else buf[i] - sm
        buf[i] = sm
    n = int(dur * RATE)
    out = [0.0] * n
    idx = 0
    prev = 0.0
    ax = ay = 0.0
    for i in range(n):
        x = buf[idx]
        avg = decay * 0.5 * (x + prev)
        prev = x
        y = C * avg + ax - C * ay
        ax, ay = avg, y
        buf[idx] = y
        out[i] = x
        idx += 1
        if idx == N:
            idx = 0
    f = int(0.01 * RATE)
    for i in range(f):
        out[n - f + i] *= 1.0 - i / f
    _KS_CACHE[key] = out
    return out


def bell(mix, start, freq, vol, pan=0.0, rev=0.0):
    """종소리(배음이 정수배가 아닌 사인파 여러 개)예요."""
    n = int(2.6 * RATE)
    parts = ((1.0, 1.0, 1.4), (2.0, 0.45, 0.9), (2.76, 0.35, 0.6), (5.4, 0.18, 0.3))
    out = [0.0] * n
    for ratio, amp, dec in parts:
        f = freq * ratio
        if f > RATE * 0.45:
            continue
        k = -1.0 / (dec * RATE)
        for i in range(n):
            out[i] += amp * math.sin(TAU * f * i / RATE) * math.exp(k * i)
    a = int(0.002 * RATE)
    for i in range(a):
        out[i] *= i / a
    mix.put(start, out, vol, pan, rev)


def chirp(mix, start, vol, pan, rev, rng):
    """새소리: 아주 짧은 사인파 휘파람 2~4번이에요."""
    t = start
    for _ in range(rng.randint(2, 4)):
        d = rng.uniform(0.045, 0.08)
        n = int(d * RATE)
        fa, fb = rng.uniform(2800, 3600), rng.uniform(3900, 5200)
        if rng.random() < 0.5:
            fa, fb = fb, fa
        out = [0.0] * n
        p = 0.0
        for i in range(n):
            x = i / n
            p += (fa + (fb - fa) * x) / RATE
            out[i] = math.sin(TAU * p) * math.sin(math.pi * x) ** 2
        mix.put(t, out, vol, pan, rev)
        t += n + int(rng.uniform(0.02, 0.05) * RATE)


class Song:
    """박자 격자 위에 음을 놓는 도우미예요. 한 칸은 16분음표, 한 마디는 16칸이에요."""

    def __init__(self, bpm, bars, tail=4.0, seed=1):
        self.step = round(RATE * 60.0 / bpm / 4.0)
        self.bar = self.step * 16
        self.bars = bars
        self.mix = Mix(self.bar * bars, int(tail * RATE))
        self.rng = random.Random(seed)

    def at(self, bar, step=0.0):
        return int(round((bar * 16 + step) * self.step))

    def play(self, bar, text, inst, shift=0.0, vol=1.0, pan=None, transpose=0):
        inst = dict(inst)
        gate = inst.pop('gate', 0.9)
        base_vol = inst.pop('vol', 0.2)
        if pan is not None:
            inst['pan'] = pan
        events, _ = parse(text)
        for pos, ln, m in events:
            if m is None:
                continue
            tone(self.mix, self.at(bar, pos + shift), ln * self.step / RATE * gate,
                 mtof(m + transpose), vol=base_vol * vol, **inst)


def render_wav(mix, path, loop, peak=0.89, soft=0.0):
    """버퍼를 16비트 스테레오 WAV로 저장해요. soft를 주면 큰 봉우리만 부드럽게 눌러요."""
    if loop:
        mix.fold()
    else:
        mix.trim()
    L, R = mix.L, mix.R
    m = max(max(abs(v) for v in L), max(abs(v) for v in R)) or 1.0
    g = 1.0 / m
    if soft:
        th = 1.0 - soft

        def shape(v):
            a = abs(v)
            if a <= th:
                return v
            y = th + soft * math.tanh((a - th) / soft)
            return y if v > 0 else -y
        L = array.array('d', [shape(v * g) for v in L])
        R = array.array('d', [shape(v * g) for v in R])
        m2 = max(max(abs(v) for v in L), max(abs(v) for v in R)) or 1.0
        g = peak / m2
    else:
        g *= peak
    n = len(L)
    pcm = array.array('h', bytes(4 * n))
    pcm[0::2] = array.array('h', [max(-32768, min(32767, int(round(v * g * 32767)))) for v in L])
    pcm[1::2] = array.array('h', [max(-32768, min(32767, int(round(v * g * 32767)))) for v in R])
    if sys.byteorder == 'big':
        pcm.byteswap()
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())
    return n / RATE


# --- 세트별 배경 음악 --------------------------------------------------------

def song_bright():
    """밝은 8비트 음악: 다장조, 144BPM, 24마디(A 8마디, A' 8마디, B 8마디)."""
    s = Song(bpm=144, bars=24, seed=11)
    chords = ['C', 'G', 'Am', 'F', 'C', 'G', 'F', 'G',
              'C', 'G', 'Am', 'F', 'F', 'G', 'C', 'C',
              'F', 'G', 'Em', 'Am', 'Dm', 'G', 'F', 'G7']
    a_part = [
        'E5:2 G5:2 C6:2 G5:2 A5:2 G5:2 E5:2 C5:2',
        'D5:2 G5:2 B5:2 D6:2 C6:2 B5:2 G5:4',
        'C6:3 B5:1 A5:2 E5:2 A5:2 C6:2 E6:4',
        'D6:2 C6:2 A5:2 F5:2 G5:6 r:2',
    ]
    lead = a_part + [
        'E5:2 G5:2 C6:2 G5:2 A5:2 G5:2 E5:2 G5:2',
        'B5:2 D6:2 G6:3 F#6:1 G6:2 D6:2 B5:4',
        'A5:2 C6:2 F6:3 E6:1 D6:2 C6:2 A5:4',
        'B5:2 C6:2 D6:4 G5:6 r:2',
    ] + a_part + [
        'A5:2 C6:2 F6:4 E6:2 D6:2 C6:2 A5:2',
        'B5:2 D6:2 G6:4 F6:2 E6:2 D6:2 B5:2',
        'C6:4 G5:2 E5:2 G5:2 C6:2 E6:2 G6:2',
        'C6:6 r:4 G5:2 A5:2 B5:2',
        'C6:6 A5:2 F6:4 E6:4',
        'D6:6 B5:2 G5:8',
        'E6:6 D6:2 B5:4 G5:4',
        'A5:8 C6:4 E6:4',
        'F6:6 E6:2 D6:4 A5:4',
        'B5:6 C6:2 D6:8',
        'C6:2 D6:2 C6:2 A5:2 F5:2 A5:2 C6:2 F6:2',
        'G6:4 F6:2 D6:2 B5:2 G5:2 F5:2 D5:2',
    ]
    lead_a = dict(kind='pulse', duty=0.25, vol=0.20, a=0.002, d=0.12, s=0.6, r=0.03, gate=0.85,
                  vib=0.004, vib_rate=6.0, vib_delay=0.18)
    lead_b = dict(lead_a, duty=0.5, vol=0.18, d=0.25, s=0.7, gate=0.92)
    for bar, line in enumerate(lead):
        inst = lead_b if bar >= 16 else lead_a
        s.play(bar, line, inst, pan=0.0)
        echo = dict(inst, duty=0.125, vib=0.0)
        s.play(bar, line, echo, shift=3, vol=0.38 if bar >= 16 else 0.28, pan=-0.45)

    stab = dict(kind='pulse', duty=0.5, a=0.002, d=0.05, s=0.25, r=0.02, cutoff=5000)
    bass = dict(kind='tri4', vol=0.42, a=0.002, d=0.0, s=1.0, r=0.02)
    for bar, ch in enumerate(chords):
        freqs = [mtof(m) for m in chord_notes(ch, 60)]
        r2 = bass_root(ch, 36)
        if bar < 16:
            for st in (2, 6, 10, 14):
                tone(s.mix, s.at(bar, st), s.step * 1.4 / RATE, freqs[0], vol=0.085, pan=0.4,
                     arp=freqs, **stab)
            pattern = [r2, r2 + 12, r2, r2 + 12, r2, r2 + 12, r2, r2 + 7]
            for k, m in enumerate(pattern):
                tone(s.mix, s.at(bar, 2 * k), s.step * 1.6 / RATE, mtof(m), **bass)
        else:
            for half in (0, 8):
                tone(s.mix, s.at(bar, half), s.step * 7 / RATE, freqs[0], vol=0.07, pan=0.4,
                     arp=freqs, **dict(stab, d=0.35, s=0.35, r=0.08))
            for st, ln, m in ((0, 4, r2), (4, 2, r2 + 7), (6, 2, r2 + 12), (8, 4, r2), (12, 2, r2 + 7), (14, 2, r2 + 12)):
                tone(s.mix, s.at(bar, st), s.step * ln * 0.85 / RATE, mtof(m), **bass)

    rng = s.rng
    kick = kick_wave(f0=180, f1=52, sweep=0.03, decay=0.09, click=0.3)
    snares = [noise_burst(rng, 0.22, 0.07, hp=False, cutoff=7000, body=0.6, body_freq=200, body_decay=0.04) for _ in range(3)]
    hats = [noise_burst(rng, 0.05, 0.012) for _ in range(4)]
    crash = noise_burst(rng, 1.6, 0.4)
    toms = [kick_wave(f0=f, f1=f * 0.55, sweep=0.06, decay=0.12, click=0.1) for f in (300, 240, 190, 150)]
    m = s.mix
    for bar in range(24):
        b_section = bar >= 16
        kicks = (0, 6, 8) if b_section else ((0, 8, 10) if bar % 2 else (0, 8))
        for st in kicks:
            m.put(s.at(bar, st), kick, 0.5)
        fill = {7: (12, 13, 14, 15), 15: (8, 10, 12, 13, 14, 15)}.get(bar, ())
        for st in (4, 12):
            if st not in fill:
                m.put(s.at(bar, st), rng.choice(snares), 0.30, -0.05)
        for i, st in enumerate(fill):
            m.put(s.at(bar, st), rng.choice(snares), 0.18 + 0.03 * i, -0.05)
        if bar == 23:
            for i, st in enumerate((8, 10, 12, 14)):
                m.put(s.at(bar, st), toms[i], 0.42, -0.3 + 0.2 * i)
        hat_steps = range(0, 16) if b_section else range(0, 16, 2)
        for st in hat_steps:
            if bar == 23 and st >= 8:
                break
            accent = st % 4 == 2
            m.put(s.at(bar, st), rng.choice(hats), (0.09 if accent else 0.055) * (0.8 if b_section else 1.0), 0.25)
        if bar in (0, 8, 16):
            m.put(s.at(bar, 0), crash, 0.16, 0.2)
    return s


def song_space():
    """긴장감 있는 신스 음악: 라단조, 136BPM, 24마디(A 그루브, B 주제, C 다리와 고조)."""
    s = Song(bpm=136, bars=24, seed=22)
    chords = ['Dm', 'Dm', 'Bb', 'C', 'Dm', 'Dm', 'Bb', 'A',
              'Dm', 'F', 'Bb', 'A', 'Gm', 'Bb', 'A', 'A',
              'Bb', 'C', 'Dm', 'Dm', 'Bb', 'C', 'A', 'A']
    m = s.mix
    bass = dict(kind='saw', vol=0.23, a=0.002, d=0.07, s=0.55, r=0.02, cutoff=650, poles=2)
    arp_i = dict(kind='pulse', duty=0.25, a=0.002, d=0.05, s=0.3, r=0.02, cutoff=3200)
    pad = dict(kind='saw', vol=0.050, a=0.35, d=0.0, s=1.0, r=0.5, cutoff=1100, poles=2, detune=9.0, rev=0.0)
    for bar, ch in enumerate(chords):
        r2 = bass_root(ch, 38)
        if 16 <= bar < 20:
            pattern = [(0, 6, r2), (6, 2, r2 + 12), (8, 6, r2), (14, 2, r2 + 12)]
        else:
            octs = (2, 6, 10, 13)
            pattern = [(st, 1, r2 + 12 if st in octs else r2) for st in range(16)]
        for st, ln, note_m in pattern:
            tone(m, s.at(bar, st), s.step * ln * 0.62 / RATE, mtof(note_m), **bass)

        tones = chord_notes(ch, 62)
        seq = [tones[0], tones[2], tones[0] + 12, tones[1] + 12, tones[2] + 12, tones[1] + 12, tones[0] + 12, tones[2]]
        up = 12 if bar >= 16 else 0
        level = 0.075 if bar < 8 else 0.058
        for st in range(16):
            note_m = seq[st % 8] + up
            if bar in (19, 23):          # 다리 끝에서는 올라가는 아르페지오로 긴장을 쌓아요
                note_m = tones[st % 3] + 12 * (st // 3) - 12 + up
            tone(m, s.at(bar, st), s.step * 0.8 / RATE, mtof(note_m), vol=level, pan=0.5, **arp_i)
            tone(m, s.at(bar, st + 3), s.step * 0.8 / RATE, mtof(note_m), vol=level * 0.35, pan=-0.5, **arp_i)
        if bar >= 8:
            for note_m in chord_notes(ch, 50):
                tone(m, s.at(bar, 0), s.bar / RATE * 0.98, mtof(note_m), pan=0.0, **pad)

    lead = dict(kind='pulse', duty=0.5, vol=0.17, a=0.01, d=0.2, s=0.75, r=0.12, cutoff=2600,
                detune=6.0, vib=0.005, vib_rate=5.2, vib_delay=0.25, gate=0.95)
    theme = [
        'D5:6 F5:2 A5:8', 'G5:4 F5:4 E5:4 C5:4', 'D5:6 F5:2 Bb5:8', 'A5:8 G5:4 E5:4',
        'G5:6 Bb5:2 D6:8', 'C6:4 Bb5:4 A5:4 G5:4', 'A5:4 C#6:4 E6:8', 'F6:4 E6:4 C#6:4 A5:4',
        'F5:16', 'E5:8 G5:8', 'A5:16', 'r:8 A5:2 C6:2 D6:4',
        'F6:12 E6:2 D6:2', 'E6:8 C6:8', 'C#6:16', 'E6:8 r:8',
    ]
    for k, line in enumerate(theme):
        bar = 8 + k
        s.play(bar, line, lead)
        s.play(bar, line, dict(lead, vib=0.0), shift=6, vol=0.32, pan=-0.55 if k % 2 else 0.55)

    rng = s.rng
    kick = kick_wave(f0=140, f1=44, sweep=0.04, decay=0.16, click=0.2)
    claps = [noise_burst(rng, 0.25, 0.09, hp=True, cutoff=5000, body=0.35, body_freq=185, body_decay=0.05) for _ in range(3)]
    hats = [noise_burst(rng, 0.05, 0.014) for _ in range(4)]
    opens = [noise_burst(rng, 0.25, 0.05) for _ in range(2)]
    crash = noise_burst(rng, 1.8, 0.5)
    for bar in range(24):
        half_time = 16 <= bar < 20
        kicks = (0, 10) if half_time else (0, 4, 8, 12)
        if 8 <= bar < 16 and bar % 2:
            kicks = kicks + (14,)
        for st in kicks:
            m.put(s.at(bar, st), kick, 0.48)
        if bar == 23:
            for st in range(16):
                m.put(s.at(bar, st), rng.choice(claps), 0.10 + 0.017 * st, 0.0)
        elif half_time:
            m.put(s.at(bar, 8), rng.choice(claps), 0.30)
        elif bar >= 4:
            for st in (4, 12):
                m.put(s.at(bar, st), rng.choice(claps), 0.30)
        for st in (range(0, 16, 2) if half_time else range(16)):
            if st % 4 == 2:
                m.put(s.at(bar, st), rng.choice(opens), 0.06, 0.3)
            else:
                m.put(s.at(bar, st), rng.choice(hats), 0.05, 0.3)
        if bar in (0, 8, 16, 20):
            m.put(s.at(bar, 0), crash, 0.14, -0.2)
    riser(m, s.at(23, 0), s.bar / RATE, 0.10, f0=300, f1=7000)
    return s


def song_forest():
    """잔잔한 숲 음악: 사장조, 90BPM, 16마디(A 8마디, B 8마디). 하프 같은 뜯는 소리와 피리 소리예요."""
    s = Song(bpm=90, bars=16, seed=33)
    chords = ['G', 'D/F#', 'Em', 'C', 'G', 'Bm', 'C', 'D',
              'Em', 'C', 'G', 'D', 'Em', 'C', 'Am7', 'D']
    voicing = {
        'G': 'G3 D4 G4 B4 D5', 'D/F#': 'F#3 A3 D4 F#4 A4', 'Em': 'E3 B3 E4 G4 B4',
        'C': 'C3 G3 C4 E4 G4', 'Bm': 'B2 F#3 B3 D4 F#4', 'D': 'D3 A3 D4 F#4 A4',
        'Am7': 'A2 E3 G3 C4 E4',
    }
    m = s.mix
    rng = s.rng
    order = [0, 2, 1, 3, 2, 4, 3, 2]
    for bar, ch in enumerate(chords):
        notes = [midi(x) for x in voicing[ch].split()]
        for k, idx in enumerate(order):
            nm = notes[idx]
            start = s.at(bar, 2 * k) + int(rng.uniform(-0.004, 0.004) * RATE)
            w = pluck_wave(mtof(nm), 1.6, bright=0.55, decay=0.997, seed=nm % 5)
            vol = (0.20 if k == 0 else 0.15) * rng.uniform(0.88, 1.05)
            m.put(start, w, vol, pan=-0.3 if idx < 2 else 0.3, rev=0.35)
        r2 = bass_root(ch, 36)
        for st, note_m in ((0, r2), (8, r2 + 7)):
            tone(m, s.at(bar, st), s.step * 7.5 / RATE, mtof(note_m), kind='tri', vol=0.30, a=0.01,
                 d=0.6, s=0.55, r=0.2, cutoff=500, pan=0.0)
        if bar >= 8:
            for note_m in chord_notes(ch, 55):
                tone(m, s.at(bar, 0), s.bar / RATE * 0.95, mtof(note_m), kind='tri', vol=0.045,
                     a=0.7, s=1.0, r=0.6, cutoff=1400, pan=0.0, rev=0.5)

    flute = dict(kind='tri', vol=0.20, a=0.06, d=0.3, s=0.8, r=0.18, cutoff=3200, vib=0.006,
                 vib_rate=5.0, vib_delay=0.25, rev=0.45, gate=0.93)
    melody = [
        'B4:4 D5:4 G5:6 F#5:2', 'E5:4 D5:4 A4:8', 'B4:4 E5:4 G5:6 A5:2', 'G5:4 E5:4 C5:8',
        'D5:4 G5:4 B5:6 A5:2', 'F#5:4 D5:4 B4:8', 'C5:4 E5:4 G5:4 E5:4', 'A5:6 G5:2 F#5:8',
        'G5:6 F#5:2 E5:8', 'E5:4 G5:4 C6:8', 'B5:6 A5:2 G5:8', 'A5:8 F#5:8',
        'G5:6 A5:2 B5:8', 'C6:4 B5:4 G5:8', 'A5:4 G5:4 E5:4 C5:4', 'D5:8 r:4 A4:2 C5:2',
    ]
    for bar, line in enumerate(melody):
        s.play(bar, line, flute, pan=0.08)

    shakers = [noise_burst(rng, 0.08, 0.025, hp=True, cutoff=9000) for _ in range(4)]
    soft_kick = kick_wave(f0=90, f1=48, sweep=0.05, decay=0.12, click=0.0)
    for bar in range(16):
        for st in range(0, 16, 2):
            m.put(s.at(bar, st), rng.choice(shakers), 0.05 if st % 4 == 2 else 0.032, 0.35)
        if bar >= 8:
            m.put(s.at(bar, 0), soft_kick, 0.30)
            m.put(s.at(bar, 8), soft_kick, 0.18)
            for st in (4, 12):
                tone(m, s.at(bar, st), 0.02, 880.0, kind='sine', vol=0.05, a=0.001, d=0.02, s=0.0, r=0.03,
                     pan=-0.25, rev=0.3)
    for bar, st, pan in ((1, 6, -0.6), (5, 10, 0.6), (10, 4, -0.5), (13, 12, 0.55)):
        chirp(m, s.at(bar, st), 0.05, pan, 0.5, rng)
    m.reverb(room=0.84, damp=0.3, wet=1.0)
    return s


SONGS = {'bright': song_bright, 'space': song_space, 'forest': song_forest}


# --- 엔딩 영상용 짧은 음악(징글) ------------------------------------------------

def S(t):
    return int(round(t * RATE))


def jingle_bright(land_times):
    mix = Mix(int(DUR * RATE), 0)
    rng = random.Random(5)
    blip = dict(kind='pulse', duty=0.25, a=0.002, d=0.06, s=0.3, r=0.03)
    for t, nm in zip(land_times, ('C5', 'E5', 'G5', 'C6', 'E6', 'G6')):
        tone(mix, S(t), 0.09, mtof(midi(nm)), vol=0.22, pan=0.0, **blip)
    kick = kick_wave(f0=180, f1=52, sweep=0.03, decay=0.1, click=0.3)
    pop = noise_burst(rng, 0.35, 0.08, hp=False, cutoff=6000, body=0.4, body_freq=220, body_decay=0.05)
    crash = noise_burst(rng, 2.2, 0.6)
    mix.put(S(1.05), kick, 0.55)
    mix.put(S(1.05), pop, 0.40)
    lead = dict(kind='pulse', duty=0.5, a=0.002, d=0.2, s=0.75, r=0.05, vib=0.006, vib_rate=6.0, vib_delay=0.2)
    melody = [(1.10, 0.09, 'G5'), (1.20, 0.09, 'C6'), (1.30, 0.09, 'E6'), (1.40, 0.28, 'G6'),
              (1.70, 0.09, 'E6'), (1.80, 0.55, 'G6'), (2.45, 0.13, 'A6'), (2.60, 0.13, 'G6'),
              (2.75, 0.13, 'F6'), (2.90, 0.13, 'D6'), (3.05, 1.25, 'C6')]
    for t, d, nm in melody:
        tone(mix, S(t), d, mtof(midi(nm)), vol=0.22, pan=0.0, **lead)
        tone(mix, S(t + 0.075), d, mtof(midi(nm)), vol=0.07, pan=-0.5, **dict(lead, duty=0.125))
    harm = dict(kind='pulse', duty=0.125, a=0.002, d=0.4, s=0.5, r=0.15)
    for t, d, ch in ((1.40, 1.0, 'C'), (2.45, 0.6, 'G'), (3.05, 1.6, 'C')):
        freqs = [mtof(x) for x in chord_notes(ch, 64)]
        tone(mix, S(t), d, freqs[0], vol=0.10, pan=0.45, arp=freqs, **harm)
    bass = dict(kind='tri4', a=0.002, s=1.0, r=0.04)
    for t, d, nm in ((1.40, 0.3, 'C3'), (1.80, 0.25, 'G2'), (2.10, 0.3, 'C3'), (2.45, 0.55, 'G2'), (3.05, 1.4, 'C3')):
        tone(mix, S(t), d, mtof(midi(nm)), vol=0.42, **bass)
    for t in (1.40, 1.80, 3.05):
        mix.put(S(t), kick, 0.5)
    snare = noise_burst(rng, 0.2, 0.06, hp=False, cutoff=7000, body=0.5, body_freq=200, body_decay=0.04)
    for i in range(8):
        mix.put(S(2.45 + i * 0.075), snare, 0.12 + 0.025 * i, -0.05)
    mix.put(S(3.05), crash, 0.22, 0.15)
    for nm in ('C4', 'E4', 'G4', 'C5'):         # 끝까지 조용히 남는 화음
        tone(mix, S(3.05), 2.6, mtof(midi(nm)), kind='tri', vol=0.05, a=0.3, d=1.2, s=0.45, r=1.0, pan=0.0)
    sparkle = [midi(x) for x in ('C7', 'D7', 'E7', 'G7', 'A7', 'C8')]
    t = 3.2
    while t < 6.5:
        nm = rng.choice(sparkle)
        tone(mix, S(t), 0.05, mtof(nm), kind='tri', vol=0.06 * (1.0 - (t - 3.2) / 3.5), a=0.001, d=0.08, s=0.0,
             r=0.05, pan=rng.uniform(-0.7, 0.7))
        t += rng.uniform(0.07, 0.16)
    return mix


def jingle_space():
    mix = Mix(int(DUR * RATE), 0)
    rng = random.Random(6)
    riser(mix, S(0.0), 1.35, 0.20, f0=250, f1=8000, seed=9)
    arp = dict(kind='pulse', duty=0.25, a=0.002, d=0.05, s=0.3, r=0.02, cutoff=3500)
    tones_ = [midi(x) for x in ('D4', 'F4', 'A4', 'D5', 'F5', 'A5')]
    t, k = 0.15, 0
    while t < 1.30:
        tone(mix, S(t), 0.06, mtof(tones_[k % 6]), vol=0.05 + 0.08 * t, pan=0.4 if k % 2 else -0.4, **arp)
        t += 0.085
        k += 1
    boom = kick_wave(f0=120, f1=34, sweep=0.06, decay=0.55, click=0.2)
    mix.put(S(1.35), boom, 0.70)
    mix.put(S(1.35), noise_burst(rng, 2.4, 0.7), 0.20, 0.0)
    pad = dict(kind='saw', a=0.02, d=1.5, s=0.6, r=1.6, cutoff=2200, poles=2, detune=10.0)
    for nm in ('D3', 'A3', 'D4', 'F#4', 'A4'):
        tone(mix, S(1.35), 3.6, mtof(midi(nm)), vol=0.075, pan=0.0, **pad)
    lead = dict(kind='pulse', duty=0.5, a=0.01, d=0.25, s=0.8, r=0.5, cutoff=3000, detune=7.0,
                vib=0.006, vib_rate=5.4, vib_delay=0.2)
    for t0, d, nm in ((1.40, 0.18, 'A5'), (1.62, 0.18, 'D6'), (1.84, 0.52, 'F#6'),
                      (2.42, 0.18, 'E6'), (2.64, 0.24, 'F#6'), (2.92, 1.6, 'A6')):
        tone(mix, S(t0), d, mtof(midi(nm)), vol=0.17, pan=0.0, **lead)
        tone(mix, S(t0 + 0.33), d, mtof(midi(nm)), vol=0.055, pan=-0.6, **lead)
    sp = [midi(x) for x in ('D6', 'F#6', 'A6', 'D7', 'A6', 'F#6')]
    t, k = 3.0, 0
    while t < 6.3:
        tone(mix, S(t), 0.05, mtof(sp[k % 6]), kind='pulse', duty=0.125, vol=0.05 * (1 - (t - 3.0) / 3.5),
             a=0.001, d=0.06, s=0.0, r=0.04, pan=0.5 if k % 2 else -0.5)
        t += 0.11
        k += 1
    return mix


def jingle_forest():
    mix = Mix(int(DUR * RATE), int(3 * RATE))
    rng = random.Random(7)
    for k, nm in enumerate(('G3', 'B3', 'D4', 'G4', 'B4', 'D5', 'G5')):
        m = midi(nm)
        mix.put(S(0.30 + 0.11 * k), pluck_wave(mtof(m), 2.4, bright=0.6, decay=0.998, seed=m % 5), 0.22,
                pan=-0.4 + 0.13 * k, rev=0.4)
    flute = dict(kind='tri', a=0.07, d=0.4, s=0.8, r=0.5, cutoff=3200, vib=0.007, vib_rate=5.0, vib_delay=0.2)
    for t, d, nm in ((1.20, 0.42, 'D5'), (1.65, 0.42, 'E5'), (2.10, 1.5, 'G5')):
        tone(mix, S(t), d, mtof(midi(nm)), vol=0.22, pan=0.05, rev=0.5, **flute)
    for nm in ('G3', 'B3', 'D4'):
        tone(mix, S(1.2), 3.8, mtof(midi(nm)), kind='tri', vol=0.06, a=0.6, s=1.0, r=1.2, cutoff=1500, rev=0.5)
    tone(mix, S(1.2), 3.8, mtof(midi('G2')), kind='tri', vol=0.13, a=0.05, d=1.5, s=0.5, r=1.0, cutoff=500)
    bell(mix, S(2.7), mtof(midi('G6')), 0.09, pan=0.3, rev=0.5)
    bell(mix, S(3.05), mtof(midi('D7')), 0.06, pan=-0.3, rev=0.5)
    chirp(mix, S(3.4), 0.05, -0.6, 0.5, rng)
    chirp(mix, S(4.7), 0.045, 0.6, 0.5, rng)
    for k, nm in enumerate(('G2', 'D3', 'G3', 'B3', 'D4')):
        m = midi(nm)
        mix.put(S(3.7 + 0.035 * k), pluck_wave(mtof(m), 3.2, bright=0.5, decay=0.998, seed=m % 5), 0.17,
                pan=-0.2 + 0.1 * k, rev=0.45)
    mix.reverb(room=0.86, damp=0.3, wet=1.0)
    return mix


# --- 효과음 -------------------------------------------------------------------

def make_sfx(out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(8)

    def save(name, mix, seconds, level=0.5):
        mix.n = int(seconds * RATE)
        mix.trim(fade=0.01)
        x = mix.L
        peak = max(abs(v) for v in x) or 1.0
        g = level / peak
        pcm = array.array('h', [int(round(v * g * 32767)) for v in x])
        if sys.byteorder == 'big':
            pcm.byteswap()
        with wave.open(str(out_dir / name), 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(pcm.tobytes())
        log(f'  sfx/{name}: {seconds:.2f}초')

    jump = Mix(int(0.32 * RATE), 0)
    tone(jump, 0, 0.22, 940.0, kind='pulse', duty=0.25, vol=1.0, a=0.002, d=0.12, s=0.25, r=0.06,
         glide=(250.0, 0.17))
    save('jump.wav', jump, 0.30)

    coin = Mix(int(0.5 * RATE), 0)
    tone(coin, 0, 0.065, mtof(midi('B5')), kind='pulse', duty=0.5, vol=1.0, a=0.001, s=1.0, r=0.004)
    tone(coin, S(0.068), 0.36, mtof(midi('E6')), kind='pulse', duty=0.5, vol=1.0, a=0.001, d=0.13, s=0.0, r=0.05)
    save('coin.wav', coin, 0.45)

    hit = Mix(int(0.4 * RATE), 0)
    hit.put(0, noise_burst(rng, 0.3, 0.06, hp=False, cutoff=4000), 1.0)
    tone(hit, 0, 0.24, 70.0, kind='pulse', duty=0.5, vol=0.9, a=0.001, d=0.1, s=0.2, r=0.05,
         glide=(480.0, 0.22), cutoff=3000)
    held = 0.0
    for i in range(hit.size):   # 샘플 3개마다 값을 붙잡아서 옛 게임기처럼 거칠게
        if i % 3 == 0:
            held = hit.L[i]
        hit.L[i] = held
    save('hit.wav', hit, 0.32, level=0.7)


# ---------------------------------------------------------------------------
# 2. 글자 그리기(TrueType 글꼴을 직접 읽어서 다각형으로 칠해요)
# ---------------------------------------------------------------------------

class Font:
    """TrueType(.ttf) 글꼴에서 글자 윤곽선을 읽어요. glyf 표가 있는 글꼴만 돼요."""

    def __init__(self, path):
        self.path = str(path)
        d = self.data = Path(path).read_bytes()
        base = struct.unpack('>I', d[12:16])[0] if d[:4] == b'ttcf' else 0
        num = struct.unpack('>H', d[base + 4:base + 6])[0]
        self.tab = {}
        for i in range(num):
            r = base + 12 + 16 * i
            self.tab[d[r:r + 4].decode('latin-1')] = struct.unpack('>I', d[r + 8:r + 12])[0]
        if 'glyf' not in self.tab:
            raise ValueError(f'{path}: TrueType 윤곽선(glyf)이 없는 글꼴이에요')
        h = self.tab['head']
        self.upem = struct.unpack('>H', d[h + 18:h + 20])[0]
        long_loca = struct.unpack('>h', d[h + 50:h + 52])[0] == 1
        nglyph = struct.unpack('>H', d[self.tab['maxp'] + 4:self.tab['maxp'] + 6])[0]
        lo = self.tab['loca']
        if long_loca:
            self.loca = struct.unpack('>%dI' % (nglyph + 1), d[lo:lo + 4 * (nglyph + 1)])
        else:
            self.loca = [v * 2 for v in struct.unpack('>%dH' % (nglyph + 1), d[lo:lo + 2 * (nglyph + 1)])]
        hh = self.tab['hhea']
        self.nhm = struct.unpack('>H', d[hh + 34:hh + 36])[0]
        self._read_cmap()
        self._read_kern()

    def _read_cmap(self):
        d, c = self.data, self.tab['cmap']
        sub = None
        for i in range(struct.unpack('>H', d[c + 2:c + 4])[0]):
            pid, eid, off = struct.unpack('>HHI', d[c + 4 + 8 * i:c + 12 + 8 * i])
            if struct.unpack('>H', d[c + off:c + off + 2])[0] == 4 and (pid, eid) in ((3, 1), (0, 3), (0, 4), (0, 1), (0, 0)):
                sub = c + off
                if (pid, eid) == (3, 1):
                    break
        if sub is None:
            raise ValueError('cmap 형식 4가 없는 글꼴이에요')
        seg = struct.unpack('>H', d[sub + 6:sub + 8])[0] // 2
        p = sub + 14
        self._ends = struct.unpack('>%dH' % seg, d[p:p + 2 * seg])
        p += 2 * seg + 2
        self._starts = struct.unpack('>%dH' % seg, d[p:p + 2 * seg])
        p += 2 * seg
        self._deltas = struct.unpack('>%dh' % seg, d[p:p + 2 * seg])
        p += 2 * seg
        self._ro_pos = p
        self._ros = struct.unpack('>%dH' % seg, d[p:p + 2 * seg])

    def _read_kern(self):
        self.kern = {}
        k = self.tab.get('kern')
        if k is None:
            return
        d = self.data
        if struct.unpack('>H', d[k:k + 2])[0] != 0:
            return
        p = k + 4
        _, length, coverage = struct.unpack('>HHH', d[p:p + 6])
        if coverage >> 8 == 0 and coverage & 1:
            npairs = struct.unpack('>H', d[p + 6:p + 8])[0]
            q = p + 14
            for j in range(npairs):
                left, right, v = struct.unpack('>HHh', d[q + 6 * j:q + 6 * j + 6])
                self.kern[(left, right)] = v

    def gid(self, ch):
        c = ord(ch)
        for i, end in enumerate(self._ends):
            if end >= c:
                if self._starts[i] > c:
                    return 0
                if self._ros[i] == 0:
                    return (c + self._deltas[i]) & 0xFFFF
                a = self._ro_pos + 2 * i + self._ros[i] + 2 * (c - self._starts[i])
                g = struct.unpack('>H', self.data[a:a + 2])[0]
                return (g + self._deltas[i]) & 0xFFFF if g else 0
        return 0

    def advance(self, g):
        p = self.tab['hmtx'] + 4 * min(g, self.nhm - 1)
        return struct.unpack('>H', self.data[p:p + 2])[0]

    def contours(self, g):
        d = self.data
        start, end = self.loca[g], self.loca[g + 1]
        if start == end:
            return []
        p = self.tab['glyf'] + start
        ncont = struct.unpack('>h', d[p:p + 2])[0]
        p += 10
        if ncont < 0:            # 다른 글자를 조합한 글자
            out = []
            while True:
                flags, idx = struct.unpack('>HH', d[p:p + 4])
                p += 4
                if flags & 1:
                    a1, a2 = struct.unpack('>hh', d[p:p + 4])
                    p += 4
                else:
                    a1, a2 = struct.unpack('>bb', d[p:p + 2])
                    p += 2
                xa, xb, ya, yb = 1.0, 0.0, 0.0, 1.0
                if flags & 8:
                    xa = yb = struct.unpack('>h', d[p:p + 2])[0] / 16384.0
                    p += 2
                elif flags & 0x40:
                    xa, yb = (v / 16384.0 for v in struct.unpack('>hh', d[p:p + 4]))
                    p += 4
                elif flags & 0x80:
                    xa, xb, ya, yb = (v / 16384.0 for v in struct.unpack('>hhhh', d[p:p + 8]))
                    p += 8
                dx, dy = (a1, a2) if flags & 2 else (0, 0)
                for cont in self.contours(idx):
                    out.append([(xa * x + ya * y + dx, xb * x + yb * y + dy, on) for x, y, on in cont])
                if not flags & 0x20:
                    return out
        ends = struct.unpack('>%dH' % ncont, d[p:p + 2 * ncont])
        p += 2 * ncont
        p += 2 + struct.unpack('>H', d[p:p + 2])[0]
        npts = ends[-1] + 1 if ncont else 0
        flags = []
        while len(flags) < npts:
            f = d[p]
            p += 1
            flags.append(f)
            if f & 8:
                flags.extend([f] * d[p])
                p += 1
        xs, x = [], 0
        for f in flags:
            if f & 2:
                x += d[p] if f & 16 else -d[p]
                p += 1
            elif not f & 16:
                x += struct.unpack('>h', d[p:p + 2])[0]
                p += 2
            xs.append(x)
        ys, y = [], 0
        for f in flags:
            if f & 4:
                y += d[p] if f & 32 else -d[p]
                p += 1
            elif not f & 32:
                y += struct.unpack('>h', d[p:p + 2])[0]
                p += 2
            ys.append(y)
        out, s = [], 0
        for e in ends:
            out.append([(xs[i], ys[i], flags[i] & 1) for i in range(s, e + 1)])
            s = e + 1
        return out

    def layout(self, text, size, tracking=0.0):
        """글자마다 (펜 x 위치, 다각형 목록)을 돌려줘요. 기준선이 y=0이고 아래쪽이 +예요."""
        sc = size / self.upem
        x, prev, out = 0.0, None, []
        for ch in text:
            g = self.gid(ch)
            if prev is not None:
                x += self.kern.get((prev, g), 0) * sc
            polys = [_flatten(c, sc) for c in self.contours(g)]
            out.append((x, [p for p in polys if len(p) > 2]))
            x += self.advance(g) * sc + tracking
            prev = g
        return out, x - tracking


def _flatten(pts, sc):
    seq = []
    n = len(pts)
    for i in range(n):
        x0, y0, on0 = pts[i]
        x1, y1, on1 = pts[(i + 1) % n]
        seq.append((x0, y0, on0))
        if not on0 and not on1:
            seq.append(((x0 + x1) / 2.0, (y0 + y1) / 2.0, 1))
    first = next(i for i, p in enumerate(seq) if p[2])
    seq = seq[first:] + seq[:first]
    m = len(seq)
    cx, cy = seq[0][0], seq[0][1]
    out = [(cx * sc, -cy * sc)]
    i = 1
    while i <= m:
        x, y, on = seq[i % m]
        if on:
            out.append((x * sc, -y * sc))
            cx, cy = x, y
            i += 1
        else:
            ex, ey, _ = seq[(i + 1) % m]
            k = max(3, int(math.hypot(ex - cx, ey - cy) * sc / 2.5))
            for j in range(1, k + 1):
                t = j / k
                a, b, c = (1 - t) * (1 - t), 2 * (1 - t) * t, t * t
                out.append(((a * cx + b * x + c * ex) * sc, -(a * cy + b * y + c * ey) * sc))
            cx, cy = ex, ey
            i += 2
    return out


def raster(polys, w, h, ox, oy, ss=6):
    """다각형을 w×h 덮임 지도(0~1)로 칠해요. 0이 아닌 감김 규칙, 한 줄에 ss번 표본을 써요."""
    rows = [[] for _ in range(h)]
    for poly in polys:
        n = len(poly)
        for i in range(n):
            x0, y0 = poly[i]
            x1, y1 = poly[(i + 1) % n]
            x0 += ox
            x1 += ox
            y0 += oy
            y1 += oy
            if y0 == y1:
                continue
            dirn = 1
            if y0 > y1:
                x0, y0, x1, y1, dirn = x1, y1, x0, y0, -1
            e = (y0, y1, x0, (x1 - x0) / (y1 - y0), dirn)
            for r in range(max(0, int(y0)), min(h - 1, int(y1)) + 1):
                rows[r].append(e)
    cov = [0.0] * (w * h)
    wgt = 1.0 / ss
    for r in range(h):
        es = rows[r]
        if not es:
            continue
        acc = [0.0] * (w + 2)
        diff = [0.0] * (w + 2)
        for k in range(ss):
            y = r + (k + 0.5) / ss
            xs = sorted((x0 + (y - y0) * sl, dn) for (y0, y1, x0, sl, dn) in es if y0 <= y < y1)
            wind = 0
            for j in range(len(xs) - 1):
                wind += xs[j][1]
                if wind:
                    xa = max(0.0, xs[j][0])
                    xb = min(float(w), xs[j + 1][0])
                    if xb <= xa:
                        continue
                    ia, ib = int(xa), int(xb)
                    if ia == ib:
                        acc[ia] += (xb - xa) * wgt
                    else:
                        acc[ia] += (ia + 1 - xa) * wgt
                        diff[ia + 1] += wgt
                        diff[ib] -= wgt
                        acc[ib] += (xb - ib) * wgt
        run = 0.0
        base = r * w
        for x in range(w):
            run += diff[x]
            v = acc[x] + run
            cov[base + x] = 1.0 if v > 1.0 else v
    return cov


def _dt1(f):
    """1차원 제곱 거리 변환(Felzenszwalb 방식)이에요."""
    n = len(f)
    d = [0.0] * n
    v = [0] * n
    z = [0.0] * (n + 1)
    k = 0
    z[0], z[1] = -1e20, 1e20
    for q in range(1, n):
        s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k])
        while s <= z[k]:
            k -= 1
            s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k])
        k += 1
        v[k] = q
        z[k] = s
        z[k + 1] = 1e20
    k = 0
    for q in range(n):
        while z[k + 1] < q:
            k += 1
        d[q] = (q - v[k]) ** 2 + f[v[k]]
    return d


def distance(cov, w, h):
    """각 픽셀에서 글자 안쪽까지의 거리(픽셀)를 구해요. 테두리를 둥글게 두르는 데 써요."""
    f = [0.0 if c >= 0.5 else 1e12 for c in cov]
    tmp = [0.0] * (w * h)
    for x in range(w):
        tmp[x::w] = _dt1(f[x::w])
    out = [0.0] * (w * h)
    for y in range(h):
        out[y * w:(y + 1) * w] = [math.sqrt(v) for v in _dt1(tmp[y * w:(y + 1) * w])]
    return out


def _box(line, r):
    n = len(line)
    k = 2 * r + 1
    out = [0.0] * n
    s = sum(line[i] for i in range(0, min(n, r + 1)))
    for i in range(n):
        out[i] = s / k
        a, b = i + r + 1, i - r
        if a < n:
            s += line[a]
        if b >= 0:
            s -= line[b]
    return out


def blur(a, w, h, r, passes=3):
    if r <= 0:
        return list(a)
    a = list(a)
    for _ in range(passes):
        for y in range(h):
            a[y * w:(y + 1) * w] = _box(a[y * w:(y + 1) * w], r)
        for x in range(w):
            a[x::w] = _box(a[x::w], r)
    return a


def shift(a, w, h, dx, dy):
    out = [0.0] * (w * h)
    for y in range(h):
        sy = y - dy
        if 0 <= sy < h:
            for x in range(max(0, dx), min(w, w + dx)):
                out[y * w + x] = a[sy * w + x - dx]
    return out


def hex_rgb(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def text_sprite(polys, top, bottom, outline, out_px, shadow=None, glow=None):
    """글자 다각형을 테두리, 그림자, 빛번짐이 있는 RGBA 그림으로 만들어요.

    돌려주는 값: (RGBA 바이트, 너비, 높이, 펜 원점 x, 기준선 y)
    """
    pts = [p for poly in polys for p in poly]
    minx, maxx = min(p[0] for p in pts), max(p[0] for p in pts)
    miny, maxy = min(p[1] for p in pts), max(p[1] for p in pts)
    pad = out_px + 4
    if shadow:
        pad = max(pad, out_px + max(abs(shadow[0]), abs(shadow[1])) + 3 * shadow[2] + 4)
    if glow:
        pad = max(pad, out_px + 3 * glow[1] + 4)
    w = int(maxx - minx + 2 * pad) + 1
    h = int(maxy - miny + 2 * pad) + 1
    ox, oy = pad - minx, pad - miny
    cov = raster(polys, w, h, ox, oy)
    dist = distance(cov, w, h)
    sil = [1.0 if c >= 0.5 else max(0.0, min(1.0, out_px + 0.5 - dd)) for c, dd in zip(cov, dist)]
    sil = [max(a, c) for a, c in zip(sil, cov)]
    layers = []
    if glow:
        color, radius, alpha = glow
        layers.append((hex_rgb(color), [min(1.0, v * alpha * 1.6) for v in blur(sil, w, h, radius)]))
    if shadow:
        dx, dy, rad, alpha, color = shadow
        layers.append((hex_rgb(color), [v * alpha for v in blur(shift(sil, w, h, dx, dy), w, h, rad)]))
    layers.append((hex_rgb(outline), sil))
    top_c, bot_c = hex_rgb(top), hex_rgb(bottom)
    y0, y1 = oy + miny, oy + maxy
    px = bytearray(w * h * 4)
    for y in range(h):
        t = min(1.0, max(0.0, (y - y0) / max(1.0, y1 - y0)))
        t = t * t * (3 - 2 * t)
        fill = tuple(top_c[i] + (bot_c[i] - top_c[i]) * t for i in range(3))
        for x in range(w):
            i = y * w + x
            pr = pg = pb = pa = 0.0
            for (cr, cg, cb), al in layers:
                a = al[i]
                if a > 0.0:
                    k = 1.0 - a
                    pr = cr * a + pr * k
                    pg = cg * a + pg * k
                    pb = cb * a + pb * k
                    pa = a + pa * k
            a = cov[i]
            if a > 0.0:
                k = 1.0 - a
                pr = fill[0] * a + pr * k
                pg = fill[1] * a + pg * k
                pb = fill[2] * a + pb * k
                pa = a + pa * k
            if pa > 0.0:
                j = 4 * i
                px[j] = min(255, int(pr / pa + 0.5))
                px[j + 1] = min(255, int(pg / pa + 0.5))
                px[j + 2] = min(255, int(pb / pa + 0.5))
                px[j + 3] = min(255, int(pa * 255 + 0.5))
    return bytes(px), w, h, ox, oy


def write_png(path, w, h, rgba):
    raw = b''.join(b'\x00' + rgba[y * w * 4:(y + 1) * w * 4] for y in range(h))

    def chunk(tag, body):
        return struct.pack('>I', len(body)) + tag + body + struct.pack('>I', zlib.crc32(tag + body) & 0xFFFFFFFF)
    data = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
    Path(path).write_bytes(data)


def find_font(role, override=None):
    if override:
        return Font(override)
    for p in FONT_CANDIDATES[role]:
        if Path(p).exists():
            try:
                return Font(p)
            except Exception:
                continue
    raise SystemExit('영상 글자에 쓸 TrueType 글꼴을 찾지 못했어요. --font /경로/글꼴.ttf 로 알려 주세요.')


def fit_size(font, text, max_w, tracking_ratio=0.0, start=320):
    size = start
    while size > 20:
        _, width = font.layout(text, size, size * tracking_ratio)
        if width <= max_w:
            return size
        size -= 4
    return size


# ---------------------------------------------------------------------------
# 3. 엔딩 영상(파이썬이 파티클 층을 그리고 ffmpeg가 합쳐요)
# ---------------------------------------------------------------------------

class Layer:
    """1280×720 RGBA 투명 층이에요. 색종이, 별, 반딧불이를 여기에 그려서 ffmpeg로 넘겨요."""

    def __init__(self):
        self.zero = bytes(W * H * 4)
        self.buf = bytearray(self.zero)

    def clear(self):
        self.buf[:] = self.zero

    def hline(self, x0, x1, y, rgba):
        if y < 0 or y >= H:
            return
        x0, x1 = max(0, int(x0)), min(W, int(x1))
        if x1 <= x0:
            return
        i = (y * W + x0) * 4
        self.buf[i:i + 4 * (x1 - x0)] = rgba * (x1 - x0)

    def blend(self, x, y, r, g, b, a):
        if a <= 0.003 or x < 0 or y < 0 or x >= W or y >= H:
            return
        if a > 1.0:
            a = 1.0
        buf = self.buf
        i = (y * W + x) * 4
        da = buf[i + 3] / 255.0
        if da == 0.0:
            buf[i] = r
            buf[i + 1] = g
            buf[i + 2] = b
            buf[i + 3] = int(a * 255)
            return
        oa = a + da * (1.0 - a)
        k = a / oa
        buf[i] = int(r * k + buf[i] * (1.0 - k))
        buf[i + 1] = int(g * k + buf[i + 1] * (1.0 - k))
        buf[i + 2] = int(b * k + buf[i + 2] * (1.0 - k))
        buf[i + 3] = int(oa * 255)

    def sprite(self, spr, cx, cy, alpha, rgb):
        r, g, b = rgb
        x0, y0 = int(cx), int(cy)
        for dx, dy, a in spr:
            self.blend(x0 + dx, y0 + dy, r, g, b, a * alpha)


def glow_sprite(radius, core, halo):
    out = []
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            d = math.hypot(dx, dy)
            a = 0.95 * math.exp(-(d / core) ** 2) + 0.35 * math.exp(-(d / halo) ** 2)
            if a > 0.01:
                out.append((dx, dy, min(1.0, a)))
    return out


def leaf_sprites(n_angles=24, length=26, width=12):
    sprites = []
    for k in range(n_angles):
        ang = TAU * k / n_angles
        ca, sa = math.cos(ang), math.sin(ang)
        pts = {}
        r = length // 2 + 2
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                cov = 0
                for sy in range(3):
                    for sx in range(3):
                        px = dx + (sx + 0.5) / 3 - 0.5
                        py = dy + (sy + 0.5) / 3 - 0.5
                        u = px * ca + py * sa
                        v = -px * sa + py * ca
                        half = length / 2.0
                        if abs(u) < half:
                            lim = (width / 2.0) * max(0.0, math.sin(math.pi * (u + half) / length)) ** 0.8
                            if abs(v) < lim:
                                cov += 1
                if cov:
                    pts[(dx, dy)] = cov / 9.0
        sprites.append([(dx, dy, a) for (dx, dy), a in pts.items()])
    return sprites


def rays_png(path, size=1000, count=18):
    """엔딩 글자 뒤에서 도는 햇살 무늬(투명 PNG)를 만들어요."""
    px = bytearray(size * size * 4)
    c = size / 2.0
    for y in range(size):
        for x in range(size):
            dx, dy = x + 0.5 - c, y + 0.5 - c
            r = math.hypot(dx, dy) / c
            if r >= 1.0:
                continue
            ray = 0.5 + 0.5 * math.cos(math.atan2(dy, dx) * count)
            ray = max(0.0, min(1.0, (ray - 0.3) * 2.5))
            a = (0.36 * ray + 0.32 * math.exp(-(r / 0.3) ** 2)) * (1.0 - r) ** 1.4
            i = 4 * (y * size + x)
            px[i:i + 4] = bytes((255, 250, 225, min(255, int(a * 255))))
    write_png(path, size, size, bytes(px))


def plan_bright(work, fonts):
    font = fonts['heavy']
    text = 'CLEAR!'
    track = 0.10
    size = fit_size(font, text, 1000, track)
    glyphs, width = font.layout(text, size, size * track)
    colors = [('#FF7A7A', '#E0283C'), ('#FFC163', '#F57C00'), ('#FFF07A', '#F2B200'),
              ('#8AF5A8', '#18A957'), ('#7FD0FF', '#1E6FE0'), ('#E2A8FF', '#8E44EC')]
    allpts = [p for _, polys in glyphs for poly in polys for p in poly]
    cy_text = (min(p[1] for p in allpts) + max(p[1] for p in allpts)) / 2.0
    base_y = 320 - cy_text
    start_x = (W - width) / 2.0
    layers = []
    rays = work / 'bright-rays.png'
    rays_png(rays)
    layers.append({'kind': 'image', 'path': rays,
                   'pre': "scale=1700:1700,rotate=a='0.30*t':ow=1280:oh=790:c=none,fade=t=in:st=0.25:d=0.8:alpha=1",
                   'x': '0', 'y': '-35'})
    land = []
    for k, ((pen, polys), (top, bottom)) in enumerate(zip(glyphs, colors)):
        rgba, w, h, ox, oy = text_sprite(polys, top, bottom, '#24205A', 11,
                                         shadow=(7, 9, 4, 0.45, '#120F33'))
        p = work / f'bright-letter-{k}.png'
        write_png(p, w, h, rgba)
        x = int(round(start_x + pen - ox))
        y = int(round(base_y - oy))
        t0 = 0.30 + 0.11 * k
        land.append(t0 + math.pi / 18.0)
        wave_ = f"if(gte(t,1.9),7*min(1,(t-1.9)/0.4)*sin(6.9115*(t-1.9)-{0.75 * k:.2f}),0)"
        layers.append({'kind': 'image', 'path': p, 'x': str(x),
                       'y': f"{y}-420*exp(-4.2*(t-{t0:.2f}))*abs(cos(9*(t-{t0:.2f})))-{wave_}",
                       'enable': f'gte(t,{t0:.2f})'})
    layers.append({'kind': 'particles'})

    rng = random.Random(21)
    palette = [hex_rgb(c) for c in ('#FF4D4D', '#FFB000', '#FFE14D', '#3DDC84', '#4DA3FF', '#B36BFF', '#FF6FD8', '#FFFFFF')]
    pieces = []
    for side in (1, -1):                # 1은 왼쪽 아래에서 오른쪽 위로, -1은 오른쪽 아래에서 왼쪽 위로 쏴요
        for _ in range(75):
            ang = math.radians(rng.uniform(58, 82))
            sp = rng.uniform(1300, 2300)
            pieces.append(dict(t0=1.05 + rng.uniform(0, 0.08), x=640.0 - side * 560, y=760.0,
                               vx=side * sp * math.cos(ang), vy=-sp * math.sin(ang)))
    for _ in range(70):
        pieces.append(dict(t0=1.5 + rng.uniform(0, 4.5), x=rng.uniform(0, W), y=-30.0, vx=rng.uniform(-30, 30),
                           vy=rng.uniform(120, 200)))
    for p in pieces:
        p.update(col=rng.choice(palette), w=rng.uniform(9, 15), h=rng.uniform(14, 22), flip=rng.uniform(5, 12),
                 ph=rng.uniform(0, TAU), sway=rng.uniform(15, 40), sw=rng.uniform(2.5, 5.5), sh=rng.uniform(0, TAU),
                 alive=False)
    dt = 1.0 / FPS

    def draw(layer, t, frame):
        for p in pieces:
            if t < p['t0']:
                continue
            for _ in range(2):          # 1/60초씩 두 번 움직여요
                h2 = dt / 2
                p['vy'] += (600.0 - 3.2 * p['vy']) * h2
                p['vx'] += -2.2 * p['vx'] * h2
                p['x'] += p['vx'] * h2
                p['y'] += p['vy'] * h2
            age = t - p['t0']
            cx = p['x'] + p['sway'] * math.sin(p['sw'] * age + p['sh']) * min(1.0, age)
            cy = p['y']
            if cy > H + 30 or cy < -400:
                continue
            c = math.cos(p['flip'] * age + p['ph'])
            w = max(1.5, p['w'] * abs(c))
            r, g, b = p['col']
            if c < 0:
                r, g, b = int(r * 0.78), int(g * 0.78), int(b * 0.78)
            rgba = bytes((r, g, b, 255))
            hgt = p['h']
            shear = 0.7 * math.sin(p['flip'] * 0.6 * age + p['sh'])
            for j in range(int(hgt)):
                off = shear * (j - hgt / 2)
                layer.hline(cx - w / 2 + off, cx + w / 2 + off + 1, int(cy - hgt / 2 + j), rgba)

    return dict(layers=layers, draw=draw, fade=(0.35, 'white'),
                bg=dict(blur=2.2, brightness=0.0, saturation=1.08, zoom=0.045, color='0x8FD3FF'),
                jingle=lambda: jingle_bright(land))


def plan_space(work, fonts):
    font = fonts['heavy']
    lines = ['MISSION', 'COMPLETE']
    track = 0.04
    size = fit_size(font, 'COMPLETE', 980, track)
    layers = []
    layers.append({'kind': 'particles'})
    sprites = []
    for line in lines:
        glyphs, width = font.layout(line, size, size * track)
        polys = []
        for pen, ps in glyphs:
            polys += [[(x + pen, y) for x, y in poly] for poly in ps]
        rgba, w, h, ox, oy = text_sprite(polys, '#FFFFFF', '#8FE3FF', '#0B1E5B', 9,
                                         glow=('#35C8FF', 9, 0.8), shadow=(0, 8, 5, 0.5, '#050A26'))
        sprites.append((rgba, w, h, ox, oy, width))
    cap = size * 0.716
    gap = size * 0.30
    total = 2 * cap + gap
    top = 330 - total / 2.0
    for k, (rgba, w, h, ox, oy, width) in enumerate(sprites):
        p = work / f'space-line-{k}.png'
        write_png(p, w, h, rgba)
        base = top + cap + k * (cap + gap)
        x = int(round((W - width) / 2.0 - ox))
        y = int(round(base - oy))
        t0 = 0.55 + 0.12 * k
        sign = '-' if k == 0 else '+'
        layers.append({'kind': 'image', 'path': p,
                       'x': f"{x}{sign}1500*pow(1-min(1,max(0,(t-{t0:.2f})/0.7)),3)", 'y': str(y),
                       'enable': f'gte(t,{t0:.2f})'})
    layers.append({'kind': 'flash', 'color': 'white', 'in': (1.28, 0.06), 'out': (1.34, 0.55)})

    rng = random.Random(31)
    stars = []
    for _ in range(260):
        stars.append([rng.uniform(-1.7, 1.7), rng.uniform(-1.0, 1.0), rng.uniform(0.05, 1.0),
                      rng.choice(((255, 255, 255), (200, 225, 255), (255, 220, 250), (180, 255, 245))),
                      rng.uniform(0, TAU), rng.uniform(1.5, 4.0)])
    cx, cy, f = W / 2.0, 330.0, 330.0
    dt = 1.0 / FPS

    def speed(t):
        return 2.4 * math.exp(-t / 0.5) + 0.05

    def draw(layer, t, frame):
        v = speed(t)
        for st in stars:
            x, y, z, col, ph, tw = st
            z_prev = z + v * dt
            z -= v * dt
            if z < 0.03:
                st[0], st[1], st[2] = rng.uniform(-1.7, 1.7), rng.uniform(-1.0, 1.0), 1.0
                continue
            st[2] = z
            sx, sy = cx + x / z * f, cy + y / z * f
            px_, py_ = cx + x / z_prev * f, cy + y / z_prev * f
            if not (-200 < sx < W + 200 and -200 < sy < H + 200):
                continue
            bright = min(1.0, 0.4 + 0.9 * (1.0 - z)) * (0.75 + 0.25 * math.sin(tw * t + ph))
            dx, dy = sx - px_, sy - py_
            length = math.hypot(dx, dy)
            if length > 150:
                px_, py_ = sx - dx / length * 150, sy - dy / length * 150
                length = 150
            steps = max(1, int(length))
            r, g, b = col
            thick = z < 0.45 and length > 2      # 가까운 별은 두 줄로 굵게
            ox_, oy_ = (0, 1) if abs(dx) > abs(dy) else (1, 0)
            for i in range(steps + 1):
                u = i / steps
                xx, yy = int(px_ + (sx - px_) * u), int(py_ + (sy - py_) * u)
                a = bright * (0.15 + 0.85 * u)
                layer.blend(xx, yy, r, g, b, a)
                if thick:
                    layer.blend(xx + ox_, yy + oy_, r, g, b, a * 0.8)
            if z < 0.35:
                for ddx, ddy in ((1, 0), (0, 1), (1, 1)):
                    layer.blend(int(sx) + ddx, int(sy) + ddy, r, g, b, bright * 0.9)
        if 1.30 <= t <= 2.0:            # 글자 뒤를 지나가는 빛줄기
            u = (t - 1.30) / 0.7
            head = -300 + u * (W + 900)
            for yy in range(-7, 8):
                fy = math.exp(-(yy / 3.0) ** 2)
                for xx in range(0, 700, 2):
                    a = fy * (xx / 700.0) ** 2 * 0.9 * (1.0 - u * 0.5)
                    layer.blend(int(head - 700 + xx), int(330 + yy), 220, 245, 255, a)
                    layer.blend(int(head - 700 + xx + 1), int(330 + yy), 220, 245, 255, a)

    return dict(layers=layers, draw=draw, fade=(0.5, 'black'),
                bg=dict(blur=1.5, brightness=-0.10, saturation=1.10, zoom=0.06, color='0x1B1450'),
                jingle=jingle_space)


def plan_forest(work, fonts):
    font = fonts['round']
    text = 'THE END'
    track = 0.06
    size = fit_size(font, text, 860, track)
    glyphs, width = font.layout(text, size, size * track)
    polys = []
    for pen, ps in glyphs:
        polys += [[(x + pen, y) for x, y in poly] for poly in ps]
    rgba, w, h, ox, oy = text_sprite(polys, '#FFFBEA', '#FFD978', '#1B4332', 8,
                                     glow=('#FFF3B0', 10, 0.45), shadow=(4, 7, 5, 0.45, '#0B2016'))
    p = work / 'forest-title.png'
    write_png(p, w, h, rgba)
    pts = [q for poly in polys for q in poly]
    cy_text = (min(q[1] for q in pts) + max(q[1] for q in pts)) / 2.0
    x = int(round((W - width) / 2.0 - ox))
    y = int(round(330 - cy_text - oy))
    layers = [
        {'kind': 'image', 'path': p, 'pre': 'fade=t=in:st=1.0:d=1.6:alpha=1', 'x': str(x),
         'y': f"{y}+26*pow(1-min(1,max(0,(t-1.0)/1.8)),3)"},
        {'kind': 'particles'},
    ]
    rng = random.Random(41)
    flies = []
    for _ in range(30):
        flies.append(dict(x=rng.uniform(30, W - 30), y=rng.uniform(150, H - 20), ax=rng.uniform(20, 55),
                          ay=rng.uniform(10, 30), fx=rng.uniform(0.08, 0.22), fy=rng.uniform(0.1, 0.3),
                          px=rng.uniform(0, TAU), py=rng.uniform(0, TAU), rise=rng.uniform(4, 14),
                          blink=rng.uniform(0.35, 0.8), bp=rng.uniform(0, TAU), size=rng.choice((0, 0, 1))))
    glows = [glow_sprite(11, 2.6, 6.5), glow_sprite(14, 3.4, 8.5)]
    leaves = leaf_sprites()
    leaf_cols = [hex_rgb(c) for c in ('#8BC34A', '#CDDC39', '#FFB74D', '#FF8A65', '#AED581')]
    falling = []
    for _ in range(11):
        falling.append(dict(t0=rng.uniform(-3.0, 5.0), x=rng.uniform(60, W - 60), vy=rng.uniform(55, 85),
                            amp=rng.uniform(35, 70), fq=rng.uniform(0.35, 0.65), ph=rng.uniform(0, TAU),
                            col=rng.choice(leaf_cols), rot=rng.uniform(0, TAU)))

    def draw(layer, t, frame):
        for lf in falling:
            age = t - lf['t0']
            if age < 0:
                continue
            yy = -20 + lf['vy'] * age
            if yy > H + 20:
                continue
            sway = math.sin(TAU * lf['fq'] * age + lf['ph'])
            xx = lf['x'] + lf['amp'] * sway
            ang = lf['rot'] + 0.8 * sway
            spr = leaves[int((ang % TAU) / TAU * len(leaves)) % len(leaves)]
            layer.sprite(spr, xx, yy, 0.95, lf['col'])
        for fl in flies:
            xx = fl['x'] + fl['ax'] * math.sin(TAU * fl['fx'] * t + fl['px'])
            yy = fl['y'] - fl['rise'] * t + fl['ay'] * math.sin(TAU * fl['fy'] * t + fl['py'])
            b = 0.25 + 0.75 * max(0.0, math.sin(TAU * fl['blink'] * t + fl['bp'])) ** 2
            layer.sprite(glows[fl['size']], xx, yy, b, (255, 241, 150))

    return dict(layers=layers, draw=draw, fade=(0.9, 'black'),
                bg=dict(blur=1.2, brightness=-0.06, saturation=1.05, zoom=0.05, color='0x2E6B4F'),
                jingle=jingle_forest)


PLANS = {'bright': plan_bright, 'space': plan_space, 'forest': plan_forest}


def ffmpeg_bin(override=None):
    ff = override or os.environ.get('FFMPEG') or shutil.which('ffmpeg')
    if not ff:
        raise SystemExit('ffmpeg를 찾지 못했어요. 설치하거나 --ffmpeg /경로/ffmpeg 로 알려 주세요.')
    return ff


def loudnorm(ff, src, dst, codec_args, target=-16.0, tp=-1.5):
    """ffmpeg loudnorm을 두 번 돌려서(측정, 적용) 소리 크기를 target LUFS에 맞춰요."""
    probe = subprocess.run([ff, '-hide_banner', '-nostats', '-i', str(src), '-af',
                            f'loudnorm=I={target}:TP={tp}:LRA=20:print_format=json', '-f', 'null', '-'],
                           capture_output=True, text=True, check=True)
    js = probe.stderr
    m = json.loads(js[js.rindex('{'):js.rindex('}') + 1])
    af = (f"loudnorm=I={target}:TP={tp}:LRA=20:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
          f"linear=true:print_format=json")
    run = subprocess.run([ff, '-y', '-hide_banner', '-nostats', '-i', str(src), '-af', af, '-ar', str(RATE)]
                         + codec_args + [str(dst)], capture_output=True, text=True, check=True)
    js = run.stderr
    out = json.loads(js[js.rindex('{'):js.rindex('}') + 1])
    return m, out


def make_music(ff, name, work):
    t0 = time.time()
    song = SONGS[name]()
    wav = work / f'music-{name}.wav'
    secs = render_wav(song.mix, wav, loop=True, soft=0.25)
    dst = MEDIA / name / 'music.mp3'
    dst.parent.mkdir(parents=True, exist_ok=True)
    before, after = loudnorm(ff, wav, dst, ['-ac', '2', '-c:a', 'libmp3lame', '-b:a', '128k'])
    log(f'  {name}/music.mp3: {secs:.2f}초, 입력 {before["input_i"]} LUFS, 출력 {after["output_i"]} LUFS '
        f'({after["normalization_type"]}), {dst.stat().st_size // 1024} KB, {time.time() - t0:.0f}초 걸림')


def make_video(ff, name, work, fonts, crf=24):
    t0 = time.time()
    plan = PLANS[name](work, fonts)
    jingle_raw = work / f'jingle-{name}.wav'
    jingle = work / f'jingle-{name}-norm.wav'
    render_wav(plan['jingle'](), jingle_raw, loop=False)
    loudnorm(ff, jingle_raw, jingle, ['-ac', '2', '-c:a', 'pcm_s16le'])
    poster = MEDIA / name / 'poster.png'
    bg = plan['bg']
    args = [ff, '-y', '-hide_banner', '-loglevel', 'error']
    filters = []
    if poster.exists():
        args += ['-loop', '1', '-framerate', str(FPS), '-t', str(DUR), '-i', str(poster)]
        filters.append(f"[0:v]scale=3200:1800:flags=lanczos,zoompan=z='1+{bg['zoom']}*on/{NF - 1}':"
                       f"x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps={FPS},"
                       f"gblur=sigma={bg['blur']},eq=brightness={bg['brightness']}:saturation={bg['saturation']}[bg]")
    else:
        log(f'  {name}: poster.png가 없어서 단색 배경으로 만들어요')
        args += ['-f', 'lavfi', '-i', f"color=c={bg['color']}:s={W}x{H}:r={FPS}:d={DUR}"]
        filters.append('[0:v]null[bg]')
    idx, cur, pipe_used = 1, 'bg', False
    for k, layer in enumerate(plan['layers']):
        if layer['kind'] == 'image':
            args += ['-loop', '1', '-framerate', str(FPS), '-t', str(DUR), '-i', str(layer['path'])]
            pre = ',' + layer['pre'] if layer.get('pre') else ''
            filters.append(f'[{idx}:v]format=rgba{pre}[i{k}]')
            en = f":enable='{layer['enable']}'" if layer.get('enable') else ''
            filters.append(f"[{cur}][i{k}]overlay=x='{layer['x']}':y='{layer['y']}'{en}:format=rgb[c{k}]")
            idx += 1
        elif layer['kind'] == 'particles':
            args += ['-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-framerate', str(FPS), '-i', 'pipe:0']
            filters.append(f'[{cur}][{idx}:v]overlay=0:0:format=rgb[c{k}]')
            idx += 1
            pipe_used = True
        elif layer['kind'] == 'flash':
            (a, b), (c, d) = layer['in'], layer['out']
            filters.append(f"color=c={layer['color']}:s={W}x{H}:r={FPS}:d={DUR},format=rgba,"
                           f"fade=t=in:st={a}:d={b}:alpha=1,fade=t=out:st={c}:d={d}:alpha=1[f{k}]")
            filters.append(f'[{cur}][f{k}]overlay=0:0:format=rgb[c{k}]')
        cur = f'c{k}'
    fade_d, fade_c = plan['fade']
    filters.append(f'[{cur}]fade=t=in:st=0:d={fade_d}:color={fade_c},format=yuv420p[v]')
    args += ['-i', str(jingle)]
    out = MEDIA / name / 'ending.mp4'
    out.parent.mkdir(parents=True, exist_ok=True)
    args += ['-filter_complex', ';'.join(filters), '-map', '[v]', '-map', f'{idx}:a',
             '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-profile:v', 'high', '-pix_fmt', 'yuv420p',
             '-r', str(FPS), '-c:a', 'aac', '-b:a', '128k', '-ar', str(RATE), '-ac', '2',
             '-t', str(DUR), '-movflags', '+faststart', str(out)]
    errlog = work / f'ffmpeg-{name}.log'
    with open(errlog, 'wb') as err:
        proc = subprocess.Popen(args, stdin=subprocess.PIPE if pipe_used else subprocess.DEVNULL, stderr=err)
        if pipe_used:
            layer = Layer()
            try:
                for f in range(NF):
                    layer.clear()
                    plan['draw'](layer, f / FPS, f)
                    proc.stdin.write(layer.buf)
            finally:
                proc.stdin.close()
        code = proc.wait()
    if code != 0:
        raise SystemExit(f'ffmpeg가 실패했어요. 기록: {errlog}\n' + errlog.read_text(errors='replace')[-2000:])
    log(f'  {name}/ending.mp4: {out.stat().st_size // 1024} KB, {time.time() - t0:.0f}초 걸림')


# ---------------------------------------------------------------------------
# 4. 포스터 다듬기와 ZIP
# ---------------------------------------------------------------------------

def make_poster(ff, name, src, crop_y=None, limit=1_500_000):
    """받은 그림을 16:9로 자르고 1600×900 PNG로 저장해요. 너무 크면 256색으로 줄여요."""
    dst = MEDIA / name / 'poster.png'
    dst.parent.mkdir(parents=True, exist_ok=True)
    y = f'{crop_y}' if crop_y is not None else '(ih-iw*9/16)/2'
    vf = f"crop=iw:iw*9/16:0:{y},scale=1600:900:flags=lanczos"
    subprocess.run([ff, '-y', '-hide_banner', '-loglevel', 'error', '-i', str(src), '-vf', vf,
                    '-pix_fmt', 'rgb24', '-compression_level', '9', '-pred', 'mixed', str(dst)], check=True)
    kind = '전체 색'
    if dst.stat().st_size > limit:
        subprocess.run([ff, '-y', '-hide_banner', '-loglevel', 'error', '-i', str(src), '-filter_complex',
                        f"[0:v]{vf},split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];"
                        f"[b][p]paletteuse=dither=sierra2_4a",
                        '-compression_level', '9', '-pred', 'mixed', str(dst)], check=True)
        kind = '256색'
    log(f'  {name}/poster.png: 1600×900, {kind}, {dst.stat().st_size // 1024} KB')


ZIP_DATE = (2026, 10, 15, 0, 0, 0)


def _zip_add(z, path, arcname):
    info = zipfile.ZipInfo(arcname, date_time=ZIP_DATE)
    info.external_attr = 0o644 << 16
    packed = path.suffix.lower() in ('.png', '.mp3', '.mp4')
    info.compress_type = zipfile.ZIP_STORED if packed else zipfile.ZIP_DEFLATED
    z.writestr(info, path.read_bytes())


def make_zips():
    missing = [f'{s}/{f}' for s in SETS for f in ('poster.png', 'music.mp3', 'ending.mp4')
               if not (MEDIA / s / f).exists()]
    if missing:
        raise SystemExit('ZIP을 만들 수 없어요. 없는 파일: ' + ', '.join(missing))
    pack = KIT / 'media-pack.zip'
    with zipfile.ZipFile(pack, 'w') as z:
        _zip_add(z, MEDIA / 'README.md', 'README.md')
        for s in SETS:
            for f in ('poster.png', 'music.mp3', 'ending.mp4'):
                _zip_add(z, MEDIA / s / f, f'{s}/{f}')
        for f in ('jump.wav', 'coin.wav', 'hit.wav'):
            _zip_add(z, MEDIA / 'sfx' / f, f'sfx/{f}')
    log(f'  media-pack.zip: {pack.stat().st_size / 1e6:.2f} MB')
    for s in SETS:
        p = KIT / f'media-{s}.zip'
        with zipfile.ZipFile(p, 'w') as z:
            for f in ('poster.png', 'music.mp3', 'ending.mp4'):
                _zip_add(z, MEDIA / s / f, f)
        log(f'  media-{s}.zip: {p.stat().st_size / 1e6:.2f} MB')


def main():
    ap = argparse.ArgumentParser(description='게임 미디어 묶음(음악, 효과음, 엔딩 영상, ZIP)을 다시 만들어요.')
    ap.add_argument('what', nargs='*', choices=['music', 'sfx', 'video', 'zip', 'poster', 'all'], default=['all'])
    ap.add_argument('--set', choices=SETS, help='한 세트만 만들 때')
    ap.add_argument('--src', help='poster 명령에서 쓸 원본 그림')
    ap.add_argument('--crop-y', type=int, help='poster 명령에서 위에서부터 자를 위치(픽셀). 없으면 가운데')
    ap.add_argument('--work', help='중간 파일을 둘 폴더. 없으면 임시 폴더를 쓰고 끝나면 지워요')
    ap.add_argument('--ffmpeg', help='ffmpeg 경로')
    ap.add_argument('--font', help='영상 글자에 쓸 .ttf 글꼴(세트 셋에 모두 써요)')
    ap.add_argument('--crf', type=int, default=24, help='영상 화질(낮을수록 좋고 파일이 커져요)')
    args = ap.parse_args()
    what = set(args.what)
    if 'all' in what:
        what = {'music', 'sfx', 'video', 'zip'}
    sets = [args.set] if args.set else list(SETS)
    ff = ffmpeg_bin(args.ffmpeg)
    tmp = None
    if args.work:
        work = Path(args.work)
        work.mkdir(parents=True, exist_ok=True)
    else:
        tmp = tempfile.TemporaryDirectory()
        work = Path(tmp.name)
    try:
        if 'poster' in what:
            if not (args.src and args.set):
                raise SystemExit('poster 명령에는 --set과 --src가 필요해요.')
            log('포스터')
            make_poster(ff, args.set, args.src, args.crop_y)
        if 'music' in what:
            log('배경 음악')
            for s in sets:
                make_music(ff, s, work)
        if 'sfx' in what:
            log('효과음')
            make_sfx(MEDIA / 'sfx')
        if 'video' in what:
            log('엔딩 영상')
            fonts = {'heavy': find_font('heavy', args.font), 'round': find_font('round', args.font)}
            log(f"  글꼴: {Path(fonts['heavy'].path).name}, {Path(fonts['round'].path).name}")
            for s in sets:
                make_video(ff, s, work, fonts, crf=args.crf)
        if 'zip' in what:
            log('ZIP')
            make_zips()
    finally:
        if tmp:
            tmp.cleanup()


if __name__ == '__main__':
    main()
