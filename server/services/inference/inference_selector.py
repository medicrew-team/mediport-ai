import os
from server.config import env_mode


if  env_mode == "local":            # 개발 환경
    from server.services.inference import inference_local as inference_impl
elif env_mode == "cloud_runpod":    # runpod 배포 환경
    from server.services.inference import inference_cloud as inference_impl


# 입력값 전달 후 추론 결과 받기
def run_inference(prompt: str) -> str:
    return inference_impl.run(prompt)