### server\.env 에 있는 환경 변수 들을 불러 와주는 중간 다리 역할을 하는 파일 ###

import os
from dotenv import load_dotenv

# server\.env 파일 내용을 불러옴
load_dotenv()

# 환경 변수 'LOCAL_COLAB_SERVER_URL' 값을 가져옴
LOCAL_COLAB_SERVER_URL = os.getenv("LOCAL_COLAB_SERVER_URL")