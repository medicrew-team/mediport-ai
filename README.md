  🛠️ 프로젝트 정보 및 협업 규칙 🛠️
  
  1. 개발 환경 정보
  - Python 버전: 3.12.5 
  
  2. 의존성 설치 명령어 (작업하기 전에 실행 필수)
    "pip install -r requirements.txt"
  
  3. requirements.txt 관리 규칙
  - 개인 작업 브랜치에서 개발 도중 외부 라이브러리를 설치 했을 경우 push 또는 develop 브랜치에 PR 하기 전에 꼭 "pip freeze > requirements.txt" 명령으로 버전 동기화 해야합니다! (버전 충돌 방지 목적)
  
  4. Git 협업 규칙 (GitFlow)
        - 기본 브랜치 : 'develop'
        - 모든 작업은 'develop' 브랜치에서 새로운 작업 브랜치를 따서 진행
        - 작업 완료 후 Pull Request(PR)는 'develop' 브랜치로 보내기
    
  4-1. 브랜치 네이밍 규칙 (작업번호 중복XX)
        - 형식 : "타입/작업내용(#작업번호)" ex) feat/fastapi-서버-초기-구성(#2)
        - Pull Request시에 title은 브랜치 명이랑 동일하게 작성

  4-2. 커밋 메시지 규칙
        - 형식 : "타입 : 작업내용" ex) fix : 인코딩 문제로 인해 requirements.txt를 UTF-8로 변경
