import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional

import config
from canva_api import CanvaClient, CanvaAPIError
from ai_service import AIService

app = FastAPI(title="Canva AI Automation Studio")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
canva = CanvaClient()

# 정적 파일 경로
STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

import templates_manager

class AIContentRequest(BaseModel):
    topic: str
    dataset: Optional[Dict[str, Any]] = {}

class AutofillRequest(BaseModel):
    brand_template_id: str
    title: str
    data: Dict[str, Any]

class CustomTemplateRequest(BaseModel):
    title: str
    brand_template_id: Optional[str] = ""
    fields: Optional[list] = []
    width: Optional[int] = 1080
    height: Optional[int] = 1080

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """메인 대시보드 웹 페이지"""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>index.html not found</h1>", status_code=404)

@app.get("/callback")
async def oauth_callback(code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None):
    """Canva Developer Portal에서 리디렉션되는 OAuth Callback"""
    if error:
        return HTMLResponse(f"<h3>Canva 인증 오류: {error}</h3><p><a href='/'>돌아가기</a></p>", status_code=400)
    if not code:
        return HTMLResponse("<h3>오류: Authorization code가 제공되지 않았습니다.</h3><p><a href='/'>돌아가기</a></p>", status_code=400)

    try:
        canva.exchange_code_for_token(code=code, state=state or "")
        return RedirectResponse(url="/?auth=success")
    except CanvaAPIError as e:
        return HTMLResponse(f"<h3>토큰 교환 실패</h3><p>{str(e)}</p><p><a href='/'>돌아가기</a></p>", status_code=500)

@app.get("/api/status")
async def get_status():
    """현재 Canva OAuth 연동 상태 확인"""
    tokens = config.load_tokens()
    if not tokens or not tokens.get("access_token"):
        return {"connected": False}

    try:
        user_info = canva.get_current_user()
        return {"connected": True, "user": user_info}
    except Exception:
        return {"connected": True, "user": None}

@app.get("/api/auth/url")
async def get_auth_url():
    """Canva 로그인 URL 생성"""
    try:
        return canva.get_authorization_url()
    except CanvaAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/logout")
async def logout():
    """토큰 삭제"""
    config.clear_tokens()
    return {"message": "로그아웃 완료"}

@app.get("/api/templates")
async def list_templates():
    """견본 프리셋 + 사용자 템플릿 + Canva 공식 브랜드 템플릿 목록 조회"""
    combined = []
    # 1. 견본 프리셋 및 로컬 등록 템플릿
    local_templates = templates_manager.load_all_templates()
    combined.extend(local_templates)

    # 2. Canva 계정에 실제 등록된 브랜드 템플릿이 있으면 추가
    try:
        canva_res = canva.list_brand_templates()
        for item in canva_res.get("items", []):
            combined.append({
                "id": item.get("id"),
                "is_preset": False,
                "title": f"🎨 [Canva 연동] {item.get('title')}",
                "thumbnail": item.get("thumbnail", {}).get("url")
            })
    except Exception:
        pass

    return {"items": combined}

@app.get("/api/templates/{brand_template_id}/dataset")
async def get_template_dataset(brand_template_id: str):
    """브랜드 템플릿 또는 견본 프리셋 데이터셋 스키마 조회"""
    tmpl = templates_manager.get_template_by_id(brand_template_id)
    if tmpl:
        return {
            "dataset": tmpl.get("fields", {}),
            "default_topic": tmpl.get("default_topic", ""),
            "width": tmpl.get("width", 1080),
            "height": tmpl.get("height", 1080),
            "is_preset": tmpl.get("is_preset", False),
            "canva_search": tmpl.get("canva_search", "")
        }

    try:
        return canva.get_template_dataset(brand_template_id)
    except CanvaAPIError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))

@app.post("/api/templates/custom")
async def create_custom_template(req: CustomTemplateRequest):
    """새로운 사용자 템플릿 추가 및 영구 저장"""
    new_tmpl = templates_manager.add_custom_template(
        title=req.title,
        brand_template_id=req.brand_template_id or "",
        fields=req.fields or ["headline", "subheadline", "cta_text"],
        width=req.width or 1080,
        height=req.height or 1080
    )
    return new_tmpl

@app.post("/api/generate-content")
async def generate_content(req: AIContentRequest):
    """주제 및 템플릿 스키마에 맞는 카피라이팅 자동 생성"""
    try:
        generated = AIService.generate_content_for_template(req.topic, req.dataset or {})
        return {"topic": req.topic, "generated": generated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"콘텐츠 생성 실패: {str(e)}")

import time
import banner_generator

@app.post("/api/autofill")
async def execute_autofill(req: AutofillRequest):
    """Canva 디자인 자동 생성 실행 (완성된 그래픽 에셋 디자인 생성 또는 브랜드 템플릿 Autofill)"""
    try:
        tmpl = templates_manager.get_template_by_id(req.brand_template_id)

        # 1. 견본 프리셋이거나 실제 Canva 브랜드 템플릿 ID가 없는 경우
        # -> AI 그래픽 배너 이미지를 자동 렌더링하여 Canva 에셋으로 업로드 후 디자인 생성!
        if tmpl and (tmpl.get("is_preset") or not tmpl.get("brand_template_id")):
            w = tmpl.get("width", 1080)
            h = tmpl.get("height", 1080)
            try:
                # 고화질 그래픽 배너 자동 렌더링 (템플릿 테마 적용)
                theme = tmpl.get("theme", "magazine")
                png_bytes = banner_generator.render_banner(w, h, data=req.data, topic=req.title, theme_name=theme)
                # Canva 미디어 라이브러리에 에셋 자동 업로드
                asset_id = canva.upload_asset(png_bytes, f"ai_banner_{int(time.time())}.png")
                # 해당 그래픽이 얹혀진 새 디자인 생성
                result = canva.create_design(title=req.title, asset_id=asset_id)
            except Exception as ex:
                print(f"[Banner Render/Upload Error, Fallback to Blank Canvas]: {ex}")
                design_type = {"type": "custom", "width": w, "height": h}
                result = canva.create_design(title=req.title, design_type=design_type)

            result["mode"] = "direct_design"
            return result

        # 2. 실제 Canva Brand Template ID가 있는 경우 -> Canva Autofill 비동기 파이프라인
        actual_id = tmpl.get("brand_template_id") if tmpl else req.brand_template_id
        job = canva.create_autofill_job(
            brand_template_id=actual_id,
            title=req.title,
            dataset_values=req.data
        )
        job_id = job.get("job_id")
        if not job_id:
            raise HTTPException(status_code=500, detail="작업 ID 발급 실패")

        result = canva.poll_autofill_job(job_id=job_id)
        result["mode"] = "autofill"
        return result
    except CanvaAPIError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=config.HOST, port=config.PORT, reload=True)
