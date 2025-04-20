# tests/semantic_search/test_semantic_search.py

from sentence_transformers import SentenceTransformer, util

def main():
    print("📘 Semantic Search 테스트 시작\n")

    # ✅ 모델 로드
    model = SentenceTransformer("jhgan/ko-sroberta-multitask")

    # ✅ 테스트 문서 리스트
    documents = [
        "AI 기술이 반도체 산업에 미치는 영향",
        "스마트폰 시장 동향",
        "반도체 공정 기술",
        "국내 경제 성장률",
        "AI 및 기술 관련 최신 뉴스"
    ]

    # ✅ 쿼리 설정
    query = "AI 반도체 산업 뉴스"

    # ✅ 임베딩 계산
    doc_embeddings = model.encode(documents)
    query_embedding = model.encode(query)

    # ✅ 코사인 유사도 계산
    cos_scores = util.cos_sim(query_embedding, doc_embeddings)[0]
    top_k = cos_scores.argsort(descending=True)[:3]

    # ✅ 결과 출력
    print(f"🔍 쿼리: '{query}' 와 유사한 문서 Top 3:\n")
    for idx in top_k:
        print(f"- ({cos_scores[idx]:.4f}) {documents[idx]}")


if __name__ == "__main__":
    main()
