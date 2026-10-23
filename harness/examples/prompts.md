# 번외 예시 문장 · 모델과 하네스

그대로 보내도 되고, `⟨ ⟩` 안을 내 것으로 바꿔 보내도 돼요. 보낼 때 `⟨ ⟩` 표시는 지워요. 결과는 사람마다 조금씩 달라요.

## 실습 1 · 같은 질문 두 모델에 보내기 (6분)

1. Code 탭에서 **+ New session**을 누르고 `labs/harness/compare` 폴더를 골라요. 모드는 **Manual**이에요.
2. 모델 메뉴에서 모델 A(예: Sonnet 5.5)를 고르고 아래 문장을 그대로 보내요.
3. 다시 **+ New session**으로 같은 폴더를 열어요. 모델 B(예: Opus 5.5)로 같은 문장을 보내요.

```text
changes.md를 읽고 배포 전에 확인할 것을 다섯 줄로 정리해 줘.
```

모델 메뉴가 회색이면 회사 설정으로 막힌 거예요. 그때는 같은 모델에서 effort를 Low와 High로 바꿔서 비교해요.

**실제 결과**: 교안을 만들 때는 아래의 조금 더 긴 문장으로 돌렸어요.

```text
changes.md를 읽고 배포 전에 확인할 항목을 다섯 줄 안으로 정리해 줘. 줄마다 근거가 된 변경 ID를 붙여 줘. 파일은 고치지 마.
```

Sonnet 5.5는 10.5초, Opus 5.5는 12.8초가 걸렸어요. 둘 다 서로 부딪히는 변경 두 곳을 찾았어요. 주문 상태 값을 소문자로 바꾸면 결제완료 필터가 0건이 되고, 야간 매출 리포트가 0원이 돼요. API 값으로 바꾸면 Sonnet은 $0.043, Opus는 $0.082였어요. 원문은 [made-by-claude/01-sonnet.md](made-by-claude/01-sonnet.md)와 [made-by-claude/02-opus.md](made-by-claude/02-opus.md)예요.

## 실습 2 · 내 폴더의 하네스 부품 찾기 (6분)

오전 3교시에 쓴 `~/legacy/cafe-points`를 **Manual** 세션으로 열고 보내요. 없으면 강의 저장소의 `labs/rules`를 열어요. 파일은 고치지 않아요.

```text
이 폴더에 있는 하네스 부품(CLAUDE.md, 스킬, 훅, 권한, MCP)을 찾아 표로 정리해 줘. 없는 것은 '없음'으로 적고, 파일은 고치지 마.
```

`ls`나 `find` 승인 카드가 뜨면 목록만 보는 명령이라 **Allow once**를 눌러도 돼요. 빈 지도는 [harness-parts.md](harness-parts.md)예요.

**실제 결과**: 교안을 만들 때는 방명록에 `labs/rules`의 `CLAUDE.md`와 `.claude`를 넣은 폴더에서 아래의 조금 더 긴 문장으로 돌렸어요.

```text
이 폴더에 있는 하네스 부품을 찾아 표로 정리해 줘. 칸은 부품, 파일, 하는 일 한 줄, 언제 작동하는지예요. CLAUDE.md, .claude/skills, .claude/commands, .claude/settings*.json(훅과 권한), .claude/agents, .mcp.json을 보고 없는 것은 '없음'으로 적어 줘. 표 아래에 지금 네가 쓸 수 있는 도구 이름을 한 줄로 적어 줘. 파일은 고치지 마.
```

21초가 걸렸어요. 지침 1개, 스킬 4개, 명령 1개를 찾았고 훅, 권한, 서브에이전트, MCP는 "없음"이었어요. 원문은 [made-by-claude/03-parts.md](made-by-claude/03-parts.md)예요.

## 실습 3 · 다른 하네스 README 읽기 (6분)

1. Code 탭에서 **+ New session**을 누르고 `labs/harness/compare` 폴더를 골라요. 모드는 **Manual**이에요. 파일은 고치지 않아요.
2. 아래 문장을 그대로 보내요.
3. 웹 페이지를 읽는 승인 카드가 뜨면 주소가 `github.com`인지 보고 **Allow once**를 눌러요.

```text
https://github.com/can1357/oh-my-pi 의 README를 읽고, 이 하네스가 모델 바깥에서 더해 주는 것 세 가지를 쉬운 말로 한 줄씩 적어 줘. README에 없는 내용은 지어내지 마.
```

세 줄이 나오면 그 가운데 모델을 바꾼 것이 있는지, 모두 모델 바깥의 도구와 장치인지 봐요. 더 해 보려면 주소만 `https://github.com/code-yeongyu/oh-my-openagent`로 바꿔 같은 문장을 보내고 두 답을 비교해요. 회사망에서 github.com이 막히면 강사 화면으로 같이 봐요.

**실제 결과**: 교안을 만들 때 같은 문장을 Sonnet 5.5로 한 번 보냈어요. 19.8초가 걸렸어요. 세 줄은 일을 나눠 맡기는 서브에이전트, 해시로 줄을 가리키는 편집과 LSP·디버거, 규칙에 걸리면 끊고 다시 하게 하는 감시 장치와 검토 모델이었어요. 원문은 [made-by-claude/06-omp-readme.md](made-by-claude/06-omp-readme.md)예요.
