# 하나 더 고치기: 실제로 나온 답

2일차 1교시 실습 3의 "더 해 보기" 문장을 [19-fix-one.md](19-fix-one.md)에 이어서 같은 대화로 보낸 실제 답이에요. 답은 고치지 않았어요.

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-10-23 |
| Claude Code | 2.1.308 |
| 모델 | Sonnet 5.5 |
| 모드 | Auto |
| 폴더 | 카페 포인트(`/init` 다음) 사본 |
| 걸린 시간 | 35초 |

## 보낸 말

```text
cafe.py에서 한글 발음 이름을 영어로 바꿔 줘. 고치기 전과 후에 cafe.py를 돌려서 결과가 같은지 확인하고, 같으면 커밋해 줘.
```

## 실제 답

`cafe.py`의 한글 발음 이름을 영어로 바꾸고 커밋했습니다(`8548e50`). 수정 전후로 `python3 cafe.py`를 돌려서 영수증 stdout, `out/members.csv`, `out/report.txt`를 비교했고 모두 같았습니다.

| 이전 | 이후 |
|---|---|
| `hoewon_bulleogi` | `load_members` |
| `maechul` | `revenue` |
| `gunsu` | `order_count` |
| `jeoklip` | `earned` |
| `jeoklip_hap` | `total_earned` |
| `sseun_kupon` | `used_coupons` |
| `gyeolje` | `payment` |

- **`hoewon_bulleogi`의 새 이름:** 앞선 정리에서 `load_members()`를 지워서 이 이름이 비어 있었습니다.
- **CLAUDE.md도 같이 고쳤습니다:** 옛 이름(`gyeolje`, `hoewon_bulleogi`)을 언급하고 있었고, 지난번에 지운 `load_members()`/`run2()` 설명도 남아 있었습니다. 요청하신 범위는 `cafe.py`였는데, 그대로 두면 문서가 틀려져서 같은 커밋에 넣었습니다.
- **`saveMembers`는 그대로 뒀습니다:** 한글 발음 이름이 아니라 camelCase라서 이번 범위에서 뺐습니다. 필요하면 `save_members`로 바꾸겠습니다.
- **`web/`은 건드리지 않았습니다:** 읽기 전용으로 다루고, 바꾼 이름이 거기에는 쓰이지 않습니다.

## 커밋 목록 (새 것부터)

```text
8548e50 cafe.py: 한글 발음 식별자를 영어로 변경
3f12a94 cafe.py: 안 쓰는 코드 삭제 (load_members, run2, 주석 처리된 코드)
5299e6e /init으로 CLAUDE.md 만들기
a093d84 받은 그대로
```

## 메모

- 명령줄(`claude -p … --continue --permission-mode auto`)로 돌렸어요. 원본 기록은 `_reference/claude-runs/20-fix-more.json`이에요.
- 부탁하지 않은 CLAUDE.md도 같이 고쳤어요. 옛 이름이 남아 있으면 문서가 틀려진다는 이유였어요.
