from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor
import asyncio

from app.common.db.vector.vector_util import VectorUtil

embedding_model = SentenceTransformer("jhgan/ko-sroberta-multitask")

vector_util = VectorUtil()
collection = vector_util.get_collection()

comma = ","

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
        loop = asyncio.get_event_loop()

        for article in news_articles:
            article_id = str(article.get("id"))
            summary = article.get("summary_ko", "")
            reason = article.get("reason", "")
            full_text = summary + "\n" + reason

            if not full_text.strip():
                continue

            embedding = await loop.run_in_executor(executor, embedding_model.encode, full_text)

            collection.add(
                documents=[full_text],
                embeddings=[embedding],
                ids=[article_id],
                metadatas=[{
                    "title": article.get("title_ko", ""),
                    "published_at": article.get("published_at", ""),
                    "importance": article.get("importance", "")
                }]
            )

