import pymongo
import os

from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# 환경 변수 로드
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")

class NewsService:
    @staticmethod
    def get_recent_news(limit: int = 10, theme: Optional[str] = None) -> List[Dict[str, Any]]:
        """MongoDB 에서 최근 뉴스 기사를 가져옵니다

        :param limit: 가져올 기사 수
        :param theme: 특정 테마 관련 기사 필터링
        :return: 뉴스 기사 목록 가져온다.
        """
        try:
            client = MongoClient(MONGODB_URI)
            db = client.get_default_database()
            collection = db["news_articles"]

            # 테마 기반 필터링 쿼리 구성
            query = {}
            if theme:
                # 테마 관련 키워드를 포함하는 기사 검색
                theme_keywords = {
                    "에너지": ["energy", "oil", "gas", "renewable", "solar", "wind"],
                    "반도체": ["semiconductor", "chip", "processor", "TSMC", "intel", "nvidia"],
                    "기술": ["technology", "tech", "AI", "artificial intelligence", "software"],
                    "원자재": ["commodity", "material", "raw material", "mining", "metals"]
                }

                keywords = theme_keywords.get(theme, [theme])
                keyword_query = {"$or": [{"title": {"$regex": kw, "$options": "i"}} for kw in keywords]}
                query = keyword_query

            # 최신 기사부터 가져오기
            articles = list(collection.find(query).sort("published_date", pymongo.DESCENDING).limit(limit))

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
            print(f"MongoDB 에서 뉴스 데이터 가져오기 실패 : {str(e)}")
            return []