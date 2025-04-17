import re

from datetime import datetime, timedelta

from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor
import asyncio
import logging

from app.common.db.vector.vector_util import VectorUtil

embedding_model = SentenceTransformer("jhgan/ko-sroberta-multitask")
vector_util = VectorUtil()
collection = vector_util.get_collection()

comma = ","

# 로거 설정
logger = logging.getLogger(__name__)

# 쓰레드 풀
executor = ThreadPoolExecutor(max_workers=4)

def clean_text(text: str) -> str:
    """GPT 프롬프트용 텍스트 정제"""
    text = re.sub(r"<[^>]+>", "", text)  # HTML 태그 제거
    text = re.sub(r"\s+", " ", text)     # 연속 공백 제거
    text = text.strip()
    return text

# rag 기반 서비스를 제공
class RagService:
    
    def __init__(self):
        """RagService 초기화 - 전역 collection 객체 사용"""
        global collection
        self.collection = collection

    # 뉴스 데이터를 반환
    def get_news_data(self, categories, n_results=5, min_relevance_score=0.6):
        """관련성 점수 기반으로 뉴스 필터링"""
        query = comma.join(categories)
        query_embedding = embedding_model.encode(query)

        # 더 많은 결과를 가져와서 필터링
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results * 2,  # 더 많은 후보 검색
            include=["documents", "metadatas", "distances"]  # 거리 정보 포함
        )

        # 결과와 관련성 점수 결합
        news_with_scores = []
        for i, (doc, meta, distance) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0])):

            # 거리를 유사도 점수로 변환 (1에 가까울수록 유사)
            similarity_score = 1 - min(distance, 1.0)

            if similarity_score >= min_relevance_score:
                news_with_scores.append({
                    "title": meta.get("title", ""),
                    "source": meta.get("publisher", ""),
                    "published_date": meta.get("published_at", ""),
                    "summary": doc,
                    "relevance_score": similarity_score
                })

        # 관련성 점수로 정렬하고 상위 n_results 반환
        news_articles = sorted(news_with_scores, key=lambda x: x["relevance_score"], reverse=True)[:n_results]
        return news_articles

    # 뉴스 데이터를 저장
    async def save_news_data(self, news_articles):
        """뉴스 데이터를 벡터 DB에 저장"""
        if not news_articles:
            logger.warning("저장할 뉴스 기사가 없습니다.")
            return

        loop = asyncio.get_event_loop()
        success_count = 0
        error_count = 0

        for article in news_articles:
            try:
                # 필수 필드 확인
                article_id = str(article.get("id", ""))
                if not article_id:
                    logger.warning("기사 ID가 없어 건너뜀")
                    error_count += 1
                    continue

                # 중복 기사 제거 로직 추가
                existing_ids = self.collection.get(ids=[article_id])["ids"]

                if existing_ids:
                    logger.info(f"중복 기사 생략 : ID = {article_id}")
                    continue

                # 텍스트 필드 안전하게 가져오기
                summary_ko = article.get("summary_ko", "") or ""
                summary = article.get("summary", "") or ""
                reason = article.get("reason", "") or ""

                summary_text = summary_ko if summary_ko else summary
                full_text = f"{summary_text}\n{reason}".strip()
                full_text = clean_text(full_text)  # ✅ 정제 함수 적용

                if not full_text:
                    logger.warning(f"기사 {article_id}의 텍스트가 비어 있어 건너뜀")
                    error_count += 1
                    continue

                # 임베딩 생성
                embedding = await loop.run_in_executor(executor, embedding_model.encode, full_text)

                # 메타데이터 구성 (None 값 처리)
                metadata = {
                    "title": article.get("title_ko", "") or article.get("title", "") or "",
                    "published_at": article.get("published_at", ""),
                    "importance": article.get("importance", "medium"),
                    "publisher": article.get("publisher", ""),
                    "theme": article.get("theme", "")
                }

                # 메타데이터의 None 값 처리
                for key, value in metadata.items():
                    if value is None:
                        metadata[key] = ""

                # logger.info(f"🧪 기사 저장 시도: ID={article_id}, 제목={metadata['title'][:30]}, 임베딩 길이={len(embedding)}")

                # 벡터 DB에 저장
                self.collection.add(
                    documents=[full_text],
                    embeddings=[embedding.tolist()],
                    ids=[article_id],
                    metadatas=[metadata]
                )

                success_count += 1

                # logger.info(f"✅ 저장 완료: {article_id}")

            except Exception as e:
                logger.error(f"기사 {article.get('id', 'unknown')} 저장 중 오류: {str(e)}")
                error_count += 1

        logger.info(f"뉴스 데이터 저장 완료: 성공 {success_count}건, 실패 {error_count}건")
        return success_count

    # 오래된 기사 데이터 삭제
    async def delete_old_documents(self, days: int = 30):
        """지정된 날짜 이전의 문서를 삭제 (기본 30일 이전)

        :param days:
        :return:
        """
        # 현재 날짜에서 days일 이전 계산
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        logger.info(f"🧹 {cutoff_date} 이전의 기사 제거 시도 중...")

        try:
            # 1. 모든 문서의 메타데이터를 가져옴
            all_results = self.collection.get(include=["metadatas"])

            # 2. 파이썬에서 날짜 비교 수행
            old_ids = []
            for i, metadata in enumerate(all_results.get("metadatas", [])):
                if not metadata:
                    continue

                published_at = metadata.get("published_at", "")
                if not published_at:
                    continue

                # 날짜 형식 비교 (YYYY-MM-DD 형식 가정)
                if published_at < cutoff_date:
                    old_ids.append(all_results["ids"][i])

            if not old_ids:
                logger.info("🟢 삭제 대상 문서 없음")
                return 0

            logger.info(f"🗑 {len(old_ids)}개 문서 삭제 시작...")

            # 3. 오래된 문서 삭제
            self.collection.delete(ids=old_ids)

            logger.info(f"✅ {len(old_ids)}개 문서 삭제 완료")
            return len(old_ids)

        except Exception as e:
            logger.error(f"오래된 문서 삭제 중 오류: {str(e)}")
            return 0