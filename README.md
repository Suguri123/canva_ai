# 🎨 Canva AI Automation Studio

**Canva Connect API**와 최신 LLM(Google Gemini / OpenAI)을 연동하여, 브랜드 템플릿 기반의 카드뉴스/배너/홍보 디자인을 **원클릭으로 완전 자동 생성**하는 Python 자동화 솔루션입니다.

---

## 🌟 주요 기능

1. **공식 OAuth 2.0 PKCE 인증 지원**:
   - 보안 규격에 맞춘 `code_verifier` & `code_challenge` (S256) 자동 처리.
   - 원클릭 Canva 로그인 및 자동 토큰 갱신(`refresh_token`).
2. **템플릿 자동 감지 및 스키마 분석**:
   - Canva 계정의 **Brand Template** 목록을 조회하고, 각 템플릿의 텍스트/이미지 데이터셋 필드를 자동 추출합니다.
3. **AI 기반 문구/카피라이팅 자동 생성**:
   - 사용자가 원하는 디자인 주제만 입력하면, 템플릿 필드 규격에 맞는 카피라이팅을 자동 생성합니다.
   - Google Gemini 1.5 Flash / OpenAI 지원 (API 키 미등록 시 스마트 룰 기반 생성 지원).
4. **Canva Autofill API 연동**:
   - Canva 백엔드로 비동기 Autofill 작업을 전송하여 템플릿에 데이터를 주입하고 완성된 디자인 URL을 반환합니다.
5. **웹 대시보드 & CLI 모드 제공**:
   - 비개발자도 쓰기 편한 직관적인 웹 인터페이스 (`server.py`)
   - 배치 작업 및 스케줄러(cron) 연동을 위한 터미널 CLI 도구 (`cli_autofill.py`)

---

## 🚀 시작하기

### 1. 사전 준비 (Canva Developer Portal 설정)

Canva Connect API를 사용하려면 무료 Canva 개발자 등록이 필요합니다:

1. [Canva Developers 포털](https://www.canva.com/developers)에 접속하여 로그인합니다.
2. **"Create an integration"** (또는 앱 생성) 버튼을 클릭합니다.
3. 앱 설정 화면에서 다음 항목을 구성합니다:
   - **Redirect URI**: `http://localhost:8000/callback` 등록
   - **Scopes (권한)**:
     - `asset:read`
     - `asset:write`
     - `brandtemplate:meta:read`
     - `brandtemplate:content:read`
     - `design:content:write`
     - `design:meta:read`
     - `profile:read`
4. 발급된 **Client ID**와 **Client Secret**을 복사합니다.

> 💡 **참고**: Canva의 **Brand Template** 및 **Autofill API** 기능은 Canva Pro, Canva Teams, Canva Enterprise 계정에서 지원됩니다. 디자인을 템플릿으로 게시할 때 "브랜드 템플릿(Brand Template)"으로 저장해 두어야 연동할 수 있습니다.

---

### 2. 환경 변수 설정 (`.env`)

프로젝트 루트의 `.env` 파일에 발급받은 키를 입력합니다:

```env
CANVA_CLIENT_ID=여러분의_CANVA_CLIENT_ID
CANVA_CLIENT_SECRET=여러분의_CANVA_CLIENT_SECRET
CANVA_REDIRECT_URI=http://localhost:8000/callback

# (선택) 고품질 AI 문구 생성을 원할 경우 입력
GEMINI_API_KEY=
OPENAI_API_KEY=

HOST=127.0.0.1
PORT=8000
```

---

### 3. 패키지 설치

터미널에서 필요한 패키지를 설치합니다:

```bash
pip install -r requirements.txt
```

---

### 4. 웹 대시보드 실행

FastAPI 기반의 대시보드를 실행합니다:

```bash
python server.py
```

브라우저에서 `http://localhost:8000`으로 접속합니다.

#### 💡 사용 순서
1. **[Step 1] Canva 연동**: `Canva 로그인 및 연동` 버튼을 클릭하여 권한을 승인합니다.
2. **[Step 2] 템플릿 선택**: 내 브랜드 템플릿을 선택하면 변경 가능한 필드가 자동 감지됩니다.
3. **[Step 3] AI 문구 생성**: 주제를 입력하고 `AI 문구 생성`을 누르면 필드에 알맞은 문구가 채워집니다.
4. **[Step 4] 디자인 생성**: `Canva 디자인 자동 생성 시작`을 누르면 즉시 새 디자인이 만들어지며 Canva에서 바로 열 수 있는 링크가 제공됩니다!

---

### 5. CLI 배치 자동화 모드

터미널 스크립트나 외부 시스템(CRM, 웹훅)에서 호출할 수 있는 CLI 도구도 지원합니다:

```bash
python cli_autofill.py --template "DAFb1234567" --topic "가을맞이 캠핑 용품 특별전" --title "2026 캠핑 프로모션 배너"
```

---

## 📁 프로젝트 구조

```
canva_ai/
├── README.md               # 가이드 문서
├── requirements.txt        # 의존성 패키지 목록
├── .env.example            # 환경 변수 예시
├── .env                    # 실제 환경 설정 (API 키)
├── config.py               # 설정 및 토큰 관리 모듈
├── canva_api.py            # Canva Connect API 클라이언트 (OAuth PKCE, Autofill)
├── ai_service.py           # Gemini / OpenAI 문구 생성기
├── server.py               # FastAPI 웹 서버 및 REST API
├── cli_autofill.py         # 터미널용 자동화 배치 스크립트
├── static/
│   └── index.html          # 모던 반응형 웹 대시보드 UI
└── tokens.json             # (자동 생성) 발급받은 OAuth 토큰 저장소
```
