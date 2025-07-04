### 실행 환경에 맞는 환경 변수 들을 불러 와주는 중간 다리 역할을 하는 파일 ###

import os
from dotenv import load_dotenv

# 현재 파일 위치 기준 base 경로
base_dir = os.path.dirname(os.path.abspath(__file__))


# .env 파일에서 실행 환경(local or cloud) 정보만 불러옴
env_path = os.path.join(base_dir, "envs", ".env")
load_dotenv(dotenv_path=env_path)
env_mode = os.getenv("ENV_MODE")


# 실행 환경에 맞는 .env 파일 경로 생성
env_file_path = os.path.join(base_dir, "envs", f".env.{env_mode}")

#  실행 환경에 맞는 .env 파일이 존재하면 재로딩
if os.path.exists(env_file_path):
    load_dotenv(dotenv_path=env_file_path, override=True)
else:
    raise FileNotFoundError(f"{env_file_path} not found.")


### 환경 변수 ###

# 개발 환경일 때만 사용하는 환경 변수
if env_mode == "local":
    LOCAL_COLAB_SERVER_URL = os.getenv("LOCAL_COLAB_SERVER_URL")


# 공통 환경 변수
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")