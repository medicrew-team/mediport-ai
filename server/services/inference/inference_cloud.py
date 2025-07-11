
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
import torch
import os
from server.config import BASE_DIR

### Hugging Face 로그인 ###

# Hugging Face 토큰 파일 경로
HF_TOKEN_PATH = os.path.join(BASE_DIR, "secrets", "huggingface_token.txt")

# 토큰 파일 읽어서 로그인
if os.path.exists(HF_TOKEN_PATH):
    with open(HF_TOKEN_PATH, "r") as f:
        hf_token = f.read().strip()
    login(hf_token)
else:
    raise FileNotFoundError(f"[ERROR] Hugging Face token not found at: {HF_TOKEN_PATH}")

### Hugging Face 로그인 ###


# 모델 로드
model_name = "Bllossom/llama-3.2-Korean-Bllossom-AICA-5B"

# 토크나이저 및 모델 로드
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,  # GPU 메모리 절약을 위한 float16 사용
    device_map="auto"           # 여러 GPU 환경 또는 단일 GPU 자동 할당
)
model.eval()

# 추론 함수 (유지보수 쉽게 하기 위해 Colab 서버 코드 스타일과 통일)
def run(prompt: str) -> str:
    # 입력 프롬프트 토크나이징
    inputs = tokenizer(prompt, return_tensors="pt", padding=True)
    input_ids = inputs["input_ids"].to(model.device)
    attention_mask = inputs["attention_mask"].to(model.device)

    # 모델 추론
    with torch.no_grad():
        output = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=512,                     # 생성 최대 길이
            do_sample=True,                         # 샘플링 기반 생성 (비결정적)
            temperature=0.7,                        # 생성 다양성 제어 (낮을수록 보수적)
            top_p=0.9,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id     # padding 시 EOS 토큰 재사용
        )

    # 디코딩 (토큰 → 텍스트)
    decoded = tokenizer.decode(output[0], skip_special_tokens=True)

    # 프롬프트 부분 제거하고 생성된 응답만 반환
    if decoded.startswith(prompt):
        return decoded[len(prompt):].strip()
    else:
        return decoded