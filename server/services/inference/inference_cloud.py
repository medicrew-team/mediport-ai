from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# 모델 로드
model_name = "Bllossom/llama-3.2-Korean-Bllossom-AICA-5B"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)
model.eval()


# 추론 함수 (유지보수 쉽게 하기 위해 Colab 서버 코드 스타일과 통일)
def run(user_input: str) -> str:
    inputs = tokenizer(user_input, return_tensors="pt", padding=True)
    input_ids = inputs["input_ids"].to(model.device)
    attention_mask = inputs["attention_mask"].to(model.device)

    with torch.no_grad():
        output = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id
        )

    decoded = tokenizer.decode(output[0], skip_special_tokens=True)

    if decoded.startswith(user_input):
        return decoded[len(user_input):].strip()
    else:
        return decoded