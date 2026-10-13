import os
import json
from pathlib import Path
from dotenv import load_dotenv

# .env 로드
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

def reload_env():
    load_dotenv(BASE_DIR / ".env", override=True)

def get_client_id() -> str:
    reload_env()
    return os.getenv("CANVA_CLIENT_ID", "").strip()

def get_client_secret() -> str:
    reload_env()
    return os.getenv("CANVA_CLIENT_SECRET", "").strip()

def get_redirect_uri() -> str:
    reload_env()
    return os.getenv("CANVA_REDIRECT_URI", "http://127.0.0.1:8000/callback").strip()

CANVA_CLIENT_ID = get_client_id()
CANVA_CLIENT_SECRET = get_client_secret()
CANVA_REDIRECT_URI = get_redirect_uri()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

TOKEN_FILE = BASE_DIR / "tokens.json"
SESSION_FILE = BASE_DIR / "oauth_session.json"

REQUIRED_SCOPES = [
    "asset:read",
    "asset:write",
    "brandtemplate:meta:read",
    "brandtemplate:content:read",
    "design:content:write",
    "design:meta:read",
    "profile:read"
]

def load_tokens() -> dict:
    """저장된 OAuth 토큰 반환"""
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_tokens(token_data: dict):
    """OAuth 토큰 저장"""
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2, ensure_ascii=False)

def clear_tokens():
    """OAuth 토큰 삭제"""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()

def save_session(session_data: dict):
    """PKCE state / code_verifier 저장"""
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

def load_session() -> dict:
    """PKCE state / code_verifier 불러오기"""
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}
