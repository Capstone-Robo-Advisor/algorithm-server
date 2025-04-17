import logging
from chromadb import PersistentClient

logger = logging.getLogger(__name__)

# 벡터 DB 접근을 위한 유틸 클래스
class VectorUtil:
    _chroma_client = None
    _collection = None

    def __init__(self, collection_name="articles", persist_directory="./chroma_storage"):
        self._collection_name = collection_name
        self._persist_directory = persist_directory

    # ChromaDB 클라이언트 초기화
    def __get_vector_client(self):
        if self._chroma_client is None:
            try:
                self._chroma_client = PersistentClient(path=self._persist_directory)
                logger.info("ChromaDB client 초기화 완료.")
            except Exception as e:
                logger.error("ChromaDB client 초기화 실패", exc_info=True)
                raise RuntimeError(f"ChromaDB client 초기화 실패: {e}")
        return self._chroma_client

    # Chroma DB 컬렉션 받아 오기
    # TODO: 오래된 기사 삭제 로직 추가하기(날짜 단위 파악하기) -> 이건 뉴스 데이터를 DB에 넣을 때 고려하기
    def get_collection(self):
        if self._collection is None:
            try:
                self._collection = self.__get_vector_client().get_or_create_collection(self._collection_name)
                logger.info(f"ChromaDB collection '{self._collection_name}' 준비 완료.")
            except Exception as e:
                logger.error("ChromaDB collection 초기화 실패", exc_info=True)
                raise RuntimeError(f"ChromaDB collection 초기화 실패: {e}")
        return self._collection
