# check_vector_db.py
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_check")

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트 디렉토리 계산
project_root = Path(__file__).parent.parent.parent
chroma_storage_path = str(project_root / "chroma_storage")
os.environ["VECTOR_PERSIST_PATH"] = chroma_storage_path

# 벡터 DB 접근
from app.common.db.vector.vector_util import VectorUtil

# 컬렉션 확인
vector_util = VectorUtil()
collection = vector_util.get_collection()

# 데이터 확인
try:
    all_docs = collection.get(include=["documents", "metadatas"])
    doc_count = len(all_docs["ids"]) if "ids" in all_docs else 0

    logger.info(f"벡터 DB 데이터 확인: 총 {doc_count}개 문서 저장됨")

    if doc_count > 0:
        # 샘플 데이터 출력
        for i in range(min(3, doc_count)):
            doc = all_docs["documents"][i]
            meta = all_docs["metadatas"][i]
            logger.info(f"문서 #{i + 1}:")
            logger.info(f"  - 제목: {meta.get('title', '제목 없음')}")
            logger.info(f"  - 테마: {meta.get('theme', '테마 없음')}")
            logger.info(f"  - 내용 일부: {doc[:100]}...")
    else:
        logger.warning("벡터 DB에 저장된 문서가 없습니다!")

except Exception as e:
    logger.error(f"벡터 DB 확인 중 오류 발생: {str(e)}")