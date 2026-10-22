# 토끼 당근 피하기 (밝은 8비트)

`index.html`을 더블클릭하면 바로 열려요. 설치도 서버도 필요 없어요.

## 폴더

| 파일 | 내용 |
| --- | --- |
| `index.html` | 게임 전체 (엔딩 영상 애니메이션도 이 안에서 그려져요) |
| `assets/poster.png` | 시작 화면 포스터 |
| `assets/music.wav` | 배경 음악 (12.8초 반복) |
| `qr.png` | 배포 주소로 가는 QR |
| `tools/` | 위 파일들을 다시 만드는 파이썬 스크립트 (배포에는 필요 없어요) |
| `.nojekyll` | GitHub Pages가 파일을 그대로 올리게 해요 |

## 배포 (정적 호스팅이면 어디든 돼요)

- **GitHub Pages**: 저장소를 GitHub에 올리고 Settings → Pages → Branch `main` / `/ (root)`.
  주소는 `https://<아이디>.github.io/<저장소 이름>/` 예요.
- **Netlify Drop** 등: 이 폴더를 통째로 끌어다 놓으면 돼요.

## 주소가 정해지면 QR 다시 만들기

    python3 tools/make_qr.py https://실제주소/ qr.png

## 점검

    python3 tools/check.py

## 에셋 다시 만들기

    python3 tools/make_poster.py assets/poster.png
    python3 tools/make_music.py assets/music.wav
