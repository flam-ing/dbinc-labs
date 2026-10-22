#!/bin/bash
# 게임 샘플의 미디어 세 개(포스터, 배경 음악, 엔딩 영상)를 이 Mac에서 다시 만들어요. 생성형 AI 서비스는 쓰지 않아요.
#
# 쓰는 프로그램: Google Chrome, python3, ffmpeg
# 사용법: bash labs/onepager/game/make_media.sh
#   다른 위치의 프로그램을 쓰려면 FFMPEG=/경로/ffmpeg CHROME=/경로/chrome 처럼 앞에 붙여요.
set -euo pipefail
cd "$(dirname "$0")"

FFMPEG="${FFMPEG:-ffmpeg}"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
OUT=media
TMP=../.build   # 중간 파일. 저장소의 .gitignore가 .build/를 빼 줘요.
mkdir -p "$OUT" "$TMP"

echo "1/3 포스터: media-src/poster.html(교안 그림 토끼와 당근)을 Chrome으로 1280×720 PNG로 찍어요"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --window-size=1280,720 --virtual-time-budget=3000 \
  --screenshot="$PWD/$OUT/poster.png" "file://$PWD/media-src/poster.html" >/dev/null 2>&1

echo "2/3 배경 음악: make_music.py로 16초 반복 음악을 WAV로 만들고 ffmpeg로 MP3로 바꿔요"
python3 media-src/make_music.py "$TMP/music.wav"
"$FFMPEG" -y -loglevel error -i "$TMP/music.wav" -codec:a libmp3lame -b:a 96k "$OUT/music.mp3"

echo "3/3 엔딩 영상: 포스터를 5초 동안 천천히 확대하는 영상으로 만들어요(소리 없음, 16:9가 아니면 흰 여백을 붙여요)"
"$FFMPEG" -y -loglevel error -loop 1 -i "$OUT/poster.png" \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=white,zoompan=z='min(zoom+0.0012,1.18)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=150:s=1280x720:fps=30,format=yuv420p" \
  -frames:v 150 -c:v libx264 -crf 28 -movflags +faststart -an "$OUT/ending.mp4"

echo "끝. 만든 파일:"
ls -l "$OUT"
