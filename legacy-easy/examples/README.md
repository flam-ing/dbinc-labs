# 쉬운 레거시 예시

카페 포인트 실습에서 보내는 말과, 강사가 사본에서 실제로 받은 답이에요. Claude가 한 말과 만든 파일은 고치지 않았어요. 이 폴더는 내 레거시 폴더에 복사하지 않고 따로 열어서 봐요.

| 파일 | 무엇 |
| --- | --- |
| [`prompts.md`](prompts.md) | 1일차 5교시와 2일차 1교시에 보내는 말 |
| [`kb-prompts.md`](kb-prompts.md) | 2일차 2교시에 보내는 말 |

## 수업에서 보는 답

| 시간 | 실습 | 실제 답 |
| --- | --- | --- |
| 1일차 5교시 | 실습 1: 폴더에 넣고 돌려 보기 | [`02-run.md`](02-run.md) |
| 1일차 5교시 | 실습 2: `/init`으로 CLAUDE.md 만들기 | [`06-init.md`](06-init.md), 만든 CLAUDE.md는 [`claude-md-init.md`](claude-md-init.md) |
| 1일차 5교시 | 실습 3: 내 눈으로 먼저 찾기 | [`00-smells.md`](00-smells.md) |
| 1일차 5교시 | 실습 4: 규칙 표 받고 한 줄 직접 확인 | [`03-rules.md`](03-rules.md), 더 해 보기는 [`01-flow.md`](01-flow.md) |
| 1일차 5교시 | 실습 5: 정책 카드 하나, 고칠 곳 세기 | [`07-count-cafe1.md`](07-count-cafe1.md) |
| 1일차 5교시 | 실습 6: 위키 자료 읽히기 | [`06-wiki.md`](06-wiki.md) |
| 2일차 1교시 | 실습 1: 이상한 곳 찾기 | [`00-smells.md`](00-smells.md) |
| 2일차 1교시 | 실습 2: Plan 모드로 계획 받기 | [`17-plan.md`](17-plan.md) |
| 2일차 1교시 | 실습 3: 하나 골라 고치고 비교하기 | [`19-fix-one.md`](19-fix-one.md), 더 해 보기는 [`20-fix-more.md`](20-fix-more.md) |
| 2일차 1교시 | 발표 설명 장면: 결과 저장해 두기, 한 번에 하나씩 고치고 커밋 | [`10-net.md`](10-net.md), [`18-do.md`](18-do.md) |
| 2일차 2교시 | 실습 1: 지식베이스 만들기 | [`23-kb.md`](23-kb.md) |
| 2일차 2교시 | 실습 2: 새 자료 넣기 | [`24-wiki.md`](24-wiki.md) |
| 2일차 2교시 | 실습 3: 옵시디언으로 열기 | [`25-links.md`](25-links.md) |
| 2일차 2교시 | 실습 1 더 해 보기: 온톨로지 | [`50-ontology.md`](50-ontology.md) |
| 2일차 2교시 | 같은 질문, 다른 답(강사 화면) | [`51-ask-before-after.md`](51-ask-before-after.md) |
| 2일차 2교시 | 재미로 해 보기: 카톡 대화 | [`21-kakao-kb.md`](21-kakao-kb.md), [`22-kakao-update.md`](22-kakao-update.md) |

## 수업 뒤에 볼 답

수업에서는 쓰지 않지만, 수업 뒤에 더 해 볼 때 견주어 봐요. 보낸 말은 [`prompts.md`](prompts.md)의 "수업 뒤에 해 볼 것"에 있어요.

| 파일 | 무엇 |
| --- | --- |
| `08-sort.md` ~ `16-docs.md` | 끝까지 리팩토링하기. 나누기, 규칙 넣기, 안전망, 여덟 단계, 화면 정리, 클래스, 정책 두 개, 문서. 안전망 `10-net.md`는 2일차 1교시 발표에서도 봐요 |
| `claude-md-rules.md` | 코드 규칙 절을 더한 CLAUDE.md |
| `after-refactor/` | 여덟 단계와 화면 정리, 클래스까지 끝난 코드 |
| `final/` | 정책 두 개와 문서까지 끝난 코드. CLAUDE.md는 `claude-md-final.md`예요 |
| `04-ham-rules.md`, `05-ham-run.md`, `07-count-ham1.md` | HAMURABI 규칙 표, 1년 돌리기, 정책 카드 |

CLAUDE.md 견본은 모두 `claude-md-*.md`로 이름을 바꿔 두었어요. 이름이 CLAUDE.md이면 교안 저장소를 연 Claude가 이 파일을 자기 안내문으로 읽어 버려요.
