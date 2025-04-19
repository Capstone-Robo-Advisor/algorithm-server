# test_threshold_sensitivity.py
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("jhgan/ko-sroberta-multitask")

test_examples = [
    ("반도체", "반도체 산업 동향 및 시장 전망"),
    ("AI", "인공지능 기술 발전 방향"),
    ("기술", "혁신 기술이 산업에 미치는 영향"),
    ("반도체", "컴퓨터 프로세서 생산 과정"),
    ("반도체", "여행 계획 세우기"),  # 비관련 예시
]

thresholds = [0.6, 0.5, 0.4, 0.3, 0.2, 0.15, 0.1]

print("🎯 임계값 민감도 테스트\n-----------------------------")
for threshold in thresholds:
    pass_count = 0

    for query, doc in test_examples:
        vec1 = model.encode(query)
        vec2 = model.encode(doc)
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

        if similarity >= threshold:
            pass_count += 1

    print(
        f"임계값 {threshold:.2f}: {pass_count}/{len(test_examples)} 항목 통과 ({pass_count / len(test_examples) * 100:.1f}%)")