import io
import math
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, Tuple

FONT_BOLD = r"C:\Windows\Fonts\malgunbd.ttf"
FONT_REGULAR = r"C:\Windows\Fonts\malgun.ttf"

def get_font(size: int, bold: bool = False):
    try:
        font_path = FONT_BOLD if bold else FONT_REGULAR
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

def draw_sparkle(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, fill: Tuple[int, int, int]):
    """귀여운 반짝이 별(4-point star) 그리기"""
    points = [
        (x, y - size),
        (x + size * 0.25, y - size * 0.25),
        (x + size, y),
        (x + size * 0.25, y + size * 0.25),
        (x, y + size),
        (x - size * 0.25, y + size * 0.25),
        (x - size, y),
        (x - size * 0.25, y - size * 0.25),
    ]
    draw.polygon(points, fill=fill)

def draw_cute_tangerine(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int):
    """귀여운 귤 캐릭터/일러스트 그리기"""
    # 1. 귤 몸통 (밝고 탐스러운 주황색)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 140, 0), outline=(230, 90, 0), width=max(2, r // 15))
    # 2. 잎사귀 (초록색 타원 2개)
    leaf_w, leaf_h = int(r * 0.6), int(r * 0.35)
    draw.ellipse((cx - leaf_w, cy - r - leaf_h // 2, cx, cy - r + leaf_h // 2), fill=(76, 175, 80))
    draw.ellipse((cx, cy - r - leaf_h // 2, cx + leaf_w, cy - r + leaf_h // 2), fill=(129, 199, 132))
    # 3. 귤 꼭지
    draw.rectangle((cx - 3, cy - r - 4, cx + 3, cy - r + 4), fill=(93, 64, 55))
    # 4. 볼터치 (핑크 블러셔)
    blush_r = int(r * 0.22)
    draw.ellipse((cx - int(r * 0.55), cy + 5, cx - int(r * 0.55) + blush_r, cy + 5 + blush_r), fill=(255, 130, 150))
    draw.ellipse((cx + int(r * 0.35), cy + 5, cx + int(r * 0.35) + blush_r, cy + 5 + blush_r), fill=(255, 130, 150))
    # 5. 귀여운 눈 (점 2개)
    eye_r = max(3, r // 12)
    draw.ellipse((cx - int(r * 0.35), cy - 2, cx - int(r * 0.35) + eye_r, cy - 2 + eye_r), fill=(40, 20, 10))
    draw.ellipse((cx + int(r * 0.35) - eye_r, cy - 2, cx + int(r * 0.35), cy - 2 + eye_r), fill=(40, 20, 10))
    # 6. 하이라이트 광택
    draw.ellipse((cx - int(r * 0.6), cy - int(r * 0.6), cx - int(r * 0.35), cy - int(r * 0.35)), fill=(255, 200, 100))

def draw_wrapped_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int, start_x: int, start_y: int, fill: Tuple[int, int, int], line_spacing: int = 15, align: str = "center") -> int:
    words = text.split(" ")
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_w = bbox[2] - bbox[0]
        if line_w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    curr_y = start_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        x = start_x - (line_w // 2) if align == "center" else start_x
        draw.text((x, curr_y), line, font=font, fill=fill)
        curr_y += line_h + line_spacing

    return curr_y

def extract_text(data: Dict[str, Any], key: str, default: str = "") -> str:
    if not data or key not in data:
        return default
    val = data[key]
    if isinstance(val, dict):
        return val.get("text") or default
    if isinstance(val, str) and val.strip():
        return val.strip()
    return default

# =========================================================================
# 5가지 서로 완전히 다른 독창적 레이아웃 엔진
# =========================================================================

def render_cute_pop(width: int, height: int, data: Dict[str, Any], topic: str) -> Image.Image:
    """1. 🍊 큐트 팝 일러스트 (파스텔 옐로우 & 도트 & 귀여운 귤 캐릭터)"""
    img = Image.new("RGB", (width, height), (255, 248, 225))  # 따뜻한 바닐라 크림 배경
    draw = ImageDraw.Draw(img)

    # 파스텔 도트 땡땡이 패턴
    dot_step = int(width * 0.08)
    for x in range(0, width, dot_step):
        for y in range(0, height, dot_step):
            draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 213, 79, 120))

    # 반짝이 별 장식
    draw_sparkle(draw, int(width * 0.15), int(height * 0.12), 24, (255, 112, 67))
    draw_sparkle(draw, int(width * 0.85), int(height * 0.2), 30, (255, 179, 0))
    draw_sparkle(draw, int(width * 0.12), int(height * 0.78), 20, (255, 183, 77))

    # 귀여운 귤 캐릭터 (우측 상단 & 좌측 하단)
    draw_cute_tangerine(draw, int(width * 0.82), int(height * 0.14), int(width * 0.08))
    draw_cute_tangerine(draw, int(width * 0.16), int(height * 0.84), int(width * 0.09))

    # 몽글몽글 둥근 구름 카드 (중앙)
    card_margin = int(width * 0.09)
    card_rect = (card_margin, int(height * 0.22), width - card_margin, int(height * 0.76))
    # 그림자 효과
    draw.rounded_rectangle((card_rect[0] + 8, card_rect[1] + 12, card_rect[2] + 8, card_rect[3] + 12), radius=40, fill=(255, 204, 128))
    # 메인 화이트 카드
    draw.rounded_rectangle(card_rect, radius=40, fill=(255, 255, 255), outline=(255, 152, 0), width=5)

    center_x = width // 2
    curr_y = card_rect[1] + int(height * 0.06)

    # 톡톡 튀는 뱃지
    badge_text = extract_text(data, "badge_text", "🍊 제주 꿀당도 보장")
    font_badge = get_font(max(18, int(width * 0.03)), bold=True)
    b_box = draw.textbbox((0, 0), badge_text, font=font_badge)
    b_w = b_box[2] - b_box[0] + 36
    draw.rounded_rectangle((center_x - b_w // 2, curr_y, center_x + b_w // 2, curr_y + 42), radius=21, fill=(255, 235, 59), outline=(255, 112, 67), width=3)
    draw.text((center_x - (b_box[2] - b_box[0]) // 2, curr_y + 8), badge_text, font=font_badge, fill=(191, 54, 12))

    curr_y += 70

    # 동글동글 굵은 메인 타이틀
    headline = extract_text(data, "headline", topic)
    font_head = get_font(max(32, int(width * 0.062)), bold=True)
    curr_y = draw_wrapped_text(draw, headline, font_head, int((width - card_margin * 2) * 0.86), center_x, curr_y, fill=(62, 39, 35), line_spacing=16)

    curr_y += 20

    # 귀여운 보조 문구
    sub = extract_text(data, "subheadline", "한 번 맛보면 잊을 수 없는 새콤달콤함!")
    font_sub = get_font(max(20, int(width * 0.032)), bold=False)
    draw_wrapped_text(draw, sub, font_sub, int((width - card_margin * 2) * 0.86), center_x, curr_y, fill=(120, 80, 60), line_spacing=12)

    # 알록달록 스마일 버튼
    btn_text = extract_text(data, "cta_text", "지금 바로 주문하기 🍊")
    font_btn = get_font(max(22, int(width * 0.032)), bold=True)
    btn_bbox = draw.textbbox((0, 0), btn_text, font=font_btn)
    btn_w = btn_bbox[2] - btn_bbox[0] + 54
    btn_y = card_rect[3] - 65
    draw.rounded_rectangle((center_x - btn_w // 2, btn_y, center_x + btn_w // 2, btn_y + 54), radius=27, fill=(255, 112, 67))
    draw.text((center_x - (btn_bbox[2] - btn_bbox[0]) // 2, btn_y + 12), btn_text, font=font_btn, fill=(255, 255, 255))

    return img

def render_retro_funky(width: int, height: int, data: Dict[str, Any], topic: str) -> Image.Image:
    """2. ⚡ 레트로 팝 펑키 (비비드 핑크 & 옐로우 & 네오 브루탈리즘 볼드 블랙 테두리)"""
    img = Image.new("RGB", (width, height), (255, 94, 150))  # 팝 핑크 배경
    draw = ImageDraw.Draw(img)

    # 배경 사선 지그재그 패턴
    for i in range(-width, width * 2, 80):
        draw.line([(i, 0), (i + height, height)], fill=(255, 130, 180), width=24)

    # 옐로우 박스 카드 (두꺼운 만화풍 블랙 테두리 & 블랙 드롭 섀도우)
    margin = int(width * 0.08)
    cx1, cy1, cx2, cy2 = margin, int(height * 0.16), width - margin, height - margin
    # 레트로 하드 블랙 섀도우
    draw.rounded_rectangle((cx1 + 14, cy1 + 14, cx2 + 14, cy2 + 14), radius=24, fill=(0, 0, 0))
    # 옐로우 카드
    draw.rounded_rectangle((cx1, cy1, cx2, cy2), radius=24, fill=(255, 235, 59), outline=(0, 0, 0), width=6)

    center_x = width // 2
    curr_y = cy1 + int(height * 0.05)

    # 네온 민트 팝 뱃지
    badge_text = extract_text(data, "badge_text", "🔥 HIT 인기 폭발")
    font_badge = get_font(max(18, int(width * 0.03)), bold=True)
    b_box = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = b_box[2] - b_box[0] + 36
    draw.rectangle((center_x - bw // 2 + 5, curr_y + 5, center_x + bw // 2 + 5, curr_y + 44), fill=(0, 0, 0))
    draw.rectangle((center_x - bw // 2, curr_y, center_x + bw // 2, curr_y + 39), fill=(0, 230, 118), outline=(0, 0, 0), width=4)
    draw.text((center_x - (b_box[2] - b_box[0]) // 2, curr_y + 6), badge_text, font=font_badge, fill=(0, 0, 0))

    curr_y += 70

    # 볼드 블랙 타이틀
    headline = extract_text(data, "headline", topic)
    font_head = get_font(max(32, int(width * 0.065)), bold=True)
    curr_y = draw_wrapped_text(draw, headline, font_head, int((width - margin * 2) * 0.88), center_x, curr_y, fill=(0, 0, 0), line_spacing=18)

    curr_y += 25

    # 서브 텍스트
    sub = extract_text(data, "subheadline", "놓치면 후회하는 초특급 특가전!")
    font_sub = get_font(max(20, int(width * 0.032)), bold=False)
    draw_wrapped_text(draw, sub, font_sub, int((width - margin * 2) * 0.88), center_x, curr_y, fill=(50, 50, 50), line_spacing=12)

    # 팝아트 블랙 버튼
    btn_text = extract_text(data, "cta_text", "특가 혜택 잡기 >>")
    font_btn = get_font(max(22, int(width * 0.034)), bold=True)
    btn_bbox = draw.textbbox((0, 0), btn_text, font=font_btn)
    btn_w = btn_bbox[2] - btn_bbox[0] + 50
    btn_y = cy2 - 75
    draw.rectangle((center_x - btn_w // 2 + 6, btn_y + 6, center_x + btn_w // 2 + 6, btn_y + 56), fill=(0, 0, 0))
    draw.rectangle((center_x - btn_w // 2, btn_y, center_x + btn_w // 2, btn_y + 50), fill=(255, 61, 0), outline=(0, 0, 0), width=4)
    draw.text((center_x - (btn_bbox[2] - btn_bbox[0]) // 2, btn_y + 10), btn_text, font=font_btn, fill=(255, 255, 255))

    return img

def render_split_modern(width: int, height: int, data: Dict[str, Any], topic: str) -> Image.Image:
    """3. 📸 모던 스플릿 (상단 비비드 탠저린 오렌지 + 하단 퓨어 화이트 2단 분할)"""
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    split_h = int(height * 0.45)
    # 상단 탠저린 오렌지 블록
    draw.rectangle((0, 0, width, split_h), fill=(255, 112, 67))
    # 사선 감성 배색 밴드
    draw.polygon([(0, split_h), (width, split_h - int(height * 0.08)), (width, split_h), (0, split_h)], fill=(255, 138, 101))

    # 상단 화이트 뱃지
    badge_text = extract_text(data, "badge_text", "JEJU PREMIUM EDITION")
    font_badge = get_font(max(16, int(width * 0.026)), bold=True)
    draw.text((int(width * 0.08), int(height * 0.08)), badge_text, font=font_badge, fill=(255, 235, 238))

    # 상단 빅 헤드라인 (화이트 텍스트)
    headline = extract_text(data, "headline", topic)
    font_head = get_font(max(32, int(width * 0.06)), bold=True)
    draw_wrapped_text(draw, headline, font_head, int(width * 0.84), int(width * 0.08), int(height * 0.14), fill=(255, 255, 255), line_spacing=16, align="left")

    # 하단 콘텐츠
    curr_y = split_h + int(height * 0.08)
    sub = extract_text(data, "subheadline", "청정 제주의 바람과 햇살을 듬뿍 머금은 프리미엄 감귤")
    font_sub = get_font(max(20, int(width * 0.032)), bold=False)
    draw_wrapped_text(draw, sub, font_sub, int(width * 0.84), int(width * 0.08), curr_y, fill=(60, 60, 70), line_spacing=14, align="left")

    # 하단 세련된 캡슐 버튼
    btn_text = extract_text(data, "cta_text", "컬렉션 자세히 보기 >")
    font_btn = get_font(max(20, int(width * 0.03)), bold=True)
    btn_bbox = draw.textbbox((0, 0), btn_text, font=font_btn)
    btn_w = btn_bbox[2] - btn_bbox[0] + 46
    btn_y = height - int(height * 0.14)
    draw.rounded_rectangle((int(width * 0.08), btn_y, int(width * 0.08) + btn_w, btn_y + 48), radius=24, fill=(33, 33, 33))
    draw.text((int(width * 0.08) + 23, btn_y + 11), btn_text, font=font_btn, fill=(255, 255, 255))

    return img

def render_organic_kraft(width: int, height: int, data: Dict[str, Any], topic: str) -> Image.Image:
    """4. 🌿 내추럴 오가닉 (포레스트 그린 & 크라프트 올리브 감성)"""
    img = Image.new("RGB", (width, height), (244, 241, 234))  # 따뜻한 내추럴 크라프트 베이지
    draw = ImageDraw.Draw(img)

    # 앤틱 보더 테두리
    m = int(width * 0.05)
    draw.rectangle((m, m, width - m, height - m), outline=(46, 125, 50), width=4)
    draw.rectangle((m + 8, m + 8, width - m - 8, height - m - 8), outline=(129, 199, 132), width=1)

    center_x = width // 2
    curr_y = int(height * 0.12)

    # 오가닉 엠블럼 뱃지
    badge_text = extract_text(data, "badge_text", "🌿 100% 무농약 자연 재배")
    font_badge = get_font(max(18, int(width * 0.028)), bold=True)
    b_box = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = b_box[2] - b_box[0] + 36
    draw.rounded_rectangle((center_x - bw // 2, curr_y, center_x + bw // 2, curr_y + 40), radius=20, fill=(232, 245, 233), outline=(46, 125, 50), width=2)
    draw.text((center_x - (b_box[2] - b_box[0]) // 2, curr_y + 7), badge_text, font=font_badge, fill=(27, 94, 32))

    curr_y += 75

    # 묵직한 오가닉 그린 타이틀
    headline = extract_text(data, "headline", topic)
    font_head = get_font(max(32, int(width * 0.06)), bold=True)
    curr_y = draw_wrapped_text(draw, headline, font_head, int(width * 0.8), center_x, curr_y, fill=(27, 94, 32), line_spacing=18)

    curr_y += 25

    # 서브 텍스트
    sub = extract_text(data, "subheadline", "정직한 농부의땀방울로 길러낸 건강한 맛")
    font_sub = get_font(max(20, int(width * 0.03)), bold=False)
    draw_wrapped_text(draw, sub, font_sub, int(width * 0.8), center_x, curr_y, fill=(85, 107, 47), line_spacing=14)

    # 보태니컬 버튼
    btn_text = extract_text(data, "cta_text", "농장 이야기 보러가기")
    font_btn = get_font(max(20, int(width * 0.03)), bold=True)
    btn_bbox = draw.textbbox((0, 0), btn_text, font=font_btn)
    btn_w = btn_bbox[2] - btn_bbox[0] + 48
    btn_y = height - int(height * 0.16)
    draw.rounded_rectangle((center_x - btn_w // 2, btn_y, center_x + btn_w // 2, btn_y + 50), radius=25, fill=(46, 125, 50))
    draw.text((center_x - (btn_bbox[2] - btn_bbox[0]) // 2, btn_y + 11), btn_text, font=font_btn, fill=(255, 255, 255))

    return img

def render_royal_premium(width: int, height: int, data: Dict[str, Any], topic: str) -> Image.Image:
    """5. 🎁 로열 프리미엄 (럭셔리 다크 네이비 & 샴페인 골드)"""
    img = Image.new("RGB", (width, height), (15, 23, 42))  # 미드나잇 다크 네이비
    draw = ImageDraw.Draw(img)

    # 골드 프레임 라인
    m = int(width * 0.06)
    draw.rectangle((m, m, width - m, height - m), outline=(212, 175, 55), width=2)
    # 네 모서리 골드 장식
    c_len = int(width * 0.04)
    for cx, cy in [(m, m), (width - m, m), (m, height - m), (width - m, height - m)]:
        draw.rectangle((cx - 4, cy - 4, cx + 4, cy + 4), fill=(212, 175, 55))

    center_x = width // 2
    curr_y = int(height * 0.14)

    # 샴페인 골드 뱃지
    badge_text = extract_text(data, "badge_text", "✨ PRESTIGE LUXURY GIFT")
    font_badge = get_font(max(16, int(width * 0.026)), bold=True)
    b_box = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = b_box[2] - b_box[0] + 40
    draw.rounded_rectangle((center_x - bw // 2, curr_y, center_x + bw // 2, curr_y + 36), radius=18, fill=(30, 41, 59), outline=(212, 175, 55), width=1)
    draw.text((center_x - (b_box[2] - b_box[0]) // 2, curr_y + 6), badge_text, font=font_badge, fill=(245, 215, 110))

    curr_y += 65

    # 골드 헤드라인
    headline = extract_text(data, "headline", topic)
    font_head = get_font(max(32, int(width * 0.06)), bold=True)
    curr_y = draw_wrapped_text(draw, headline, font_head, int(width * 0.8), center_x, curr_y, fill=(245, 230, 180), line_spacing=18)

    curr_y += 25

    # 실버-그레이 서브 텍스트
    sub = extract_text(data, "subheadline", "귀한 분의 품격에 어울리는 엄선된 선물세트")
    font_sub = get_font(max(20, int(width * 0.03)), bold=False)
    draw_wrapped_text(draw, sub, font_sub, int(width * 0.8), center_x, curr_y, fill=(180, 195, 215), line_spacing=14)

    # 샴페인 골드 버튼
    btn_text = extract_text(data, "cta_text", "VIP 사전 예약하기")
    font_btn = get_font(max(20, int(width * 0.03)), bold=True)
    btn_bbox = draw.textbbox((0, 0), btn_text, font=font_btn)
    btn_w = btn_bbox[2] - btn_bbox[0] + 50
    btn_y = height - int(height * 0.16)
    draw.rounded_rectangle((center_x - btn_w // 2, btn_y, center_x + btn_w // 2, btn_y + 50), radius=25, fill=(212, 175, 55))
    draw.text((center_x - (btn_bbox[2] - btn_bbox[0]) // 2, btn_y + 11), btn_text, font=font_btn, fill=(15, 23, 42))

    return img

def render_banner(width: int, height: int, data: Dict[str, Any], topic: str, theme_name: str = "cute") -> bytes:
    """테마별 완전히 색다른 레이아웃으로 렌더링"""
    if theme_name in ("magazine", "cute"):
        img = render_cute_pop(width, height, data, topic)
    elif theme_name in ("youtube", "promo", "timesale"):
        img = render_retro_funky(width, height, data, topic)
    elif theme_name in ("story", "ranking"):
        img = render_split_modern(width, height, data, topic)
    elif theme_name in ("organic", "cafe"):
        img = render_organic_kraft(width, height, data, topic)
    elif theme_name == "premium":
        img = render_royal_premium(width, height, data, topic)
    else:
        img = render_cute_pop(width, height, data, topic)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
