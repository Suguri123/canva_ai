import json
import requests
from typing import Dict, Any
import config

class AIService:
    @staticmethod
    def generate_content_for_template(topic: str, dataset_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        주어진 주제(topic)와 템플릿의 데이터셋 스키마(dataset_schema)에 맞추어
        Canva Autofill에 바로 사용할 수 있는 텍스트/데이터를 생성합니다.
        """
        # 데이터셋 내의 텍스트 필드 추출
        # schema 구조: {"dataset": {"field_name": {"type": "text"}, ...}}
        raw_dataset = dataset_schema.get("dataset", {})
        text_fields = []
        for name, info in raw_dataset.items():
            if isinstance(info, dict) and info.get("type") == "text":
                text_fields.append(name)
            elif isinstance(info, str) and info == "text":
                text_fields.append(name)

        if not text_fields:
            # 텍스트 필드가 명시되지 않은 경우 기본 추천 필드 사용
            text_fields = ["headline", "subheadline", "cta_text"]

        # 1. Gemini API 키가 있는 경우
        if config.GEMINI_API_KEY:
            try:
                return AIService._generate_with_gemini(topic, text_fields)
            except Exception as e:
                print(f"[AI Service] Gemini 호출 실패 ({e}), Fallback 생성기를 사용합니다.")

        # 2. OpenAI API 키가 있는 경우
        if config.OPENAI_API_KEY:
            try:
                return AIService._generate_with_openai(topic, text_fields)
            except Exception as e:
                print(f"[AI Service] OpenAI 호출 실패 ({e}), Fallback 생성기를 사용합니다.")

        # 3. API 키가 없거나 실패한 경우 규칙 기반 지능형 Mock 생성
        return AIService._generate_smart_fallback(topic, text_fields)

    @staticmethod
    def _generate_with_gemini(topic: str, text_fields: list) -> Dict[str, Any]:
        """Google Gemini REST API 호출"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={config.GEMINI_API_KEY}"
        
        prompt = f"""
다음 주제에 맞춰 Canva 디자인 템플릿에 들어갈 한국어 텍스트 문구를 작성하세요.
주제: "{topic}"

작성해야 할 필드 목록:
{json.dumps(text_fields, ensure_ascii=False)}

반드시 각 필드 이름을 키로 하고, 작성된 문구를 값으로 하는 유효한 JSON 객체만 반환하세요.
예시:
{{
  "title": "여름맞이 특별 할인전",
  "subtitle": "최대 50% 할인 혜택을 지금 만나보세요"
}}
마크다운 코드 블록(```json) 없이 순수 JSON만 출력하세요.
"""
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "responseMimeType": "application/json"
            }
        }

        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        parsed = json.loads(raw_text)

        # Canva Autofill 포맷으로 래핑
        result = {}
        for k, v in parsed.items():
            result[k] = {"type": "text", "text": str(v)}
        return result

    @staticmethod
    def _generate_with_openai(topic: str, text_fields: list) -> Dict[str, Any]:
        """OpenAI API 호출"""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {config.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        prompt = f"""
다음 주제에 맞춰 Canva 템플릿에 적용할 카피라이팅 텍스트를 작성하세요.
주제: "{topic}"
필드 목록: {json.dumps(text_fields, ensure_ascii=False)}

반드시 순수 JSON 객체(키: 필드명, 값: 작성 문구)만 반환하세요.
"""
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)

        result = {}
        for k, v in parsed.items():
            result[k] = {"type": "text", "text": str(v)}
        return result

    @staticmethod
    def _generate_smart_fallback(topic: str, text_fields: list) -> Dict[str, Any]:
        """API 키가 없을 때 기본 규칙 기반으로 생성하는 Fallback 데이터"""
        result = {}
        for field in text_fields:
            field_lower = field.lower()
            if any(k in field_lower for k in ["title", "headline", "제목"]):
                text = f"{topic} 특별 안내"
            elif any(k in field_lower for k in ["sub", "desc", "content", "설명", "본문"]):
                text = f"최고의 품질과 특별한 혜택으로 만나는 {topic}입니다."
            elif any(k in field_lower for k in ["cta", "button", "버튼", "action"]):
                text = "자세히 보기"
            elif any(k in field_lower for k in ["date", "날짜", "기간"]):
                text = "2026.10.15 - 2026.10.31"
            elif any(k in field_lower for k in ["price", "할인", "sale"]):
                text = "UP TO 30% OFF"
            else:
                text = f"{topic} - {field}"
            result[field] = {"type": "text", "text": text}
        return result
