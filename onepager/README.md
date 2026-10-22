# 3교시 실습 자료 · 1인분 HTML

1일차 3교시 [실습 1-1: 1인분 HTML 만들고 배포하기](../../docs/day1-onepager.md)에서 쓰는 예시 자료예요. 수강생은 이 폴더에서 작업하지 않아요. 바탕화면 `my-game` 폴더에서 Claude에게 맡겨 내 게임을 만들고, 이 폴더는 필요할 때 열어 보기만 해요.

실습 순서와 보내는 문장은 [examples/prompts.md](examples/prompts.md)에 있어요.

## 들어 있는 파일

| 파일 | 무엇 |
| --- | --- |
| `game/index.html` | 완성 게임 예시예요. 토끼가 떨어지는 당근을 피해요. 3교시 발표의 완성 예시 장면이 이 파일을 열어요 |
| `game/media/` | 게임 예시의 그림, 음악, 영상(`poster.png`, `music.mp3`, `ending.mp4`) |
| `examples/` | 실습 문장과 강사가 실제로 돌려 본 결과 |
| `sample/index.html` | 업무 보고서 한 장 예시예요. 표, 차트, 그림, 음성, 영상을 넣었어요 |
| `check.py` | 올릴 폴더를 검사하는 스크립트예요. 수업에서는 쓰지 않아요 |
| `MEMO.md`, `PRD.md`, `game/MEMO.md`, `game/PRD.md` | 예시를 만들 때 쓴 메모와 PRD예요. 4교시에 작은 PRD가 어떻게 생겼는지 볼 때 열어요 |
| `make_media.sh`, `game/make_media.sh`, `media-src/`, `game/media-src/` | 예시 미디어를 다시 만드는 스크립트와 원본이에요. 강사용이에요 |
| `_reference/claude-runs/` | 강사용 실제 실행 기록이에요. 학생용 ZIP에는 없어요 |

게임에 붙일 그림과 음악 세트, 막혔을 때 쓰는 견본 게임은 [game-kit](../game-kit/examples/README.md)에 있어요.

## 예시 열기

`game/index.html`과 `sample/index.html`은 더블클릭해서 열어도 그림, 소리, 영상이 나와요. 게임 예시는 시작 버튼을 누르면 음악이 나와요. 15초쯤 버티면 300점이 되어 엔딩 영상이 나와요.

올린 사이트와 같은 조건으로 보고 싶으면 그 폴더에서 서버를 켜요. Windows는 `py`, macOS는 `python3`을 써요.

```powershell
cd ~/dbinc-ai-course/labs/onepager/game
py -m http.server 8080 --bind 127.0.0.1
```

브라우저에서 http://127.0.0.1:8080/ 을 열어요. 다 보면 그 터미널에서 `Ctrl+C`로 서버를 꺼요. 4교시에는 Spring Boot가 8080번을 쓰니 켜 둔 채로 두지 않아요.

## 올릴 폴더 검사하기

수업에서는 내가 직접 열어 보는 것으로 충분해요. 교안 저장소가 내 PC에 있으면 이 스크립트로 한 번 더 볼 수 있어요. `index.html`이 부르는 파일이 모두 있는지, 대소문자가 맞는지, 비밀값처럼 보이는 글자가 없는지 봐요.

```powershell
cd ~/dbinc-ai-course
py labs/onepager/check.py labs/onepager/game
```

마지막 줄이 `오류 0개, 경고 0개`이면 괜찮아요. 내 폴더는 같은 자리에서 `py labs/onepager/check.py $HOME/Desktop/my-game`처럼 경로를 넘겨요. 오류가 있으면 종료 코드 1로 끝나요.

## 예시 미디어

미디어는 모두 이 강의에서 직접 만들었어요. 생성형 AI 서비스는 쓰지 않았어요. 게임 예시의 포스터는 `game/media-src/poster.html`을 화면 없는 Chrome으로 찍었어요. 음악은 `game/media-src/make_music.py`로 만들고 ffmpeg로 MP3로 바꿨어요. 엔딩 영상은 포스터를 ffmpeg로 천천히 확대했어요.

다시 만들 때는 macOS에서 저장소 폴더로 가서 실행해요. ffmpeg가 Homebrew 위치에 있으면 앞에 경로를 붙여요.

```bash
cd ~/dbinc-ai-course
FFMPEG=/opt/homebrew/bin/ffmpeg bash labs/onepager/game/make_media.sh
```

보고서 예시의 미디어는 `bash labs/onepager/make_media.sh`로 다시 만들어요. 중간 파일은 `labs/onepager/.build/`에 남고, 커밋되지 않아요.
