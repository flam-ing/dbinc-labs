# 2교시에 보내는 말

`<꺾쇠>` 안이 내 것으로 바꿀 곳이에요. "실제로 보냄"이 붙은 말은 강사가 수업 전에 보내 본 그대로이고, 답은 [answers.md](answers.md)에 있어요.

## 실습 ① 설치와 로그인 확인 (터미널)

macOS·Linux 터미널에서 설치해요.

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Windows PowerShell에서 설치해요.

```powershell
irm https://claude.ai/install.ps1 | iex
```

새 터미널 창에서 확인하고 로그인해요.

```bash
claude --version
claude
```

설치 명령은 공식 문서(https://code.claude.com/docs/en/setup)에 있는 그대로예요. 강사 맥에서는 `2.1.302 (Claude Code)`가 나왔어요.

## 실습 ② 아티팩트 하나 (Chat 탭)

```text
우리 팀 <점심 메뉴 투표판>을 아티팩트로 만들어 줘. 메뉴 다섯 개, 누르면 표가 하나씩 올라가게 해 줘.
```

채팅이라 미리 돌려 보지 못했어요. 창이 안 뜨고 코드만 나오면 "아티팩트로 보여 줘"라고 한 번 더 보내요.

## 실습 ③ Code 탭 첫 요청 (dbinc-notes 폴더)

Manual 모드로 보내요. 실제로 보냄.

```text
이 폴더에 뭐가 있어?
```

모드를 Plan으로 바꾼 뒤, 그다음 Accept edits로 바꾼 뒤 같은 말을 보내요. 둘 다 실제로 보냄.

```text
orders.csv에서 <매장별> 주문 수와 금액 합계를 표로 만들어 store-total.md에 저장해 줘.
```

`<매장별>` 자리에 "날짜별", "상품별"을 넣어도 돼요(따로 돌려 보지 않았어요).

## 실습 ④ / 명령 세 개

입력창에 하나씩 쳐요. 보기만 하고 바꾸지 않아요.

```text
/context
/model
/memory
```

## 실습 ⑤ 같은 질문을 터미널로

```bash
cd ~/Desktop/dbinc-notes
claude
```

`claude`가 열리면 실습 ③과 같은 말을 보내요. 실제로 보냄(터미널 `claude -p`).

```text
이 폴더에 뭐가 있어?
```

끝나면 `/exit`로 나와요.

## 실습 ⑥ GitHub CLI 연결하기 (터미널)

3교시에 게임을 GitHub Pages에 올릴 때 쓰는 GitHub CLI(`gh`)를 설치해요. 개인 GitHub 계정이 필요해요.

Windows PowerShell에서 설치해요.

```powershell
winget install --id GitHub.cli
```

macOS 터미널에서 설치해요.

```bash
brew install gh
```

`brew: command not found`가 나오면 Mac에 Homebrew가 없는 거예요. Code 탭에 아래의 "GitHub CLI 설치하고 로그인 도와줘."를 보내거나 손을 들어요.

Windows는 설치한 뒤 새 터미널 창을 열어요. 새 창에서 로그인하고 확인해요.

```bash
gh auth login
gh auth status
```

`gh auth login`에서는 GitHub.com, HTTPS, 브라우저 로그인을 골라요. 화면에 나온 코드를 브라우저에 넣고 승인해요. `gh auth status`에 `Logged in`이 보이면 돼요.

명령을 직접 치기 어려우면 Code 탭에 이 말을 보내요. 미리 돌려 보지 못했어요. 로그인 코드를 브라우저에 넣는 일은 내가 해요.

```text
GitHub CLI 설치하고 로그인 도와줘.
```
