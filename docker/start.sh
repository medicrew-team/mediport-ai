echo "FAISS 벡터 DB 저장 여부 확인 중..."

if [ ! -f "./data/medicine_faiss.index" ]; then
    echo "벡터 DB가 없어서 save_to_faiss.py 실행합니다."
    PYTHONPATH=./ python server/services/vector_store/save_to_faiss.py
else
    echo "벡터 DB가 이미 존재합니다. 그대로 서버 실행합니다."
fi

echo "FastAPI 서버 실행 시작"
uvicorn server.main:app --host 0.0.0.0 --port 8000