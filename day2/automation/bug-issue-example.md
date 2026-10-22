# 실습용 버그 이슈 예시

`make_repo.py`로 만든 실습 저장소에 올릴 이슈 예시예요. GitHub의 **Issues** 탭에서 **New issue**를 누르고 **버그 신고** 템플릿을 고르면 같은 칸이 나와요. 내가 직접 재현한 결과로 칸을 채우고, 아래 예시는 비교용으로 봐요.

## 제목

```text
[버그] billing 오류율이 66.67%가 아니라 25.0%로 나와요
```

## 본문

````markdown
## 입력

fixtures/events.json(8건)으로 재현 스크립트를 실행했어요.

```bash
python tools/reproduce.py
```

공백이 붙은 서비스 이름도 확인했어요.

```bash
python -c "import json, report; print(report.summarize(json.load(open('fixtures/events.json')), service=' billing ')['total'])"
```

## 기대

- SPEC.md: "error_count: HTTP 상태가 500 이상인 이벤트 수", "error_rate_pct: round(error_count / total * 100, 2)"
- billing은 3건 중 2건(500, 503)이 오류라서 (오류 수, 오류율, 느린 요청 수)가 (2, 66.67, 2)여야 해요.
- catalog는 404가 오류가 아니고 500ms는 느린 요청이라서 (0, 0.0, 1)이어야 해요.
- 없는 서비스는 SPEC.md "필터 결과가 0건이면 수량은 0, 비율과 평균은 0.0"에 따라 (0, 0.0, 0)이어야 해요.
- SPEC.md "필터가 문자열이면 앞뒤 공백을 제거해"에 따라 service=" billing "도 billing 3건을 찾아야 해요.

## 실제

```text
ERROR 없는 서비스: ZeroDivisionError: division by zero
FAIL 오류 비율의 분모: actual=(2, 25.0, 1) expected=(2, 66.67, 2)
FAIL 404와 500ms 경계: actual=(1, 12.5, 0) expected=(0, 0.0, 1)
재현 실패 사례: 3/3
```

공백이 붙은 이름으로 부르면 `ZeroDivisionError: division by zero`가 나요.
````

## 이슈를 만든 뒤

- 루틴 방식: 오른쪽 **Labels**에서 `auto-fix`를 붙여요. 라벨이 없으면 먼저 **Issues** 탭의 **Labels**에서 **New label**을 눌러 만들어요.
- GitHub Actions 방식: 이슈 댓글에 아래 글을 남겨요.

```text
@claude 이 이슈를 CLAUDE.md 규칙대로 재현하고 고쳐줘. 고칠 때마다 python tools/reproduce.py와 python -m pytest -q를 다시 돌리고, 회귀 테스트를 tests/test_regression.py에 더해줘.
```
