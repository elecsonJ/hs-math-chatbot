# 팀 협업 가이드 (GitHub Collaboration Guide)

이 문서는 `math_bot_proto` 프로젝트를 팀원들과 함께 개발하기 위한 깃헙 사용법 및 워크플로우를 설명합니다.

## 1. 초기 연동 (프로젝트 생성자만 수행)

이미 로컬 깃 저장소는 초기화되었습니다. 이제 GitHub 원격 저장소와 연결해야 합니다.

1.  [GitHub](https://github.com/new)에 접속하여 **New Repository**를 생성합니다.
    *   Repository Name: `math_bot_proto` (또는 원하는 이름)
    *   **공개/비공개** 설정 선택 (Private 권장)
    *   *README, .gitignore, License 추가 옵션은 모두 체크 해제* (이미 로컬에 있으므로)
2.  생성 완료 후 나오는 화면에서 **"…or push an existing repository from the command line"** 부분의 코드를 복사하여 터미널에 붙여넣습니다.

    ```bash
    git remote add origin https://github.com/[YOUR_USERNAME]/math_bot_proto.git
    git branch -M main
    git push -u origin main
    ```

## 2. 팀원 개발 환경 세팅 (팀원들이 수행)

팀원들은 프로젝트를 자신의 컴퓨터로 가져와야 합니다.

```bash
# 프로젝트 클론 (다운로드)
git clone https://github.com/[YOUR_USERNAME]/math_bot_proto.git
cd math_bot_proto

# 가상환경 생성 및 패키지 설치
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. 협업 워크플로우 (Feature Branch Strategy)

메인 코드(`main`)를 안전하게 지키고 서로의 작업이 꼬이지 않게 하기 위해 **브랜치(Branch)** 전략을 사용합니다.

### 1단계: 작업 시작 전 최신화
작업을 시작하기 전에 항상 원격 저장소의 변경사항을 가져옵니다.
```bash
git checkout main
git pull origin main
```

### 2단계: 브랜치 생성
내가 할 작업에 맞는 이름으로 브랜치를 만듭니다.
*   형식: `feature/[작업내용]` 또는 `fix/[버그수정]`
*   예시: `feature/add_login_ui`, `fix/typo_correction`

```bash
git checkout -b feature/search_logic
```

### 3단계: 작업 및 커밋
코드를 수정하고 저장합니다.
```bash
git add .
git commit -m "검색 로직 개선: 상세 필터 추가"
```

### 4단계: 푸시 (Push)
내 브랜치를 깃헙에 올립니다.
```bash
git push origin feature/search_logic
```

### 5단계: 풀 리퀘스트 (Pull Request, PR)
1.  GitHub 저장소 페이지로 이동합니다.
2.  "Compare & pull request" 버튼을 클릭합니다.
3.  어떤 변경을 했는지 작성하고 `Create pull request`를 누릅니다.
4.  팀원들에게 리뷰를 요청하거나, 이상이 없으면 `Merge` 버튼을 눌러 `main`에 합칩니다.

## 4. 자주 발생하는 문제 해결

*   **충돌(Conflict) 발생 시**:
    *   내가 수정한 파일과 다른 팀원이 수정한 파일의 같은 부분이 겹쳤을 때 발생합니다.
    *   VS Code 등 에디터에서 충돌된 부분을 확인하고 올바른 코드로 정리한 뒤 다시 `git add`, `git commit` 하면 됩니다.
