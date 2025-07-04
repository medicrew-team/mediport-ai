import os
from google.cloud import vision
import io

# Vision API에서 제공하는 ImageAnnotatorClient 객체를 생성
client = vision.ImageAnnotatorClient()

def extract_text_from_image(image_bytes: bytes) -> str:
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if not texts:
        return ""
    return texts[0].description  # 전체 텍스트