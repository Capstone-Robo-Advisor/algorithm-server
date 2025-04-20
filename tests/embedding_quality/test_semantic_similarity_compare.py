# tests/embedding_quality/test_semantic_similarity_compare.py
# 목표 : 한국어 문장 임베딩 모델들의 품질을 체계적으로 테스트하고 비교 분석하기 위한 과정
# ✅ STEP2. 의미 유사도 쌍 비교 테스트
from sentence_transformers import SentenceTransformer, util, models

# 사용할 모델 리스트
model_dict = {
    "ko-sroberta": SentenceTransformer("jhgan/ko-sroberta-multitask"),
    "ko-simcse": SentenceTransformer("BM-K/KoSimCSE-roberta"),
    "kr-sbert": SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS"),
    "miniLM": SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
}

# 유사/비유사 쌍
query_pairs = [
    ("기술", "기술 산업", True),  # 유사쌍
    ("반도체", "반도체 산업", True),  # 유사쌍
    ("AI", "인공지능", True),  # 유사쌍
    ("기술", "부동산 가격", False),  # 비유사쌍
    ("반도체", "음식 요리법", False),  # 비유사쌍
    ("AI", "여행지 추천", False),  # 비유사쌍
]

print("🧠 의미 유사도 모델 비교 테스트 결과\n=============================")

for model_name, model in model_dict.items():
    print(f"\n=== {model_name} 모델 테스트 ===")
    for q1, q2, should_be_similar in query_pairs:
        emb1 = model.encode(q1)
        emb2 = model.encode(q2)
        sim = util.cos_sim(emb1, emb2).item()

        result = "✅" if (sim > 0.6) == should_be_similar else "❌"
        label = "유사쌍" if should_be_similar else "비유사쌍"
        print(f"{result} [{label}] '{q1}' ↔ '{q2}' → 유사도: {sim:.4f}")
