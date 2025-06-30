import os

# server\.env 파일에서 설정한 모드 가져옴 (기본값 : local)
inference_mode = os.getenv("INFERENCE_MODE", "local")

if inference_mode == "local": # 개발 환경일 때 실행
    from server.services.inference import inference_local as inference_impl
elif inference_mode == "cloud":# 배포 환경일 때 실행
    from server.services.inference import inference_cloud as inference_impl

# 입력값 전달 후 추론 결과 받기
def run_inference(user_input: str) -> str:
    return inference_impl.run(user_input)