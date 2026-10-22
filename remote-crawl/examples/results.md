# 내 수집기 결과 견본

[prompts.md](prompts.md)의 첫 요청을 2026-10-17에 실제로 돌려 본 결과예요. 이름은 `DBInc-3jo/1.0`, 길은 JSON이었어요. 값과 시각은 실행할 때마다 달라요.
학생 화면에서는 명령을 실행하기 전에 확인 카드가 떠요. 이 견본은 확인 카드를 미리 허락하고 돌린 것이라 카드가 없어요.

## Claude의 답

19초 동안 6번 주고받았어요. 아래는 Claude가 마지막에 한 말 원문이에요.

````markdown
README.md와 polite-crawl 스킬을 읽었고, `polite_fetch.py`의 `NAME`을 `DBInc-3jo/1.0`으로 바꿨어요(29번째 줄). JSON 길로 한 번 실행했고 오류 없이 끝났어요(종료 코드 0).

**결과 한 줄**
```
[json] 입문 키보드 35,900원 · 재고 13개 · data/live-prices.csv에 한 줄 더했어요
```

**`data/live-prices.csv` 마지막 줄**
```
2026-10-16T17:53:12+00:00,json,입문 키보드,35900,13,2026-10-16T17:53:00.000Z,https://test-server-8az.pages.dev/api/price,DBInc-3jo/1.0
```

- **캐시:** 이전에 보낸 요청 기록이 없어서 캐시는 쓰지 않았고 실제로 한 번 물었어요. 1분 안에 다시 실행하면 스크립트가 서버에 묻지 않고 캐시 값을 보여 줘요.
- **요청 수:** 처음 실행이라 `robots.txt`를 한 번 더 읽어서, 서버에는 요청이 두 번 갔어요. `robots.txt`는 없다고 나왔어요.
- **다음 값:** 2026-10-16T17:54:00Z(UTC)에 나와요. 한국 시간으로는 10월 17일 02:54예요.
````

## 바뀐 파일

`git diff`로 보면 `polite_fetch.py`의 `NAME` 한 줄만 바뀌었어요.

```diff
-NAME = "DBInc-training/1.0"   # 나를 밝히는 이름(User-Agent). 예: DBInc-3jo/1.0
+NAME = "DBInc-3jo/1.0"  # 나를 밝히는 이름(User-Agent). 예: DBInc-3jo/1.0
```

## 1분 안에 다시 실행하면

Terminal 창에서 직접 쳤어요. 서버에 묻지 않고 저장해 둔 값을 보여 줘요.

```text
$ python3 polite_fetch.py
캐시: 지난 요청이 10초 전이라 묻지 않았어요. 마지막 값 입문 키보드 35,900원 · 50초 뒤에 다시 물을 수 있어요.
```

## 1분 넘게 기다린 뒤 HTML 길로 읽으면

```text
$ python3 polite_fetch.py --route html
[html] 입문 키보드 40,900원 · 재고 18개 · data/live-prices.csv에 한 줄 더했어요
$ cat data/live-prices.csv
fetched_at,route,name,price,stock,updated_at,source_url,user_agent
2026-10-16T17:53:12+00:00,json,입문 키보드,35900,13,2026-10-16T17:53:00.000Z,https://test-server-8az.pages.dev/api/price,DBInc-3jo/1.0
2026-10-16T18:04:04+00:00,html,입문 키보드,40900,18,,https://test-server-8az.pages.dev/,DBInc-3jo/1.0
```

HTML 줄은 `updated_at`이 비어 있어요. 시각은 UTC예요. 한국 시각은 여기에 9시간을 더해요(17:53 UTC는 다음 날 한국 시각 02:53이에요).

## 끝났을 때 확인할 것

- `data/live-prices.csv`에 내 이름이 들어간 줄이 하나 이상 있어요.
- 1분 안에 다시 실행하면 `캐시:`로 시작하는 줄이 나와요.
- `git diff`에 `NAME`(필요하면 `ROUTE`) 말고 바뀐 줄이 없어요.
