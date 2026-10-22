# ClaimReview

보험금 청구 자동 심사 배치예요. VB6 심사 프로그램(2004)에서 배치 부분만 C#으로 옮겼어요. 심사 화면은 아직 VB6를 써요.

- 만든 사람: 정민호 (2012-03)
- 개발 환경: Visual Studio 2010, .NET Framework 4.0
- 빌드: `ClaimReview.sln`을 열고 Release로 빌드해요.

## 실행

```
ClaimReview.exe <청구 CSV> <상품 CSV> <기준일 yyyyMMdd>
```

예: `ClaimReview.exe D:\CLAIM\IN\claim_20120601.csv D:\CLAIM\IN\product.csv 20120601`

작업 스케줄러(CLAIM_REVIEW)가 매일 07:30에 전날 접수분을 돌려요.

## 결과

결과는 `D:\CLAIM\OUT\result_<기준일>.csv`로 저장돼요. 보상팀이 심사 화면에서 이 파일을 올려요.

| 결과 | 뜻 |
| --- | --- |
| AUTO | 자동 승인 |
| PART | 부분 지급 |
| REJECT | 거절 |
| MANUAL | 사람 심사 |

사유 코드는 `modGlobal.cs` 맨 위 주석을 봐요.

## 주의

- 상품 CSV의 칸 순서를 바꾸지 마세요.
- 서버 지역 설정이 달라도 괜찮아요. 코드에서 고정했어요.
- 심사 기준은 위키(보상시스템 > 심사 기준)를 봐요.

---

2024-05 추가: 서버 교체 검토 때 .NET 8 SDK용 프로젝트 파일(`src/ClaimReview.csproj`)을 새로 만들었어요. .NET 8 SDK가 있으면 이 폴더에서 아래처럼 돌아가요. `data/`는 2013-03 운영 자료에서 개인 정보를 지우고 만든 검증용 자료예요.

```
dotnet run --project src -- data/claims.csv data/products.csv 20130304
```
