import os
from server.config import env_mode


if  env_mode == "local": # 개발 환경
    from server.services.inference import inference_local as inference_impl
elif env_mode == "cloud":# 배포 환경
    from server.services.inference import inference_cloud as inference_impl
else:
    raise ValueError(f"Unsupported ENV_MODE: {env_mode}")

# 입력값 전달 후 추론 결과 받기
def run_inference(user_input: str) -> str:
    return inference_impl.run(user_input)