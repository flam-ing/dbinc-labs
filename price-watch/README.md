# 가격 추적 실습 자료 (price-watch)

예전 2일차 4교시에 쓰던 자료예요. 지금 [6교시](../../docs/day2-knowledge.md)에서는 이 폴더를 쓰지 않아요. 수업 뒤 심화로 남겼어요.
가격이 매일 바뀌고 페이지 구조도 가끔 바뀌는 가상 쇼핑몰(연습몰)을 수집해서 지식베이스에 쌓고, 쌓인 기록으로 추이를 계산해 리포트로 묶어요.
상품, 가격, 소식, 회사 이름은 모두 수업을 위해 지어낸 것이에요. 실제 사이트에는 요청하지 않아요.
원격 사이트(test-server)를 예의 있게 모으는 심화는 [labs/remote-crawl](../remote-crawl/README.md)에 있어요. 이 폴더의 연습몰은 30일을 짧은 시간에 돌려 보는 시뮬레이터라서, 지식베이스와 예측에 써요.
Python 표준 라이브러리만 써서 `pip install`이 필요 없어요.

## 들어 있는 것

| 폴더·파일 | 무엇 | 수강생 작업 폴더로 복사하나요 |
| --- | --- | --- |
| `shop/` | 연습몰 서버(포트 8766). 상대 사이트 역할이에요 | 아니요. 이 자리에서 켜요 |
| `starter/` | 작업 폴더의 시작 상태. 수집기, 지식베이스, 서브에이전트, 스킬, 훅, 도구, 테스트 | 예. `~/dbinc-price-watch`로 복사해요 |
| `reference/` | 정답 자료. 네 구조를 모두 읽는 `collect.py`, 구조별 테스트와 스냅숏, 위키 예시, 30일 리포트 예시 | 폴더째는 아니요. 7절(15일)에서 `collect.py`와 `tests/`를 작업 폴더에 복사해요 |
| `tests/` | 이 자료 자체의 검사. 서버와 30일 전체 흐름 | 아니요 |
| `examples/` | 학생용 예시 요청 모음(`prompts.md`), 실제로 나온 결과 견본(`results.md`), 하네스에 더할 규칙 예시(`team-rules.md`) | 아니요. 저장소나 교안 사이트에서 열어 봐요 |
| `_reference/claude-runs/` | 강사용. 2026-10-17에 실습 예시 요청을 실제 Claude Code로 돌린 기록과 Claude가 만든 파일(README에 표) | 아니요 |

## 연습몰

서버 창(터미널 하나)에서 켜요. Claude 데스크톱 앱 Code 탭의 Terminal 창에서 켜도 돼요.

```bash
cd ~/dbinc-ai-course/labs/price-watch
python3 shop/server.py --port 8766
```

Windows는 `python3` 대신 `py`를 써요. python.org 설치본에는 `python3` 명령이 없어요.

실행 결과:

```text
연습몰(교육용 가상 쇼핑몰): http://127.0.0.1:8766/products
시뮬레이션 날짜: 2026-11-01 (1일차) · 끄려면 Ctrl+C
```

서버 창에는 요청이 올 때마다 한 줄씩 찍혀요. 수집기가 요청 간격(1초)을 지키는지 여기서 볼 수 있어요.

```text
[11-23 · 23일차] GET /api/catalog?page=1 200 · 지난 요청 후 1.0초 · DBIncPriceWatch/1.0 (training)
[11-23 · 23일차] GET /api/catalog?page=2 429 · 지난 요청 후 1.0초 · DBIncPriceWatch/1.0 (training)
```

| 주소 | 내용 |
| --- | --- |
| `/products` | 상품 10개의 오늘 판매가와 정가. 날짜에 따라 구조가 바뀌어요 |
| `/news`, `/api/news` | 오늘까지 나온 가상 소식(HTML, JSON). 구조가 바뀌지 않아요 |
| `/api/catalog?page=N` | 23일부터 생기는 JSON API. 한 쪽에 5개, 날마다 2쪽 첫 요청은 429(Retry-After: 1) |
| `/robots.txt`, `/terms` | 수집 규칙: `/admin` 금지, Crawl-delay 1, 1초에 한 번 이하 |
| `/admin/day` | 수업 진행용 날짜 바꾸기(GET 보기, POST `{"day": 8}` 또는 `{"next": true}`) |

모든 응답에는 `X-Sim-Date`(시뮬레이션 날짜) 헤더가 붙어요. 날짜는 2026-11-01(1일차)부터 2026-11-30(30일차)까지예요.
`--day 8`로 켜면 8일차부터 시작하고, `--no-failures`로 켜면 429를 내지 않아요.

### 날짜별 구조

| 날짜 | 구조 | 데이터가 있는 곳 |
| --- | --- | --- |
| 1~7일 | A: 정적 HTML 목록 | `li.product[data-sku]`, `span.name`, `span.price`, 할인 때 `s.list-price` |
| 8~14일 | B: 카드형 | `article.card[data-item-id]`, `h3`, 할인 때 `<del>정가</del> <strong>판매가</strong>` |
| 15~22일 | C: 화면은 JavaScript가 그림 | `<script id="__SHOP_STATE__" type="application/json">` 안 JSON |
| 23~30일 | D: 빈 껍데기와 JSON API | HTML에는 `<div id="app">`뿐, `/api/catalog?page=N`을 `next`가 null일 때까지 |

### 가격과 소식의 관계(예측 연습용)

가격은 시드를 고정한 계산이라 같은 날에는 언제나 같아요. 날마다 상품 하나가 "오늘의 특가"(5%)로 나와요.
아래 변화는 며칠 앞서 관련 소식이 나와요. 소식과 무관한 작은 정가 조정도 몇 번 섞여 있어요.

| 가격 변화 | 앞선 소식 |
| --- | --- |
| 전원(PW-103, PW-104) 정가가 6일부터 나흘마다 약 2% 오름 | 3일 "배터리 셀 원가 오름세" |
| 오디오(PW-101, PW-102) 12~14일 12% 할인 | 9일 "이웃몰 11월 12~14일 오디오 기획전 예고" |
| 연결·영상(PW-107, PW-108) 19일 정가 5% 오름 | 16일 "환율 부담 커져 수입 주변기기 값 오를 듯" |
| 입력(PW-105, PW-106) 25~27일 10% 할인 | 20일 "이웃몰 11월 25~27일 입력기기 특가 예고" |
| 모니터암(PW-109) 26일부터 이틀마다 정가 1.5% 내림 | 24일 "모니터암 신모델 출시 예고" |
| 없음. 30일 뒤의 일이라 예측 표의 "주의" 표시를 보는 연습용이에요 | 28일 "이웃몰 12월 3~5일 전원기기 기획전 예고" |

## 작업 폴더 만들기

```bash
cp -R ~/dbinc-ai-course/labs/price-watch/starter ~/dbinc-price-watch
cd ~/dbinc-price-watch
git init
git add .
git commit -m "가격 추적 시작 상태"
python3 -m unittest discover -s tests
```

테스트의 마지막 줄은 `Ran 19 tests in ...`와 `OK`예요. 사용법은 작업 폴더의 `GUIDE.md`와 `CLAUDE.md`에 있어요.

탐색기(macOS는 Finder)로 `starter`를 홈 폴더에 `dbinc-price-watch`로 복사하고, Code 탭에서 그 폴더를 고른 다음 git init과 첫 커밋, 테스트를 부탁해도 돼요.

하네스 훅(`starter/.claude/hooks/guard.py`)의 `EXTRA_BLOCKS` 목록은 교안 부록 C(선택 심화)에서 수강생이 막을 명령을 한 줄 더하는 자리예요. 처음에는 `git push` 예시 줄이 주석이라 이 목록으로 막는 것은 없어요. 이 훅은 연습몰(127.0.0.1, localhost) 말고는 모두 막아요. 원격 test-server 수집은 이 폴더에서 하지 않아요.

## 확인 명령

이 폴더에서 실행해요.

```bash
python3 -m unittest discover -s tests
(cd starter && python3 -m unittest discover -s tests)
(cd reference && python3 -m unittest discover -s tests)
```

첫 줄은 연습몰을 빈 포트로 띄워서 1~7일 수집, 8일 구조 변경으로 멈춤, 정답 수집기로 30일까지 수집, 위키 정리, 예측, 리포트, 묶기, 다른 폴더에 풀어서 다시 실행까지 한 번에 돌려요(13개, 3초 정도). 둘째 줄은 19개, 셋째 줄은 13개가 `OK`로 끝나요.
macOS에서 Python 3.12와 3.14로 확인했어요. Windows에서는 확인하지 않았어요.

## 정답 자료(reference)

| 파일 | 내용 |
| --- | --- |
| `reference/collect.py` | A·B·C·D를 모두 읽는 수집기. `PARSERS = [parse_state_c, parse_cards_b, parse_list_a]`, D는 `fetch_catalog_d` |
| `reference/tests/test_layout_b.py`, `_c.py`, `_d.py` | 구조마다 새로 더한 테스트. 예전 `test_collect.py`는 그대로예요 |
| `reference/tests/fixtures/` | 8일, 15일, 23일 스냅숏과 23일 카탈로그 JSON |
| `reference/wiki/` | 세 번의 변경을 적은 `selector-changes.md`, `incidents.md`, 메모를 채운 상품 페이지 두 개 |
| `reference/out/report.md`, `summary.md` | 30일 기록으로 만든 리포트와 요약 예시 |

90분 수업에서는 8일 구조 변경만 직접 고치고, 15일부터는 정답 수집기와 정답 테스트를 같이 가져와서 이어서 모아요(교안 7절). 8일 고치기가 끝나지 않았을 때도 같은 명령을 써요. 작업 폴더(`~/dbinc-price-watch`)의 Terminal 창에서 쳐요.

```bash
cp ~/dbinc-ai-course/labs/price-watch/reference/collect.py collect.py
cp -R ~/dbinc-ai-course/labs/price-watch/reference/tests/. tests/
python3 -m unittest discover -s tests
```

수집기만 바꾸면 안 돼요. 내 Claude가 만든 `tests/test_layout_b.py` 같은 테스트가 내 파서 이름(예: `parse_card_b`)을 불러서 실패하고, 그러면 `package.py`도 묶지 않아요. 정답 테스트를 같이 가져오면 같은 이름의 내 테스트를 덮어쓰고, 테스트 24개가 모두 통과해요(2026-10-17에 해 봤어요).
