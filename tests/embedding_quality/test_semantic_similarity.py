from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("jhgan/ko-sroberta-multitask")

query_pairs = [
    ("기술", "기술 산업 최신 이슈"),
    ("AI", "AI 및 반도체 산업 동향에 대한 뉴스"),
    ("기술", "반도체"),
    ("기술", "경제")
]

print("📏 코사인 유사도 측정 결과\n-----------------------------")

for q1, q2 in query_pairs:
    vec1 = model.encode(q1)
    vec2 = model.encode(q2)
    cosine_sim = util.cos_sim(vec1, vec2).item()
    print(f"'{q1}' ↔ '{q2}' → 유사도: {cosine_sim:.4f}")