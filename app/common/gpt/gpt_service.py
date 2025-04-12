import os
import json
import openai

from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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

            # 뉴스 기사 요약을 위한 전처리
            news_summaries = []
            for article in news_articles[:5]:  # 상위 5개 기사만 사용
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
  {
    "name": "포트폴리오 1",
    "stocks": [
      {"ticker": "AAPL", "name": "Apple Inc.", "allocation": 25.0},
      {"ticker": "MSFT", "name": "Microsoft Corp.", "allocation": 25.0},
      ...
    ],
    "description": "이 포트폴리오는 기술 섹터에 중점을 두고..."
  },
  ...
]
```

각 주식의 ticker(심볼)와 회사명(name)을 정확히 표기해주세요.
"""
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

            # GPT 응답 파싱
            try:
                content = response.choices[0].message.content

                # JSON 부분 추출 (마크다운 코드 블록에서)
                json_str = content
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()

                # JSON 파싱
                portfolios = json.loads(json_str)
                return portfolios

            except Exception as e:
                print(f"GPT 응답 파싱 실패: {str(e)}")
                print(f"원본 응답: {content}")
                # 파싱 실패 시 빈 결과 반환
                return []

        except Exception as e:
            print(f"포트폴리오 추천 생성 실패 : {str(e)}")
            return []