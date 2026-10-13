import json
from pathlib import Path
from typing import List, Dict, Any

TEMPLATES_FILE = Path(__file__).resolve().parent / "templates_data.json"

DEFAULT_PRESETS = [
    {
        "id": "tmpl_01_magazine_card",
        "is_preset": True,
        "title": "🍊 1. [인스타] 감성 매거진 카드뉴스 (1080x1080)",
        "type": "custom",
        "width": 1080,
        "height": 1080,
        "theme": "magazine",
        "default_topic": "제주 산지직송 당일 수확 햇감귤 이야기",
        "canva_search": "제주 감성 카드뉴스",
        "fields": {
            "headline": {"type": "text", "description": "메인 헤드라인"},
            "subheadline": {"type": "text", "description": "감성 스토리 / 서브 카피"},
            "badge_text": {"type": "text", "description": "상단 뱃지 (예: JEJU SPECIAL)"},
            "cta_text": {"type": "text", "description": "클릭 유도 문구"}
        }
    },
    {
        "id": "tmpl_02_youtube_food",
        "is_preset": True,
        "title": "🎬 2. [유튜브] 맛집/여행 썸네일 (1280x720)",
        "type": "custom",
        "width": 1280,
        "height": 720,
        "theme": "youtube",
        "default_topic": "제주도민이 꼽은 숨은 귤맛집 지도 BEST 5",
        "canva_search": "유튜브 썸네일 맛집",
        "fields": {
            "headline": {"type": "text", "description": "시선 강탈 메인 타이틀"},
            "badge_text": {"type": "text", "description": "강조 뱃지 (예: 조회수 폭발)"},
            "subheadline": {"type": "text", "description": "상세 요약 설명"},
            "cta_text": {"type": "text", "description": "지금 시청하기 >"}
        }
    },
    {
        "id": "tmpl_03_vivid_promo",
        "is_preset": True,
        "title": "🏷️ 3. [프로모션] 비비드 팝 할인 배너 (1200x628)",
        "type": "custom",
        "width": 1200,
        "height": 628,
        "theme": "promo",
        "default_topic": "2026 귤시즌 개막 기념 전 품목 30% 특별 할인전",
        "canva_search": "할인 프로모션 배너",
        "fields": {
            "headline": {"type": "text", "description": "파격 세일 타이틀"},
            "badge_text": {"type": "text", "description": "할인율 (예: UP TO 30% OFF)"},
            "subheadline": {"type": "text", "description": "상세 혜택 안내"},
            "cta_text": {"type": "text", "description": "할인받고 구매하기"}
        }
    },
    {
        "id": "tmpl_04_story_shorts",
        "is_preset": True,
        "title": "📱 4. [쇼츠/스토리] 풀스크린 세로형 배너 (1080x1920)",
        "type": "custom",
        "width": 1080,
        "height": 1920,
        "theme": "story",
        "default_topic": "지금 주문하면 오늘 바로 따서 보내드려요!",
        "canva_search": "인스타그램 스토리 프로모션",
        "fields": {
            "headline": {"type": "text", "description": "세로형 임팩트 타이틀"},
            "subheadline": {"type": "text", "description": "신선도 / 배송 안내"},
            "badge_text": {"type": "text", "description": "상단 태그 (예: 당일수확 산지직송)"},
            "cta_text": {"type": "text", "description": "위로 올려 바로보기"}
        }
    },
    {
        "id": "tmpl_05_ranking_list",
        "is_preset": True,
        "title": "🗺️ 5. [정보공유] 인포그래픽 BEST 5 순위형 (1080x1350)",
        "type": "custom",
        "width": 1080,
        "height": 1350,
        "theme": "ranking",
        "default_topic": "실패 없는 제주 농장 직송 감귤 품종 BEST 5 가이드",
        "canva_search": "리스트 카드뉴스 BEST",
        "fields": {
            "headline": {"type": "text", "description": "정보형 메인 타이틀"},
            "subheadline": {"type": "text", "description": "핵심 큐레이션 안내"},
            "badge_text": {"type": "text", "description": "랭킹 뱃지 (예: 2026 추천 가이드)"},
            "cta_text": {"type": "text", "description": "자세히 알아보기"}
        }
    },
    {
        "id": "tmpl_06_organic_natural",
        "is_preset": True,
        "title": "🌿 6. [오가닉] 내추럴 친환경 농산물 포스터 (1080x1440)",
        "type": "custom",
        "width": 1080,
        "height": 1440,
        "theme": "organic",
        "default_topic": "자연을 담은 무농약 친환경 제주 타이벡 감귤",
        "canva_search": "유기농 포스터",
        "fields": {
            "headline": {"type": "text", "description": "신뢰감 있는 메인 타이틀"},
            "subheadline": {"type": "text", "description": "친환경 재배 철학 설명"},
            "badge_text": {"type": "text", "description": "인증 뱃지 (예: 100% 무농약 인증)"},
            "cta_text": {"type": "text", "description": "농장 직송 구경하기"}
        }
    },
    {
        "id": "tmpl_07_timesale_urgency",
        "is_preset": True,
        "title": "⚡ 7. [타임세일] 한정수량 마감 임박 배너 (1200x628)",
        "type": "custom",
        "width": 1200,
        "height": 628,
        "theme": "timesale",
        "default_topic": "오늘 자정 마감! 당일 수확 한정 100박스 타임세일",
        "canva_search": "타임세일 배너",
        "fields": {
            "headline": {"type": "text", "description": "긴급 타임세일 헤드라인"},
            "badge_text": {"type": "text", "description": "한정수량 (예: 선착순 100박스)"},
            "subheadline": {"type": "text", "description": "마감 임박 혜택 안내"},
            "cta_text": {"type": "text", "description": "품절 전 서두르기"}
        }
    },
    {
        "id": "tmpl_08_review_proof",
        "is_preset": True,
        "title": "⭐ 8. [리뷰인증] 고객 찐후기 추천 카드뉴스 (1080x1080)",
        "type": "custom",
        "width": 1080,
        "height": 1080,
        "theme": "review",
        "default_topic": "별점 5.0 만점! 벌써 3번째 재구매하는 꿀당도 감귤 후기",
        "canva_search": "고객 후기 카드뉴스",
        "fields": {
            "headline": {"type": "text", "description": "고객 실제 생생 후기"},
            "badge_text": {"type": "text", "description": "평점 뱃지 (예: ★★★★★ 만점 리뷰)"},
            "subheadline": {"type": "text", "description": "재구매율 98% 인증 설명"},
            "cta_text": {"type": "text", "description": "리뷰 1,200개 더보기"}
        }
    },
    {
        "id": "tmpl_09_premium_gift",
        "is_preset": True,
        "title": "🎁 9. [선물세트] 프리미엄 명절 기프트 배너 (1080x1080)",
        "type": "custom",
        "width": 1080,
        "height": 1080,
        "theme": "premium",
        "default_topic": "소중한 분께 전하는 최고급 제주 프리미엄 황금향 선물세트",
        "canva_search": "선물세트 기획전",
        "fields": {
            "headline": {"type": "text", "description": "격식 있는 명절 선물 헤드라인"},
            "badge_text": {"type": "text", "description": "프리미엄 뱃지 (예: PREMIUM GIFT)"},
            "subheadline": {"type": "text", "description": "고급 보자기 포장 & 무료배송"},
            "cta_text": {"type": "text", "description": "선물세트 예약하기"}
        }
    },
    {
        "id": "tmpl_10_cafe_menu",
        "is_preset": True,
        "title": "☕ 10. [카페/디저트] 감성 시즌 메뉴 포스터 (1080x1440)",
        "type": "custom",
        "width": 1080,
        "height": 1440,
        "theme": "cafe",
        "default_topic": "겨울 한정 제주 생귤 에이드 & 수제 귤 타르트 출시",
        "canva_search": "카페 시즌 메뉴 포스터",
        "fields": {
            "headline": {"type": "text", "description": "시즌 신메뉴 타이틀"},
            "badge_text": {"type": "text", "description": "시즌 한정 (예: WINTER SPECIAL)"},
            "subheadline": {"type": "text", "description": "메뉴 맛과 특징 소개"},
            "cta_text": {"type": "text", "description": "매장에서 바로 맛보기"}
        }
    }
]

def load_all_templates() -> List[Dict[str, Any]]:
    """10개 견본 프리셋과 사용자가 추가한 커스텀 템플릿을 합쳐서 반환"""
    custom_templates = []
    if TEMPLATES_FILE.exists():
        try:
            with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
                custom_templates = json.load(f)
        except Exception:
            custom_templates = []

    return DEFAULT_PRESETS + custom_templates

def add_custom_template(title: str, brand_template_id: str = "", fields: List[str] = None, width: int = 1080, height: int = 1080) -> Dict[str, Any]:
    """새로운 사용자 템플릿 추가 및 영구 저장"""
    all_custom = []
    if TEMPLATES_FILE.exists():
        try:
            with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
                all_custom = json.load(f)
        except Exception:
            all_custom = []

    fields_dict = {}
    if fields:
        for f in fields:
            f_name = f.strip()
            if f_name:
                fields_dict[f_name] = {"type": "text", "description": f_name}
    else:
        fields_dict = {
            "headline": {"type": "text", "description": "제목"},
            "subheadline": {"type": "text", "description": "부제목"},
            "cta_text": {"type": "text", "description": "버튼"}
        }

    template_id = brand_template_id.strip() if brand_template_id.strip() else f"custom_{len(all_custom) + 1}"
    new_template = {
        "id": template_id,
        "is_preset": False,
        "is_custom": True,
        "title": f"⭐ [내 템플릿] {title}",
        "brand_template_id": brand_template_id.strip(),
        "type": "custom",
        "width": width,
        "height": height,
        "fields": fields_dict
    }

    all_custom.append(new_template)
    with open(TEMPLATES_FILE, "w", encoding="utf-8") as f:
        json.dump(all_custom, f, indent=2, ensure_ascii=False)

    return new_template

def get_template_by_id(template_id: str) -> Dict[str, Any]:
    """ID로 템플릿 정보 검색"""
    for tmpl in load_all_templates():
        if tmpl["id"] == template_id:
            return tmpl
    return None
