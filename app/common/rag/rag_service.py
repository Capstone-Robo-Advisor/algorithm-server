from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor
import asyncio
import logging

from app.common.db.vector.vector_util import VectorUtil

embedding_model = SentenceTransformer("jhgan/ko-sroberta-multitask")

vector_util = VectorUtil()
collection = vector_util.get_collection()

comma = ","

# 로거 설정
logger = logging.getLogger(__name__)

# 쓰레드 풀
executor = ThreadPoolExecutor(max_workers=4)

# rag 기반 서비스를 제공
class RagService:

    # 뉴스 데이터를 반환
    def get_news_data(self, categories):
        query = comma.join(categories)
        query_embedding = embedding_model.encode(query)
        news_articles = []

        #TODO: n_result 파라미터를 몇 개로 지정할 것인가?
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5 # 임시
        )

        for doc, meta in zip(results["documents"], results["metadatas"]):
            meta = meta[0]
            news_articles.append({
                "title": meta.get("title", ""),
                "source": meta.get("publisher", ""),
                "published_date": meta.get("published_at", ""),
                "summary": doc[0]
            })

        return news_articles

    # 뉴스 데이터를 저장
    async def save_news_data(self, news_articles):
        """뉴스 데이터를 벡터 DB에 저장"""
        if not news_articles:
            logger.warning("저장할 뉴스 기사가 없습니다.")
            return

        loop = asyncio.get_event_loop()

        success_count = 0
        error_count = 0

        for article in news_articles:
            try:
                # 필수 필드 확인
                article_id = str(article.get("id", ""))
                if not article_id:
                    logger.warning("기사 ID가 없어 건너뜀")
                    error_count += 1
                    continue

                # 텍스트 필드 안전하게 가져오기
                summary_ko = article.get("summary_ko", "")
                summary = article.get("summary", "")
                reason = article.get("reason", "")

                # None 값 처리
                summary_ko = "" if summary_ko is None else summary_ko
                summary = "" if summary is None else summary
                reason = "" if reason is None else reason

                # 요약 텍스트 (한국어 우선)
                summary_text = summary_ko if summary_ko else summary

                # 전체 텍스트 구성
                full_text = f"{summary_text}\n{reason}".strip()

                if not full_text:
                    logger.warning(f"기사 {article_id}의 텍스트가 비어 있어 건너뜀")
                    error_count += 1
                    continue

                # 임베딩 생성
                embedding = await loop.run_in_executor(executor, embedding_model.encode, full_text)

                # 메타데이터 구성 (None 값 처리)
                metadata = {
                    "title": article.get("title_ko", "") or article.get("title", "") or "",
                    "published_at": article.get("published_at", ""),
                    "importance": article.get("importance", "medium"),
                    "publisher": article.get("publisher", ""),
                    "theme": article.get("theme", "")
                }

                # 메타데이터의 None 값 처리
                for key, value in metadata.items():
                    if value is None:
                        metadata[key] = ""

                # 벡터 DB에 저장
                collection.add(
                    documents=[full_text],
                    embeddings=[embedding.tolist()],
                    ids=[article_id],
                    metadatas=[metadata]
                )

                success_count += 1

            except Exception as e:
                logger.error(f"기사 {article.get('id', 'unknown')} 저장 중 오류: {str(e)}")
                error_count += 1

        logger.info(f"뉴스 데이터 저장 완료: 성공 {success_count}건, 실패 {error_count}건")
        return success_count

