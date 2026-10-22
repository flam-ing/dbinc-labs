# 문서도 같이 고치기: 실제로 나온 답

[prompts.md](prompts.md)의 말을 그대로 보낸 실제 답이에요. 답은 고치지 않았어요.

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-10-19 |
| Claude Code | 2.1.302 |
| 모델 | Sonnet 5.5 |
| 모드 | Auto |
| 폴더 | 카페 포인트(CAFE-4 다음) 사본 |
| 걸린 시간 | 53초 |

## 보낸 말

```text
지금까지 바뀐 것에 맞춰 문서를 고쳐 줘. README의 쓰는 법과 규칙, CLAUDE.md의 구조와 '규칙이 흩어져 있는 곳' 절, 바뀐 이름 표(docs/renames.md), 짧은 변경 기록(CHANGELOG.md)이에요. 코드는 고치지 마. 커밋해 줘.
```

## 실제 답

문서 네 곳을 고치고 한 번에 커밋했어요(`8ea1ef7`). 코드는 건드리지 않았어요.

- **README.md**: 쓰는 법에 실행 위치, 정책 숫자가 `config.py`에 있다는 것, 두 문서(`docs/renames.md`, `CHANGELOG.md`)의 위치를 더했어요. 규칙은 날짜별 적립률 표(일반 1→2%, 골드 5%)로 바꿨어요.
- **CLAUDE.md**:
  - 구조 절에 `RATE_SCHEDULE`의 등급 순서가 곧 등급 순서라는 점을 한 줄 더했어요.
  - '규칙이 흩어져 있는 곳' 절은 원래 없어서 새로 만들었어요. 규칙마다 어느 파일에 있는지 표로 정리했어요. `web/`에 따로 복사된 값도 표시했어요.
- **docs/renames.md** (새 파일): 옛 이름과 새 이름 표예요. `hoewon_bulleogi`→`load_members`, `maechul`→`sales`, `VIP_THRESHOLD`→`GRADE_THRESHOLDS` 같은 것과 지운 것(`run2`, `reset_points`, `ADMIN_PASSWORD`), `web/src`의 파일 이름 변경을 담았어요.
- **CHANGELOG.md** (새 파일): 2026-10-19 한 날짜에 정책(CAFE-1, CAFE-4), 정리 작업, 아직 안 한 이슈(CAFE-2, 3, 5)를 적었어요.

- **날짜 기준**: 변경 기록은 커밋이 모두 2026-10-19라서 그 날짜 하나로 묶었어요.
- **옛 이름 표**: 일부 옛 이름은 diff에서 읽어 정리했어요. 예를 들어 `sseun_kupon`은 `LoyaltyPolicy`가 기억하는 쓴 쿠폰으로 옮겨졌다고 적었어요.
- **README 규칙**: "한 번 오른 등급은 내려가지 않아요"는 `upgraded_grade`의 동작을 보고 넣었어요. 크리스마스 두 배 한 줄도 같은 이유로 넣었어요.

`out/`은 원래 git에 올리지 않는 폴더라 그대로 뒀어요.

## 참고

고친 문서와 코드 전체는 [final/](final/)에 있어요.
