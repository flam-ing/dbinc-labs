# 번외 실습 예시

번외 "웹앱을 앱으로"에서 보내는 문장과, 강사가 실제로 해 본 결과 견본이에요. 막히거나 내 결과와 비교하고 싶을 때 열어 봐요.

| 파일 | 무엇 |
| --- | --- |
| [prompts.md](prompts.md) | 실습 1·2 문장, Python 길 문장, 막히면 문장, 수업 뒤에 해 볼 문장 |
| `pwa-react/index.html`, `pwa-react/manifest.webmanifest` | 실습 문장을 보낸 실제 결과 |
| `pwa-react/vite.config.js` | 막히면: `/api` proxy를 더한 실제 결과 |
| `pwa-python/` | Python 길로 만든 방명록에 붙였을 때 바뀐 줄 |
| `screens/react-ready.png`, `screens/react-notified.png` | 끝났을 때 모습과 알림이 간 뒤 모습 |
| `pwa-react/theme-color.diff`, `pwa-react/notify-title.diff`, `screens/web-off.png` | 수업 뒤에 해 볼 것: 테마 색, 알림 제목, 서버를 끈 화면 |
| `extension-5173/`, `extension-popup-3.diff`, `screens/ext-popup-5173.png` | 실습 2: 크롬 확장 견본과 팝업 화면 |

견본은 4교시 방명록과 같은 모양의 연습 폴더(주제 "칭찬 릴레이", 화면 5173, API 8080)에서 나왔어요. 글은 모두 가상 내용이에요. 원본(`labs/app/pwa`, `labs/app/extension`)은 고치지 않아요.
