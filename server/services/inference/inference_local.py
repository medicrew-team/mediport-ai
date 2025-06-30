### 개발 환경 ###

import os
import requests

# 추론용 local colab 서버 URL을 불러옴
from server.config import LOCAL_COLAB_SERVER_URL


def run(user_input: str) -> str:
    # colab 서버의 /inference로 POST 요청을 보냄
    response = requests.post(f"{LOCAL_COLAB_SERVER_URL}/inference", json={"user_input": user_input})
    response.raise_for_status()
    return response.json()["result"]