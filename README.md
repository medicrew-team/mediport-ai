  🛠️ 프로젝트 정보 및 협업 규칙 🛠️
  
  1. 개발 환경 정보
  - Python 버전: 3.12.5 
  
  2. 의존성 설치 명령어 (작업하기 전에 실행 필수)
    "pip install -r requirements.txt"
  
  3. requirements.txt 관리 규칙
  - 개인 작업 브랜치에서 개발 도중 외부 라이브러리를 설치 했을 경우 push 또는 develop 브랜치에 PR 하기 전에 꼭 "pip freeze > requirements.txt" 명령으로 버전 동기화 해야합니다! (버전 충돌 방지 목적)
  - PR 전에 UTF-8 인코딩인지 체크하기 (인코딩이 다른 형식이면 텍스트가 깨질 수 있음)

  
  4. 키 파일 관리
     - 키 관련 보안 파일은 https://drive.google.com/drive/folders/1OfOvF2gVPBus1PwJPDEPCjekq3Gaxu4b 에서 관리합니다
     - 키 파일별 적용 경로
       - vision-api-key.json (secrets)
       - huggingface_token.txt (colab_server/mediport_llm_colab.ipynb)
       - ngrok_token.txt (mediport/colab_server/mediport_llm_colab.ipynb)
