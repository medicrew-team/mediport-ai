import re
from typing import List, Dict, Any


# def map_medicines_to_dosages(raw_text: str, known_medicine_names: List[str]) -> Dict[str, Dict[str, str]]:
#
#     """
#     전체 OCR 텍스트에서 약명과 복약정보를 순서대로 매핑
#     """
#     medicine_dosage_map = {}
#     found_meds = []
#     found_dosages = []
#
#     # 약명 후보 수집
#     for med_name in known_medicine_names:
#         if med_name in raw_text:
#             found_meds.append(med_name)
#
#
#     # 복약정보 수집 (띄어쓰기/붙어쓰기 모두 대응)
#     dosage_matches = re.findall(r"(\d+)\s*정\s*씩\s*(\d+)\s*회\s*(\d+)\s*일\s*분", raw_text)
#     if not dosage_matches:
#         # 예: '1정씩2회5일분' 같은 형태도 대응
#         dosage_matches = re.findall(r"(\d+)정씩(\d+)회(\d+)일분", raw_text)
#
#     found_dosages = dosage_matches
#
#
#
#     # 매핑
#     for med, dosage in zip(found_meds, found_dosages):
#         medicine_dosage_map[med] = {
#             "투약량": dosage[0],
#             "횟수": dosage[1],
#             "일수": dosage[2],
#         }
#
#     return medicine_dosage_map


# def map_medicines_to_dosages(raw_text: str, words: List[Dict[str, Any]], known_medicine_names: List[str]) -> Dict[str, Dict[str, str]]:
#     """
#     위치 기반 라인 재구성 후 약명 + 복약정보가 같은 라인에 있을 때만 매핑.
#     약명만 있을 경우 null 값 초기화. 복약 정보만 있는 경우는 무시.
#     """
#     # 라인 그룹핑: Y 중심값 기준
#     def group_by_lines(words: List[Dict], threshold: int = 15) -> List[List[Dict]]:
#         lines = []
#         for word in sorted(words, key=lambda w: w["y_center"]):
#             added = False
#             for line in lines:
#                 if abs(line[0]["y_center"] - word["y_center"]) <= threshold:
#                     line.append(word)
#                     added = True
#                     break
#             if not added:
#                 lines.append([word])
#         return lines
#
#     # 라인 단위로 나누기
#     lines = group_by_lines(words)
#
#     # 약명 포함 여부 확인용
#     med_map = {med: {"투약량": None, "횟수": None, "일수": None} for med in known_medicine_names}
#
#     # 각 라인에서 복약정보 + 약명 함께 있는지 확인
#     for line in lines:
#         line_text = "".join([w["text"] for w in line])
#
#         # 복약정보 패턴 찾기
#         match = re.search(r"(\d+\.?\d*)\s*정\s*씩\s*(\d+)\s*회\s*(\d+)\s*일\s*분", line_text)
#         if not match:
#             match = re.search(r"(\d+\.?\d*)정씩(\d+)회(\d+)일분", line_text)
#         if not match:
#             continue  # 복약정보 없는 줄은 스킵
#
#         # 라인에 포함된 약명 중 하나 찾기
#         for med in known_medicine_names:
#             if med in line_text:
#                 med_map[med] = {
#                     "투약량": match.group(1),
#                     "횟수": match.group(2),
#                     "일수": match.group(3),
#                 }
#                 break  # 한 줄당 하나만 매핑
#
#     return med_map


# 각 단어의 y_center (중앙 y값)을 기준으로 비슷한 위치에 있는 단어들끼리 같은 줄로 간주하는 방식
# def map_medicines_to_dosages(raw_text: str, words: List[Dict[str, Any]], known_medicine_names: List[str]) -> Dict[str, Dict[str, str]]:
#     """
#     위치 기반 라인 재구성 후 약명 + 복약정보가 같은 라인에 있을 때만 매핑.
#     복약정보가 아예 없을 경우 약명만 null 값으로 반환.
#     """
#     # 라인 그룹핑: Y 중심값 기준
#     def group_by_lines(words: List[Dict], threshold: int = 15) -> List[List[Dict]]:
#         lines = []
#         for word in sorted(words, key=lambda w: w["y_center"]):
#             added = False
#             for line in lines:
#                 if abs(line[0]["y_center"] - word["y_center"]) <= threshold:
#                     line.append(word)
#                     added = True
#                     break
#             if not added:
#                 lines.append([word])
#         return lines
#
#     # 약명 초기화
#     med_map = {med: {"투약량": None, "횟수": None, "일수": None} for med in known_medicine_names}
#
#     # 복약정보가 존재하는지 먼저 검사
#     has_dosage_info = bool(
#         re.search(r"(\d+\.?\d*)\s*정\s*씩\s*(\d+)\s*회\s*(\d+)\s*일\s*분", raw_text)
#         or re.search(r"(\d+\.?\d*)정씩(\d+)회(\d+)일분", raw_text)
#     )
#
#     if not has_dosage_info:
#         return med_map  # 약명만 리턴
#
#     # 줄 단위 그룹핑
#     lines = group_by_lines(words)
#
#     # 매핑 수행
#     for line in lines:
#         line_text = "".join([w["text"] for w in line])
#
#         # 복약정보 추출
#         match = re.search(r"(\d+\.?\d*)\s*정\s*씩\s*(\d+)\s*회\s*(\d+)\s*일\s*분", line_text)
#         if not match:
#             match = re.search(r"(\d+\.?\d*)정씩(\d+)회(\d+)일분", line_text)
#         if not match:
#             continue
#
#         # 줄에 약명이 포함돼 있는지 확인
#         for med in known_medicine_names:
#             if med in line_text:
#                 med_map[med] = {
#                     "투약량": match.group(1),
#                     "횟수": match.group(2),
#                     "일수": match.group(3),
#                 }
#                 break  # 첫 약명에만 매핑
#
#     return med_map


# 각 단어의 bounding_box로부터 **상하 경계값 (y_min, y_max)**을 계산하고 이 범위에 다른 단어가 겹쳐 있으면 같은 줄로 보는 방식
# def map_medicines_to_dosages(raw_text: str, words: List[Dict[str, Any]], known_medicine_names: List[str]) -> Dict[str, Dict[str, str]]:
#
#     """
#     위치 기반 라인 재구성 (Y 중심값이 아닌 bounding box의 상하 경계값 기준).
#     약명 + 복약정보가 같은 라인에 있을 때만 매핑.
#     복약정보가 아예 없을 경우 약명만 null 값으로 반환.
#     """
#
#     # 상하 y경계 기준으로 줄 그룹핑 (2번 방식)
#     def group_by_lines_bbox(words: List[Dict], threshold: int = 10) -> List[List[Dict]]:
#         lines = []
#         for word in sorted(words, key=lambda w: w["y_center"]):
#             y_coords = [y for _, y in word["bounding_box"]]
#             y_min, y_max = min(y_coords), max(y_coords)
#             added = False
#
#             for line in lines:
#                 ref_y_coords = [y for _, y in line[0]["bounding_box"]]
#                 ref_min = min(ref_y_coords)
#                 ref_max = max(ref_y_coords)
#
#                 # 경계선끼리 겹치면 같은 라인으로 간주
#                 if y_max >= ref_min - threshold and y_min <= ref_max + threshold:
#                     line.append(word)
#                     added = True
#                     break
#
#             if not added:
#                 lines.append([word])
#
#         return lines
#
#     # 약명 초기화
#     med_map = {med: {"투약량": None, "횟수": None, "일수": None} for med in known_medicine_names}
#
#     # 복약정보가 존재하는지 먼저 검사
#     has_dosage_info = bool(
#         re.search(r"(\d+\.?\d*)\s*정\s*씩\s*(\d+)\s*회\s*(\d+)\s*일\s*분", raw_text)
#         or re.search(r"(\d+\.?\d*)정씩(\d+)회(\d+)일분", raw_text)
#     )
#     if not has_dosage_info:
#         return med_map  # 약명만 리턴
#
#     # 줄 단위 그룹핑 (bounding box 방식)
#     lines = group_by_lines_bbox(words)
#
#     # 매핑 수행
#     for line in lines:
#         line_text = "".join([w["text"] for w in line])
#
#         # 복약정보 추출
#         match = re.search(r"(\d+\.?\d*)\s*정\s*씩\s*(\d+)\s*회\s*(\d+)\s*일\s*분", line_text)
#         if not match:
#             match = re.search(r"(\d+\.?\d*)정씩(\d+)회(\d+)일분", line_text)
#         if not match:
#             continue
#
#         # 줄에 약명이 포함돼 있는지 확인
#         for med in known_medicine_names:
#             if med in line_text:
#                 med_map[med] = {
#                     "투약량": match.group(1),
#                     "횟수": match.group(2),
#                     "일수": match.group(3),
#                 }
#                 break  # 첫 약명에만 매핑
#
#     return med_map


# # 각 단어의 bounding_box로부터 **상하 경계값 (y_min, y_max)**을 계산하고 이 범위에 다른 단어가 겹쳐 있으면 같은 줄로 보는 방식
# def map_medicines_to_dosages(raw_text: str, words: List[Dict[str, Any]], known_medicine_names: List[str]) -> Dict[str, Dict[str, str]]:
#     """
#     위치 기반 라인 재구성 (bounding box 기준).
#     약명 기준으로 줄을 돌며 복약정보를 추출하고 매핑.
#     복약정보가 없으면 해당 약명은 null 값으로 유지.
#     """
#
#     # 복약 정보가 전체 텍스트에 단 1개도 없다면 매핑 시도할 필요 없음
#     has_dosage_info = bool(
#         re.search(r"(\d+\.?\d*)\s*정\s*씩\s*(\d+)\s*회\s*(\d+)\s*일\s*분", raw_text)
#         or re.search(r"(\d+\.?\d*)정씩(\d+)회(\d+)일분", raw_text)
#     )
#     if not has_dosage_info:
#         return {med: {"투약량": None, "횟수": None, "일수": None} for med in known_medicine_names}
#
#
#     # 상하 y경계 기준으로 줄 그룹핑 (2번 방식)
#     def group_by_lines_bbox(words: List[Dict], threshold: int = 10) -> List[List[Dict]]:
#         lines = []
#         for word in sorted(words, key=lambda w: w["y_center"]):
#             y_coords = [y for _, y in word["bounding_box"]]
#             y_min, y_max = min(y_coords), max(y_coords)
#             added = False
#
#             for line in lines:
#                 ref_y_coords = [y for _, y in line[0]["bounding_box"]]
#                 ref_min = min(ref_y_coords)
#                 ref_max = max(ref_y_coords)
#
#                 # 경계선끼리 겹치면 같은 라인으로 간주
#                 if y_max >= ref_min - threshold and y_min <= ref_max + threshold:
#                     line.append(word)
#                     added = True
#                     break
#
#             if not added:
#                 lines.append([word])
#
#         return lines
#
#     # 약명 → 복약정보 매핑 딕셔너리 초기화
#     med_map = {med: {"투약량": None, "횟수": None, "일수": None} for med in known_medicine_names}
#
#     # 줄 단위 그룹핑
#     lines = group_by_lines_bbox(words)
#
#     # 약명별 줄 탐색
#     for med in known_medicine_names:
#         for line in lines:
#             line_text = "".join([w["text"] for w in line])
#             if med in line_text:
#                 # 해당 줄에서 복약정보 추출
#                 match = re.search(r"(\d+\.?\d*)\s*정\s*씩\s*(\d+)\s*회\s*(\d+)\s*일\s*분", line_text)
#                 if not match:
#                     match = re.search(r"(\d+\.?\d*)정씩(\d+)회(\d+)일분", line_text)
#
#                 if match:
#                     med_map[med] = {
#                         "투약량": match.group(1),
#                         "횟수": match.group(2),
#                         "일수": match.group(3),
#                     }
#                 break  # 해당 약명에 대해 첫 번째 매칭 줄만 처리
#
#     return med_map




def map_medicines_to_dosages(words: List[Dict[str, Any]], known_medicine_names: List[str]) -> Dict[str, Dict[str, str]]:
    """
    약명 기준으로 OCR 단어(words)에서 가장 가까운 복약정보를 추출하여 매핑.
    - 약명 단어 주변(같은 줄 + 오른쪽 범위)의 텍스트만 합쳐서 복약정보를 찾음
    - 복약정보가 없으면 None 값으로 처리
    - 유사도 매칭 없이 정확히 OCR 단어를 기반으로 함
    """

    # 최종 결과 딕셔너리 (약명별 투약량, 횟수, 일수)
    med_map = {med: {"투약량": None, "횟수": None, "일수": None} for med in known_medicine_names}

    # Y축 같은 줄로 간주할 임계값 (픽셀 단위)
    Y_THRESHOLD = 15
    # 약명 오른쪽 단어만 탐색할 X 거리 제한
    X_DISTANCE_LIMIT = 500

    # 각 약명에 대해 반복
    for med in known_medicine_names:
        # OCR 단어 중에서 약명에 포함된 단어들 찾기
        med_tokens = [w for w in words if w["text"] in med]

        # 약명을 OCR에서 찾지 못한 경우 → None 유지
        if not med_tokens:
            continue

        # 약명 단어들의 중심 좌표 계산
        avg_y = sum(w["y_center"] for w in med_tokens) / len(med_tokens)
        avg_x = sum(w["x_center"] for w in med_tokens) / len(med_tokens)

        # 약명 주변의 같은 줄(y축 비슷) + 오른쪽(x 큰) 단어만 후보로 선택
        candidate_words = [
            w for w in words
            if abs(w["y_center"] - avg_y) < Y_THRESHOLD and
               0 < (w["x_center"] - avg_x) < X_DISTANCE_LIMIT
        ]

        # 후보 단어들을 x 좌표 순으로 정렬
        candidate_words.sort(key=lambda w: w["x_center"])

        # 후보 단어들을 하나로 합쳐서 복약정보 패턴 검색
        line_text = "".join(w["text"] for w in candidate_words)

        # 정규식으로 복약정보 추출
        match = re.search(r"(\d+\.?\d*)\s*정\s*씩\s*(\d+)\s*회\s*(\d+)\s*일\s*분", line_text)
        if not match:
            match = re.search(r"(\d+\.?\d*)정씩(\d+)회(\d+)일분", line_text)

        # 복약정보가 있으면 결과에 매핑
        if match:
            med_map[med] = {
                "투약량": match.group(1),
                "횟수": match.group(2),
                "일수": match.group(3),
            }

    return med_map