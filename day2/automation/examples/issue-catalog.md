# 이슈 하나 더: catalog 예시

`../bug-issue-example.md`(billing)를 쓴 다음, 다른 증상으로 이슈를 하나 더 쓸 때 보는 예시예요. 버그 신고 템플릿의 세 칸을 그대로 채웠어요. 숫자는 실습 저장소에서 `python3 tools/reproduce.py`를 실제로 돌린 출력이에요.

루틴은 번호가 가장 작은 이슈 하나만 처리해요. 이 이슈는 다음 실행이나 Run now를 한 번 더 눌렀을 때 처리돼요. 첫 이슈의 PR이 이 버그까지 고쳤다면, 루틴이 "재현되지 않음"으로 댓글만 남기고 끝날 수도 있어요. 그것도 맞는 동작이에요.

## 제목

```text
[버그] catalog에서 404가 오류로 세지고 500ms 요청은 느린 요청에서 빠져요
```

## 본문

````markdown
## 입력

fixtures/events.json(8건)으로 재현 스크립트를 실행했어요. catalog는 3건(200/90ms, 404/499ms, 200/500ms)이에요.

```bash
python tools/reproduce.py
```

## 기대

- SPEC.md: "error_count: HTTP 상태가 500 이상인 이벤트 수", "slow_count: 응답 시간이 slow_ms 이상인 이벤트 수"
- 404는 오류가 아니고 500ms는 느린 요청이라서 (오류 수, 오류율, 느린 요청 수)가 (0, 0.0, 1)이어야 해요.

## 실제

```text
FAIL 404와 500ms 경계: actual=(1, 12.5, 0) expected=(0, 0.0, 1)
```
````

## 이슈를 만든 뒤

- 루틴 방식: 오른쪽 **Labels**에서 `auto-fix`를 붙여요.
- GitHub Actions 방식: 댓글에 `@claude`로 불러요. 문장은 `prompts.md` 5번에 있어요.
