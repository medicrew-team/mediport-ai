# Mediport-AI

> Mediport 프로젝트 내 AI(의약품 OCR + 다국어 챗봇) 시스템



---

## 개요

**Mediport-AI**는 Mediport 플랫폼 내에서 AI 관련 기능 전담 모듈로, 두 개의 핵심 시스템으로 구성되어 있습니다.

* **OCR 시스템**: 약봉투 이미지를 분석하여 약명과 복약정보를 추출하는 비전 기반 AI
* **챗봇 시스템**: 사용자의 질의(증상·약품명 등)에 따라 일반의약품 정보를 RAG 기반으로 검색하고, 다국어로 응답하는 LLM 챗봇
---

## 배포 주소
| 구분 | URL |
|------|------|
| AI 서버 | [https://mediport-ai-dev.store](https://mediport-ai-dev.store) |
| API 문서 | [https://mediport-ai-dev.store/docs](https://mediport-ai-dev.store/docs) |

---

## 기술 스택

| 구분        | 기술                                                         |
| --------- | ---------------------------------------------------------- |
| Backend   | Python 3.12, FastAPI, Uvicorn                              |
| Embedding | SentenceTransformers (jhgan/ko-sroberta) |
| Search    | FAISS, BM25, RRF 앙상블                                       |
| LLM       | Blossom 8B (RunPod) / OpenAI API (AWS)              |
| OCR       | Google Cloud Vision API                                    |
| Infra     | Docker, RunPod, AWS EC2, Cloudflare Tunnel          |


---

## 서버 병행 구조

Mediport-AI의 챗봇 서버는 서비스 성장 단계에 따라 비용 효율성을 중심으로 전환 가능한 두 가지 추론 환경으로 구성되어 있습니다.

| 모드                         | 설명                                                                                                                                                               |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AWS OpenAPI 모드 (초기 단계)** | 서비스 초기에 사용자가 많지 않을 때 GPU 유지비 절감을 위한 비용 효율 중심 모드 입니다. AWS EC2의 FastAPI 서버가 외부 LLM API(OpenAI 호환)를 호출하여 추론을 수행하며, 안정적인 성능을 유지하면서도 운영비가 낮아 초기 서비스 운영에 적합합니다. |
| **RunPod 클라우드 모드 (확장 단계)** | 사용량이 일정 수준 이상으로 증가하면 GPU 클라우드 환경(A100)에서 양자화된 Blossom 8B 모델을 직접 서빙하도록 전환됩니다. 일정 트래픽 이상에서는 OpenAPI 호출 대비 시간당 GPU 비용이 더 경제적이기 때문에, 비용 효율 관점에서 GPU 클라우드로 전환하도록 설계되었습니다.                                            |

`.env`의 `ENV_MODE` 설정을 변경해 손쉽게 환경을 전환할 수 있습니다.

```bash
### 실행 환경 선택 ###
ENV_MODE=local         # 로컬 개발 환경
#ENV_MODE=cloud_runpod # RunPod (Blossom 8B 직접 서빙)
#ENV_MODE=cloud_aws    # AWS (OpenAI API)
```

이 구조를 통해 서비스 초기에는 비용 절감 중심(AWS OpenAPI) 으로 운영하고, 사용량이 증가해 GPU 사용이 더 경제적인 시점이 되면 GPU 클라우드 환경(RunPod) 으로 전환하여 운영할 수 있습니다.

---

## 시스템 구성 요약

| 구분             | 설명                                                       |
| -------------- | -------------------------------------------------------- |
| **OCR 시스템**    | Google Vision API 기반 텍스트 인식 → 약명·복약정보 추출 → 금기·상호작용 조회    |
| **챗봇 시스템**     | 사용자 질의 기반 검색 + LLM 응답 (RunPod Blossom 8B 또는 AWS OpenAPI) |
| **번역 모듈**      | 의학적 용어 비번역 보호 처리 기반 다국어 번역 (5개 언어 지원)                            |
| **운영 환경** | 서비스 초기에는 AWS 환경(OpenAPI)을 활용하고, 사용량 증가 시 RunPod GPU 서버로 전환 가능한 이중 추론 환경 구조   |
---

## AI 아키텍처

### 1) LLM 챗봇 시스템 아키텍처

```
User ─▶ 질의 입력
   │
   ▼
[FastAPI 서버]
   ├─▶ 검색 엔진 (BM25 + FAISS + RRF)
   ├─▶ 문서 컨텍스트 구성
   ├─▶ 선택된 환경으로 요청 전달
   │     ├─ RunPod: Blossom 8B 직접 서빙 (GPU)
   │     └─ AWS: OpenAI API 호출
   └─▶ 응답 생성 → 다국어 번역 → 사용자 반환
```

---

### 2) OCR 시스템 아키텍처

```
User ─▶ 약봉투 이미지 업로드
   │
   ▼
[OCR 모듈]
   ├─▶ Google Vision API 호출
   ├─▶ 텍스트 정제 및 파싱
   ├─▶ 약명/복약정보 1:1 매칭
   ├─▶ 금기·상호작용·보관법 정보 조회 (내부 DB)
   └─▶ 결과 번역 및 반환
```


---

## 개발 환경 설정 및 협업 규칙

  1. 개발 환경 정보
  - Python 버전: 3.12.5 
  
  2. 의존성 설치 명령어 (작업하기 전에 실행 필수)<br>
  ```pip install -r requirements.txt```
  
  3. requirements.txt 관리 규칙
  - 개인 작업 브랜치에서 개발 도중 외부 라이브러리를 설치 했을 경우 push 또는 develop 브랜치에 PR 하기 전에 꼭 ```pip freeze > requirements.txt``` 명령으로 버전 동기화 해야합니다! (버전 충돌 방지 목적)
  - PR 전에 UTF-8 인코딩인지 체크하기 (인코딩이 다른 형식이면 텍스트가 깨질 수 있음)

  
  4. 키 파일 관리 (※ 키 관련 보안 파일들은 slack 협업툴에 공유돼있는 구글 드라이브에서 관리합니다 ※ )
          
     - 개발환경 구축에 필요한 보완키 적용 경로 
        - 파일 이름 : secrets/vision-api-key.json &nbsp; 적용 경로 : secrets/ 
        - 파일 이름 : secrets/huggingface_token.txt &nbsp; 적용 경로 : colab_server/mediport_llm_colab.ipynb (Colab 환경에서 실행 시 huggingface 토큰 입력 부분에 직접 토큰을 입력해줘야 합니다) 
        - 파일 이름 : secrets/ngrok_token.txt &nbsp; 적용 경로 : colab_server/mediport_llm_colab.ipynb (Colab 환경에서 실행 시 ngrok 토큰 입력 부분에 직접 토큰을 입력해줘야 합니다)




---

## 향후 개선 로드맵

- 사용자 복용 이력·기저질환 기반 개인 맞춤형 약 추천 서비스 추가
- 멀티에이전트 기반 검증 시스템 추가 (응답 신뢰도 향상)
- OCR 인식 오류 보완: 텍스트 임베딩 기반 유사도 매칭 시스템 도입
- 챗봇 입력 방식 확장: 텍스트 입력뿐 아니라 음성 입력(STT) 지원

---

## Maintainer

* 김동윤 (AI 시스템 담당)
* Email: kdy9416@naver.com
