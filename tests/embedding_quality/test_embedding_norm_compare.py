"""
✅ 1. "SentenceTransformer 모델"이란?
모델의 정의
- 문장을 고차원 벡터로 변환해주는 모델 : 이러한 벡터는 문장 간 의미 유사도, 검색, 클러스터링 등에 사용
즉, 사람이 읽는 "문장" 을 -> 컴퓨터가 이해할 수 있는 "숫자 벡터"로 바꿔주는 임베딩 모델

SentenceTransformer = HuggingFace 기반의 문장 임베딩 툴킷
- 내부적으로는 BERT, RoBERTTa, 또는 SBERT 등 사전 학습된 Transformer 기반 모델을 사용
- 768차원 또는 1024차원짜리 숫자 벡터를 문장마다 반환함
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