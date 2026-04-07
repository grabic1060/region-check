## 인스타 계정 국가 확인 프로그램
- ### 제작 동기: 한국어를 쓰는 스팸/분탕 계정이 정말 한국에서 사용하는 계정인지 의문이 들었음.

# ⚠️경고
- ## 이 프로그램은 인스타그램의 약관을 위반할 수 있으며, 이로 인한 IP 차단 등의 제재는 사용자가 감수해야 합니다.
- ### 이 프로그램은 계정에 등록된 전화번호의 국가 코드를 추출하여 보여줄 뿐, 해당 계정의 사용자의 국적이 국가 코드와 일치함을 보장하지 않습니다.

## 사용법
- 난 코딩같은 건 모른다/아는데 귀찮다: releases 에서 exe 파일을 다운로드해서 실행
- 난 코딩을 할 줄 안다: 파이썬 필요
    ```shell
    git clone https://github.com/grabic1060/region-check.git
    cd region-check
    python -m venv .venv
    . .venv/bin/activate (windows의 경우 .venv\Scripts\activate)
    pip install -r requirements.txt
    python final.py
    ```

### 개발일지
- 03/28/2026 인스타 비밀번호 찾다가 전번에 국가코드 모자이크 안된거 보고 아이디어 떠올라서 CLI 기반으로 만듬.
- 03/31/2026 제미나이의 힘을 빌려 GUI 씌움. 앞으로도 프론트는 바이브코딩 예정
- 04/05/2026 깃헙 리포지토리 만들고 Actions 설정.
- 04/07/2026 브라우저 엔진 자동설치 기능 추가
