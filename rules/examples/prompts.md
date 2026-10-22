# 수업 뒤에 해 볼 것 · 지침 비교와 스킬 세 개

3교시 수업 문장은 [prompts-30min.md](prompts-30min.md)에 있어요. 이 파일은 수업 뒤에 방명록으로 더 해 볼 문장이에요. `⟨ ⟩` 안은 내 것으로 바꿔도 돼요. 보낼 때 `⟨ ⟩` 표시는 지워요.

강사 결과는 Claude Code 2.1.301과 2.1.302(Sonnet 5.5)로 돌린 결과예요. 내 결과는 조금씩 달라요.

## 1. 지침이 있을 때와 없을 때 비교

강의 저장소 폴더(`~/dbinc-ai-course`)로 Code 탭 세션을 열고 준비를 맡겨요. 사본은 다른 프로젝트 밖에 둬요. 위 폴더의 `CLAUDE.md`가 섞이지 않게 하려는 거예요.

```text
labs/guestbook을 ⟨바탕화면⟩의 compare-without-rules와 compare-with-rules 두 곳에 복사해 줘.
compare-with-rules에만 labs/rules/CLAUDE.md를 넣어 줘.
두 폴더 모두 git 저장소로 만들고 "시작 상태"로 첫 커밋을 해 줘.
마지막으로 두 폴더에서 smoke_test.py를 실행해서 결과를 보여 줘.
```

두 폴더 모두 `Ran 3 tests`와 `OK`가 보이면 돼요. 그다음 두 폴더를 각각 + New session으로 열고(모드 Manual), 아래 문장을 똑같이 넣어요.

```text
방명록 제목을 ‘DB Inc 실습 방명록’으로 바꾸고, 잘못된 입력에 대한 오류 안내를 사용자가 알아보기 쉽게 정리해줘. 기존 등록·조회 동작은 유지해줘.
```

강사 결과에서는 지침 없는 사본이 `<title>`과 `<h1>`을 둘 다 바꿨어요. 지침 있는 사본은 보고 순서는 지켰지만 400 응답에 `field` 키를 더했어요. 같은 요청도 할 때마다 결과가 달라요.

비교에서 본 문제는 규칙 한 줄로 바꿔요.

```text
CLAUDE.md의 ⟨코딩 컨벤션⟩ 묶음에 "⟨- 제목을 바꿀 때는 <title>과 <h1>을 함께 바꾼다.⟩"를 한 줄 더해 줘. 다른 줄은 고치지 마.
```

강사 결과에서는 5초 만에 그 한 줄만 더했어요. 더한 뒤에는 새 세션을 열어야 반영돼요.

## 2. 스킬 세 개 써 보기

비교가 끝난 사본에서 보내요. `.claude` 폴더에 쓰는 일이라 승인 카드가 떠요.

```text
~/dbinc-ai-course/labs/rules/.claude 폴더를 이 폴더에 그대로 복사해 줘. 복사한 뒤 .claude/skills 안의 폴더 이름을 보여 줘.
```

새 세션을 열고 하나씩 보내요.

```text
/check-change ⟨제목과 오류 안내 변경 뒤 입력 검증을 확인⟩
/readme-for-people
/polish-ko ⟨방명록 오류 안내 수정 완료. smoke_test 통과함 → 화면 확인은 미실시.⟩
```

- `/check-change`는 파일을 고치지 않고 검토만 해요. 강사 결과는 [check-change-report.md](made-by-claude/check-change-report.md)에 있어요.
- `/readme-for-people`은 `README.people.md`를 새로 만들어요. 강사 결과는 [README.people.md](made-by-claude/README.people.md)에 있어요.
- `/polish-ko`는 글을 쉬운 해요체로 다듬어요. 파일은 고치지 않아요.

## 3. 내 스킬 만들기

```text
⟨check-change⟩ 스킬을 참고해서, ⟨방명록 검사를 돌리고 결과만 짧게 보고하는⟩ ⟨run-checks⟩ 스킬을 .claude/skills에 만들어 줘. 내가 /⟨run-checks⟩로 부를 때만 돌고, 파일은 고치지 않는 스킬이야.
```

Claude가 쓴 스킬은 [made-by-claude/run-checks/SKILL.md](made-by-claude/run-checks/SKILL.md)에 있어요. 강사 결과에서는 `/run-checks`가 검사를 한 번 돌리고 결과 두 줄만 답했어요. 사람이 쓴 예시는 [run-checks/SKILL.md](run-checks/SKILL.md)예요.
