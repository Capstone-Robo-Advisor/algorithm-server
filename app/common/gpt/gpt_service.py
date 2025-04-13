import os
import json
import traceback

import openai
import re
import logging

from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gpt_service")

class GPTService:
    @staticmethod
    async def generate_portfolio_recommendations(
            portfolio_count: int,
            stocks_per_portfolio: int,
            theme: str,
            news_articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """GPT API 를 사용하여 포트폴리오 추천을 생성합니다.
        :param portfolio_count: 생성할 포트폴리오 수
        :param stocks_per_portfolio: 각 포트폴리오당 주식 수
        :param theme: 투자 테마 (에너제, 반도체, 기술, 원자재 등)
        :param news_articles: 관련 뉴스 기사 목록
        :return: 포트폴리오 추천 목록
        """
        try:
            # API 키 설정
            client = openai.OpenAI(api_key=OPENAI_API_KEY)

            # 프롬프트 로깅
            logger.info("GPT API 호출 준비: 테마=%s, 포트폴리오 수=%d", theme, portfolio_count)
            logger.info("뉴스 기사 수: %d", len(news_articles))

            # 뉴스 기사 요약을 위한 전처리
            news_summaries = []
            for article in news_articles[:5]:  # 상위 100개 기사 사용
                title = article.get("title", "")
                source = article.get("source", "")
                published_date = article.get("published_date", "")
                summary = article.get("summary", article.get("content", "")[:200])

                news_summaries.append(f"제목: {title}\n출처: {source}\n날짜: {published_date}\n요약: {summary[:200]}...")

            news_text = "\n\n".join(news_summaries)



            #GPT에 전달할 프롬프트 구성
            prompt = f"""
당신은 주식 포트폴리오 추천 전문가입니다. 다음 정보를 바탕으로 투자자에게 적합한 포트폴리오를 추천해주세요:

1. 투자자는 총 {portfolio_count}개의 포트폴리오를 구성하고 싶어합니다.
2. 각 포트폴리오는 {stocks_per_portfolio}개의 주식으로 구성되어야 합니다.
3. 투자자가 관심 있는 테마는 '{theme}'입니다.
4. 다음은 최근 관련 뉴스 기사입니다:  

{news_text}

위 정보를 바탕으로:
1. {portfolio_count}개의 서로 다른 포트폴리오를 추천해주세요.
2. 각 포트폴리오는 {stocks_per_portfolio}개의 주식으로 구성하고, 각 주식의 비율(%)을 명시해주세요.
3. 각 포트폴리오에 대한 간략한 설명과 투자 전략을 제공해주세요.
4. 포트폴리오 구성 시 분산투자 원칙을 고려해주세요.

응답은 다음 JSON 형식으로 제공해주세요:
```json
[
  {{
    "name": "포트폴리오 1",
    "stocks": [
      {{"ticker": "AAPL", "name": "Apple Inc.", "allocation": 25.0}},
      {{"ticker": "MSFT", "name": "Microsoft Corp.", "allocation": 25.0}}
    ],
    "description": "이 포트폴리오는 기술 섹터에 중점을 두고..."
  }}
]
```

각 주식의 ticker(심볼)와 회사명(name)을 정확히 표기해주세요.
"""

            # API 호출 직전 로깅
            logger.info("GPT API 호출 시작...")

            # GPT API 호출
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system",
                     "content": "You are a financial advisor specialized in stock portfolio recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            # GPT API 호출 결과 로딩
            logger.info("GPT API 호출 완료: 응답 토큰 수 = %d", response.usage.completion_tokens)

            # 응답 내용 로깅 (일부만)
            content = response.choices[0].message.content
            # 안전한 방식으로 로깅
            # safe_preview = repr(content[:200] + "...")
            # logger.info("GPT 응답 내용 (처음 200자):\n%s", safe_preview)

            # GPT 응답 파싱
            try:
                # json_str 변수 미리 초기화
                json_str = ""
                
                # 디버깅용 파일에 응답 저장
                try:
                    with open("gpt_response.txt", "w") as f:
                        f.write(content)
                except:
                    pass
                
                # 정규식을 사용한 JSON 추출
                json_pattern = r"```(?:json)?\s*([\s\S]*?)```"
                matches = re.findall(json_pattern, content)

                if matches:
                    json_str = matches[0].strip()
                    logger.info("✅ 코드 블록에서 JSON 추출 성공")
                else:
                    # 코드 블록이 없는 경우 전체 내용에서 JSON 형식 찾기
                    json_str = content
                    # 처음과 마지막 [ ] 찾기
                    if '[' in json_str and ']' in json_str:
                        start = json_str.find('[')
                        end = json_str.rfind(']') + 1
                        json_str = json_str[start:end]
                        logger.info("전체 내용에서 [ ] 기반으로 JSON 추출")

                # JSON 일부 출력 - 안전한 방식으로 로깅
                logger.info("파싱할 JSON (처음 100자): %s", (json_str[:100] + "...") if len(json_str) > 100 else json_str)

                # 디버깅용 파일에 추출된 JSON 저장
                try:
                    with open("extracted_json.txt", "w") as f:
                        f.write(json_str)
                except:
                    pass

                # JSON 파싱
                portfolios = json.loads(json_str)
                logger.info("JSON 파싱 성공: 포트폴리오 %d개 추출됨", len(portfolios))
                return portfolios

            except Exception as e:
                error_json = "정의되지 않음"
                if 'json_str' in locals() and json_str:
                    # 오류 난 JSON의 시작 부분만 안전하게 출력
                    error_json = json_str[:50] + "..." if len(json_str) > 50 else json_str
                
                logger.error("JSON 파싱 실패: %s", str(e))
                # repr()을 사용하여 안전하게 출력
                logger.error("파싱 시도한 문자열 시작 부분: %s", repr(error_json))
                return []

        except Exception as e:
            # 안전한 방식으로 로깅
            logger.error("GPT API 호출 또는 처리 중 오류 발생: " + repr(e))
            logger.error(traceback.format_exc())
            return []