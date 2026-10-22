# 4교시 실습 순서와 문장

1일차 4교시 실습의 순서와 보내는 문장이에요. `<꺾쇠>` 안만 내 것으로 바꿔요. 꺾쇠 기호는 보내지 않아요. 설명은 [4교시 교안](../../../docs/day1-guestbook.md)에 있어요.

같은 폴더에 리허설 결과가 있어요.

| 파일 | 무엇 |
| --- | --- |
| [PRD-praise-relay.md](PRD-praise-relay.md) | 인터뷰로 실제로 만든 PRD예요. 시간이 모자라면 작업 폴더에 `PRD.md`로 저장해서 써요 |
| [praise-relay-done.webp](praise-relay-done.webp) | 다 만든 칭찬 릴레이 화면이에요 |
| [smoke-ok.txt](smoke-ok.txt) | 확인 도구가 3개 모두 ok일 때의 출력이에요 |
| [prd-compare-answer.md](prd-compare-answer.md) | PRD와 다르게 동작하는 곳을 찾아 달라고 했을 때 실제로 온 답이에요 |

## 따라 하기 · 시작 폴더 열기 (3분)

1. 탐색기(macOS는 Finder)에서 `dbinc-ai-course/labs/guestbook/starter` 폴더를 복사해요.
2. 홈 폴더 아래 `dbinc-work`에 붙여 넣고, 이름을 `praise-relay`처럼 바꿔요. 영어 소문자와 `-`로 지어요.
3. Code 탭에서 **+ New session**, **Local**, **Select folder**로 그 폴더를 골라요. 모드는 **Plan**으로 해요.
4. 입력창에 `/`를 쳐서 `prd-interview`가 보이면 끝이에요.

## 실습 1 · 인터뷰로 PRD (12분)

```text
/prd-interview <칭찬 릴레이>
```

질문 카드가 오면 골라서 넘겨요. 내 말로 답하고 싶으면 Other 칸에 써요. PRD 내용이 계획으로 나오면 읽고 **Yes, manually approve edits**로 승인해요. 리허설에서는 질문 여섯 개 뒤에 36줄짜리 PRD가 생겼어요.

## 실습 2-1 · 계획 받고 승인하기 (8분)

**+ New session**으로 같은 폴더를 열고 모드를 **Plan**으로 해요. 회사에서 쓰는 다른 백엔드가 있으면 `<꺾쇠>` 안만 바꿔요.

```text
PRD.md대로 React 화면, <Spring Boot> 서버, DB로 방명록을 만들어서 켜 줘.
```

계획에 JPA나 로그인이 들어 있으면 **No, keep planning**을 고르고 보내요.

```text
JPA와 로그인은 빼 줘. PRD.md의 "이번에 하지 않는 것"은 계획에도 넣지 마.
```

계획이 PRD와 맞으면 **Yes, manually approve edits**로 승인해요. 리허설에서는 같은 일을 두 번에 나눠 보냈고, 모두 6분쯤 걸렸어요. 나눠 보낸 문장은 [단계별 요청 모음](../REQUIREMENTS-PROMPTS.md)에 있어요.

## 실습 2-2 · 켜서 글 써 보기 (14분)

권한 카드를 읽고 허락해요. 다 되면 http://localhost:5173 을 열고 글을 남겨요. 주소를 말하지 않으면 보내요.

```text
방명록을 켜고 열어 볼 주소를 알려 줘.
```

글이 목록에 보이고, 새로고침하거나 서버를 껐다 켜도 남아 있으면 성공이에요.

8080을 다른 프로그램이 쓰고 있으면 보내요.

```text
8080은 다른 프로그램이라 끄지 마. 우리 서버를 <8081>로 바꾸고, launch.json과 확인 도구 주소도 <8081>로 맞춰서 다시 검사해 줘.
```

npm이나 Gradle 내려받기가 두 번 넘게 막히면 새 세션에서 보내요.

```text
PRD.md대로 Python 표준 라이브러리만 써서 방명록을 만들어서 켜 줘.
```

## 실습 3-1 · 디자인 하나 바꾸기 (7분)

```text
목록 카드를 <우리 팀 색>으로 바꿔 줘.
```

색 대신 글씨 크기나 버튼 모양이어도 돼요. 화면이 깨지면 "방금 바꾼 것을 되돌려 줘"라고 보내요.

## 실습 3-2 · 기능 하나 바꾸기 (6분)

```text
목록 위에 <지금까지 남긴 글 개수>를 보여 줘.
```

화면에서 끝나는 기능으로 골라요. Claude가 서버 파일까지 고치려 하면 "화면만 바꿔 줘"라고 해요.

## 실습 4-1 · Supabase 표 만들기 (12분)

아래 문장을 그대로 보내요. 이 문장은 리허설 때 확인해요.

```text
이 방명록을 Vercel과 Supabase로 배포하고, 가입이나 로그인이나 키 입력이 필요하면 멈추고 알려 줘.
```

Claude가 멈추면 [supabase.com](https://supabase.com)에 가입하고 새 프로젝트를 만들어요. **SQL Editor**에 Claude가 만든 `schema.sql` 내용을 붙여 넣고 **Run**을 눌러요. `schema.sql`에 RLS가 없으면 보내요.

```text
RLS를 켜고 읽기와 글쓰기만 허락해 줘.
```

## 실습 4-2 · 키 넣고 확인하기 (8분)

**Connect** 창에서 Project URL과 publishable 키를 복사해서 `web/.env.local`에 붙여 넣고 저장해요. secret 키는 쓰지 않아요. 키는 대화창에 붙여 넣지 않아요.

```text
키를 web/.env.local에 넣었어. 내 PC에서 Supabase로 글이 써지는지 확인해 줘.
```

## 실습 4-3 · Vercel로 올리기 (14분)

세션 위쪽 **Terminal**에서 `web` 폴더로 가서 `npx vercel login`을 쳐요. PowerShell에서 막히면 `npx.cmd vercel login`으로 쳐요. 로그인한 뒤 보내요.

```text
Vercel에 로그인했어. 이어서 배포하고 열 주소를 알려 줘.
```

받은 https 주소를 휴대폰으로 열어 한 줄 남겨요. 빌드 오류가 나면 오류 글을 통째로 붙여 넣고 보내요.

```text
아래는 Vercel 빌드 오류 글 전체야. 고치기 전에 원인부터 말해 줘.
<오류 글 전체 붙여 넣기>
```

수업이 끝나면 Vercel 프로젝트와 Supabase 프로젝트를 지우거나 멈춰 둬요.
