import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.common.utils.deepsearch_client import DeepSearchClient
from app.common.rag.rag_service import RagService  # 대문자로 시작하는 클래스명으로 수정

# 로거 설정
logger = logging.getLogger(__name__)


class DailyNewsCollector:
    """DeepSearch API를 사용한 일일 뉴스 수집 및 RAG 시스템에 저장 서비스
    RAG(Retrieval-Augmented Generation) 시스템에 저장하는 서비스

    이 클래스는 다음 기능을 제공합니다.
    1. 정기적인 뉴스 수집 스케줄링 (매일 새벽 3시)
    2. 저장된 테마 키워드에 대한 뉴스 기사 검색
    3. 수집된 뉴스의 RAG 시스템 저장 (벡터 DB에 임베딩과 함께 저장)
    4. 초기 데이터 수집 (서버 시작 시)

    """

    # 관심 테마 목록 - 각 키워드는 DeepSearch API 의 검색어로 사용됨
    # 이 키워드들은 포트폴리오 추천 시 사용된는 테마와 일치하도록 설정되어 있음
    DEFAULT_THEMES = [
        "에너지",
        "철강",
        "건설",
        "여행",
        "은행",
        "증권",
        "반도체",
        "AI",
        "5G",
        "부동산"
    ]

    # 싱글톤 인스턴스 - 전체 애플리케이션에서 하나의 인스턴스만 사용
    _instance = None

    @classmethod
    def get_instance(cls):
        """DailyNewsCollector의 싱글톤 인스턴스 반환

        Returns: DailyNewsCollector : 싱글톤 인스턴스

        사용 예 : collector = DailyNewsCollector.get_instance()
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """RAG 서비스 초기화 및 스케줄러 설정"""
        # RAG 서비스 초기화
        self.rag_service = RagService()

        # 스케줄러 초기화
        self.scheduler = BackgroundScheduler()
        self._setup_scheduler()

        logger.info("일일 뉴스 수집기 초기화 완료")

    def _setup_scheduler(self):
        """스케줄러 설정"""
        # 매일 새벽 3시에 뉴스 수집 실행
        self.scheduler.add_job(
            self.collect_and_store_daily_news,
            CronTrigger(hour=3, minute=0),
            id='daily_news_collection'
        )
        self.scheduler.start()
        logger.info("뉴스 수집 스케줄러 시작됨")

    async def collect_and_store_daily_news(self, themes: List[str] = None, days_back: int = 1) -> int:
        """
        지정된 테마에 대한 뉴스를 수집하고 RAG 시스템에 저장

        Args:
            themes: 수집할 테마 목록 (기본값: None, 기본 테마 사용)
            days_back: 몇 일 전 데이터까지 수집할지 (기본값: 1)

        Returns:
            총 저장된 기사 수
        """
        if themes is None:
            themes = self.DEFAULT_THEMES

        # 날짜 범위 설정
        today = datetime.now().strftime("%Y-%m-%d")
        past_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        logger.info(f"일일 뉴스 수집 시작 - 날짜: {past_date} ~ {today}, 테마: {', '.join(themes)}")

        total_stored = 0
        theme_stats = {}   # 테마별 통계

        # 각 테마별로 처리
        for theme in themes:
            logger.info(f"🔍테마 '{theme}' 뉴스 수집 중...")

            # DeepSearch API 호출
            articles = DeepSearchClient.fetch_articles(
                keyword=theme,
                date_from=past_date,
                date_to=today,
                page_limit=10  # 테마당 최대 10페이지
            )

            if not articles:
                logger.warning(f"테마 '{theme}'에 대한 최신 뉴스가 없습니다.")
                theme_stats[theme] = 0
                continue

            logger.info(f"테마 '{theme}'에 대해 {len(articles)}개 기사 수집됨")

            # 유효한 기사만 필터링
            valid_articles = []
            for i, article in enumerate(articles):
                try:
                    # None 값 체크 및 안전한 처리
                    article_id = article.get('id')
                    title = article.get('title_ko', '') or article.get('title', '') or ''
                    summary = article.get('summary_ko', '') or article.get('summary', '') or ''
                    publisher = article.get('publisher', '') or ''
                    published_at = article.get('published_at', '')
                    published_date = published_at.split('T')[0] if published_at else ''

                    # 중요 필드 누락 체크
                    if not article_id or not (title or summary):
                        logger.warning(f"⚠️ 테마 '{theme}' - 기사 #{i + 1}: 중요 필드 누락으로 건너뜀 (ID: {article_id})")
                        continue

                    # 날짜 유효성 검증
                    if published_date and (published_date < past_date or published_date > today):
                        logger.warning(f"⚠️ 테마 '{theme}' - 기사 #{i + 1}: 날짜 범위 밖의 기사 ({published_date})")

                    # 테마 정보 추가
                    article['theme'] = theme

                    # 검증된 기사 추가
                    valid_articles.append(article)

                except Exception as e:
                    logger.warning(f"테마 '{theme}' - 기사 #{i + 1}: 데이터 처리 중 오류 발생: {str(e)}")
                    continue

            if not valid_articles:
                logger.warning(f"테마 '{theme}': 유효한 기사가 없어 저장 건너뜀")
                theme_stats[theme] = 0
                continue

            logger.info(f"테마 '{theme}': 유효한 기사 {len(valid_articles)}개 중 {len(articles)}개 필터링됨")

            theme_stored = 0
            # RAG 서비스의 save_news_data 메서드 사용하여 저장
            try:
                # 배치 크기 지정 (메모리 초과 방지)
                batch_size = 50
                for i in range(0, len(valid_articles), batch_size):
                    batch = valid_articles[i:i + batch_size]
                    logger.info(
                        f"테마 '{theme}' - 배치 {i // batch_size + 1}/{(len(valid_articles) + batch_size - 1) // batch_size}: {len(batch)}개 기사 저장 시작")

                    # 비동기 메서드 실행을 위한 이벤트 루프 생성
                    # loop = asyncio.new_event_loop()
                    # asyncio.set_event_loop(loop)
                    #
                    # # save_news_data 메서드 호출
                    # loop.run_until_complete(self.rag_service.save_news_data(batch))
                    # loop.close()
                    # 저장 시작 시간
                    start_time = datetime.now()

                    await self.rag_service.save_news_data(batch)

                    logger.info(f"✅ 테마 '{theme}' - 배치 {i // batch_size + 1}: {len(batch)}개 기사 저장 완료")
                    total_stored += len(batch)

                    # 저장 소요 시간 계산
                    elapsed_time = (datetime.now() - start_time).total_seconds()

                    logger.info(
                        f"✅ 테마 '{theme}' - 배치 {i // batch_size + 1}: {len(batch)}개 기사 저장 완료 (소요 시간: {elapsed_time:.2f}초)")
                    theme_stored += len(batch)
                    total_stored += len(batch)

                # 테마별 통계 저장
                theme_stats[theme] = total_stored

            except Exception as e:
                logger.error(f"RAG 시스템 저장 중 오류 발생: {str(e)}")
                # 오류 디버깅을 위한 추가 정보
                import traceback
                logger.error(f"상세 오류: {traceback.format_exc()}")

            # 전체 통계 로깅
        logger.info(f"📊 일일 뉴스 수집 및 저장 완료 - 총 {total_stored}개 기사")
        logger.info("📈 테마별 저장 통계:")
        for theme, count in theme_stats.items():
            logger.info(f"  - {theme}: {count}개 기사")

        # 오래된 기사 자동 삭제 (30일 전 이전)
        try:
            deleted_count = await self.rag_service.delete_old_documents(days=30)
            logger.info(f"🧹 오래된 기사 {deleted_count}개 삭제 완료")
        except Exception as e:
            logger.error(f"❌ 오래된 기사 삭제 중 오류 발생: {str(e)}")

        return total_stored

    async def collect_initial_data(self):
        """초기 데이터 수집 (앱 시작 시 실행)"""
        logger.info("초기 뉴스 데이터 수집 시작")

        try:
            # 30일치 데이터 수집
            await self.collect_and_store_daily_news(days_back=30)

            # 데이터 수집 확인
            await self.check_collected_data()

            logger.info("🎉 초기 데이터 수집 및 확인 완료")
        except Exception as e:
            logger.error(f"❌ 초기 데이터 수집 중 오류: {str(e)}")

    def shutdown(self):
        """스케줄러 종료"""
        if hasattr(self, 'scheduler'):
            self.scheduler.shutdown()
            logger.info("뉴스 수집 스케줄러 종료됨")

    async def check_collected_data(self):
        """수집된 뉴스 데이터 상태 로깅"""
        logger.info("🔍 벡터 DB 데이터 수집 현황 확인 중...")

        try:
            # 벡터 DB 연결 확인
            collection = self.rag_service.collection

            # 모든 문서의 메타데이터 가져오기
            all_results = collection.get(include=["metadatas"])

            if not all_results or "ids" not in all_results or not all_results["ids"]:
                logger.warning("⚠️ 벡터 DB에 저장된 문서가 없습니다.")
                return

            total_docs = len(all_results["ids"])
            logger.info(f"📊 벡터 DB에 총 {total_docs}개 기사가 저장되어 있습니다.")

            # 날짜별 통계 수집
            date_counts = {}
            theme_counts = {}

            for metadata in all_results.get("metadatas", []):
                if not metadata:
                    continue

                # 날짜 정보 추출 및 저장
                published_at = metadata.get("published_at", "")
                pub_date = published_at.split("T")[0] if published_at and "T" in published_at else published_at

                if pub_date:
                    date_counts[pub_date] = date_counts.get(pub_date, 0) + 1

                # 테마 정보 추출 및 저장
                theme = metadata.get("theme", "unknown")
                theme_counts[theme] = theme_counts.get(theme, 0) + 1

            # 날짜 범위 확인
            if date_counts:
                dates = sorted(date_counts.keys())
                earliest_date = dates[0] if dates else "없음"
                latest_date = dates[-1] if dates else "없음"

                logger.info(f"📅 수집된 기사 날짜 범위: {earliest_date} ~ {latest_date}")

                # 날짜별 분포 로깅 (5일 단위로 요약)
                date_groups = {}
                for date, count in date_counts.items():
                    # 날짜를 5일 단위로 그룹화
                    if not date:
                        continue
                    try:
                        date_obj = datetime.strptime(date, "%Y-%m-%d")
                        group_key = date_obj.strftime("%Y-%m-%d") + " ~ " + (date_obj + timedelta(days=4)).strftime(
                            "%Y-%m-%d")
                        date_groups[group_key] = date_groups.get(group_key, 0) + count
                    except ValueError:
                        # 날짜 파싱 오류 처리
                        continue

                logger.info("📆 5일 단위 기사 분포:")
                for group, count in sorted(date_groups.items()):
                    logger.info(f"  - {group}: {count}개 기사")

            # 테마별 분포 로깅
            if theme_counts:
                logger.info("🏷️ 테마별 기사 수:")
                for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True):
                    logger.info(f"  - {theme}: {count}개 기사")

                # 누락된 테마 확인
                missing_themes = [t for t in self.DEFAULT_THEMES if t not in theme_counts]
                if missing_themes:
                    logger.warning(f"⚠️ 다음 테마의 기사가 없습니다: {', '.join(missing_themes)}")

            logger.info("✅ 데이터 수집 현황 확인 완료")

        except Exception as e:
            logger.error(f"❌ 데이터 확인 중 오류 발생: {str(e)}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")