  🛠️ 프로젝트 정보 및 협업 규칙 🛠️
  
  1. 개발 환경 정보
  - Python 버전: 3.12.5 
  
  2. 의존성 설치 명령어 (작업하기 전에 실행 필수)
    "pip install -r requirements.txt"
  
  3. requirements.txt 관리 규칙
  - 개인 작업 브랜치에서 개발 도중 외부 라이브러리를 설치 했을 경우 push 또는 develop 브랜치에 PR 하기 전에 꼭 "pip freeze > requirements.txt" 명령으로 버전 동기화 해야합니다! (버전 충돌 방지 목적)
  - PR 전에 UTF-8 인코딩인지 체크하기 (인코딩이 다른 형식이면 텍스트가 깨질 수 있음)

  
  4. 키 파일 관리 (※ 키 관련 보안 파일들은 slack 협업툴에 공유돼있는 구글 드라이브에서 관리합니다 ※ )
          
     - 개발환경 구축에 필요한 보완키 적용 경로 
        - 파일 이름 : secrets/vision-api-key.json &nbsp; 적용 경로 : secrets/ 
        - 파일 이름 : secrets/huggingface_token.txt &nbsp; 적용 경로 : colab_server/mediport_llm_colab.ipynb (Colab 환경에서 실행 시 huggingface 토큰 입력 부분에 직접 토큰을 입력해줘야 합니다) 
        - 파일 이름 : secrets/ngrok_token.txt &nbsp; 적용 경로 : colab_server/mediport_llm_colab.ipynb (Colab 환경에서 실행 시 ngrok 토큰 입력 부분에 직접 토큰을 입력해줘야 합니다)



