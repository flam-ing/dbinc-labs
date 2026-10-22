# 수업 뒤에 해 볼 것 · 테스트가 빌드를 막고, 훅이 Claude를 막아요

2일차 3교시 [프로젝트 지침, 스킬, TDD와 훅](../../docs/day2-rules.md)에서는 테스트 먼저와 훅을 설명으로만 봐요. 이 폴더는 수업 뒤에 직접 해 볼 자료예요. 우리 회사 규칙(`RULES.md`, 개인정보 가리기)을 테스트로 먼저 쓰고, 테스트가 실패하면 빌드가 막히는 것을 봐요. 그다음 같은 테스트를 훅으로 걸어서 Claude가 규칙을 깨지 못하게 해요.

이 폴더를 강의 저장소 밖으로 복사해서 써요. 보낼 문장은 [examples/prompts.md](examples/prompts.md)에 있어요.

## 폴더

| 폴더·파일 | 내용 |
| --- | --- |
| `RULES.md` | 우리 회사 규칙이에요. 휴대폰 번호와 주민등록번호를 가려요 |
| `api/` | 방명록 서버예요(Spring Boot, Gradle). 테스트가 실패하면 jar가 생기지 않아요 |
| `web/` | 방명록 화면이에요(React, Vite, Vitest). 테스트가 실패하면 `dist`가 생기지 않아요 |
| `py/` | JDK와 Node가 없는 PC에서 쓰는 파이썬 버전이에요 |
| `hooks/` | 테스트를 훅으로 거는 스크립트(`gate.py`)와 설정 예시예요 |
| `examples/` | 보내는 문장(`prompts.md`), CLAUDE.md 예시, 스킬 예시, 실제로 나온 결과(`01-red.md`~`05-hook.md`)예요 |

처음 상태에서 `PrivacyMasker.mask`(웹은 `mask`)는 글을 그대로 돌려줘요. 테스트를 먼저 쓰고 이 함수를 채워요.

## 실행하는 법

서버(api)는 JDK 17 이상이 있어야 해요. 처음 한 번은 Gradle과 라이브러리를 내려받느라 시간이 걸려요.

| 어디서 | 명령 |
| --- | --- |
| macOS 터미널, Git Bash | `./gradlew build` |
| Windows 명령 프롬프트(cmd) | `gradlew.bat build` |
| Windows PowerShell | `.\gradlew.bat build` |

`api` 폴더에서 쳐요. 성공하면 `api/build/libs/`에 jar가 생겨요. 테스트만 돌릴 때는 `build` 대신 `test`를 써요.

화면(web)은 Node 22.12 이상이 있어야 해요. `web` 폴더에서 `npm install`, `npm run build`를 한 줄씩 쳐요. `npm run build`는 테스트가 통과해야 빌드로 넘어가요.

파이썬(py)은 Python 3.10 이상이면 돼요. `py` 폴더에서 macOS는 `python3 -m unittest`, Windows는 `py -m unittest`를 쳐요.

## 훅 거는 법

Claude Code는 이 폴더 맨 위에서 열어요. `hooks/settings.api.json`(화면은 `settings.web.json`, 파이썬은 `settings.py.json`)을 `.claude/settings.json`으로 복사하고 새 세션을 열어요. Windows는 이름에 `.windows`가 붙은 파일을 써요. 테스트 폴더까지 잠그려면 `settings.api.protect-tests.json`을 써요.

이 폴더는 `node_modules`, `build`, `dist` 없이 나눠 줘요. 받은 사람이 위 명령으로 직접 설치하고 빌드해요.
