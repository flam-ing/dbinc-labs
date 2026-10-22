#!/bin/bash
# 완성 샘플의 미디어 네 개 중 세 개(그림, 음성, 영상)를 이 Mac에서 다시 만들어요.
# 표지 그림 sample/media/cover.svg는 직접 그린 SVG 파일이라 이 스크립트가 만들지 않아요.
#
# 쓰는 프로그램: sips, say, afconvert(macOS 기본), Google Chrome, ffmpeg
# 사용법: bash labs/onepager/make_media.sh
#   다른 위치의 프로그램을 쓰려면 FFMPEG=/경로/ffmpeg CHROME=/경로/chrome 처럼 앞에 붙여요.
#   음성을 바꾸려면 VOICE=Yuna 대신 say -v '?' 목록에 있는 다른 이름을 넣어요.
set -euo pipefail
cd "$(dirname "$0")"

FFMPEG="${FFMPEG:-ffmpeg}"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
VOICE="${VOICE:-Yuna}"
OUT=sample/media
TMP=.build   # 중간 파일. 저장소의 .gitignore가 .build/를 빼 줘요.
mkdir -p "$OUT" "$TMP"

echo "1/3 그림: assets/project-handbook-orange.png를 가로 480px로 줄여요"
sips -Z 480 ../../assets/project-handbook-orange.png --out "$OUT/checklist.png" >/dev/null

echo "2/3 음성: say($VOICE)로 읽고 afconvert로 AAC(m4a)로 바꿔요"
if ! say -v "$VOICE" -o "$TMP/summary.aiff" -f media-src/narration.txt 2>/dev/null; then
  echo "   $VOICE 음성이 없어서 기본 음성으로 읽어요"
  say -o "$TMP/summary.aiff" -f media-src/narration.txt
fi
afconvert -f m4af -d aac -b 64000 "$TMP/summary.aiff" "$OUT/summary.m4a"

echo "3/3 영상: 프레임 SVG 3장을 Chrome으로 PNG로 찍고, ffmpeg로 이어 붙여요"
for n in 1 2 3; do
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --window-size=640,360 \
    --screenshot="$PWD/$TMP/frame-$n.png" "file://$PWD/media-src/frame-$n.svg" >/dev/null 2>&1
done
# 장마다 2.5초, 장 사이 0.5초 겹쳐 바뀌기(xfade). 전체 6.5초, 소리 없음.
"$FFMPEG" -y -loglevel error \
  -framerate 30 -loop 1 -t 2.5 -i "$TMP/frame-1.png" \
  -framerate 30 -loop 1 -t 2.5 -i "$TMP/frame-2.png" \
  -framerate 30 -loop 1 -t 2.5 -i "$TMP/frame-3.png" \
  -filter_complex "[0][1]xfade=transition=fade:duration=0.5:offset=2[a];[a][2]xfade=transition=fade:duration=0.5:offset=4,format=yuv420p[v]" \
  -map "[v]" -c:v libx264 -preset medium -crf 30 -movflags +faststart -an "$OUT/highlight.mp4"

echo "끝. 만든 파일:"
ls -l "$OUT"
