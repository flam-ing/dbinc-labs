# 회의실 예약 (RoomBatch)

총무팀 회의실 예약 요청을 처리하는 프로그램이에요. 2010년 2월에 전산팀 정태윤이 만들었어요.

※ 교육용 가상 자료예요. 회사, 사람, 규정은 모두 지어낸 것이에요.

## 빌드

    javac -d classes src/com/nuri/room/*.java

2012-06 김도현 덧붙임: 소스 파일을 MS949에서 UTF-8로 바꿨어요. 컴파일할 때 `-encoding UTF-8`을 붙여 주세요.

## 실행

    java -cp classes;lib/ojdbc14.jar com.nuri.room.RoomBatch D:\room\req\today.txt

DB 접속 정보는 `conf/db.properties`에 있어요.

## 요청 파일

한 줄에 요청 하나예요. 칸은 쉼표로 나눠요.

    RSV,요청시각,사번,이름,회의실,날짜,시작,종료,인원,제목
    CXL,요청시각,사번,예약번호

요청시각은 yyyyMMddHHmm, 날짜는 yyyyMMdd, 시작과 종료는 HHmm으로 적어요.

## 규칙

- 30분 단위로만 예약해요.
- 한 번에 2시간까지 예약해요. 임원은 제한이 없어요.
- 대회의실은 12시 30분부터 13시 30분까지 청소 시간이라 예약을 막아요.
- 본인 예약만 취소할 수 있어요.

## 문의

전산팀 정태윤(내선 2231)
