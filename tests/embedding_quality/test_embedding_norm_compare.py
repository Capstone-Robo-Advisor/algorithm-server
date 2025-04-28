"""
목표 : 한국어 문장 임베딩 모델들의 품질을 체계적으로 테스트하고 비교 분석하기 위한 과정
✅ STEP1. 임베딩 벡터 노름 테스트
"""

from sentence_transformers import SentenceTransformer, models
import numpy as np

# 테스트 쿼리 리스트
queries = [
    "기술",
    "반도체",
    "AI",
    "기술, 반도체",
    "AI 및 반도체 산업 동향에 대한 뉴스",
    "기술 산업 최신 이슈"
]

word_embedding_model = models.Transformer("BM-K/KoSimCSE-roberta")
pooling_model = models.Pooling(
    word_embedding_model.get_word_embedding_dimension(),
    pooling_mode='mean'
)
model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

models = {
    "ko-sroberta": SentenceTransformer("jhgan/ko-sroberta-multitask"),
    "ko-simcse": SentenceTransformer("BM-K/KoSimCSE-roberta"),
    "kr-sbert": SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS"),
    "multilingual-MiniLM": SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
}

print("🧪 임베딩 벡터 노름 테스트 결과\n-----------------------------")
for model_name, model in models.items():
    print(f"\n=== {model_name} 모델 테스트 ===")
    for query in queries:
        vec = model.encode(query)
        norm = np.linalg.norm(vec)
        print(f"'{query}' → 벡터 노름: {norm:.4f}")

        if norm < 0.1:
            print("⚠️  벡터 노름이 너무 작음 → 임베딩 품질 의심됨")