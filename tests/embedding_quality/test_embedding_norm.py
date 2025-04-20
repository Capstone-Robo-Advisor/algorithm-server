from sentence_transformers import SentenceTransformer
import numpy as np

# ✅ 현재 사용 중인 모델
model = SentenceTransformer("jhgan/ko-sroberta-multitask")

# 테스트 쿼리 리스트
queries = [
    "기술",
    "반도체",
    "AI",
    "기술, 반도체",
    "AI 및 반도체 산업 동향에 대한 뉴스",
    "기술 산업 최신 이슈"
]

print("🧪 임베딩 벡터 노름 테스트 결과\n-----------------------------")
for query in queries:
    vec = model.encode(query)
    norm = np.linalg.norm(vec)
    print(f"'{query}' → 벡터 노름: {norm:.4f}")

    if norm < 0.1:
        print("⚠️  벡터 노름이 너무 작음 → 임베딩 품질 의심됨")