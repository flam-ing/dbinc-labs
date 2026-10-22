# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 개요

동네카페 포인트 적립 프로그램. 매일 마감 때 `python3 cafe.py`를 실행한다(저장소 루트에서 실행해야 `data/` 상대경로가 맞는다). 외부 의존성, 빌드, 린트, 테스트 설정은 없다.

- 입력: `data/orders.csv`(오늘 주문), `data/members.csv`(회원 명부)
- 출력: `out/members.csv`(갱신된 명부), `out/report.txt`(마감 보고), 영수증은 stdout. `out/`는 git에 올리지 않는 산출물이다.
- `cafe.py`는 모듈 끝에서 `run()`을 바로 호출한다. import만 해도 마감이 돌아가므로 함수 단위로 import해서 테스트할 수 없다.
- `issues/CAFE-*.md`에 요청된 정책 변경과 버그가 있다(적립률, VIP 기준, 생일 쿠폰, 새 등급, 적립 버그). 작업 전에 해당 이슈의 "같이 바꿀 것"을 확인한다.

## 구조와 주의점

**규칙이 여러 곳에 복제되어 있다.** 정책 하나를 바꾸면 아래를 모두 찾아서 맞춰야 한다.

- 적립률(일반 1% / VIP 3%): `cafe.py`의 `run()`에 생일 쿠폰 분기와 일반 분기 두 곳, 영수증 문구 "(일반 1%, VIP 3%)"가 두 곳, 마감 보고의 "적립률" 줄, `web/src/points.js`의 `calcPoint`.
- VIP 기준(누적 10만 원): `run()`의 두 분기(`>= 100000`), "VIP까지 N원 남았어요" 문구, 마감 보고 문구.
- 생일 쿠폰(3,000원, 5,000원 이상): 생일 분기 조건과 영수증 문구 `-3000`.
- 관리자 비밀번호: `cafe.py`와 `web/src/App.tsx`에 각각 하드코딩되어 있고 서로 같아야 한다.

**`run()`의 두 분기는 거의 같은 코드의 복사본이다.** 생일 쿠폰 분기는 적립을 쿠폰 차감 전 금액 `amt`로 계산하고, 일반 분기는 결제 금액 `gyeolje`로 계산한다(CAFE-5 버그의 원인). 한쪽만 고치면 어긋나므로 같이 확인한다.

**등급은 문자열과 enum이 섞여 있다.** `members.csv`의 등급은 `"일반"`/`"VIP"` 문자열이고, `run()`은 `a["grade"] == "VIP"` 같은 문자열 비교를 쓴다. `grades.py`의 `Grade` enum은 마감 보고의 VIP 인원 집계에서만 쓰인다. 등급 추가(CAFE-4)는 이 이중 구조를 감안해야 한다.

**죽은 코드/중복.** `hoewon_bulleogi()`(실제 사용)와 `load_members()`(미사용)는 같은 일을 한다. `run2()`는 미완성이며 호출되지 않는다. `reset_points()`는 모든 포인트를 0으로 만드는 관리자용 함수이므로 실행하지 않는다. `time.sleep(1)`에는 "지우지 마시오" 주석이 있다. 이유가 확인되지 않았으니 요청 없이 건드리지 않는다. 크리스마스(`2020-12-25`) 포인트 두 배 이벤트 분기도 남아 있다.

**`saveMembers` 실패는 조용히 무시된다**(`try/except: pass`). 출력이 안 나오면 이 부분을 의심한다.

## web/

키오스크 회원 화면(React, `App.tsx`/`GradeBadge.jsx`/`points.js`). `package.json`이 없어 빌드·실행할 수 없고 읽기 전용으로 취급한다(`web/README.md`). 포인트 계산 로직이 Python과 별도로 중복되어 있어 정책 변경 시 함께 확인한다.
