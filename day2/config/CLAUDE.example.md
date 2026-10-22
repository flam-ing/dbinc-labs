# DB Inc 교육용 Day 2 프로젝트

실제 사내 시스템과 고객 데이터는 없습니다. fixtures/events.json만 사용합니다.

- 집계 계약: SPEC.md. 연동 계약: integration/CONTRACT.md.
- tests/test_contract.py와 fixture의 예상 값을 구현에 맞춰 바꾸지 않습니다.
- TDD 구현은 work/tdd/report.py, 디버깅 구현은 work/debug/report.py입니다. 연동 작업의 집계 함수로는 work/tdd/report.py를 씁니다.
- 조회 담당은 work/integration/query.py, 가공 담당은 process.py, 보고서 담당은 report.py만 수정합니다.
- 병렬 담당자는 같은 파일에 동시에 쓰지 않습니다. Git 변경은 통합 담당만 합니다.
- 결과 보고에는 실행한 명령과 실제 출력을 함께 적습니다. 실행하지 않은 검사는 구분합니다.
- 테스트: python -m pytest tests --impl work/tdd/report.py -q
- 통합: python tools/run_report.py --impl work/tdd/report.py --modules work/integration
