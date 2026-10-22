# 누리상사 레거시 시스템 10개

이 폴더에는 가상 회사 "누리상사"의 사내 시스템 10개가 들어 있어요. 레거시(오래돼서 손대기 조심스러운 기존 코드)를 읽고, 정리하고, 다른 구조나 다른 언어로 옮겨 보는 실습에 써요. 시스템마다 다른 팀이 다른 해에 만들어서 언어와 코드 스타일이 제각각이에요. 회사, 사람, 상품, 금액, 규정은 모두 지어낸 것이에요.

지금 수업 시간에는 이 폴더를 쓰지 않아요. 수업의 레거시 실습은 [`labs/legacy-easy/`](../legacy-easy/README.md)의 카페 포인트로 해요. 이 폴더는 수업 뒤에 더 큰 레거시로 같은 방법을 해 보고 싶을 때 써요.

## 시스템 목록

| 폴더 | 시스템 | 분야 | 언어·시대 |
| --- | --- | --- | --- |
| [`settle-cs`](settle-cs/) | 매장 일일 정산 배치 | 매장의 하루 주문을 모아 매장별 정산표를 만들어요. | C# .NET 2.0, 2006년 |
| [`claim-cs`](claim-cs/) | 보험금 청구 자동 심사 | 보험금 청구를 규칙에 따라 자동으로 심사해요. | C# .NET 4, 2012년 |
| [`room-java`](room-java/) | 회의실 예약 | 회의실 예약, 취소, 변경 요청을 처리하고 예약표를 만들어요. | Java 6 스타일, 2010년 |
| [`points-java`](points-java/) | 포인트 적립·소멸 | 온라인몰 회원 포인트의 적립, 사용, 소멸을 계산해요. | Java 8, 2016년 |
| [`payroll-java`](payroll-java/) | 급여 계산 | 직원 명단과 근태 기록으로 월 급여 명세를 만들어요. | Java 5, 8, 17 스타일이 섞인 코드, 2008~2021년 |
| [`inventory-py`](inventory-py/) | 재고·발주 | 창고 재고와 판매량으로 발주 파일을 만들어요. | Python 2에서 3으로 옮긴 코드, 2015년 |
| [`expense-py`](expense-py/) | 출장비 정산 | 출장 신청서와 환율표로 출장비를 정산해요. | Python 3, 2019년 |
| [`notice-js`](notice-js/) | 사내 공지 알림 봇 | 공지를 누구에게, 어떤 채널로, 언제 보낼지 정해요. | Node.js, 2016~2022년 |
| [`triage-js`](triage-js/) | 상담 티켓 분류 | 고객 문의를 분류하고 담당 팀과 처리 기한을 정해요. | 브라우저 JavaScript와 Node.js, 2018~2020년 |
| [`library-php`](library-php/) | 사내 도서 대여 | 사내 도서관의 대출, 반납, 연체를 관리해요. | PHP 5 스타일, 2011년 |

## 폴더 하나에 들어 있는 것

| 경로 | 내용 |
| --- | --- |
| `README.md` | 그 시절 담당자가 쓴 안내예요. 일부러 낡게 두어서 지금 코드와 맞지 않는 곳이 있어요. |
| 소스(`src/` 등) | 프로그램 코드예요. 외부 라이브러리 없이 그 언어의 표준 라이브러리만 써요. |
| `data/` | 손으로 만든 작은 입력 파일이에요. 무엇이 든 파일인지는 `wiki/`의 기획서 "입력 파일" 절에 있어요. |
| `wiki/` | 사내 위키 페이지예요. 그 시절 기획서(PRD) 한 쪽과, 운영하면서 정한 규칙과 사정이 적혀 있어요. |
| `issues/` | 이슈 트래커(버그와 할 일을 모아 두는 게시판)에 올라온 카드예요. |

폴더마다 기획서는 이 파일이에요. 처음 만들 때 쓴 문서라서, 그 뒤에 바뀐 규칙은 낡은 채로 남아 있어요.

| 폴더 | 기획서 |
| --- | --- |
| `settle-cs` | `wiki/settle-prd-2006.txt` |
| `claim-cs` | `wiki/claim-batch-prd-2012.md` |
| `room-java` | `wiki/room-booking-prd-2010.md` |
| `points-java` | `wiki/point-batch-prd-2016.md` |
| `payroll-java` | `wiki/급여-프로그램-기획서-2008.md` |
| `inventory-py` | `wiki/reorder-prd-2012.md` |
| `expense-py` | `wiki/expense-batch-prd-2019.md` |
| `notice-js` | `wiki/notice-bot-prd-2016.md` |
| `triage-js` | `wiki/triage-helper-prd-2018.md` |
| `library-php` | `wiki/사내-도서관-프로그램-기획서.md` |

## 고르는 법

- 익숙한 언어를 고르면 코드를 읽기 쉬워요. 옮겨 보고 싶은 언어가 있으면 그 기준으로 골라도 돼요.
- 원본을 직접 실행하려면 그 언어의 실행 환경이 PC에 있어야 해요. 아래 "필요한 프로그램"을 먼저 확인해요.
- 화면이 있는 것을 보고 싶으면 `triage-js`와 `library-php`를 골라요.

## 예시 파일

[`examples/`](examples/) 폴더에는 보낼 문장의 예시와, 강사가 실제로 돌려서 받은 결과 견본이 있어요. 코드를 읽고 묻는 예시는 [`examples/5교시/`](examples/5교시/README.md), 지식베이스 예시는 [`examples/번외2/`](examples/번외2/README.md), 고치기 예시는 검사 도구 옆 [`labs/legacy-checks/examples/`](../legacy-checks/examples/README.md)에 있어요. 폴더 이름은 예전 수업 순서를 따른 것이에요. 이 폴더들은 내 레거시 폴더에 복사하지 않고 따로 열어서 봐요. 복사하면 Claude가 견본까지 읽어서 내 답에 섞여요.

## 고치기 전에 동작을 기록하는 법

폴더에는 검사 도구가 없어요. 코드를 고치기 전에 Claude에게 "고치기 전에 지금 동작을 기록해 두자"고 해요. 그러면 Claude가 `data/`의 입력으로 원본을 돌려서 결과를 저장하고, 고친 뒤 다시 돌려 비교하는 방법을 만들어 줘요. 이것을 안전망이라고 불러요.

원본을 돌릴 실행 환경이 없거나 시간이 모자라면, 미리 만든 검사 도구를 꺼내 써요. `labs/legacy-checks/<폴더>/`에 레거시마다 `expected/`(원본을 실제로 실행해서 남긴 기록)와 `verify.py`(같은 입력으로 내 프로그램을 돌려 기록과 비교하는 스크립트)가 있어요. 둘 다 내 레거시 폴더에 복사해 넣고 그 폴더에서 `python3 verify.py`를 실행해요. Windows는 `py verify.py`로 쳐요. 레거시가 Java인데 검사 도구가 Python인 이유는, 코드를 읽지 않고 실행 결과만 비교해서 언어와 상관이 없기 때문이에요. 자세한 쓰는 법은 [`labs/legacy-checks/README.md`](../legacy-checks/README.md)에 있어요.

## 필요한 프로그램

| 언어 | 폴더 | 원본을 실행할 때 필요한 것 | 확인 명령 |
| --- | --- | --- | --- |
| Java | `room-java`, `points-java`, `payroll-java` | JDK 17 이상(`javac`, `java`) | `javac -version` |
| C# | `settle-cs`, `claim-cs` | .NET 8 SDK | `dotnet --list-sdks` |
| JavaScript | `notice-js`, `triage-js` | Node.js 18 이상 | `node --version` |
| PHP | `library-php` | PHP 8 이상 | `php -v` |
| Python | `inventory-py`, `expense-py`, 그리고 미리 만든 검사 도구(`verify.py`) | Python 3.9 이상 | `python3 --version`(Windows는 `py --version`) |

- 실행 환경이 없으면 원본을 돌려 볼 수 없어요. 그래도 미리 만든 검사 도구의 `expected/`에 원본의 실행 결과가 기록되어 있어요. 다른 언어로 옮긴 프로그램은 그 언어의 실행 환경만 있으면 `--cmd`로 검사할 수 있어요.
