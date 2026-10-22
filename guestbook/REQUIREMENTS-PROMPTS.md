# 방명록 단계별 요청 모음

1일차 4교시 방명록을 단계별로 나눠 만들 때 쓰는 요청 모음이에요. 수업 시간의 실습 문장은 [examples/prompts.md](examples/prompts.md)에 있어요. 이 파일은 한 문장으로 맡기기가 잘 안 될 때, Python으로 만들 때, 그리고 수업 뒤에 봐요. 강사 방명록도 이 순서로 만들었어요.

요청은 예시예요. 그대로 써도 되고 내 주제와 내 말로 바꿔도 돼요. 확인 도구 줄의 `python3`은 Windows에서 `py`로 바뀌어요. Claude가 알아서 바꿔 실행해요.

시작 폴더 복사와 인터뷰 순서는 [4교시 교안](../../docs/day1-guestbook.md) 1절에 있어요.

## 인터뷰 모드

### 스킬로 시작하기

Plan 모드로 바꾼 뒤 입력창에 보내요. 주제만 내 것으로 바꿔요.

```text
/prd-interview 칭찬 릴레이
```

### 복사용 프롬프트

스킬이 `/` 목록에 안 보이면 아래 글을 붙여 넣어요. 첫 줄의 주제만 내 것으로 바꾸고, Plan 모드에서 넣어요.

```text
PRD 인터뷰를 해 줘. 만들고 싶은 것은 "칭찬 릴레이"야.
- 질문 카드로 한 번에 하나씩 물어봐 줘. 머리말은 12자 이내, 선택지는 2~4개, 가장 권하는 것은 맨 앞에 "(추천)"으로. 직접 쓰는 칸은 따로 넣지 않아도 돼.
- 물어볼 것은 쓰는 사람, name 칸과 message 칸을 화면에서 부를 이름표, 더할 선택 칸, 목록 모양, 분위기, 이번에 하지 않을 것이야. 일곱 개 이하로 끝내 줘. 기술 스택은 묻지 마. 설계에서 정할 거야.
- 아래 API 약속은 묻지 말고 PRD에 그대로 넣어. 수업의 확인 도구 smoke_test.py가 이 약속으로 검사해.
  GET /api/entries는 200과 {"entries": [...]}, 최신 글부터 최대 200개. POST /api/entries는 JSON 본문의 name, message를 저장하고 201과 {"entry": {...}}.
  글 하나에는 id, name, message, created_at(UTC ISO 문자열). name과 message는 앞뒤 공백을 지운 뒤 각각 1~40자, 1~500자이고, 문자열이 아니면 거절.
  실패하면 {"error": "설명"}. 잘못된 값과 깨진 JSON은 400, 8KiB가 넘는 본문은 413, JSON이 아닌 형식은 415, 없는 주소는 404.
  JSON 키 name, message는 바꾸지 않고, 더하는 칸은 비어도 201로 저장되는 선택 칸으로만.
- 다 물으면 PRD.md에 목적, 쓰는 사람, 화면, API 약속, 더한 칸, 확인, 이번에 하지 않는 것 순서로 짧은 해요체 문장으로 정리해 줘. 확인에는 python3 ~/dbinc-ai-course/labs/guestbook/smoke_test.py --url http://127.0.0.1:8080 을 적어.
- 코드는 만들지 말고 PRD.md 하나만 써. 지금 Plan 모드니까 PRD 내용을 계획으로 보여 주고, 내가 승인하면 그때 써.
```

PRD.md가 생기면 "이 폴더를 git 저장소로 만들고 지금까지를 커밋해 줘"라고 부탁해요.

## 설계 요청 (React와 Spring)

새 세션을 같은 폴더로 열고 Plan 모드로 바꾼 뒤 넣어요.

```text
@PRD.md 대로 만들 설계 계획을 세워 줘. 아직 파일은 만들지 마.
- 화면은 web 폴더에 React와 Vite로 만들어. 개발 서버는 5173이야.
- 서버는 api 폴더에 Spring Boot(Gradle)로 만들어. 포트는 8080이야.
- DB는 SQLite 파일 하나로 시작해. 파일은 api/data 폴더에 두고 Git에는 올리지 않아. JPA 같은 ORM은 쓰지 마.
- DB 주소는 application.properties의 spring.datasource.url에 적어 둬. 나중에 환경 변수로 바꿀 수 있게.
- 화면(5173)과 서버(8080)는 출처가 달라. Vite proxy로 풀지 서버에서 CORS를 허락할지 질문 카드로 물어봐. 백엔드를 Spring Boot 말고 다른 것으로 바꿀지도 같이 물어봐.
- API 약속은 PRD.md 그대로야. 확인 도구는 python3 ~/dbinc-ai-course/labs/guestbook/smoke_test.py --url http://127.0.0.1:8080 이고 이 파일은 고치지 마. ~/dbinc-ai-course 폴더의 다른 파일은 열지 마.
- 맨 위 index.html은 Python 길에서 쓰는 시작 화면이라 손대지 마.
- 개발 서버 두 개는 .claude/launch.json에 api와 web으로 적어서 Browser 창에서 켜고 끌 수 있게 해 줘.
- 단계는 1) 서버와 DB 2) 화면 연결로 나누고, 단계마다 무엇으로 확인할지 적어 줘.
- 내가 계획을 승인하면 1단계만 만들고 확인 도구 결과를 보여 준 뒤 멈춰. 실패가 있으면 고치기 전에 원인부터 말해 줘.
```

다른 백엔드로 할 때는 서버 줄과 포트, 확인 도구 주소를 바꿔요.

## 범위 줄이기

계획에 PRD에 없는 것이 들어 있으면 Plan 창의 그 줄에 "빼 줘" 댓글을 달거나, `No, keep planning`을 고르고 범위를 줄여요. 내 길에 맞는 문장을 골라요.

```text
범위를 줄여 줘. JPA, Spring Security, 로그인, 수정·삭제는 빼. 서버는 컨트롤러 하나와 schema.sql로 끝내고, 화면은 App.jsx 하나로 해. PRD.md의 "이번에 하지 않는 것"은 계획에도 넣지 마.
```

```text
범위를 줄여 줘. Flask, SQLAlchemy, 로그인, 수정·삭제는 빼. 파일은 app.py와 static 폴더의 index.html, style.css, app.js 네 개로 끝내고, PRD.md의 "이번에 하지 않는 것"은 계획에도 넣지 마.
```

계획이 PRD와 맞으면 `Yes, manually approve edits`를 골라요.

## 1단계 바로잡기

확인 도구가 실패를 잡으면 지금 단계에 맞는 것만 고치게 해요. 아래는 이름과 내용의 앞뒤 공백 처리가 빠졌을 때의 예예요.

```text
이름과 내용의 앞뒤 공백 문제만 고쳐. 앞뒤 공백을 지운 뒤 검사해. 화면은 2단계에서 할 거라 지금 만들지 마. smoke_test.py도 고치지 마.
```

확인 도구가 통과하면 "커밋해 줘"라고 부탁해요.

## Python 길 (설계 요청)

npm, start.spring.io, Gradle 내려받기가 두 번 넘게 막히면 같은 폴더에서 새 세션을 열고 Plan 모드로 넣어요. PRD.md는 그대로 써요.

```text
@PRD.md 대로 만들 계획을 세워 줘. 아직 파일은 만들지 마.
- Python 표준 라이브러리(http.server, sqlite3)만 쓰고 패키지는 설치하지 마.
- 서버는 app.py 하나이고 화면과 API를 함께 내보내. 포트는 8000이고, 테스트용으로 --port와 --db 옵션도 받게 해 줘.
- 화면은 맨 위 index.html을 static/index.html로 옮겨서 쓰고, CSS는 static/style.css, JavaScript는 static/app.js로 나눠.
- 확인 도구는 python3 ~/dbinc-ai-course/labs/guestbook/smoke_test.py --app app.py 이고 이 파일은 고치지 마. ~/dbinc-ai-course 폴더의 다른 파일은 열지 마.
- 단계는 1) 서버와 DB 2) 화면 연결로 나눠. 내가 승인하면 1단계만 만들고 확인 도구 결과를 보여 준 뒤 멈춰.
```

Python 길의 1단계에서는 화면이 아직 없어서 `test_static_routes_and_unknown_paths` 하나만 ERROR로 나오고 마지막 줄이 `FAILED (errors=1)`이에요. 이때는 정상이에요.

## 화면 연결

같은 세션에서 이어 가도 되고, 대화가 길어졌으면 새 세션에서 넣어요. 모드는 Accept edits로 바꿔요. 파일을 고칠 때마다 묻지 않아서 여러 파일을 만드는 이 단계에 맞아요.

### React

```text
@PRD.md를 보고 web 폴더의 React 화면을 서버에 연결해 줘. src/App.jsx의 기본 화면은 지우고 PRD의 화면대로 바꿔.
- 글은 POST /api/entries로 보내고, 목록은 GET /api/entries로 받아서 보여 줘. 설계에서 proxy를 골랐으면 주소는 /api/entries 그대로 써.
- 글은 JSX의 {값}으로만 넣고 dangerouslySetInnerHTML은 쓰지 마.
- 저장하는 동안 버튼을 막아서 두 번 눌리지 않게 하고, 서버 오류는 화면에 문장으로 보여 줘.
- 이름은 40자, 내용은 500자까지만 입력되게 하고, 비어 있으면 보내지 않게 화면에서도 막아 줘.
- 모양은 src/index.css와 src/App.css로 잡고, 다른 패키지는 추가하지 마.
- 끝나면 Browser 창에서 저장, 새로고침, 목록을 확인하고 확인 도구도 다시 돌려 줘. 확인 도구는 고치지 마. 커밋은 아직 하지 마.
```

내 것으로 바꿀 곳은 "PRD의 화면대로"예요. 서버에서 CORS를 허락하는 길을 골랐으면 주소를 `http://localhost:8080/api/entries`로 써 달라고 해요. web 폴더가 아직 없으면 Claude가 `npm create vite`로 먼저 만들고 연결해요(리허설에서 그랬어요).

### Python

```text
@PRD.md를 보고 방명록 화면을 API에 연결해 줘.
index.html은 static/index.html로 옮기고, <style> 안의 CSS는 static/style.css로, JavaScript는 static/app.js로 나눠.
이름과 내용 입력을 POST /api/entries에 연결하고, 목록은 GET /api/entries로 받아서 보여 줘.
사용자 입력은 textContent로 넣고 innerHTML은 쓰지 마.
저장하는 동안 버튼을 막아서 두 번 눌리지 않게 하고, 서버 오류는 화면에 문장으로 보여 줘.
서버는 /, /style.css, /app.js만 static 폴더에서 내보내고, app.py나 data 폴더 같은 다른 파일은 404로 막아.
끝나면 python3 ~/dbinc-ai-course/labs/guestbook/smoke_test.py --app app.py 를 돌려 줘. 이 파일은 고치지 마.
~/dbinc-ai-course/labs/guestbook 폴더에서는 smoke_test.py만 실행하고, 그 폴더의 app.py와 static/은 열지 마.
```

## CSS 한 가지 직접 고치기

이 단계는 Claude에게 요청하지 않고 내 손으로 해요. 편집기로 아래 파일을 열고 맨 아래에 규칙을 붙여 넣고 저장해요.

| 길 | 파일 |
| --- | --- |
| React와 Spring | `web/src/index.css` |
| Python | `static/style.css` |

```css
input:focus,
textarea:focus {
  outline: 3px solid #FF6F0F;
  outline-offset: 2px;
}
```

브라우저를 새로고침하고 이름 칸을 누르면 굵은 주황 테두리가 보여요. Claude에게 "git diff를 보여 줘"라고 하면 내가 붙인 줄만 `+`로 나와요. 확인했으면 커밋해요.

## 수업 뒤: PRD와 비교하기

실제로 보낸 답은 [examples/prd-compare-answer.md](examples/prd-compare-answer.md)에 있어요. 내가 먼저 Changes 창이나 `git diff`로 바뀐 내용을 읽은 다음, Claude에게도 PRD와 비교하게 해요. 고칠지 말지는 목록을 보고 내가 정해요.

```text
첫 커밋부터 지금까지 바뀐 내용을 git으로 보고, PRD.md와 다르게 동작하는 곳이 있는지 찾아 줘.
고치지는 말고 목록으로만 알려 줘.
```

## 다 됐는지 확인하기

- [ ] 정상 입력은 201, 공백만 있는 이름과 길이를 넘긴 값은 400이에요.
- [ ] 화면에서 저장한 기록이 새로고침한 뒤에도 보여요.
- [ ] 서버를 끄고 다시 켜도 기록이 남아 있어요.
- [ ] 확인 도구(`--url` 또는 `--app`)가 3개 모두 ok예요.
- [ ] 커밋 목록에 PRD, 서버와 DB, 화면 연결 커밋이 있어요.

## 수업 뒤: Docker로 DB 띄우기

수업에서는 다루지 않아요. Docker가 되는 PC에서 수업 뒤에 해요. Code 탭에서 새 세션을 열고 넣어요.

### 한 덩어리 길(Next.js): libSQL 서버

```text
DB를 Docker로 띄우게 해 줘. compose.yaml에 libSQL 서버(ghcr.io/tursodatabase/libsql-server:latest) 하나만 넣고,
내 PC의 127.0.0.1:8088을 컨테이너의 8080에 연결해. 데이터는 named volume으로 /var/lib/sqld에 보존해.
코드는 바꾸지 말고, .env.local에 TURSO_DATABASE_URL=http://127.0.0.1:8088 한 줄만 적어.
Docker가 없거나 실행되지 않으면 성공했다고 말하지 말고, 막힌 이유와 내가 직접 칠 명령을 적어 줘.
```

### React + Spring: PostgreSQL

```text
DB를 SQLite 파일에서 Docker의 PostgreSQL로 바꾸고 싶어. 먼저 바꿀 파일과 이유를 계획으로 보여 주고, 내가 승인하면 바꿔.
compose.yaml에는 postgres:17 하나만 넣고, 내 PC의 127.0.0.1:5432에만 연결하고, 데이터는 named volume으로 /var/lib/postgresql/data에 보존해.
build.gradle은 sqlite-jdbc를 org.postgresql:postgresql로 바꾸고, DB 주소·사용자·비밀번호는 application.properties에 직접 적지 말고 환경 변수로 받게 해.
API 약속은 그대로야. 끝나면 smoke_test.py --url http://127.0.0.1:8080 이 다시 통과해야 해.
Docker가 없거나 실행되지 않으면 성공했다고 말하지 말고, 막힌 이유와 내가 직접 칠 명령을 적어 줘.
```

### Python

Python 길은 DB 서버를 따로 두지 않고, 앱과 SQLite 파일을 통째로 컨테이너에 넣어요. 완성본의 `Dockerfile`과 `compose.yaml`([README](README.md)의 'Docker로 실행하기')을 참고해요.

```text
방명록을 Docker로 실행하게 해 줘. Dockerfile과 compose.yaml을 추가해.
컨테이너 안에서는 0.0.0.0:8000으로 받고, 호스트(내 PC)는 127.0.0.1:8000에만 연결해.
SQLite 파일은 /data 아래에 두고 named volume으로 보존해. DB 파일과 .env는 이미지에 복사하지 마.
docker compose restart 전후에 같은 기록이 보이는지 확인해 줘.
Docker가 없거나 실행되지 않으면 성공했다고 말하지 말고, 막힌 이유와 내가 직접 칠 명령을 적어 줘.
```

## 수업 뒤: 한 덩어리 길(Next.js)

화면과 서버를 한 프로젝트로 만드는 길이에요. 강사 방명록도 이 길로 만들어 배포했어요. PRD는 1절에서 만든 것을 써요. 아래 명령과 요청은 강사 PC(macOS, Next.js 16.4)에서 끝까지 실행해서 확인 도구 3개가 모두 ok인 것을 봤어요.

### 시작 프로젝트 만들기

macOS 터미널이나 Git Bash에서 한 줄씩 쳐요.

```bash
mkdir -p ~/dbinc-work
cd ~/dbinc-work
npx create-next-app@latest guestbook-next --yes --no-tailwind --use-npm
cd guestbook-next
npm install @libsql/client
mkdir data
echo "data/" >> .gitignore
git add .
git commit -m "libsql 클라이언트 추가"
```

`create-next-app`이 git 저장소와 첫 커밋까지 만들어요. 개발 서버는 `npm run dev`로 켜고, 주소는 http://localhost:3000 이에요. 1절에서 만든 `PRD.md`를 이 폴더로 복사해 와요. PRD의 '저장' 칸에는 아래 답을 더해요.

```text
SQLite 파일 data/guestbook.db에 저장하고 재시작 뒤에도 남아야 해. @libsql/client로 열고, TURSO_DATABASE_URL 환경 변수가 있으면 그 주소를, TURSO_AUTH_TOKEN이 있으면 그 토큰을 써.
```

### 계획 세우기

새 세션에서 Plan 모드로 넣어요.

```text
@PRD.md 대로 방명록을 만들 계획을 세워 줘. 코드를 쓰기 전에 @AGENTS.md 를 읽어.
@libsql/client는 이미 설치했어. 다른 패키지는 추가하지 마.
단계는 1) DB와 API 2) 화면 연결 로 나누고, 단계마다 무엇을 실행해서 확인할지 적어 줘.
개발 서버(npm run dev)는 내가 다른 터미널에서 켜 둘게. 너는 서버를 켜거나 끄지 마.
확인 도구는 python3 ~/dbinc-ai-course/labs/guestbook/smoke_test.py --url http://localhost:3000 이야. 이 파일은 고치지 마.
~/dbinc-ai-course/labs/guestbook 폴더에서는 smoke_test.py만 실행하고, 다른 파일은 열지 마.
계획을 승인하면 1단계만 만들고, 확인 결과를 보여 준 뒤 멈춰. 실패가 있으면 고치기 전에 원인부터 말해 줘.
```

`create-next-app`이 만든 `AGENTS.md`에는 "이 버전의 Next.js는 바뀐 점이 있으니 안내를 먼저 읽으라"는 내용이 들어 있어요. Claude가 예전 방식으로 코드를 쓰지 않게 해요.

### 범위 줄이기

```text
범위를 줄여 줘. Prisma, Drizzle 같은 ORM, 로그인, 수정·삭제는 빼. 파일은 lib/db.ts, app/api/entries/route.ts, app/page.tsx와 화면 컴포넌트 하나로 끝내고, PRD.md의 "이번에 하지 않는 것"은 계획에도 넣지 마.
```

### 화면 연결

새 세션에서 넣어요.

```text
@PRD.md를 보고 방명록 화면을 API에 연결해 줘. app/page.tsx의 기본 화면은 지우고 방명록 화면으로 바꿔.
입력과 목록은 "use client" 컴포넌트 하나로 만들어. 이름과 내용은 POST /api/entries로 보내고, 목록은 GET /api/entries로 받아서 보여 줘.
글은 JSX의 {값}으로만 넣고 dangerouslySetInnerHTML은 쓰지 마.
저장하는 동안 버튼을 막아서 두 번 눌리지 않게 하고, 서버 오류는 화면에 문장으로 보여 줘.
모양은 app/globals.css와 app/page.module.css로 잡고, 다른 패키지는 추가하지 마.
끝나면 python3 ~/dbinc-ai-course/labs/guestbook/smoke_test.py --url http://localhost:3000 를 돌려 줘. 이 파일은 고치지 마.
```

`"use client"`는 이 파일이 브라우저에서 돈다는 Next.js 표시예요. 입력칸과 버튼은 브라우저에서 움직여서 필요해요.

## 수업 뒤: 배포(한 덩어리 길)

위 한 덩어리 길(Next.js) 방명록을 Turso와 Vercel로 올리는 순서예요. 강사 방명록도 이 순서로 올렸어요. 이 방명록은 `/api/entries`가 있어서 번외 [웹앱을 앱으로](../../docs/day1-app.md)의 앱 파일(`labs/app/pwa`)이 그대로 돌아요. 수업의 수강생 배포(Vercel과 Supabase)와는 모양이 달라요. 계정과 회사 네트워크가 허락하는 사람만 하고, 회사 계정과 회사 데이터는 쓰지 않아요.

Turso CLI는 공식 설치 안내([docs.turso.tech/cli/installation](https://docs.turso.tech/cli/installation))대로 설치해요. macOS는 Homebrew로, Windows는 WSL 안에서 설치해요. 그다음 작업 폴더에서 한 줄씩 쳐요.

```bash
turso auth login
turso db create guestbook
turso db show --url guestbook
turso db tokens create guestbook
```

세 번째 줄이 DB 주소를, 네 번째 줄이 토큰을 보여 줘요. 토큰은 비밀번호와 같아서 대화창이나 채팅에 붙여 넣지 않아요. 이제 Vercel CLI로 배포해요.

```bash
npx vercel login
npx vercel link
npx vercel env add TURSO_DATABASE_URL production
npx vercel env add TURSO_AUTH_TOKEN production
npx vercel --prod
```

`vercel env add`는 값을 물어보니 그때 내 터미널에서 붙여 넣어요. 환경 변수는 새 배포에만 들어가서, 키를 넣은 뒤에 `--prod`로 배포해요. 대시보드의 프로젝트 화면에서 **Environment Variables** 메뉴로 넣고 **Deployments**에서 **Redeploy**를 눌러도 같아요.

로컬에서 먼저 Turso DB로 바꿔 보려면 작업 폴더의 `.env.local`에 `TURSO_DATABASE_URL=`과 `TURSO_AUTH_TOKEN=` 두 줄을 넣고 개발 서버를 다시 켠 뒤, `python3 ~/dbinc-ai-course/labs/guestbook/smoke_test.py --url http://localhost:3000`이 3개 모두 ok인지 봐요. `create-next-app`이 만든 `.gitignore`에 `.env*`가 들어 있어서 이 파일은 커밋되지 않아요. 내 `lib/db.ts`가 토큰을 읽지 않으면 Claude에게 `TURSO_AUTH_TOKEN`을 `authToken`으로 넘기게 고쳐 달라고 해요.

끝나면 Vercel 프로젝트를 지우거나 비공개로 돌리고, Turso DB는 `turso db destroy guestbook`으로 지워요. 참고: [Vercel CLI](https://vercel.com/docs/cli), [vercel env](https://vercel.com/docs/cli/env), [Turso와 Next.js](https://docs.turso.tech/sdk/ts/guides/nextjs), [Vercel에서 SQLite](https://vercel.com/kb/guide/is-sqlite-supported-in-vercel).
