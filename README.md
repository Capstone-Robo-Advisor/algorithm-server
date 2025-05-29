# 📊 AI 기반 투자 포트폴리오 추천 백엔드 서버 (FastAPI)

이 프로젝트는 **사용자의 투자 성향 및 최신 금융 뉴스**를 기반으로 종목을 추천하고, **PyPortfolioOpt** 알고리즘을 통해 포트폴리오를 최적화하는 **FastAPI 기반 백엔드 서버**입니다.  
GPT API를 활용한 RAG(Retrieval-Augmented Generation) 시스템과 PyPortfolioOpt 기반 자산 최적화 기능을 제공합니다.

---

## ✨ 주요 기능 (Features)

- 📌 투자 성향 정보 수집 (프론트로부터 입력 받음)
- 📌 GPT API를 통한 뉴스 기반 종목 추천
- 📌 PyPortfolioOpt를 활용한 비중 최적화
- 📌 ChromaDB 기반 벡터 검색 시스템 (RAG)
- 📌 MongoDB Atlas, MariaDB 연동
- 📌 Swagger(OpenAPI) 기반 API 테스트 제공

---

## 🛠 사용 기술 (Tech Stack)

| 구분       | 기술                                                         |
|------------|--------------------------------------------------------------|
| Backend    | FastAPI, Pydantic, Uvicorn                                   |
| AI 연동    | GPT API (OpenAI), sentence-transformers (`ko-sroberta`)     |
| Vector DB  | ChromaDB                                                     |
| DB         | MongoDB Atlas, MariaDB                                       |
| Financial  | PyPortfolioOpt                                               |
| Infra      | Docker, GCP / AWS EC2 (테스트용)                             |

---

## 📁 프로젝트 구조

```
app/
┣ db/
┃ ┗ database.py # DB 연결 설정
┣ models/
┃ ┗ model.py # MongoDB / MariaDB 모델 정의
┣ routers/
┃ ┣ member_router.py # 사용자 관련 API
┃ ┣ portfolio_router.py # 포트폴리오 추천 관련 API
┃ ┗ stock_router.py # 종목 정보 관련 API
┣ schemas/
┃ ┗ [Pydantic 스키마 정의]
┣ services/
┃ ┣ member_service.py # 사용자 서비스 로직
┃ ┣ portfolio_service.py # 포트폴리오 최적화 로직
┃ ┗ rag_service.py # GPT + ChromaDB 기반 종목 추천 로직
┗ main.py # FastAPI 앱 진입점
```

---

## 🚀 설치 및 실행

### 1. 클론 및 환경 구성

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
python -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
```

### 2. 환경변수 설정
`.env` 파일을 루트 디렉토리에 생성하고 다음 항목을 설정합니다:

```bash
OPENAI_API_KEY=sk-xxx
DB_URL=mongodb+srv://...
CHROMA_PERSIST_DIR=./chroma
```

### 3. 서버 실행
```bash
uvicorn app.main:app --reload
```

---

## 📚 API 문서
FastAPI는 자동으로 Swagger 문서를 생성합니다:

Swagger UI: http://localhost:8000/docs

---

## 🧠 GPT 기반 추천 흐름 (RAG + PyPortfolioOpt)
```
flowchart TD
    A[사용자 입력: 포트폴리오 개수/종목 수/테마] --> B[MongoDB에서 기사 검색]
    B --> C[ChromaDB 임베딩 검색]
    C --> D[GPT API 호출 (RAG 프롬프트)]
    D --> E[종목 리스트 생성]
    E --> F[PyPortfolioOpt로 비중 최적화]
    F --> G[프론트로 결과 전달]
```

---

## 🔧 향후 개선 사항
- GPT 응답 캐싱 및 지연 최소화
- 포트폴리오 백테스트 및 리스크 분석 기능 추가
- 종목 추천의 설명 개선 (왜 이 종목이 추천되었는지)
- 다국어 응답 처리 및 사용자 로컬화 기능

---

## 참고 문헌

- FastAPI 공식 문서
- FMP API 공식 문서 (Financial Modeling Prep)
- DeepSearch News API
- ChromaDB GitHub
- PyPortfolioOpt 공식 문서
- PyPortfolioOpt GitHub
