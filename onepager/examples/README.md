# 3교시 예시와 실제 결과

3교시 실습을 따라 할 때 보는 파일이에요. 결과 파일은 강사가 수업 전에 Claude Code로 실제로 돌려 본 그대로예요.

| 파일 | 무엇 |
| --- | --- |
| [prompts.md](prompts.md) | 실습 네 번의 순서와 보내는 문장 |
| [result-3/plan.md](result-3/plan.md) | 수업 뒤에 해 볼 것(최고 점수)을 Plan 모드로 보냈을 때 받은 계획 |
| [result-3/best-score.diff](result-3/best-score.diff) | 그 계획대로 고친 뒤 바뀐 줄 |
| [shots/](shots/) | 결과 화면이에요. 시작 화면, 클리어 화면, 최고 점수 화면이 있어요 |
| [result-1/](result-1/) | 예전 수업에서 한 문장으로 포스터, 음악, 엔딩을 맡겨 나온 게임이에요 |
| [code-tab/game/](code-tab/game/) | 실제로 나온 게임 `index.html`, 모션그래픽 `intro.html` |
| [code-tab/report/report.html](code-tab/report/report.html) | 실제로 나온 주간 판매 보고서 |
| [code-tab/answers.md](code-tab/answers.md) | 게임 프롬프트, 모션그래픽, 보고서를 실제로 맡긴 기록이에요. 발표의 "실제 결과"가 여기서 나왔어요. QR 문장의 주소는 연습용이에요 |
| [start/index.html](start/index.html) | 미디어 없이 시작하는 게임 파일이에요 |

막혔을 때 쓰는 견본 게임은 [game-kit/examples/sample-game](../../game-kit/examples/sample-game/index.html)이에요. 이 폴더의 파일을 내 폴더에 복사해서 실습을 대신하지 않아요. 내 폴더에서 Claude에게 맡겨 보고, 결과가 이상할 때 견주어 봐요.

`result-1`에는 음악 파일을 넣지 않았어요. 그 폴더에서 `py tools/make_music.py assets/music.wav`를 실행하면 다시 만들어져요. macOS는 `py` 대신 `python3`을 써요.
