import pymongo
import os
import logging

from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# 환경 변수 로드
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")

# 로거 객체 선언
logger = logging.getLogger(__name__)

# TODO: ChromaDB로 받아오는 걸로 바꾸기
class NewsService:
    @staticmethod
    def get_recent_news(limit: int = 100, themes: List[str] = None) -> List[Dict[str, Any]]:
        """MongoDB 에서 최근 뉴스 기사를 가져옵니다

        :param limit: 가져올 기사 수
        :param themes: 특정 테마 관련 기사 필터링
        :return: 뉴스 기사 목록 가져온다.
        """
        if not themes:
            return []

        try:
            client = MongoClient(MONGODB_URI)
            db = client["deepsearch_news"]
            collection = db["articles"]
            logger.info("✅ 몽고 DB 연결 성공!")

            total_docs = collection.count_documents({})
            logger.info(f"전체 뉴스 기사 수 : {total_docs}")

            all_theme_keywords = []
            # 테마 기반 필터링 쿼리 구성

            # 테마 키워드 매핑 정의
            theme_keywords_map = {
                "에너지": ["energy", "oil", "gas", "renewable", "solar", "wind", "에너지", "석유", "가스", "재생에너지"],
                "반도체": ["semiconductor", "chip", "processor", "TSMC", "intel", "nvidia", "반도체", "칩", "프로세서"],
                "기술": ["technology", "tech", "AI", "artificial intelligence", "software", "기술", "인공지능",
                       "소프트웨어", "디지털", "IT", "정보기술", "빅데이터", "클라우드", "블록체인", "사물인터넷", "IoT"],
                "원자재": ["commodity", "material", "raw material", "mining", "metals", "원자재", "광물", "금속", "채굴"],
                "금융": ["finance", "banking", "investment", "financial", "bank", "stocks", "금융", "은행", "투자", "주식", "펀드",
                       "금융시장"]
            }

            # 각 테마의 키워드를 통합 리스트에 추가
            for theme in themes:
                keywords = theme_keywords_map.get(theme, [theme])
                all_theme_keywords.extend(keywords)
                logger.info(f"'{theme}' 테마 키워드 추가: {keywords}")

            logger.info(f"통합된 키워드 수: {len(all_theme_keywords)}")

            # 모든 키워드에 대해 통합 쿼리 생성
            keyword_query = {"$or": []}
            for field in ["title", "title_ko", "summary", "summary_ko"]:
                for kw in all_theme_keywords:
                    keyword_query["$or"].append({field: {"$regex": kw, "$options": "i"}})

            logger.info(f"다중 테마 쿼리 생성 완료. 쿼리 조건 수: {len(keyword_query['$or'])}")


            # 최신 기사부터 가져오기
            articles = list(collection.find(keyword_query).sort("published_at", pymongo.DESCENDING).limit(limit))
            logger.info(f"다중 테마 관련 기사 찾음: {len(articles)}개")

            # 결과가 없으면 필드 정보 출력
            if len(articles) == 0 and total_docs > 0:
                sample = list(collection.find().limit(1))[0]
                logger.info(f"샘플 문서 필드: {list(sample.keys())}")

            # MongoDB 의 _id 객체는 JSON 직렬화가 불가능하므로 문자열로 변환
            for article in articles:
                if "_id" in article:
                    article["_id"] = str(article["_id"])

                # ISO 형식의 날짜 문자열을 datetime 객체로 변환 (필요한 경우)
                if "published_date" in article and isinstance(article["published_date"], str):
                    try:
                        article["published_date"] = datetime.fromisoformat(article["published_date"].replace("Z", "+00:00"))
                    except ValueError:
                        pass

            return articles

        except Exception as e:
            logger.error(f"❌ MongoDB에서 뉴스 데이터 가져오기 실패: {e}")
            return []