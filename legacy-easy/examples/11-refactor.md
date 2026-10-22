# 한 단계씩 리팩터링(①~⑧): 실제로 나온 답

[prompts.md](prompts.md)의 말을 그대로 보낸 실제 답이에요. 답은 고치지 않았어요.

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-10-19 |
| Claude Code | 2.1.302 |
| 모델 | Sonnet 5.5 |
| 모드 | Auto |
| 폴더 | 카페 포인트(안전망 다음) 사본 |
| 걸린 시간 | 6분 2초 |

## 보낸 말

```text
CLAUDE.md 규칙대로 cafe.py를 한 단계씩 리팩터링해 줘. 단계마다 python3 cafe.py를 다시 돌려 화면 출력과 out 폴더가 before/와 같은지 확인한 다음 커밋해 줘. 순서는 이래요.
① 안 쓰는 코드 지우기: 주석 처리한 옛 적립 코드와 디버그 print, 아무도 부르지 않는 run2(), load_members(), reset_points()와 ADMIN_PASSWORD
② except: pass를 없애서 저장이 실패하면 오류가 보이게 하고, '지우지 마시오' 주석이 달린 time.sleep(1)을 지우기
③ 정책 숫자에 이름을 붙여 config.py 한 곳에 모으기
④ 복사한 두 분기(생일 쿠폰, 일반)를 함수 하나로 합치기
⑤ 등급별 적립률을 표 하나로 만들고, 등급은 Grade enum으로 다루기
⑥ 한글 발음 이름과 뜻이 안 보이는 이름을 영어로 바꾸고, 전역 변수 maechul 없애기
⑦ 계산과 출력 나누기
⑧ run()을 작은 함수로 나누기
크리스마스 이벤트 줄과 CAFE-5 버그는 정책이라 지우거나 고치지 말고 지금 동작 그대로 둬. 끝나면 단계별 커밋 목록과 바뀐 이름 표를 보여 줘.
```

## 실제 답

여덟 단계를 모두 끝냈고, 단계마다 `python3 cafe.py`를 다시 돌려 화면 출력과 `out/`가 `before/`와 같은지 확인한 뒤 커밋했어요. 실제 데이터에는 크리스마스 날짜나 포인트 한도 경우가 없어서, 원본(`49a73e5`)과 무작위 주문 25건을 비교하는 시험도 단계마다 돌렸고 차이는 없었어요. 이 시험은 `cafe.py`를 import하지 않고 따로 실행했어요.

## 단계별 커밋

| 커밋 | 내용 |
|---|---|
| `0fc85b4` 1단계 | 주석 처리한 옛 적립 코드, 디버그 print, `run2()`, `load_members()`, `reset_points()`, `ADMIN_PASSWORD`를 지웠어요. |
| `b046ec6` 2단계 | `except: pass`를 없앴어요. 읽기 전용 파일로 시험하니 `PermissionError`와 종료 코드 1이 나왔어요. `time.sleep(1)`과 `import time`도 지웠어요. |
| `23c03a9` 3단계 | 정책 숫자를 `config.py`에 모았어요. 영수증과 마감 보고의 숫자 문구도 이 값에서 만들어요. |
| `bcbdc34` 4단계 | 두 분기를 하나로 합쳤어요. |
| `0fab021` 5단계 | `config.POINT_RATES` 표로 적립률을 두고, 등급은 `Grade` enum으로만 다뤄요. |
| `6f8f46f` 6단계 | 이름을 영어로 바꾸고 전역 변수를 없앴어요. |
| `cc49bc5` 7단계 | 계산(`calculate_order`, `summarize`)과 출력(`format_receipt`, `format_report`)을 나눴어요. |
| `d700ba9` 8단계 | `run()`을 작은 함수로 나눴어요. |
| `e55bf58` 추가 | `CLAUDE.md`를 새 구조에 맞게 고쳤어요. |

## 바뀐 이름

| 전 | 후 |
|---|---|
| `hoewon_bulleogi` | `load_members` |
| `saveMembers` | `save_members` |
| `maechul` (전역) | `sales` (`summarize`가 합산) |
| `m` | `members` |
| `a` | `member` |
| `o` | `order` |
| `amt` | `amount` |
| `mid` | `member_id` |
| `tmp` | `balance` |
| `use` | `use_points` |
| `mon` | `month` |
| `gyeolje` | `paid` |
| `jeoklip` | `earned` |
| `jeoklip_hap` | `earned_total` |
| `gunsu` | `order_count` |
| `sseun_kupon` | `used_coupons` |
| `v` | `vip_count` |
| `f` / `r` / `w` / `rep` / `k` | `orders_file` 또는 `file` / `reader` / `writer` / `report` / `member_id` (`run()`의 VIP 세는 반복문) |

## 알아둘 점

- **크리스마스 줄과 CAFE-5**는 지금 동작 그대로 뒀어요. 크리스마스는 `config.CHRISTMAS_*`로 옮겼고, CAFE-5는 `calculate_order`의 `earn_base`에 주석을 달아 표시했어요. 이 주석은 이슈를 고치는 날 지우면 돼요.
- **`config.py`에 넣은 값**: 요청하신 정책 숫자 외에 최소 사용 포인트(1000)와 크리스마스 날짜·배수도 넣었어요.
- **등급 문자열**: 명부에 `일반`/`VIP`가 아닌 등급이 있으면, 전에는 일반 취급이었지만 이제는 읽을 때 `ValueError`가 나요.
- **추가로 한 것**: 모듈 끝을 `if __name__ == "__main__":`으로 바꿨어요. 이제 import만으로는 마감이 돌지 않아요. 단계 4에서 만든 합친 흐름은 단계 7에서 `calculate_order`로 옮겼고, `config.py`가 `grades.py`를 import하게 됐어요. 낡은 “만들다 말았음” 주석도 고쳤어요.
- **`web/`**: 읽기 전용이라 건드리지 않았어요. `App.tsx`에는 관리자 비밀번호가 아직 하드코딩되어 있어서, 따로 처리해야 해요.
- **`out/`**: 커밋하지 않았어요. `.gitignore`는 만들지 않았으니, 필요하면 알려 주세요.

## 참고

단계가 끝난 코드는 [after-refactor/](after-refactor/)에 있어요(화면 정리와 클래스까지 끝난 상태). 커밋 목록은 `_reference/claude-runs/cafe-git-log.txt`(강사용)에 있어요.
