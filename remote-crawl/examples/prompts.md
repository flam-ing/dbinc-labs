# 내 수집기 예시 요청

2일차 4교시 "내 수집기" 실습에서 Code 탭에 보낼 말의 예시예요. 그대로 써도 되지만, `<꺾쇠>` 안은 내 것으로 바꿔요. 내 말로 바꿔 써도 돼요.
첫 번째 예시는 2026-10-17에 실제로 돌려 본 문장이에요. 그때 나온 결과는 [results.md](results.md)에 있어요.

## 시작하기 전에

1. 이 폴더를 홈 폴더에 `dbinc-remote-crawl`로 복사해요.
2. Code 탭에서 **+ New session**, **Select folder**로 그 폴더를 골라요.
3. 모드 선택기를 **Manual**로 둬요. 명령을 실행하기 전마다 확인 카드가 떠요. 무엇을 실행하는지 읽고 허용해요.

## 1. 첫 요청: 내 이름으로 한 번 읽기

바꿀 곳은 두 군데예요. `<DBInc-3jo/1.0>`은 우리 조 이름, `<JSON>`은 읽을 길(JSON 또는 HTML)이에요.

```text
README.md와 polite-crawl 스킬을 먼저 읽어. polite_fetch.py의 NAME을 <DBInc-3jo/1.0>으로 바꾸고, <JSON> 길로 한 번만 실행해서 결과 한 줄과 data/live-prices.csv의 마지막 줄을 보여 줘. 1분이 안 지났으면 다시 부르지 말고 캐시 값을 보여 줘.
```

끝나면 이렇게 돼요.

- `polite_fetch.py`에서 `NAME` 한 줄만 바뀌어요.
- `data/live-prices.csv`에 내 이름(`user_agent` 칸)이 들어간 줄이 생겨요.
- 1분 안에 Terminal 창에서 `python3 polite_fetch.py`를 다시 치면 `캐시:`로 시작하는 줄이 나오고, 서버에는 묻지 않아요.

## 2. 더 해 보기

### HTML 길로 한 번 더 읽고 칸 비교하기

같은 주소에는 1분에 한 번만 물어요. 그래서 두 길을 같은 분에 같이 읽을 수는 없어요. 1분 넘게 기다린 뒤 HTML 길로 읽고, 두 줄의 칸을 비교해요.

```text
1분 넘게 지났으면 python3 polite_fetch.py --route html로 한 번만 읽어 줘. 그다음 data/live-prices.csv의 JSON 줄과 HTML 줄을 표로 놓고, 어떤 칸이 비었거나 다른지 알려 줘.
```

실제로 해 보면 HTML 줄에는 `updated_at`이 비어 있어요. HTML 화면에는 값이 바뀐 시각이 없기 때문이에요.

### v2 길 더하기

바꿀 곳은 `<1초>`(세션을 받은 뒤 기다릴 시간)예요. 1초보다 짧게 하지 않아요.

```text
polite-crawl 규칙을 지켜서 polite_fetch.py에 v2 길을 더해 줘. /v2/session에서 세션 쿠키를 받고, 같은 실행 안에서 <1초> 뒤 /v2/api/price를 읽어. 브라우저인 척하는 헤더는 넣지 마. 받아 둔 응답으로 테스트를 하나 더하고, 실제 실행은 1분이 지난 뒤 한 번만 해.
```

### 코드에 없는 것 적기

```text
data/notes.md를 만들어서 이 대상에 대해 코드만 봐서는 모르는 것(robots.txt가 없었다, 값은 1분마다 바뀐다, v2는 세션이 있어야 한다, 막혔을 때 무슨 응답이 왔다)을 적어 줘. 숫자는 data/ 파일과 실행 결과에서만 가져와.
```

### 다른 언어로

바꿀 곳은 `<Java>`예요. 그 언어가 내 PC에 있어야 해요.

```text
polite_fetch.py와 같은 규칙(이름 밝히기, 1분 간격, 캐시, 401·403·429면 멈추기)으로 <Java> 수집기를 fetch/ 폴더에 만들어 줘. 실제 실행은 1분이 지난 뒤 한 번만 해.
```

## 막히면

- test-server가 브라우저로도 안 열리면 서버 창에서 연습몰을 켜고(`python3 ~/dbinc-ai-course/labs/price-watch/shop/server.py --port 8766`) 이렇게 부탁해요.

```text
test-server가 막혀서 연습몰로 할게. python3 polite_fetch.py --shop으로 한 번만 실행해서 결과 한 줄을 보여 줘.
```

- `막혔어요(403)`나 `막혔어요(429)`가 나오면 다시 두드리지 말고 1분 넘게 기다린 뒤 한 번만 다시 해요.
