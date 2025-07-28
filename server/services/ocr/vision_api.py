import os
import io

from google.cloud import vision
from typing import List, Dict


# Vision API에서 제공하는 ImageAnnotatorClient 객체를 생성
client = vision.ImageAnnotatorClient()


# def extract_text_from_image(image_bytes: bytes) -> str:
#
#     image = vision.Image(content=image_bytes)
#     response = client.text_detection(image=image)
#     texts = response.text_annotations
#     if not texts:
#         return ""
#     return texts[0].description  # 전체 텍스트


# def extract_text_from_image(image_bytes: bytes) -> List[Dict]:
#     image = vision.Image(content=image_bytes)
#     response = client.document_text_detection(image=image)
#
#     results = []
#
#     for page in response.full_text_annotation.pages:
#         for block in page.blocks:
#             for paragraph in block.paragraphs:
#                 for word in paragraph.words:
#                     text = ''.join([s.text for s in word.symbols])
#                     box = word.bounding_box
#                     results.append({
#                         "text": text,
#                         "x": int((box.vertices[0].x + box.vertices[2].x) / 2),  # 중간 X
#                         "y": int((box.vertices[0].y + box.vertices[2].y) / 2),  # 중간 Y
#                     })
#     return results


# def extract_text_from_image(image_bytes: bytes) -> Dict:
#     """
#     전체 텍스트와 각 단어별 bounding box 포함한 위치 정보까지 추출
#     """
#     image = vision.Image(content=image_bytes)
#     response = client.document_text_detection(image=image)  # ← text_detection → document_text_detection로 변경
#
#     if not response.full_text_annotation:
#         return {"text": "", "words": []}
#
#     if response.text_annotations:
#         raw_text = response.text_annotations[0].description
#     else:
#         raw_text = ""
#
#     # full_text = response.full_text_annotation.text
#     words = []
#
#     for page in response.full_text_annotation.pages:
#         for block in page.blocks:
#             for paragraph in block.paragraphs:
#                 for word in paragraph.words:
#                     word_text = "".join([s.text for s in word.symbols])
#                     # y중심 좌표 계산
#                     y_center = sum([v.y for v in word.bounding_box.vertices]) / 4
#                     x_center = sum([v.x for v in word.bounding_box.vertices]) / 4
#
#                     words.append({
#                         "text": word_text,
#                         "x_center": x_center,
#                         "y_center": y_center,
#                         "bounding_box": [(v.x, v.y) for v in word.bounding_box.vertices]
#                     })
#
#     return {"text": raw_text, "words": words}


def extract_word_info(word) -> Dict:
    """
    단어 객체로부터 텍스트, 중심 좌표, bounding box 좌표 정보를 추출한다.

    Args:
        word: Vision API에서 반환한 단일 word 객체

    Returns:
        Dict: 단어 텍스트와 위치 정보(x_center, y_center, bounding_box)
    """
    # 단어 전체 텍스트 재구성 (symbol 단위 조합)
    word_text = "".join([s.text for s in word.symbols])

    # bounding box 좌표 정보 추출 및 중심 좌표 계산
    vertices = word.bounding_box.vertices
    bounding_box = [(v.x, v.y) for v in vertices]
    x_center = sum(x for x, _ in bounding_box) / 4
    y_center = sum(y for _, y in bounding_box) / 4

    return {
        "text": word_text,
        "x_center": x_center,
        "y_center": y_center,
        "bounding_box": bounding_box
    }


def extract_text_from_image(image_bytes: bytes) -> Dict:
    """
    Google Vision API를 사용하여 이미지에서 전체 텍스트 및 단어 단위 위치 정보를 추출한다.

    Args:
        image_bytes (bytes): 이미지 파일의 바이트 데이터

    Returns:
        Dict:
            {
                "text": 전체 텍스트 문자열,
                "words": 각 단어별 정보 리스트 (텍스트, 중심좌표, bounding box)
            }
    """
    # 이미지 객체 생성
    image = vision.Image(content=image_bytes)

    # 문서 단위 텍스트 추출 (위치 정보 포함)
    response = client.document_text_detection(image=image)

    # 추출 실패 시 빈 결과 반환
    if not response.full_text_annotation:
        return {"text": "", "words": []}

    # 전체 텍스트 (description 형태) → 맨 처음 텍스트 요소 사용
    raw_text = response.text_annotations[0].description if response.text_annotations else ""

    # 단어별 위치 정보 추출 (페이지 → 블록 → 문단 → 단어)
    words = [
        extract_word_info(word)
        for page in response.full_text_annotation.pages
        for block in page.blocks
        for paragraph in block.paragraphs
        for word in paragraph.words
    ]

    return {"text": raw_text, "words": words}


# def match_table_format(words: List[Dict]) -> List[Dict]:
#     # 기준 열 헤더들 추출 (열 제목 기준 X 좌표 확보)
#     column_keywords = ["투약량", "횟수", "일수"]
#     columns = {}
#
#     for word in words:
#         if word["text"] in column_keywords:
#             columns[word["text"]] = word["x"]
#
#     result = []
#
#     # 약명 후보: 한글+정제/정 형태로 끝나는 것만
#     for word in words:
#         if word["text"].endswith("정") or word["text"].endswith("캡슐"):
#             y = word["y"]
#             row = {"약명": word["text"]}
#
#             for col_name, col_x in columns.items():
#                 candidates = [
#                     w for w in words
#                     if abs(w["x"] - col_x) < 20 and abs(w["y"] - y) < 15 and w["text"].isdigit()
#                 ]
#                 if candidates:
#                     row[col_name] = candidates[0]["text"]
#
#             result.append(row)
#
#     return result