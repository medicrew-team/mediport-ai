# Python 3.12.5 이미지 기반
FROM python:3.12.5

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 배포에 필요한 코드 복사
COPY server/ ./server
COPY docker/start.sh ./start.sh
COPY data/ ./data
COPY secrets/ ./secrets

# 포트 개방 (FastAPI 기본 포트)
EXPOSE 8000

# 이미지 빌드(docker build)할 때 실행됨(start.sh 파일에 실행 권한 부여)
RUN chmod +x start.sh

# 컨테이너 실행 시 실행됨 (docker run)
CMD ["./start.sh"]