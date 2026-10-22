# 화면 코드를 TypeScript로, 컴포넌트 밖으로: 실제로 나온 답

[prompts.md](prompts.md)의 말을 그대로 보낸 실제 답이에요. 답은 고치지 않았어요.

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-10-19 |
| Claude Code | 2.1.302 |
| 모델 | Sonnet 5.5 |
| 모드 | Auto |
| 폴더 | 카페 포인트(리팩터링 다음) 사본 |
| 걸린 시간 | 24초 |

## 보낸 말

```text
web/src를 CLAUDE.md 규칙대로 정리해 줘. GradeBadge.jsx와 points.js를 TypeScript(.tsx, .ts)로 바꾸고, App.tsx 안에서 만든 HoewonCard 컴포넌트를 밖으로 빼서 MemberCard라는 영어 이름으로 바꿔 줘. 등급은 아무 문자열이 아니라 정해진 값만 받게 해 줘. 테스트용 console.log는 지워 줘. 화면 코드에 박힌 관리자 비밀번호는 브라우저에서 누구나 볼 수 있으니 관리자 버튼과 함께 빼 줘. 사장님이 키오스크 관리자 버튼은 안 쓴다고 했어. 빌드 설정이 없으니 읽어서 확인하고, 바꾼 이유를 짧게 알려 줘. 커밋해 줘.
```

## 실제 답

`web/src`를 정리하고 커밋했습니다. 빌드 설정이 없어서 실행하지 않았고, 파일을 읽어서 import 경로와 타입이 맞는지만 확인했습니다. `jsx`, `points.js`, `ADMIN`, `console` 문자열이 `web/`과 `CLAUDE.md`에 남아 있는지도 검색했고, 남은 건 없습니다.

- **TypeScript 전환:** `GradeBadge.jsx`는 `GradeBadge.tsx`로, `points.js`는 `points.ts`로 바꿨습니다. 화면 코드를 TS로 통일하라는 규칙을 따랐습니다.
- **등급 제한:** 새 `grades.ts`에 `Grade = "일반" | "VIP"`를 만들었습니다. 값은 `grades.py`의 `Grade` enum과 같습니다. 이전 `any` 때문에 아무 문자열이나 들어갔는데, 이제 이 두 값만 받습니다.
- **적립률:** `points.ts`의 `calcPoint`는 `{ 일반: 0.01, VIP: 0.03 }` 표를 씁니다. 이전엔 VIP가 아니면 모두 1%였는데, 지금은 등급이 두 값뿐이라 결과는 같습니다.
- **MemberCard 분리:** `App.tsx` 안에서 만들던 `HoewonCard`를 `MemberCard.tsx`로 빼고 이름을 바꿨습니다. 컴포넌트 안에서 컴포넌트를 만들지 않는 규칙 때문입니다. `Member` 타입은 `types.ts`로 옮겼고, 카드는 `m` 대신 `member`를 받습니다.
- **정리:** 테스트용 `console.log`를 지웠습니다.
- **관리자 비밀번호와 버튼:** `ADMIN_PASSWORD`와 관리자 버튼을 함께 뺐습니다. 비밀번호를 화면 코드에 두면 브라우저에서 누구나 볼 수 있어서입니다. 버튼은 사장님이 안 쓴다고 해서 같이 뺐습니다.
- **문서:** `web/README.md`의 파일 표와 `CLAUDE.md`의 web 설명을 새 파일 이름에 맞게 고쳤습니다.

`web/src/points.ts`의 적립률과 `grades.ts`의 등급 값은 여전히 Python 쪽과 따로 적혀 있습니다. 정책을 바꿀 때는 양쪽을 같이 확인해야 합니다.

`out/`은 원래대로 커밋하지 않았습니다.
