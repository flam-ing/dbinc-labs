# 데이터 출처

- 받은 시각: 2026-10-20 16:07:00 UTC (2026-10-21 01:07:00 +0900)
- 기간: 2024-10-20 ~ 2026-10-19 (UTC 날짜 기준, 오늘 2026-10-20 봉은 미완결이라 제외), 729행
- 종가·거래대금: 업비트 공개 API `https://api.upbit.com/v1/candles/days?market=KRW-BTC` (trade_price, candle_acc_trade_price; 원화, 일봉은 09:00 KST 시작)
- 공포·탐욕 지수: alternative.me `https://api.alternative.me/fng/`
- 합치기: 날짜(UTC)로 inner join. 한쪽에만 있는 날은 제외
- 생성: fetch.py
