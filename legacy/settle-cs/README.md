# DailySettle

매장 일일 정산 배치예요. 매일 06:00에 작업 스케줄러(DAILY_SETTLE)가 실행해요. 주문 CSV와 상품 CSV를 읽어서 매장별 정산표, 재고 부족 목록, ERP 업로드용 INSERT 문을 화면(표준 출력)에 찍어요.

- 만든 사람: 박 대리 (2006-03)
- 개발 환경: Visual Studio 2005, .NET Framework 2.0
- 빌드: Visual Studio 2005에서 `src/DailySettle.cs`를 열고 Release로 빌드해요.

## 실행

```
DailySettle.exe <주문 CSV> <상품 CSV> <영업일 yyyy-MM-dd>
```

예: `DailySettle.exe D:\pos\orders_20060403.csv D:\pos\products.csv 2006-04-03`

실행 기록은 `D:\batch\settle\log\`에 날짜별로 남아요.

## 알아 둘 것

- 22시 이후 주문은 다음 날 매출로 들어가요.
- 매장 코드표는 다음 버전에서 설정 파일(`stores.ini`)로 뺄 예정이에요.
- 정산 규칙과 매장 코드는 위키(정산 > 일일 정산 배치)를 봐요.

---

2024-05 추가 (Java 전환 검토, SETTLE-31)

- .NET 8 SDK로 원본을 돌려 보려고 `src/DailySettle.csproj`를 새로 만들었어요. .NET 8 SDK가 있으면 이 폴더에서 `dotnet run --project src -- data/orders.csv data/products.csv 2006-04-03`처럼 돌아가요.
- `data/`는 검증용 자료예요. `data/many/`는 `python3 make_big.py --orders 2000 --products 50 --seed 7 --dir data/many`로 만든 주문 2000줄이에요. 성능을 잴 큰 파일은 `python3 make_big.py --dir big`으로 만들어요(커밋하지 않아요).
