# 누리몰 포인트 배치

누리몰 멤버십 포인트의 적립, 사용, 소멸을 계산하는 배치예요. 매일 새벽 3시에 돌아요. 2016년 4월에 커머스개발팀 한동욱이 만들었어요.

※ 교육용 가상 자료예요. 회사, 사람, 정책은 모두 지어낸 것이에요.

## 필요한 것

- Java 8

## 빌드

    javac -encoding UTF-8 -d bin src\com\nuri\mall\point\*.java

## 실행

    run.bat

`run.bat`은 아래 명령을 실행해요.

    java -cp bin com.nuri.mall.point.PointBatch

입력 파일(`transactions.csv`, `members.csv`)은 `C:\points\data\`에 두어요. 알림 메일 파일은 `C:\points\data\outbox\`에 생겨요.

## 규칙 요약

- 일반 회원은 결제 금액의 1%, VIP는 2%를 적립해요.
- 적립일로부터 1년이 지나면 소멸해요.
- 오래된 포인트부터 먼저 써요.
- 소멸 7일 전에 안내 메일을 보내요.
- 포인트는 마이너스가 되지 않아요(2016-12 장애 뒤).

## 담당

커머스개발팀 한동욱
