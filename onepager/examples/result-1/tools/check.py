#!/usr/bin/env python3
"""배포 전 점검: index.html이 쓰는 파일이 다 있는지, 음악 파일이 정상인지 확인한다."""
import re
import struct
import sys
import wave
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
html = (root / 'index.html').read_text(encoding='utf-8')
ok = True


def check(label, cond, detail=''):
    global ok
    ok &= bool(cond)
    print(('통과 ' if cond else '실패 ') + label + (' ' + detail if detail else ''))


media = re.search(r"const MEDIA = \{([^}]*)\}", html).group(1)
for name, path in re.findall(r"(\w+): '([^']+)'", media):
    check(f'{name} 파일 있음', (root / path).is_file(), path)
check('절대 경로(/…, http)로 부른 파일 없음', not re.search(r"""(src|href)=["'](/|https?:)""", html))
png = (root / 'assets/poster.png').read_bytes()
check('포스터가 PNG', png[:8] == b'\x89PNG\r\n\x1a\n', '%dx%d' % struct.unpack('>II', png[16:24]))
with wave.open(str(root / 'assets/music.wav')) as w:
    check('음악이 WAV', True, f'{w.getnframes() / w.getframerate():.1f}초, {w.getframerate()}Hz')
check('QR 파일 있음', (root / 'qr.png').is_file())
sys.exit(0 if ok else 1)
