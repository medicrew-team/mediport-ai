import os
import json
import requests

# 테스트 데이터셋 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATASET_PATH = os.path.join(BASE_DIR, "data", "test_questions.json")

# FastAPI 서버 주소
API_URL = "http://127.0.0.1:8001/inference"  # 실제 서버 주소로 변경

def evaluate_model():
    with open(TEST_DATASET_PATH, "r", encoding="utf-8") as f:
        test_data = json.load(f)

    total = len(test_data)
    correct = 0
    incorrect = 0

    for idx, item in enumerate(test_data, start=1):
        question = item["질문"]
        expected_answers = item["추천_약품"]

        try:
            response = requests.post(API_URL, json={
                "user_input": question,
                "lang": "ko"
            })
            response_data = response.json()
            answer_text = response_data.get("result", "")

            if any(drug in answer_text for drug in expected_answers):
                correct += 1
                result_label = "맞음"
            else:
                incorrect += 1
                result_label = "틀림"

            print(f"[{idx}/{total}] {result_label}")
            print(f"   질문: {question}")
            print(f"   예측: {answer_text}")
            print(f"   정답 리스트: {expected_answers}\n")

        except Exception as e:
            print(f"[ERROR] {idx}번째 질문 평가 중 오류 발생: {e}")

    accuracy = correct / total * 100
    print("===== 평가 결과 =====")
    print(f"총 질문 수: {total}")
    print(f"맞춘 개수: {correct}")
    print(f"틀린 개수: {incorrect}")
    print(f"정확도(Top-1): {accuracy:.2f}%")

# if __name__ == "__main__":
#     evaluate_model()