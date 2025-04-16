from sentence_transformers import SentenceTransformer

from app.common.db.vector.vector_util import VectorUtil

embedding_model = SentenceTransformer("jhgan/ko-sroberta-multitask")

vector_util = VectorUtil()
collection = vector_util.get_collection()

comma = ","

# rag 기반 서비스를 제공
# 1. 뉴스 데이터 저장 하는 쿼리
# 2. 뉴스 데이터 가져 오는 쿼리
class rag_service:
    def do_query_to_vector(self, categories):
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
