# 번외 실습 문장 · 웹앱을 앱으로

1일차 번외 [웹앱을 앱으로 만들기](../../../docs/day1-app.md)에서 Code 탭에 보내는 문장이에요. `<꺾쇠>` 안은 내 것으로 바꿀 곳이에요. 보낼 때 꺾쇠 표시는 지워요.

강사가 2026-10-17에 4교시 방명록과 같은 모양의 연습 폴더(화면 `web/`은 5173, API 서버는 8080)에서 실제로 보내 봤어요. 바뀐 파일의 견본은 이 폴더에 있어요.

## 실습 1: 내 방명록을 앱으로 (8분)

4교시에 쓰던 Code 탭 세션에 붙여 넣어요. 모드는 **Accept edits**예요. 바꿀 곳은 앱 이름 하나예요. 4교시 주제 이름을 넣어요. 그대로 두어도 돼요.

```text
~/dbinc-ai-course/labs/app/pwa 폴더의 파일을 web/public에 그대로 복사해 줘.
web/index.html의 </head> 바로 앞에 아래 두 줄을 넣어 줘.
<link rel="manifest" href="/manifest.webmanifest">
<script src="/pwa.js" defer></script>
앱 이름은 manifest.webmanifest의 name과 short_name만 "<칭찬 릴레이>"로 바꿔 줘. 다른 파일은 고치지 말고, 끝나면 바뀐 줄을 보여 줘.
```

수업 저장소에서 파일을 복사하는 일이라 허락 카드가 뜰 수 있어요. 명령을 읽고 허락해요.

강사 결과는 22초 걸렸어요. `web/public`에 파일 다섯 개가 복사되고, `web/index.html`에 두 줄, manifest에 이름 두 칸이 바뀌었어요. 견본은 [pwa-react/index.html](pwa-react/index.html)과 [pwa-react/manifest.webmanifest](pwa-react/manifest.webmanifest)예요.

끝나면 이렇게 확인해요.

1. Chrome에서 http://localhost:5173 을 새로고침해요.
2. 오른쪽 아래에 "새 글 알림 켜기" 버튼과 "앱 준비됨"이 보이면 맞아요([screens/react-ready.png](screens/react-ready.png)).
3. 버튼을 눌러 알림을 허용하고, 다른 창에서 글을 하나 남겨요. 15초 안에 알림이 오면 끝이에요.

목록은 저절로 바뀌지 않아요. 새로고침하면 새 글이 보여요([screens/react-notified.png](screens/react-notified.png)). 4교시 서버 두 개(api 8080, web 5173)가 꺼졌으면 Browser 창의 Dev servers에서 다시 켜요.

먼저 끝나면 커밋을 부탁해요.

```text
커밋해 줘. 메시지는 "방명록을 앱으로"로 해 줘.
```

### Python 길로 만든 사람

```text
~/dbinc-ai-course/labs/app/pwa 폴더의 파일을 static 폴더에 그대로 복사해 줘.
static/index.html의 </head> 바로 앞에 아래 두 줄을 넣어 줘.
<link rel="manifest" href="/manifest.webmanifest">
<script src="/pwa.js" defer></script>
그리고 app.py가 /manifest.webmanifest, /sw.js, /pwa.js, /icons/icon-192.png, /icons/icon-512.png 다섯 경로를 static 폴더에서 내보내게 목록에 더해 줘. 다른 경로는 지금처럼 404로 막아 줘. 끝나면 바뀐 줄을 보여 줘.
```

강사 결과는 26초 걸렸어요. `app.py`의 목록에 다섯 줄이 더해졌어요. 바뀐 줄은 [pwa-python/app.py.diff](pwa-python/app.py.diff)와 [pwa-python/index.html.diff](pwa-python/index.html.diff)예요.

### 막히면

알림을 켰더니 "서버에 연결하지 못했어요"가 나오면 `web/vite.config.js`에 `/api` proxy가 없는 거예요. 4교시에 서버에서 CORS를 허락하는 길을 골랐을 때 생겨요.

```text
알림을 켜면 "서버에 연결하지 못했어요"가 나와. web/vite.config.js에 /api 요청을 http://127.0.0.1:8080 으로 넘기는 proxy를 더해 줘. 다른 파일은 고치지 말고, 끝나면 바뀐 줄을 보여 줘.
```

강사 결과는 30초 걸렸어요. 견본은 [pwa-react/vite.config.js](pwa-react/vite.config.js)예요.

"새 글 알림 켜기" 버튼이 안 보이면 `web/index.html`의 `</head>` 앞에 두 줄이 있는지 봐요. 그다음 강력 새로고침(Windows `Ctrl+Shift+R`, macOS `Cmd+Shift+R`)을 해요.

## 실습 2: 내 방명록 확장 (6분)

모드는 **Accept edits**예요. 바꿀 곳은 볼 주소 하나예요. React 화면이면 그대로 쓰고, Python 길이면 `http://127.0.0.1:8000`을 넣어요.

```text
~/dbinc-ai-course/labs/app/extension 폴더를 이 프로젝트의 extension 폴더로 복사해 줘. 원본은 고치지 마.
복사본에서 방명록 주소를 <http://localhost:5173> 으로 바꿔 줘. 바꿀 곳은 manifest.json의 host_permissions, background.js와 popup.js 맨 위의 GUESTBOOK 세 곳이야. 다른 줄은 고치지 말고, 끝나면 바뀐 줄을 보여 줘.
```

Chrome 주소창에 `chrome://extensions`를 치고, Developer mode를 켜고, Load unpacked로 내 프로젝트의 `extension` 폴더를 골라요. 강사 결과는 12초 걸렸고 세 파일에서 한 줄씩 바뀌었어요. 견본은 [extension-5173](extension-5173/) 폴더와 [screens/ext-popup-5173.png](screens/ext-popup-5173.png)예요. 복사가 잘 안 되고 내 방명록이 5173이면 이 견본 폴더를 바로 올려요.

더 해 보기: 팝업 글 수를 바꿔요.

```text
extension/popup.js에서 팝업에 보이는 글 수를 5개에서 <3>개로 바꿔 줘. 다른 줄은 고치지 마.
```

강사 결과는 8초 걸렸고 한 줄이 바뀌었어요([extension-popup-3.diff](extension-popup-3.diff)). 고친 뒤에는 확장 카드의 새로고침 버튼을 눌러요.

## 수업 뒤에 해 볼 것

### 테마 색 바꾸기

실습 문장의 마지막 줄을 이렇게 바꿔 보내요.

```text
앱 이름은 manifest.webmanifest의 name과 short_name만 "<고마워 릴레이>"로 바꿔 줘. 테마 색도 theme_color를 "<#2E7D32>"로 바꿔 줘. 다른 파일은 고치지 말고, 끝나면 바뀐 줄을 보여 줘.
```

강사 결과는 manifest 세 줄이 바뀌었어요([pwa-react/theme-color.diff](pwa-react/theme-color.diff)).

### 알림 제목 바꾸기

```text
알림 제목의 "새 방명록"을 "<새 칭찬>"으로 바꿔 줘. web/public/pwa.js만 고치고, 끝나면 바뀐 줄을 보여 줘.
```

강사 결과는 `pwa.js` 한 줄이 바뀌었어요([pwa-react/notify-title.diff](pwa-react/notify-title.diff)).

### 서버를 끄고 보기

Browser 창의 Dev servers에서 web(5173)을 끄고 새로고침해요. 빈 화면 대신 "서버에 연결할 수 없어요"가 보여요([screens/web-off.png](screens/web-off.png)). `sw.js`가 보여 주는 화면이에요. 확인했으면 다시 켜요.
