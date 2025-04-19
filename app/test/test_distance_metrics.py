# test_distance_metrics.py
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("jhgan/ko-sroberta-multitask")

test_pairs = [
    ("반도체", "반도체 산업 동향 보고서"),
    ("AI", "인공지능 시장 동향"),
    ("기술", "기술 혁신 사례")
]

print("📏 거리 측정 방식 비교\n-----------------------------")
for q1, q2 in test_pairs:
    vec1 = model.encode(q1)
    vec2 = model.encode(q2)

    # 코사인 유사도 (방향만 고려)
    cosine = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    # 내적 (방향과 크기 모두 고려)
    dot_product = np.dot(vec1, vec2)

    # 유클리드 거리 (공간상 실제 거리)
    euclidean = np.linalg.norm(vec1 - vec2)

    print(f"'{q1}' vs '{q2}':")
    print(f"  - 코사인 유사도: {cosine:.4f} (높을수록 유사)")
    print(f"  - 내적: {dot_product:.4f} (높을수록 유사)")
    print(f"  - 유클리드 거리: {euclidean:.4f} (낮을수록 유사)")