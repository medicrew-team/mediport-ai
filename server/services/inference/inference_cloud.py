### 배포 환경 ###


# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch
#
# tokenizer = AutoTokenizer.from_pretrained("blossom/llama-3.2-Korean-Bllossom-5b")
# model = AutoModelForCausalLM.from_pretrained("blossom/llama-3.2-Korean-Bllossom-5b")

# model.eval()
#
# def run(prompt: str) -> str:
#     inputs = tokenizer(prompt, return_tensors="pt")
#     with torch.no_grad():
#         outputs = model.generate(**inputs, max_new_tokens=100)
#     return tokenizer.decode(outputs[0], skip_special_tokens=True)

