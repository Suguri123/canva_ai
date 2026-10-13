import base64
import hashlib
import json
import secrets
import time
import requests
from typing import Dict, Any, Optional

import config

CANVA_AUTH_BASE = "https://www.canva.com/api/oauth/authorize"
CANVA_API_BASE = "https://api.canva.com/rest/v1"

class CanvaAPIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class CanvaClient:
    @property
    def client_id(self):
        return config.get_client_id()

    @property
    def client_secret(self):
        return config.get_client_secret()

    @property
    def redirect_uri(self):
        return config.get_redirect_uri()

    # -------------------------------------------------------------
    # OAuth 2.0 PKCE Helpers
    # -------------------------------------------------------------
    @staticmethod
    def generate_pkce_pair():
        """PKCE code_verifier & code_challenge (S256) 생성"""
        # 43~128 길이의 URL Safe 문자열
        code_verifier = secrets.token_urlsafe(64)[:96]
        
        # SHA256 해시 후 URL-safe Base64 인코딩
        digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
        code_challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
        
        state = secrets.token_urlsafe(24)
        return code_verifier, code_challenge, state

    def get_authorization_url(self) -> Dict[str, str]:
        """사용자를 리디렉션할 Canva 로그인 승인 URL 생성"""
        if not self.client_id:
            raise CanvaAPIError("CANVA_CLIENT_ID가 설정되지 않았습니다. .env 파일을 확인해주세요.")

        verifier, challenge, state = self.generate_pkce_pair()
        
        # 세션 파일에 verifier와 state 임시 보관
        config.save_session({
            "code_verifier": verifier,
            "state": state,
            "created_at": time.time()
        })

        scope_str = " ".join(config.REQUIRED_SCOPES)
        auth_url = (
            f"{CANVA_AUTH_BASE}?"
            f"response_type=code&"
            f"client_id={self.client_id}&"
            f"redirect_uri={requests.utils.quote(self.redirect_uri)}&"
            f"scope={requests.utils.quote(scope_str)}&"
            f"code_challenge={challenge}&"
            f"code_challenge_method=s256&"
            f"state={state}"
        )
        return {"url": auth_url, "state": state}

    def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """Authorization Code를 Access Token 및 Refresh Token으로 교환"""
        session_data = config.load_session()
        saved_state = session_data.get("state")
        verifier = session_data.get("code_verifier")

        if not verifier:
            raise CanvaAPIError("세션 검증 실패: code_verifier를 찾을 수 없습니다. 로그인을 다시 시도해주세요.")
        if saved_state and state and saved_state != state:
            raise CanvaAPIError("CSRF 보안 경고: state 파라미터가 일치하지 않습니다.")

        # Canva Token Endpoint는 HTTP Basic Auth 사용
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_creds = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_creds}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": verifier,
            "redirect_uri": self.redirect_uri
        }

        resp = requests.post(f"{CANVA_API_BASE}/oauth/token", headers=headers, data=payload)
        if resp.status_code != 200:
            raise CanvaAPIError(
                f"토큰 발급 실패: {resp.status_code} - {resp.text}",
                status_code=resp.status_code,
                response_data=resp.text
            )

        token_data = resp.json()
        token_data["created_at"] = time.time()
        config.save_tokens(token_data)
        return token_data

    def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh Token을 사용해 새 Access Token 갱신"""
        current_tokens = config.load_tokens()
        refresh_token = current_tokens.get("refresh_token")
        if not refresh_token:
            raise CanvaAPIError("Refresh Token이 없습니다. Canva 로그인을 다시 진행해주세요.")

        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_creds = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_creds}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        resp = requests.post(f"{CANVA_API_BASE}/oauth/token", headers=headers, data=payload)
        if resp.status_code != 200:
            raise CanvaAPIError(
                f"토큰 갱신 실패: {resp.status_code} - {resp.text}",
                status_code=resp.status_code,
                response_data=resp.text
            )

        new_token_data = resp.json()
        new_token_data["created_at"] = time.time()
        if "refresh_token" not in new_token_data:
            new_token_data["refresh_token"] = refresh_token
        config.save_tokens(new_token_data)
        return new_token_data

    def get_valid_access_token(self) -> str:
        """만료 시간을 확인하여 유효한 Access Token 반환 (필요시 자동 갱신)"""
        tokens = config.load_tokens()
        access_token = tokens.get("access_token")
        if not access_token:
            raise CanvaAPIError("Canva 로그인 인증 토큰이 없습니다. 먼저 로그인을 완료해주세요.")

        created_at = tokens.get("created_at", 0)
        expires_in = tokens.get("expires_in", 3600)
        # 만료 60초 전이면 미리 갱신
        if time.time() >= (created_at + expires_in - 60):
            try:
                tokens = self.refresh_access_token()
                access_token = tokens.get("access_token")
            except Exception:
                # 갱신 실패 시 기존 토큰으로 일단 시도
                pass

        return access_token

    def _authenticated_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """인증 헤더를 포함한 Canva REST API 요청 (401 발생 시 1회 재시도)"""
        url = f"{CANVA_API_BASE}/{endpoint.lstrip('/')}"
        token = self.get_valid_access_token()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"

        resp = requests.request(method, url, headers=headers, **kwargs)
        if resp.status_code == 401:
            # 토큰 갱신 후 1회 재시도
            self.refresh_access_token()
            token = self.get_valid_access_token()
            headers["Authorization"] = f"Bearer {token}"
            resp = requests.request(method, url, headers=headers, **kwargs)

        return resp

    # -------------------------------------------------------------
    # Canva Connect API Business Logic
    # -------------------------------------------------------------
    def get_current_user(self) -> Dict[str, Any]:
        """현재 로그인된 Canva 사용자 정보 조회"""
        resp = self._authenticated_request("GET", "/users/me")
        if resp.status_code != 200:
            raise CanvaAPIError(f"사용자 정보 조회 실패: {resp.status_code} - {resp.text}", resp.status_code)
        return resp.json()

    def list_brand_templates(self, continuation: Optional[str] = None) -> Dict[str, Any]:
        """사용자가 접근 가능한 브랜드 템플릿(Brand Templates) 목록 조회"""
        params = {}
        if continuation:
            params["continuation"] = continuation
        
        resp = self._authenticated_request("GET", "/brand-templates", params=params)
        if resp.status_code != 200:
            raise CanvaAPIError(
                f"브랜드 템플릿 목록 조회 실패: {resp.status_code} - {resp.text}",
                status_code=resp.status_code,
                response_data=resp.text
            )
        return resp.json()

    def get_template_dataset(self, brand_template_id: str) -> Dict[str, Any]:
        """템플릿의 자동 채우기(Autofill) 가능 필드 스키마/데이터셋 조회"""
        resp = self._authenticated_request("GET", f"/brand-templates/{brand_template_id}/dataset")
        if resp.status_code != 200:
            raise CanvaAPIError(
                f"템플릿 데이터셋 조회 실패: {resp.status_code} - {resp.text}",
                status_code=resp.status_code,
                response_data=resp.text
            )
        return resp.json()

    def upload_asset(self, file_bytes: bytes, file_name: str) -> str:
        """
        Canva 미디어 라이브러리에 에셋(이미지 등) 업로드 비동기 작업 시작 및 완료 대기
        성공 시 생성된 asset_id 반환
        """
        encoded_name = base64.b64encode(file_name.encode("utf-8")).decode("utf-8")
        headers = {
            "Content-Type": "application/octet-stream",
            "Asset-Upload-Metadata": json.dumps({"name_base64": encoded_name})
        }
        
        resp = self._authenticated_request("POST", "/asset-uploads", headers=headers, data=file_bytes)
        if resp.status_code not in (200, 202):
            raise CanvaAPIError(f"에셋 업로드 작업 생성 실패: {resp.status_code} - {resp.text}", resp.status_code)

        job_info = resp.json().get("job", {})
        job_id = job_info.get("id")
        if not job_id:
            raise CanvaAPIError("에셋 업로드 작업 ID를 찾을 수 없습니다.")

        # 폴링하여 업로드 완료 대기 (최대 30초)
        for _ in range(15):
            time.sleep(2)
            check_resp = self._authenticated_request("GET", f"/asset-uploads/{job_id}")
            if check_resp.status_code == 200:
                check_data = check_resp.json().get("job", {})
                status = check_data.get("status")
                if status == "success":
                    return check_data.get("asset", {}).get("id")
                elif status == "failed":
                    error_msg = check_data.get("error", {}).get("message", "알 수 없는 에러")
                    raise CanvaAPIError(f"에셋 업로드 실패: {error_msg}")
        
        raise CanvaAPIError("에셋 업로드 대기 시간 초과")

    def create_autofill_job(self, brand_template_id: str, title: str, dataset_values: Dict[str, Any]) -> Dict[str, Any]:
        """
        템플릿에 데이터(텍스트, 이미지)를 주입하여 새 디자인 자동 생성 비동기 작업 요청
        dataset_values 예시:
        {
            "headline": {"type": "text", "text": "생성된 제목"},
            "banner_image": {"type": "image", "asset_id": "DAG..."}
        }
        """
        headers = {"Content-Type": "application/json"}
        payload = {
            "brand_template_id": brand_template_id,
            "title": title,
            "data": dataset_values
        }

        resp = self._authenticated_request("POST", "/autofills", headers=headers, json=payload)
        if resp.status_code not in (200, 202):
            raise CanvaAPIError(f"Autofill 작업 요청 실패: {resp.status_code} - {resp.text}", resp.status_code)

        job_info = resp.json().get("job", {})
        job_id = job_info.get("id")
        return {"job_id": job_id, "status": job_info.get("status", "in_progress")}

    def poll_autofill_job(self, job_id: str, max_attempts: int = 20, interval_sec: int = 2) -> Dict[str, Any]:
        """Autofill 작업이 완료될 때까지 상태를 폴링하고 결과 디자인 정보 반환"""
        for _ in range(max_attempts):
            resp = self._authenticated_request("GET", f"/autofills/{job_id}")
            if resp.status_code == 200:
                job_data = resp.json().get("job", {})
                status = job_data.get("status")
                if status == "success":
                    design = job_data.get("result", {}).get("design", {})
                    return {
                        "status": "success",
                        "design_id": design.get("id"),
                        "title": design.get("title"),
                        "url": design.get("url"), # Canva 디자인 편집/열기 URL
                        "thumbnail": design.get("thumbnail", {}).get("url")
                    }
                elif status == "failed":
                    error = job_data.get("error", {})
                    raise CanvaAPIError(f"디자인 자동 생성 실패: {error.get('message', '알 수 없는 오류')}")
            time.sleep(interval_sec)

        raise CanvaAPIError("디자인 자동 생성 대기 시간이 초과되었습니다.")

    def create_design(self, title: str, design_type: Optional[Dict[str, Any]] = None, asset_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Canva Connect API (POST /v1/designs)를 사용하여
        사용자의 Canva 계정에 새 디자인을 직접 생성하고 바로 편집할 수 있는 URL을 반환합니다.
        asset_id가 있으면 해당 그래픽 이미지를 디자인 안에 자동 배치합니다.
        """
        headers = {"Content-Type": "application/json"}
        payload = {"title": title}

        if asset_id:
            payload["asset_id"] = asset_id
        elif design_type:
            payload["design_type"] = design_type
        else:
            payload["design_type"] = {"type": "custom", "width": 1080, "height": 1080}

        resp = self._authenticated_request("POST", "/designs", headers=headers, json=payload)
        if resp.status_code not in (200, 201):
            raise CanvaAPIError(f"새 디자인 생성 실패: {resp.status_code} - {resp.text}", resp.status_code)

        data = resp.json().get("design", {})
        urls = data.get("urls", {})
        edit_url = urls.get("edit_url") or data.get("url")

        return {
            "status": "success",
            "design_id": data.get("id"),
            "title": data.get("title", title),
            "url": edit_url,
            "thumbnail": data.get("thumbnail", {}).get("url")
        }
