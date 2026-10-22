"""1인분 HTML 폴더를 배포하기 전에 검사해요. Python 표준 라이브러리만 써요.

사용법
  python3 check.py <폴더>
      index.html이 부르는 파일이 모두 있는지, 경로와 파일 이름이 배포해도 안전한지,
      외부 리소스와 비밀값처럼 보이는 글자가 없는지, 크기가 너무 크지 않은지 봐요.
      <a href>로 건 바깥 링크는 눌러야 열리는 링크라서 정보로만 알려요.

  python3 check.py <폴더> --url http://127.0.0.1:8080/ [--screenshot shot.png]
      위 검사에 더해, 켜 둔 서버에서 파일마다 200이 오는지 확인하고
      Chrome을 화면 없이(headless) 띄워 콘솔 메시지와 미디어 상태 줄을 읽어요.
      --screenshot을 주면 그 화면을 PNG로 저장해요.

  게임 미디어: index.html이 poster.png, music.mp3, ending.mp4 중 하나라도 부르거나, 같은 폴더의
      PRD.md나 MEMO.md에 세 이름이 모두 있으면 게임 폴더로 보고, 세 파일을 부르는지 더 봐요.
      media/ 안에 두어도 되고(3교시 예시) index.html 옆에 두어도 돼요(2교시). 부르지 않는 이름은
      정보로만 알려요. Claude가 코드로 다른 이름(poster.svg, music.wav)을 만들 수 있어서예요.

끝나면 "오류 N개, 경고 M개"를 출력해요. 오류가 있으면 종료 코드 1이에요.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

MEDIA_EXT = r'png|jpe?g|gif|webp|svg|avif|mp3|m4a|aac|wav|ogg|oga|mp4|webm|mov|vtt|css|js|mjs|json'
# 스크립트 안의 '...파일.확장자' 문자열도 참조로 봐요. 예: const MEDIA = { voice: 'media/summary.m4a' }
QUOTED_PATH = re.compile(r"""['"`]([^'"`\s<>]+\.(?:%s))['"`]""" % MEDIA_EXT, re.I)
SAFE_NAME = re.compile(r'^[a-z0-9][a-z0-9._-]*$')
SECRET = re.compile(r'api[_-]?key|secret|password|passwd|token|BEGIN [A-Z ]*PRIVATE KEY', re.I)
MB = 1024 * 1024
# 게임 미디어 파일 이름(게임 키트와 3교시 예시가 같이 써요): 시작 화면, 배경 음악, 클리어 영상
GAME_MEDIA = {'poster.png': '시작 화면 포스터', 'music.mp3': '배경 음악', 'ending.mp4': '클리어 영상'}


class RefParser(HTMLParser):
    """src, href, poster 속성 값을 모아요."""

    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ('src', 'href', 'poster') and value:
                self.refs.append((f'<{tag} {name}>', value.strip()))


def exists_exact(root, rel):
    """대소문자까지 같은 이름의 파일이 있는지 봐요. macOS와 Windows는 대소문자를 무시하지만 배포 서버는 구분해요."""
    current = root
    for part in Path(rel).parts:
        if part in ('.', ''):
            continue
        if not current.is_dir() or part not in os.listdir(current):
            return False
        current = current / part
    return current.is_file()


def static_check(root, report):
    index = root / 'index.html'
    if not index.is_file():
        report.error(f'{index} 파일이 없어요. 배포 서비스는 폴더 맨 위의 index.html을 첫 화면으로 열어요.')
        return []
    html = index.read_text(encoding='utf-8', errors='replace')
    parser = RefParser()
    parser.feed(html)
    refs = parser.refs + [('스크립트 문자열', m.group(1)) for m in QUOTED_PATH.finditer(html)]

    local, seen = [], set()
    for where, ref in refs:
        if ref in seen or ref.startswith(('#', 'data:', 'mailto:', 'tel:', 'javascript:')):
            continue
        seen.add(ref)
        if re.match(r'^(https?:)?//', ref, re.I):
            if where == '<a href>':
                # 눌러야 열리는 링크(예: 배포 주소, 참고 사이트)는 페이지를 그리는 데 쓰지 않아서 오류로 보지 않아요.
                report.info(f'바깥 링크: {ref}. 눌러야 열리는 링크라 괜찮아요. 회사 내부 주소가 아닌지만 봐요.')
            else:
                report.error(f'외부 리소스: {ref} ({where}). 외부 파일은 회사망에서 막히거나 바뀔 수 있어요. 폴더 안으로 옮겨요.')
            continue
        if ref.startswith('/'):
            report.error(f'/로 시작하는 경로: {ref} ({where}). GitHub Pages 주소(/저장소이름/) 아래에서 깨져요. media/... 처럼 상대 경로로 써요.')
            continue
        path = ref.split('#')[0].split('?')[0]
        if not path:
            continue
        if not exists_exact(root, path):
            hint = ''
            target = (root / path)
            if target.exists():
                hint = ' 파일은 있지만 대소문자가 달라요. 배포 서버에서는 404가 나요.'
            elif path.startswith('media/'):
                hint = ' 미디어를 아직 넣지 않았다면, 넣은 뒤 다시 검사해요.'
            report.error(f'없는 파일: {path} ({where}).{hint}')
            continue
        local.append(path)
        report.ok(f'참조 확인: {path}')

    game_check(root, html, report)

    for match in SECRET.finditer(html):
        line = html.count('\n', 0, match.start()) + 1
        report.warn(f'index.html {line}행에 비밀값처럼 보이는 글자 "{match.group(0)}"가 있어요. 공개해도 되는지 확인해요.')

    total = 0
    referenced = {str(Path(p)) for p in local}
    for path in sorted(p for p in root.rglob('*') if p.is_file()):
        rel = path.relative_to(root)
        if rel.parts[0].startswith('.'):
            continue  # .git, .claude 같은 숨김 폴더는 배포 폴더에 넣지 않는 것을 전제로 건너뛰어요.
        size = path.stat().st_size
        total += size
        published = rel.parts[0] == 'media' or str(rel) in referenced
        if published and any(not SAFE_NAME.match(part) for part in rel.parts):
            report.warn(f'파일 이름 {rel}: 소문자, 숫자, -, _, . 만 쓰면 배포 뒤 경로 문제가 줄어요.')
        if size > 25 * MB:
            report.error(f'{rel}이 {size / MB:.1f}MB예요. GitHub 웹 업로드와 Cloudflare 끌어다 놓기는 파일 하나에 25MiB까지 받아요.')
        elif size > 10 * MB:
            report.warn(f'{rel}이 {size / MB:.1f}MB예요. GitHub는 50MB가 넘는 파일에 경고하고 100MB가 넘는 파일은 받지 않아요. 휴대폰에서 빨리 열리게 줄여요.')
        if rel.parts[0] == 'media' and str(rel) not in referenced:
            report.warn(f'{rel}은 index.html이 부르지 않는 파일이에요. 필요 없으면 빼요.')
    media_total = sum(p.stat().st_size for p in (root / 'media').rglob('*') if p.is_file()) if (root / 'media').is_dir() else 0
    report.info(f'폴더 전체 {total / MB:.2f}MB, media 폴더 {media_total / MB:.2f}MB')
    if media_total > 2 * MB:
        report.warn(f'media 폴더가 {media_total / MB:.1f}MB예요. 수업 기준(2MB)보다 커요. 올리는 데 오래 걸릴 수 있어요.')
    if (root / '.git').exists():
        report.info('폴더 안에 .git이 있어요. GitHub Pages로 올릴 준비가 됐어요. 커밋한 파일만 올라가요.')
    return local


def game_check(root, html, report):
    """게임 폴더면 미디어 세 파일을 부르는지 봐요. 파일이 있는지는 위의 참조 검사가 봐요.

    index.html이 세 이름 중 하나라도 부르면 게임 폴더예요. index.html에 세 이름이 하나도 없어도
    작업 폴더의 PRD.md나 MEMO.md에 세 이름이 모두 있으면 게임 폴더로 봐요.
    media/ 안(3교시 예시)과 index.html 옆(2교시) 모두 확인으로 봐요. 부르지 않는 이름은 오류가 아니라 정보예요.
    3교시에 Claude가 코드로 poster.svg, music.wav, 캔버스 엔딩처럼 다른 이름과 방법을 쓸 수 있어서예요.
    """
    def notes_say_game():
        for name in ('PRD.md', 'MEMO.md'):
            note = root / name
            if note.is_file() and all(media in note.read_text(encoding='utf-8', errors='replace') for media in GAME_MEDIA):
                return True
        return False

    if not any(name in html for name in GAME_MEDIA) and not notes_say_game():
        return
    report.info('게임 미디어 이름(poster.png · music.mp3 · ending.mp4)을 쓰는 폴더라서 세 파일을 부르는지도 봐요. '
                'media/ 안에 두어도 되고 index.html 옆에 두어도 돼요.')
    for name, role in GAME_MEDIA.items():
        used = re.search(r"""['"`(]([^'"`()\s<>]*%s)['"`)]""" % re.escape(name), html)
        if used:
            where = used.group(1)
            report.ok(f'게임 미디어: {role} 파일({where}{", index.html 옆" if "/" not in where else ""})')
        else:
            report.info(f'게임 미디어: index.html이 {role} 파일({name})을 부르지 않아요. '
                        f'Claude가 코드로 다른 이름이나 방법(예: poster.svg, music.wav, 캔버스 엔딩)을 썼다면 괜찮아요. '
                        f'열어서 포스터, 음악, 엔딩이 나오는지 봐요.')


def find_chrome(given):
    candidates = [given, os.environ.get('CHROME'),
                  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                  r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                  r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                  shutil.which('google-chrome'), shutil.which('chromium')]
    for c in candidates:
        if c and Path(c).exists():
            return c
    return None


def browser_check(url, local, chrome, screenshot, report):
    if not url.endswith('/'):
        url += '/'
    for path in ['index.html'] + local:
        try:
            with urlopen(Request(urljoin(url, path), method='GET'), timeout=10) as res:
                report.ok(f'서버 응답 {res.status}: {path} ({res.headers.get("Content-Type")})')
        except HTTPError as e:
            report.error(f'서버 응답 {e.code}: {path}. 서버를 켠 폴더와 파일 위치를 확인해요.')
        except URLError as e:
            report.error(f'{url}에 연결하지 못했어요({e.reason}). python3 -m http.server 8080 --bind 127.0.0.1 을 켰는지 확인해요.')
            return

    chrome = find_chrome(chrome)
    if not chrome:
        report.warn('Chrome을 찾지 못해서 콘솔 검사를 건너뛰어요. --chrome으로 경로를 알려 줘요.')
        return
    with tempfile.TemporaryDirectory() as profile:
        base = [chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--user-data-dir={profile}',
                '--virtual-time-budget=8000', '--enable-logging=stderr', '--v=0']
        run = subprocess.run(base + ['--dump-dom', url], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=90)
        if screenshot:
            out = Path(screenshot).resolve()
            subprocess.run(base + ['--window-size=1280,2600', f'--screenshot={out}', url], capture_output=True, timeout=90)
            if out.exists():
                report.ok(f'스크린샷 저장: {out}')
            else:
                report.warn('스크린샷을 만들지 못했어요.')
    messages = re.findall(r':CONSOLE(?::\d+)?\] "(.*)", source: (\S+) \((\d+)\)', run.stderr)
    errors = [m for m in messages if m[0].startswith('Uncaught')]
    for text, source, line in messages:
        (report.error if text.startswith('Uncaught') else report.info)(f'콘솔: {text} ({source} {line}행)')
    if not errors:
        report.ok('콘솔에 잡히지 않은 예외(Uncaught)가 없어요.')
    status = re.search(r'id="media-status"[^>]*>([^<]*)<', run.stdout)
    if status:
        report.info(f'미디어 상태 줄: {status.group(1).strip()}')
        if '없음' in status.group(1) or '확인 중' in status.group(1):
            report.warn('상태 줄에 "없음"이나 "확인 중"이 있어요. 파일 이름 계약과 형식을 확인해요.')


class Report:
    def __init__(self):
        self.errors = self.warnings = 0

    def ok(self, msg):
        print('  확인', msg)

    def info(self, msg):
        print('  정보', msg)

    def warn(self, msg):
        self.warnings += 1
        print('  경고', msg)

    def error(self, msg):
        self.errors += 1
        print('  오류', msg)


def main():
    parser = argparse.ArgumentParser(description='1인분 HTML 폴더 배포 전 검사')
    parser.add_argument('folder', help='index.html이 있는 폴더')
    parser.add_argument('--url', help='켜 둔 서버 주소. 예: http://127.0.0.1:8080/')
    parser.add_argument('--screenshot', help='--url과 함께 쓰면 이 경로에 PNG 스크린샷을 저장해요')
    parser.add_argument('--chrome', help='Chrome 실행 파일 경로')
    args = parser.parse_args()
    root = Path(args.folder).resolve()
    report = Report()
    print(f'[파일 검사] {root}')
    local = static_check(root, report)
    if args.url:
        print(f'[브라우저 검사] {args.url}')
        browser_check(args.url, local, args.chrome, args.screenshot, report)
    print(f'오류 {report.errors}개, 경고 {report.warnings}개')
    sys.exit(1 if report.errors else 0)


if __name__ == '__main__':
    main()
