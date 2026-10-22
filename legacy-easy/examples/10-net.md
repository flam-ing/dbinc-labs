# 안전망: 고치기 전 결과 저장: 실제로 나온 답

[prompts.md](prompts.md)의 말을 그대로 보낸 실제 답이에요. 답은 고치지 않았어요.

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-10-19 |
| Claude Code | 2.1.302 |
| 모델 | Sonnet 5.5 |
| 모드 | Auto |
| 폴더 | 카페 포인트(규칙 넣은 다음) 사본 |
| 걸린 시간 | 20초 |

## 보낸 말

```text
리팩터링하기 전에 안전망을 만들어 줘. python3 cafe.py를 돌린 화면 출력을 before/screen.txt에, out 폴더를 before/out에 저장해 줘. cafe.py는 고치지 마. CLAUDE.md 변경과 before 폴더를 커밋해 줘.
```

## 실제 답

리팩터링 전에 비교할 기준 결과를 저장하고 커밋했습니다(`49a73e5`).

- **저장한 것:** `python3 cafe.py`를 한 번 실행해서 화면 출력을 `before/screen.txt`(47줄)에, `out/` 폴더를 `before/out/`(`members.csv`, `report.txt`)에 복사했습니다.
- **실행 결과:** 종료 코드는 0이고, 출력에 `Traceback`이나 `error`는 없습니다.
- **커밋한 것:** `CLAUDE.md` 변경과 `before/` 폴더입니다. `cafe.py`는 고치지 않았습니다.
- **`out/`:** 이전 `out/`은 이번 실행으로 덮어쓰였고, 지금도 untracked 상태로 남아 있습니다.

리팩터링 뒤에 다시 실행해서 `diff before/screen.txt <(python3 cafe.py)`와 `diff -r before/out out`으로 비교하면 됩니다.

`cafe.py`에 `time.sleep(1)`이 있어서 실행에 1초쯤 걸립니다.
