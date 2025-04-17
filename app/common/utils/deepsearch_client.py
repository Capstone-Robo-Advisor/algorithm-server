import requests
import os
import logging

from typing import List, Dict, Any
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DeepSearchClient:
    BASE_URL = "https://api-v2.deepsearch.com/v1/global-articles"
    API_KEY = os.getenv("DEEPSEARCH_API_KEY")

    @staticmethod
    def fetch_articles(keyword: str, date_from: str, date_to: str, page_limit: int = 50) -> List[Dict[str, Any]]:

        all_articles = []

        try:
            for page in range(1, page_limit + 1):
                params = {
                    "date_from": date_from,
                    "date_to": date_to,
                    "keyword": keyword,
                    "page": page,
                    "page_size": 50,
                    "api_key": DeepSearchClient.API_KEY
                }

                logger.info(f"🔍 [DeepSearch] {keyword} | Page {page} 요청 중...")

                res = requests.get(DeepSearchClient.BASE_URL, params=params, timeout=10)

                if res.status_code != 200:
                    logger.warning(f"⚠️ 요청 실패 - 상태코드: {res.status_code}, 응답: {res.text}")
                    break

                data = res.json()
                items = data.get("data") or data.get("articles") or []
                all_articles.extend(items)

                logger.info(f"✅ [DeepSearch] Page {page}: {len(items)}건 수집됨")

                if len(items) < 50:
                    logger.info("⏹ 마지막 페이지 도달")
                    break

        except Exception as e:
            logger.error(f"❌ DeepSearch API 호출 실패: {e}")

        return all_articles
