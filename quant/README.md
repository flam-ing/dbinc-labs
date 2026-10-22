# 과거 데이터로 대 보기

2일차 6교시 [크롤링, 빅데이터와 예측](../../docs/day2-knowledge.md)의 실습 3과 실습 4에서 써요. 비트코인 시세와 공포·탐욕 지수로 규칙 하나를 과거 2년에 대 보고, 첫날 사서 그냥 들고 있기와 비교해요. 이어서 앞 기간에 고른 기준이 뒤 기간에도 좋은지 확인해요.

> **주의** 교육용 연습이에요. 투자를 권하는 것이 아니에요. 실제 주문이나 거래소 키는 쓰지 않고, 시세를 읽기만 해요.

## 쓰는 데이터

| 데이터 | 무엇 | 어디서 |
| --- | --- | --- |
| 비트코인 일봉 | 날짜별 종가와 거래대금 | 업비트 Open API(키 없음) `https://api.upbit.com/v1/candles/days?market=KRW-BTC` |
| 공포·탐욕 지수 | 0(겁냄)부터 100(들뜸)까지 매일 매긴 값 | alternative.me `https://api.alternative.me/fng/` (키 없음) |

회사 인터넷에서 두 주소가 막히면 [snapshot/](snapshot/SOURCE.md)의 사본을 써요. 강사가 2026-10-21에 같은 API에서 받은 799일치예요.

## 실습 3: 과거 데이터로 대 보기 (12분)

1. 빈 폴더를 하나 만들어요(예: `dbinc-quant`).
2. Code 탭에서 **+ New session**을 누르고, **Select folder**로 그 폴더를 골라요.
3. [examples/prompts.md](examples/prompts.md)의 실습 3 문장을 보내요. 허락을 물으면 내용을 보고 허락해요.
4. 표에서 규칙의 수익률과 들고 있기의 수익률을 봐요.

## 실습 4: 함정 찾기 (8분)

1. 실습 3의 세션을 그대로 써요.
2. [examples/prompts.md](examples/prompts.md)의 실습 4 문장을 보내요.
3. 앞 기간에서 가장 좋았던 기준이 나머지 기간에 몇 위였는지 봐요.

강사가 "함정 찾기" 문장을 보내 본 답은 [03-check.md](examples/03-check.md)에 있어요. 앞 1년 1등 기준(30/80)이 뒤 1년에는 49개 중 41위였어요.

`examples/`와 `_reference/`는 내 폴더로 복사하지 않아요. 같은 폴더에 있으면 Claude가 견본을 읽어서 내 답에 섞여요.

## 강사가 받은 결과

강사는 [examples/prompts.md](examples/prompts.md)의 ①번과 ②번 문장을 차례로 보냈어요. 가상 1,000만 원으로 2024-10-20부터 2026-10-19까지 대 본 결과예요.

| 방법 | 2년 수익률 |
| --- | ---: |
| 규칙(공포·탐욕 25 아래 사기, 75 위 팔기) | -18.4% |
| 첫날 사서 들고 있기 | +17.3% |

이 2년에는 규칙이 졌어요. 받은 답은 [01-fetch.md](examples/01-fetch.md)와 [02-backtest.md](examples/02-backtest.md)에 있어요. 강사 실행에는 이동평균 규칙도 함께 있었어요. Claude가 만든 파일은 [examples/results/](examples/results/)에 있어요.

## 막히면

- **업비트나 alternative.me가 막혔을 때**: `labs/quant/snapshot` 폴더를 내 폴더에 `snapshot`이라는 이름으로 복사해요. 그다음 [examples/prompts.md](examples/prompts.md)의 "막혔을 때" 문장을 보내요.
- **파이썬**: 3.10 이상이면 돼요. Mac은 `python3 --version`, Windows는 `py --version`으로 봐요. 따로 설치할 패키지는 없어요.
- **숫자가 강사와 다를 때**: 받은 날짜가 달라서 기간이 달라요. 같은 기간으로 맞추려면 snapshot을 써요.
- **Claude가 실제 주문을 만들려고 할 때**: "주문 API와 키는 쓰지 마."라고 다시 말해요.

## 강사용

- `examples/results/`에서 `backtest.py`와 `check.py`를 다시 돌려도 같은 숫자가 나와요. Windows는 `py backtest.py`처럼 쳐요.
- 실제 실행 원본은 `_reference/claude-runs/`에 있어요. 사이트와 학생 ZIP에는 들어가지 않아요.
