# 크롤링 한 번 해 보기

2일차 6교시 [크롤링, 빅데이터와 예측](../../docs/day2-knowledge.md)의 실습 1~3에서 써요. 실습 1에서는 강의 사이트의 크롤링 공방을 직접 눌러 보고, 실습 2에서는 연습 서버 test-server에서 상품 하나의 이름과 가격을 가져와요. 상품은 "입문 키보드" 하나이고, 가격은 1분마다 바뀌어요.

- 연습 서버 주소: `https://test-server-8az.pages.dev/`
- 가격만 주는 주소: `https://test-server-8az.pages.dev/api/price`
- 크롤링 공방 연습 판: `https://slides.ai-ing.org/crawl/practice/` (수업 사이트에 로그인해 둔 브라우저에서 열어요)

이 서버는 수업 연습용이라 가져와도 돼요. 다른 회사 사이트는 허락 없이 가져가지 않아요.

## 실습 1: 공방 직접 해 보기 (4분)

1. 브라우저 새 탭에서 `https://slides.ai-ing.org/crawl/practice/`를 열어요.
2. 처음에는 test-server 상품 화면이 나와요. 오른쪽 아래 "다음"을 한 번 눌러 공방 화면으로 가요.
3. 왼쪽 칸 맨 아래 "페이지 가져오기"를 눌러요. 오른쪽 RECENT LOGS 맨 위에 `GET /` 줄이 새로 생기면 끝이에요.
4. 일찍 끝나면 "같은 요청 ×30"을 한 번만 눌러 기록이 한꺼번에 쌓이는 것을 봐요.

1라운드만 해요. 다음 라운드의 차단 스위치는 반 전체가 같이 쓰는 서버에 걸려서, 누르면 다른 사람도 막혀요.

## 실습 2: 상품 하나 가져오기 (10분)

1. 빈 폴더를 하나 만들어요(예: `dbinc-crawl`).
2. Code 탭에서 **+ New session**을 누르고, **Select folder**로 그 폴더를 골라요.
3. [examples/prompts.md](examples/prompts.md)의 실습 2 문장을 보내요.
4. 허락을 물으면 내용을 보고 허락해요.
5. 상품 이름과 가격 두 줄이 나오면 끝이에요.
6. 일찍 끝나면 1분 뒤에 다시 실행해서 가격이 바뀌는지 봐요.

## 실습 3: 막을까 보이게 할까 (8분)

실습 2의 폴더를 그대로 써도 돼요. [examples/prompts.md](examples/prompts.md)의 실습 3 문장을 보내요. Claude의 답을 읽고, 내 생각과 같은지 짝에게 한 줄로 말해요.

## 끝났을 때 모습

강사가 2026-10-17에 실습 2 문장을 그대로 보내 본 결과가 [examples/results/](examples/results/)에 있어요.

- [answer.md](examples/results/answer.md): Claude의 마지막 답이에요.
- [crawl.py](examples/results/crawl.py): Claude가 만든 파일이에요. 파이썬 기본 기능만 써서 따로 설치할 것이 없어요.

실행하면 이렇게 나와요. 가격은 실행할 때마다 다를 수 있어요.

```text
상품 이름: 입문 키보드
가격: 40,900원
```

## 막히면

- 파이썬이 3.10 이상인지 봐요. Mac은 `python3 --version`, Windows는 `py --version`으로 봐요.
- 인터넷이 막혀 있으면 [examples/results/crawl.py](examples/results/crawl.py)를 열어서 코드만 같이 읽어요.
- Claude가 다른 주소까지 둘러보려고 하면 "이 주소 하나만 읽어 줘"라고 말해요.
