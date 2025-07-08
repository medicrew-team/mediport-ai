  🛠️ 프로젝트 정보 및 협업 규칙 🛠️
  
  1. 개발 환경 정보
  - Python 버전: 3.12.5 
  
  2. 의존성 설치 명령어 (작업하기 전에 실행 필수)
    "pip install -r requirements.txt"
  
  3. requirements.txt 관리 규칙
  - 개인 작업 브랜치에서 개발 도중 외부 라이브러리를 설치 했을 경우 push 또는 develop 브랜치에 PR 하기 전에 꼭 "pip freeze > requirements.txt" 명령으로 버전 동기화 해야합니다! (버전 충돌 방지 목적)
  - PR 전에 UTF-8 인코딩인지 체크하기 (인코딩이 다른 형식이면 텍스트가 깨질 수 있음)

  
  4. 환경 변수 및 키 파일 관리
     - 환경 변수 및 키 관련 보안 파일들은 slack 협업툴에 공유돼있는 구글 드라이브에서 관리합니다

     - 환경 변수 파일들 적용 경로
        - 폴더 이름 : envs &nbsp; 적용 경로 : server/
          
     - 키 파일별 적용 경로
       - 파일 이름 : vision-api-key.json 적용 경로 : secrets/
       - 파일 이름 : huggingface_token.txt 적용 경로 : secrets/
       - 파일 이름 : ngrok_token.txt 적용 경로 : mediport/colab_server/mediport_llm_colab.ipynb (ngrok 토큰 입력 부분에 직접 입력해줘야 합니다)



