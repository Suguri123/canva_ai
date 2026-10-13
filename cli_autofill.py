import argparse
import sys
import json
from canva_api import CanvaClient, CanvaAPIError
from ai_service import AIService
import config

def main():
    parser = argparse.ArgumentParser(description="Canva AI Autofill CLI Automation Tool")
    parser.add_argument("--template", "-t", required=True, help="Canva Brand Template ID (예: DAFb1234567)")
    parser.add_argument("--topic", "-p", required=True, help="디자인 생성 주제 / 기획 내용")
    parser.add_argument("--title", required=False, default=None, help="새로 생성될 디자인 제목")
    parser.add_argument("--custom-data", "-d", required=False, help="직접 입력할 JSON 데이터 파일 경로 (선택 사항)")

    args = parser.parse_args()

    client = CanvaClient()
    tokens = config.load_tokens()
    if not tokens or not tokens.get("access_token"):
        print("[오류] Canva OAuth 토큰이 없습니다.")
        print("먼저 웹 대시보드(python server.py)를 실행하여 브라우저에서 1회 로그인을 완료해주세요.")
        sys.exit(1)

    print(f"[*] 템플릿 정보 조회 중... (Template ID: {args.template})")
    try:
        dataset_info = client.get_template_dataset(args.template)
        dataset_schema = dataset_info.get("dataset", {})
        print(f"[+] 감지된 필드: {list(dataset_schema.keys())}")
    except CanvaAPIError as e:
        print(f"[!] 템플릿 스키마 조회 실패: {e}")
        dataset_schema = {}

    # 주입할 데이터 생성
    if args.custom_data:
        with open(args.custom_data, "r", encoding="utf-8") as f:
            autofill_data = json.load(f)
    else:
        print(f"[*] AI 콘텐츠 생성 중... (주제: '{args.topic}')")
        autofill_data = AIService.generate_content_for_template(args.topic, {"dataset": dataset_schema})
        print(f"[+] 생성된 데이터: {json.dumps(autofill_data, ensure_ascii=False, indent=2)}")

    design_title = args.title or f"[자동생성] {args.topic}"
    print(f"[*] Canva Autofill 작업 요청 중... (제목: '{design_title}')")
    try:
        job = client.create_autofill_job(
            brand_template_id=args.template,
            title=design_title,
            dataset_values=autofill_data
        )
        job_id = job.get("job_id")
        print(f"[+] 작업 생성 완료 (Job ID: {job_id})")
        print("[*] 디자인 완성 대기 중 (Polling)...")
        
        result = client.poll_autofill_job(job_id=job_id)
        print("\n==================================================")
        print("🎉 Canva 디자인이 성공적으로 자동 생성되었습니다!")
        print(f"- 디자인 ID : {result.get('design_id')}")
        print(f"- 제목      : {result.get('title')}")
        print(f"- 바로가기  : {result.get('url')}")
        print("==================================================\n")
    except CanvaAPIError as e:
        print(f"[오류] 자동 생성 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
