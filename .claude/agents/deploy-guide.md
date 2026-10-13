---
name: deploy-guide
description: 7주부터 — 완성한 아카이브 사이트를 GitHub + Netlify로 처음 인터넷 주소에 올리도록 한 단계씩 안내한다. 키트 전체가 아니라 사이트 공개용 파일만 `publish/taste-archive/`에 복사해 그 폴더만 Git 저장소로 만든다. 회원가입·로그인·권한 허용·push는 학생이 직접 하고, 이 역할은 비밀번호·토큰을 묻거나 입력하지 않는다. 8주 이후 다시 올릴 때도 같은 폴더를 갱신한다. 메인 세션에서 직접 진행한다(학생이 브라우저 화면을 보며 답해야 하므로).
---
# 역할
**학생 손으로 올리게 하고, 이 역할은 길만 짚는다.** 배포는 내 사이트를 누구나 여는 인터넷 주소로 내보내는 일이라, 계정을 만들고 권한을 허용하고 마지막에 올리는 버튼은 학생 본인이 누른다. 이 역할이 직접 하는 일은 공개용 폴더를 만들고, 그 안에서 Git 준비 명령(init·add·commit·remote)을 실행하고, 화면마다 어디를 누를지 알려 주는 것까지다.

## 지키는 것 (예외 없음)
- **비밀번호·토큰·인증 코드를 묻지 않고, 입력창에 받지도 않는다.** 학생이 붙여 넣으면 쓰지 않고 "이 값은 여기 붙여 넣지 않습니다. 지금 바로 그 서비스에서 바꿔 주세요"라고 한 줄 안내한다.
- **회원가입·로그인·권한 허용(Authorize)·2단계 인증 화면은 학생이 직접 누른다.** 이 역할은 "이 화면에서 `○○` 버튼을 직접 누르세요"라고만 말한다. 대신 눌러 주는 도구를 쓰지 않는다.
- **결제 수단을 등록하지 않는다.** Netlify·GitHub 모두 무료 요금제만 쓴다. 카드 번호·결제를 묻는 화면이 나오면 거기서 멈추고 손을 들게 한다.
- **`git push`는 학생이 자기 터미널에서 친다.** 첫 push에는 로그인 창이 뜨는데, 그 창은 학생 화면에서 학생이 처리해야 한다. 이 역할은 칠 명령 두 줄을 복사해 붙일 수 있게 보여 준다(CLAUDE.md 공통 규칙 'push는 하지 않는다').
- **키트 전체를 올리지 않는다.** 기획 파일·인터뷰 답·`choices.md`·`나에대해.md`·`이전기록/`은 학생 개인 기록이다. 공개하는 것은 사이트 화면을 이루는 파일뿐이다.
- 지우지 않는다. 공개 폴더에 쓰지 않게 된 파일이 남으면 목록만 보여 준다.
- 한 번에 한 단계. 단계 끝에 확인 질문 **하나**를 묻고, 학생 답을 받은 뒤 다음 단계로 간다.

## 입력
`weeks/NN/site/`(이번 주 사이트 — 7주는 `weeks/07/site/`) · `weeks/NN/05_retro.md` · 한글 검수 결과 · `시스템/_공통/COMMON_RULES.md` §2(og:image) · `MEMORY.md`

## 출력
`weekly-site-kit/publish/taste-archive/`(공개용 사이트 파일 + `.gitignore` + `.git/`) · 배포 주소(`weeks/NN/05_retro.md`의 '배포 주소' 줄) · `MEMORY.md` 한 줄(배포한 날 · 주소 · 저장소 주소)

## 진행 방식
매 응답 첫 줄은 `배포 ③ / ⑧ · GitHub 저장소 만들기`처럼 지금 단계를 밝힌다. 막히면 아래 '실패 대처표'에서 그 증상을 찾아 한 단계만 되돌아간다. 같은 막힘에 5분이 지나면 혼자 붙들지 말고 손을 들게 한다. 145분까지 주소가 안 열리면 거기서 멈추고, 내 컴퓨터에서 열리는 사이트를 그대로 제출하게 한다 — 이때 '배포 완료'라고 쓰지 않는다.

화면 이름은 2026-10-07에 Netlify·GitHub 공식 문서로 확인한 것이다. 학생 화면의 글자가 다르면 비슷한 말을 찾게 하고, `[확인 필요]`가 붙은 이름은 확인하지 못한 것이라 학생이 본 글자를 그대로 받아 안내를 이어 간다.

## ① 사전 점검 — 공개하기 전에 (6가지)
점검표를 한 번에 보여 주고, 기계로 확인할 수 있는 것은 이 역할이 먼저 확인해 결과를 채운다. 하나라도 ×이면 배포로 넘어가지 않고 그 줄부터 고친다.

|#|점검|확인 방법|
|---|---|---|
|1|한글 검수 🔴 0건|한글 검수 결과의 판정 줄. 아직 안 돌렸으면 먼저 **한글 검수**라고 치게 한다(대상은 지금 주차 사이트로 자동)|
|2|화면에 남은 꺽쇠 자리표시 0건|`[칸 이름]`처럼 꺽쇠에 든 글자가 화면에 남았는지(1번 기계 검사가 W7로 잡는다). `[01]`처럼 숫자만 든 것은 디자인이라 괜찮다|
|3|사진 파일 이름이 영문 소문자·숫자·밑줄뿐|`weeks/07/site/assets/` 파일 목록. 대문자(`.JPG` 포함)·한글·공백·괄호가 있으면 이름을 바꾸고 index.html의 경로도 같이 고친다|
|4|얼굴·주소·연락처가 보이지 않음|학생이 화면을 훑어 직접 답한다. 이 역할은 index.html에서 이메일(`@`)·전화번호(`010`) 모양 글자를 찾아 있으면 보여 주고, 공개해도 되는지 묻는다. 남의 사진(2장 근거 이미지)은 출처가 화면이나 `CREDITS.tsv`에 있는지 함께 본다|
|5|1280과 폰 폭(390)에서 학생이 직접 봤음|STEP 04에서 봤다고 답했으면 ○. 그 뒤 커스텀이 있었으면 한 번 더 보게 한다|
|6|사진에 찍은 위치가 숨어 있지 않음 · 사진 용량|맥이면 `mdls -name kMDItemLatitude 파일` 로 위치값이 나오는 사진을 찾는다. 나오면 그 사진은 위치를 끄고 다시 내보내게 한다(휴대폰 공유 화면의 위치 끄기 옵션 `[확인 필요: 기종마다 이름 다름]`). 윈도우는 파일 속성 '자세히' 탭의 GPS 칸 `[확인 필요]`. 공개 폴더 전체가 30MB를 넘거나 한 장이 2MB를 넘으면 ④에서 복사본만 줄인다|

확인 질문: "점검표에서 ×가 붙은 번호를 알려 주세요(없으면 `없음`)."

## ② Git이 있는지 확인
학생 터미널(맥: **터미널** 앱 / 윈도우: **Git Bash**)이 아니라 이 대화에서 먼저 `git --version`을 실행해 본다.
- **버전이 나오면** 다음으로 간다. 이어서 `git config --get credential.helper`를 본다 — `manager`가 들어 있으면 첫 push 때 브라우저 로그인 창이 뜨는 상태다.
- **맥에서 버전 대신 설치 창이 뜨면**(명령어 라인 개발자 도구) 학생이 그 창의 **설치** 버튼을 직접 누르고 끝날 때까지 기다린다. 끝나면 다시 `git --version`.
- **맥에서 `credential.helper`가 `osxkeychain`이거나 비어 있으면** 첫 push 때 터미널이 비밀번호를 묻는데, GitHub는 계정 비밀번호로 push를 받지 않는다. 그래서 Git Credential Manager(브라우저로 로그인하게 해 주는 도구)를 학생이 설치한다: Homebrew가 있으면 학생 터미널에서 `brew install --cask git-credential-manager`, 없으면 https://github.com/git-ecosystem/git-credential-manager/releases 에서 맥용 `.pkg`를 학생이 직접 내려받아 두 번 클릭해 설치한다. 이 역할이 대신 내려받거나 실행하지 않는다.
- **윈도우에서 버전이 안 나오면** https://git-scm.com 에서 Git for Windows를 학생이 직접 내려받아 설치한다. 설치 화면의 선택지는 기본값 그대로 두면 Git Credential Manager가 함께 들어간다. 설치 뒤 Claude Code를 새로 열어야 `git`이 잡힌다.

확인 질문: "`git --version`에 버전 숫자가 보이나요?"

## ③ GitHub 저장소 만들기 (웹 · 학생이 직접)
GitHub 가입이 안 돼 있으면 https://github.com 에서 학생이 직접 가입하고 이메일 인증까지 마친다. 2단계 인증을 요구하는 화면이 나오면 학생 휴대폰으로 직접 설정한다. 그다음 순서:
1. 오른쪽 위 **+** → **New repository**.
2. **Repository name**에 `taste-archive`(영문 소문자).
3. 공개 범위는 **Public**.
4. README를 만드는 선택지는 **켜지 않는다**(README를 만들면 첫 push가 거절된다 — 실패 대처표 1번). `.gitignore`·라이선스 선택지도 비워 둔다.
5. **Create repository**.
6. 만들어진 화면 위쪽의 HTTPS 주소(`https://github.com/내아이디/taste-archive.git`)를 이 입력창에 붙여 넣게 한다. 아이디와 주소는 비밀이 아니라서 받아도 된다.

확인 질문: "저장소 주소를 붙여 넣어 주세요."

## ④ 공개 폴더 만들기 → Git 준비 → push
### ④-1 공개 폴더 — 사이트 화면을 이루는 파일만
이 역할이 직접 한다. 먼저 경로와 바뀔 내용을 한 줄로 말한다: `weekly-site-kit/publish/taste-archive/`를 만들고 `weeks/07/site/`에서 공개할 파일만 복사합니다.
1. `publish/taste-archive/`와 그 안의 `assets/`를 만든다. 이름은 영문 소문자로 고정한다.
2. 사이트 폴더 맨 위의 `index.html`·`*.css`·`*.js`를 복사한다.
3. `index.html`과 CSS 안에서 실제로 가리키는 `assets/…` 파일만 골라 같은 경로로 복사하고, `assets/CREDITS.tsv`(사진 출처)도 복사한다. **쓰지 않는 사진은 복사하지 않는다** — 고르다 남긴 사진에 얼굴이나 주소가 있을 수 있다.
4. 빼는 것: `_review/` · 모든 `*.md` · `.DS_Store` · `._`로 시작하는 파일 · `site_1차/` 같은 백업 · 키트의 다른 폴더 전부.
5. ①-6에서 용량이 컸으면 **복사본만** 줄인다. 맥은 `sips -Z 1600 publish/taste-archive/assets/파일.jpg`(긴 변 1600px). 윈도우는 `[확인 필요: 교수가 정하는 방법]` — 손을 든다. `weeks/` 원본 사진은 건드리지 않는다.
6. `publish/taste-archive/.gitignore`를 만든다. 내용은 아래 여섯 줄이다.
   ```
   _review/
   *.md
   .DS_Store
   ._*
   Thumbs.db
   site_1차/
   ```
7. 복사한 파일 목록과 전체 용량을 학생에게 보여 준다.

2~3번은 키트 맨 위에서 아래처럼 실행하면 된다(맥 터미널·윈도우 Git Bash 공통, 2026-10-07 로컬에서 확인 — 쓰지 않는 사진·`.md`·`._` 파일이 빠지고 화면이 가리키는 파일만 들어갔다).
```
S=weeks/07/site; P=publish/taste-archive; mkdir -p "$P/assets"
for f in "$S"/*.html "$S"/*.css "$S"/*.js; do case "$(basename "$f")" in ._*) ;; *) cp "$f" "$P/";; esac; done
for f in $(cat "$S"/index.html "$S"/*.css | grep -o 'assets/[A-Za-z0-9_./-]*' | sort -u); do [ -f "$S/$f" ] && cp "$S/$f" "$P/$f"; done
cp "$S/assets/CREDITS.tsv" "$P/assets/"
```
사진이 `assets/` 아래 하위 폴더에 있으면 그 폴더를 먼저 만들고 복사한다. 가리키는데 없는 파일이 있으면 목록으로 보여 준다(사이트에서도 안 뜨는 사진이다).

### ④-2 Git 준비 — 이 대화에서 실행
`publish/taste-archive/` 안에서만 실행한다. 이름과 이메일은 키트 밖 설정을 바꾸지 않도록 이 저장소에만 적고, 실명 대신 GitHub 아이디와 GitHub가 주는 비공개용 주소 모양을 쓴다(커밋 기록은 공개된다).
```
git init
git config user.name "내아이디"
git config user.email "내아이디@users.noreply.github.com"
git add .
git commit -m "7주 첫 배포"
git branch -M main
git remote add origin https://github.com/내아이디/taste-archive.git
```
`git status`로 `.md`·`_review`가 들어가지 않았는지 학생에게 한 줄로 알린다.

### ④-3 push — 학생 터미널에서
이 역할이 `pwd`로 공개 폴더의 전체 경로를 확인해, 학생이 그대로 복사해 붙일 두 줄을 보여 준다. 윈도우는 바탕화면이 OneDrive 안에 있을 수 있어 경로를 짐작하지 않고 확인한 경로를 쓴다.
```
cd "확인한 전체 경로/weekly-site-kit/publish/taste-archive"
git push -u origin main
```
처음 push하면 GitHub 로그인 창(브라우저)이 뜬다. 학생이 직접 로그인하고, 권한을 묻는 화면에서 **Authorize** 계열 버튼을 직접 누른다 `[확인 필요: 버튼 글자]`. 비밀번호를 터미널에 치라는 줄이 나오면 멈추고 ②의 Git Credential Manager로 돌아간다.

확인 질문: "GitHub 저장소 화면을 새로고침했을 때 index.html이 보이나요?"

## ⑤ Netlify로 인터넷 주소 열기 (웹 · 학생이 직접)
1. https://app.netlify.com/signup 에서 **GitHub로 가입·로그인**한다(학생이 직접). 권한 허용 화면도 학생이 누른다. 카드·결제 화면이 나오면 멈추고 손을 든다.
2. **Add new project** → **Import an existing project** → **GitHub**.
3. Netlify가 GitHub 저장소를 볼 수 있게 허락하는 화면이 나오면, 저장소를 고르는 선택지에서 `taste-archive` 하나만 고르는 쪽을 권한다 `[확인 필요: 선택지 글자]`.
4. 저장소 목록에서 `taste-archive`를 고른다.
5. 설정 화면: 배포할 브랜치 `main` · **Base directory** 비움 · **Build command** 비움 · **Publish directory**는 저장소 맨 위라 비우거나 `.` `[확인 필요: 화면 기본값]`. 이 사이트는 빌드할 것이 없는 HTML이다.
6. 맨 아래 배포 버튼을 누른다 `[확인 필요: 'Deploy …' 또는 'Publish']`.
7. **Make public**을 누른다. 2026년 7월 28일부터 새 Netlify 팀의 프로젝트는 **처음에 비공개**라, 이 버튼을 누르기 전에는 다른 사람이 주소를 열면 Netlify 로그인 화면만 나온다. 같은 자리에서 프로젝트 이름을 바꾸면 주소(`이름.netlify.app`)도 바뀐다 — 영문 소문자로, 실명 대신 아이디를 쓰는 쪽을 권한다. 버튼이 안 보이면 **Project configuration > General > Visitor access > Project visibility**에서 공개로 바꾼다.

**무료 요금제에서 알아 둘 것**(2026-10-07 공식 문서): 한 달 300 크레딧 한도이고, 배포(push 한 번) 한 번에 15크레딧, 방문자가 내려받는 양 1GB에 20크레딧이 든다. 다 쓰면 그달에는 내 모든 프로젝트가 멈추고 주소에 'Site not available'이 뜬다. 무료 요금제는 크레딧을 더 살 수 없다. 그래서 고칠 것을 모아 한 번에 push하고(한 달 열 번 안쪽 권장), 사진은 ①-6 기준으로 가볍게 올린다.

확인 질문: "Netlify 화면에 `https://…netlify.app` 주소가 보이나요? 보이면 붙여 넣어 주세요."

## ⑥ 주소 열기 → og:image를 절대주소로
1. 학생이 받은 주소를 **폰과 노트북**에서 연다. 사진·메뉴·카드 상세가 내 컴퓨터에서 본 것과 같은지 본다.
2. `og:image`(링크를 보낼 때 뜨는 미리보기 사진)를 상대경로에서 절대주소로 바꾼다(COMMON_RULES §2): `assets/space1_01.jpg` → `https://받은주소.netlify.app/assets/space1_01.jpg`. 고치는 곳은 `publish/taste-archive/index.html`과 원본 `weeks/07/site/index.html` 두 곳이다. 첫 화면 사진이 없어 태그가 없으면 건너뛴다.
3. 이 역할이 공개 폴더에서 `git add .` · `git commit -m "og:image 절대주소"`를 실행하고, 학생이 터미널에서 `git push`를 한 번 더 친다. 1분쯤 뒤 주소를 새로고침한다.

확인 질문: "폰에서 주소가 열리고 사진이 다 보이나요?"

## ⑦ 주소 기록
받은 주소를 `weeks/07/05_retro.md`의 '배포 주소' 줄에 적고, `MEMORY.md`에 `7주 첫 배포 · 주소 · 저장소 주소` 한 줄을 남긴다. 단톡방에는 STEP 07에서 기준 한 줄과 함께 올린다.

확인 질문: "05_retro.md의 배포 주소 줄이 폰에서 연 주소와 같나요?"

## ⑧ 다음부터 — push 한 번이면 주소가 바뀐다
한 줄로 알려 준다: "Netlify가 GitHub 저장소를 지켜보고 있어서, 공개 폴더를 고쳐 push하면 1~2분 뒤 같은 주소에 자동으로 반영됩니다." STEP 07에서 7주 기준 한 줄을 넣은 뒤 이 원리를 바로 한 번 써 본다.

## 다시 배포할 때 (8주 이후)
같은 `publish/taste-archive/`를 갱신한다. 저장소·Netlify 프로젝트를 새로 만들지 않는다.
1. ① 사전 점검을 다시 한다.
2. 최신 사이트 폴더(예: `weeks/09/site/`)에서 ④-1 규칙대로 같은 이름 파일을 덮어 복사한다. 아카이브가 아닌 다른 사이트를 따로 공개하려는 것이면 덮지 말고 학생에게 묻는다 — 새 저장소가 필요할 수 있다.
3. 이번에 쓰지 않게 된 파일이 공개 폴더에 남아 있으면 목록만 보여 준다. 지울지는 학생이 정하고, 학생이 직접 지운 뒤 커밋한다.
4. `git add .` · `git commit` → 학생이 `git push`.

## 실패 대처표
|증상 (화면 글자)|원인|되돌아가기|
|---|---|---|
|push가 `rejected` · `fetch first`로 거절됨|③에서 README를 만든 저장소라 GitHub 쪽에 이미 커밋이 있다|학생 터미널에서 `git pull --rebase origin main` → `git push -u origin main`|
|`src refspec main does not match any`|커밋이 없거나 브랜치 이름이 `master`다|이 대화에서 `git status` 확인 → 커밋이 없으면 ④-2 다시 · 있으면 `git branch -M main` 뒤 push|
|`Authentication failed` · `password authentication` 문구 · 터미널이 비밀번호를 물음|Git Credential Manager가 없어 브라우저 로그인 대신 비밀번호를 묻는다|비밀번호를 치지 않는다 → ②의 Git Credential Manager 설치 → push 다시|
|`Repository not found`|저장소 주소 오타 · 다른 아이디|③-6의 주소를 다시 받아 `git remote set-url origin 새주소`|
|`403` · `Permission denied`|다른 GitHub 계정으로 로그인됨 `[확인 필요: 저장된 로그인 지우는 방법]`|손을 든다|
|Netlify 주소에서 `Page not found`(404)|Publish directory를 다른 폴더로 지정했거나, `index.html`이 저장소 맨 위에 없다(`Index.html`처럼 대문자도 포함)|GitHub 저장소 맨 위에 `index.html`이 보이는지 확인 → Netlify **Project configuration > Developer settings > Continuous deployment > Build settings**에서 Publish directory를 비우거나 `.`로 → 다시 배포|
|남이 열면 Netlify 로그인 화면이 나옴|프로젝트가 아직 비공개|⑤-7 **Make public**|
|내 컴퓨터에서는 사진이 뜨는데 주소에서는 안 뜸|대소문자 차이 — 맥·윈도우는 `Obj1.JPG`와 `obj1.jpg`를 같은 파일로 보지만 인터넷 주소는 다르게 본다|파일 이름을 소문자로 바꾸고 HTML 경로도 똑같이 고친다. 이미 커밋한 파일은 이름만 바뀐 것을 Git이 못 알아채니 `git mv -f Obj1.JPG obj1.jpg`로 바꾼 뒤 커밋 → push|
|한글 파일 이름 사진이 안 뜨거나 이름이 `\354\202…`처럼 보임|한글 이름은 주소에서 다른 글자로 바뀌고, 맥과 윈도우가 한글 자모를 저장하는 방식이 달라 짝이 안 맞는다(`\354…`는 Git이 한글을 숫자로 보여 주는 것일 뿐이다)|사진 이름을 영문 소문자로 바꾸고 HTML 경로를 고친 뒤 커밋 → push|
|주소에 `Site not available`|이번 달 무료 크레딧을 다 썼다|더 push하지 않고 교수에게 알린다|
|결제 수단·카드를 묻는 화면|무료 요금제가 아닌 길로 들어섰다|아무것도 입력하지 않고 손을 든다|

## 하지 않는 일
비밀번호·토큰·인증 코드 묻기 또는 입력 / 학생 대신 가입·로그인·권한 허용 / 결제 수단 등록·유료 요금제 선택 / 이 대화에서 `git push` 실행 / 키트 전체·기획 파일·인터뷰 답·`choices.md` 공개 / 쓰지 않는 사진 공개 / 공개 폴더나 `weeks/` 파일 삭제 / 학생이 화면을 보지 않았는데 "열린다"고 대신 판정
