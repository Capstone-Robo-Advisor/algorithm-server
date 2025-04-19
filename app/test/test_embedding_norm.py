# from sentence_transformers import SentenceTransformer
# import numpy as np
#
# # ✅ 현재 사용 중인 모델
# model = SentenceTransformer("jhgan/ko-sroberta-multitask")
#
# # 테스트 쿼리 리스트
# queries = [
#     "기술",
#     "반도체",
#     "AI",
#     "기술, 반도체",
#     "AI 및 반도체 산업 동향에 대한 뉴스",
#     "기술 산업 최신 이슈"
# ]
#
# print("🧪 임베딩 벡터 노름 테스트 결과\n-----------------------------")
# for query in queries:
#     vec = model.encode(query)
#     norm = np.linalg.norm(vec)
#     print(f"'{query}' → 벡터 노름: {norm:.4f}")
#
#     if norm < 0.1:
#         print("⚠️  벡터 노름이 너무 작음 → 임베딩 품질 의심됨")

# from sentence_transformers import SentenceTransformer
# import numpy as np
#
# # 🔍 현재 사용 중인 임베딩 모델
# model = SentenceTransformer("BM-K/KoSimCSE-roberta")
#
# # 유사 쌍
# similar_pairs = [
#     ("기술", "기술 산업 최신 이슈"),
#     ("반도체", "AI 및 반도체 산업 동향에 대한 뉴스"),
#     ("AI", "인공지능 시장 동향")
# ]
#
# # 비유사 쌍
# dissimilar_pairs = [
#     ("기술", "음식 레시피"),
#     ("반도체", "여행 명소 추천"),
#     ("AI", "자동차 엔진 구조")
# ]
#
# print("\n🔄 유사도 테스트 결과\n-----------------------------")
#
# # ✅ 유사 쌍 테스트
# print("예상 유사 쌍:")
# for q1, q2 in similar_pairs:
#     vec1 = model.encode(q1)
#     vec2 = model.encode(q2)
#     sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
#     print(f"'{q1}' vs '{q2}' → 유사도: {sim:.4f}")
#
# # ❌ 비유사 쌍 테스트
# print("\n예상 비유사 쌍:")
# for q1, q2 in dissimilar_pairs:
#     vec1 = model.encode(q1)
#     vec2 = model.encode(q2)
#     sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
#     print(f"'{q1}' vs '{q2}' → 유사도: {sim:.4f}")

# test_domain_enrichment.py
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("jhgan/ko-sroberta-multitask")


def enrich_query(query, domain="financial"):
    domain_prefixes = {
        "financial": "금융 및 경제 관점에서 ",
        "tech": "기술 산업 관점에서 ",
        "semiconductor": "반도체 산업 관점에서 "
    }
    return domain_prefixes.get(domain, "") + query


# 테스트 쿼리 쌍들
test_pairs = [
    # 원본 vs 도메인 강화
    ("반도체", enrich_query("반도체", "semiconductor")),
    ("AI", enrich_query("AI", "tech")),

    # 도메인 강화 쿼리 vs 관련 문서
    (enrich_query("반도체", "semiconductor"), "반도체 산업은 최근 공급망 이슈로 인해 가격 변동이 있습니다."),
    (enrich_query("AI", "tech"), "인공지능 기술은 다양한 산업에 혁신을 가져오고 있습니다.")
]

# 테스트 실행
print("🔍 도메인 강화 쿼리 테스트\n-----------------------------")
for q1, q2 in test_pairs:
    vec1 = model.encode(q1)
    vec2 = model.encode(q2)
    cosine_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    print(f"'{q1}' vs '{q2}' → 유사도: {cosine_sim:.4f}")