# 방명록 앱 만들기 예제 (PWA와 크롬 확장)

1일차 번외 [웹앱을 앱으로 만들기](../../docs/day1-app.md)에서 쓰는 자료예요. 4교시에 만든 방명록을 PC에 앱처럼 설치하고, 새 글이 오면 알림을 받아요.

수강생은 이 예제를 켜지 않아요. `pwa/`의 파일을 내 방명록에 붙여요. 보낼 문장은 [examples/prompts.md](examples/prompts.md)에 있어요.

## 들어 있는 파일

| 파일 | 역할 |
| --- | --- |
| `pwa/manifest.webmanifest` | 앱 이름, 아이콘, 시작 주소를 적은 파일이에요 |
| `pwa/sw.js` | 서비스 워커예요. 서버가 꺼졌을 때 안내 화면을 보여 주고, 알림을 누르면 방명록 창을 열어요 |
| `pwa/pwa.js` | "새 글 알림 켜기" 버튼을 붙이고, 15초마다 `/api/entries`를 확인해요 |
| `pwa/icons/` | 앱 아이콘(192, 512 픽셀) |
| `serve.py` | 강사 시연용이에요. 방명록 참고본(`labs/guestbook/app.py`)에 PWA 파일을 더해 8000번으로 내보내요 |
| `extension/` | 크롬 확장 프로그램이에요. 실습 2에서 내 프로젝트로 복사해 써요 |
| `check_app.py` | PWA 파일과 확장 파일이 제대로 나가는지 확인하는 검사 도구예요 |
| `make_icons.py` | 아이콘을 다시 만드는 스크립트예요 |
| `examples/` | 보내는 문장과 강사가 실제로 해 본 결과 견본이에요 |

## 강사 예제 켜기

저장소 폴더(`~/dbinc-ai-course`)에서 켜요. `labs/guestbook/app.py`가 켜져 있으면 먼저 `Ctrl+C`로 꺼요. 둘 다 8000번을 써요.

| 운영체제 | 명령 |
| --- | --- |
| Windows | `py labs/app/serve.py` |
| macOS | `python3 labs/app/serve.py` |

Chrome에서 http://127.0.0.1:8000 을 열면 방명록 오른쪽 아래에 "새 글 알림 켜기" 버튼이 보여요. 서비스 워커와 알림은 https 주소나 내 PC 주소(127.0.0.1, localhost)에서만 돼요.

## 내 방명록에 붙이기

`pwa/` 파일은 `/api/entries`의 응답 모양만 맞으면 어느 방명록에서도 그대로 써요.

| 내 방명록 | 파일을 둘 곳 | `<head>`에 넣는 것 |
| --- | --- | --- |
| React(Vite)와 Spring | `web/public/` | `web/index.html`의 `</head>` 앞에 두 줄 |
| Python 길 | `static/` | `static/index.html`에 두 줄, `app.py`가 새 파일 다섯 개도 내보내게 목록에 더하기 |

Vite 화면은 `/api` 요청을 proxy가 Spring(8080)으로 넘겨요. 그래서 브라우저에서는 화면과 API가 같은 주소(5173)로 보이고, `pwa.js`가 그대로 돌아요. 서버에서 CORS를 허락하는 길로 만들었으면 `vite.config.js`에 `/api` proxy를 먼저 더해요.

## 확인하기

저장소 폴더에서 한 줄씩 쳐요. Windows는 `python3` 대신 `py`를 써요.

```text
python3 labs/app/check_app.py
python3 labs/guestbook/smoke_test.py --app labs/app/serve.py
```

둘 다 마지막 줄이 `OK`면 돼요. 이 검사는 브라우저를 열지 않아요. 설치 버튼과 실제 알림은 Chrome에서 직접 봐요.

## 막히면

| 증상 | 해결 |
| --- | --- |
| `Address already in use`가 나와요 | 8000번을 쓰는 다른 서버를 `Ctrl+C`로 끄고 다시 켜요 |
| "새 글 알림 켜기" 버튼이 안 보여요 | 강력 새로고침(Windows `Ctrl+Shift+R`, macOS `Cmd+Shift+R`)을 해요 |
| 알림 허용 창이 안 떠요 | 주소창의 사이트 정보에서 알림을 허용해요. 회사 정책으로 막혔으면 강사 화면으로 봐요 |
| 알림을 허용했는데 화면에 안 떠요 | 운영체제 알림 설정에서 Chrome을 허용해요 |
