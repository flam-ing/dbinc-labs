---
name: run-check
description: 마감 후 python3 cafe.py를 돌리고 결과만 짧게 알려 준다. 파일은 고치지 않는다.
disable-model-invocation: true
allowed-tools: Bash(python3 cafe.py), Read
---

저장소 루트에서 `python3 cafe.py`를 한 번 실행하고 결과만 짧게 알려 준다.

1. 저장소 루트에서 `python3 cafe.py`를 실행한다(`data/` 상대경로 때문에 루트여야 한다).
2. 성공하면 한두 줄로 알린다. 영수증은 장수만, 마감 보고(`out/report.txt`)는 핵심 숫자만 전한다. 필요하면 `out/report.txt`를 읽어도 된다.
3. 실패하면 예외 종류와 메시지, 원인이 된 파일·줄만 알린다.

## 지킬 것

- 파일을 고치거나 만들지 않는다. 실행이 `out/`을 갱신하는 것은 괜찮다.
- 실패해도 코드를 고치거나 다시 시도하지 않는다. 원인만 알리고 멈춘다.
- 영수증 전문이나 긴 출력을 붙이지 않는다.
