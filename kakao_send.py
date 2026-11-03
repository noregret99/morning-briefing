"""
카카오톡 '나에게 보내기'로 메시지를 보내는 프로그램.

보내기 전에 매번 리프레시 토큰으로 새 액세스 토큰을 받아서 쓴다.
(액세스 토큰은 12시간이면 만료되니까, 매일 아침 새로 받는 게 안전)
"""
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
TOKEN_FILE = "kakao_token.json"

# 메시지 아래 '자세히 보기' 버튼이 열 주소.
# 카카오 개발자 사이트 [제품 링크 관리] > [웹 도메인]에 등록한 도메인이어야 함
LINK_URL = "https://www.naver.com"


def get_access_token():
    """저장된 리프레시 토큰으로 새 액세스 토큰을 받아온다."""
    with open(TOKEN_FILE, encoding="utf-8") as f:
        tokens = json.load(f)

    response = requests.post("https://kauth.kakao.com/oauth/token", data={
        "grant_type": "refresh_token",
        "client_id": REST_API_KEY,
        "client_secret": CLIENT_SECRET,
        "refresh_token": tokens["refresh_token"],
    })
    new_tokens = response.json()
    if "access_token" not in new_tokens:
        raise SystemExit(f"❌ 토큰 갱신 실패: {new_tokens}\n→ python kakao_auth.py 를 다시 실행해 주세요.")

    # 리프레시 토큰은 만료가 1개월 안 남았을 때만 새로 주므로, 받았을 때만 바꿔 저장
    tokens.update(new_tokens)
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)

    return tokens["access_token"]


def send_to_me(text):
    """내 카카오톡으로 글을 보낸다. (글자 수는 최대 200자)"""
    template = {
        "object_type": "text",
        "text": text,
        "link": {"web_url": LINK_URL, "mobile_web_url": LINK_URL},
    }
    response = requests.post(
        "https://kapi.kakao.com/v2/api/talk/memo/default/send",
        headers={"Authorization": f"Bearer {get_access_token()}"},
        data={"template_object": json.dumps(template, ensure_ascii=False)},
    )
    result = response.json()
    if result.get("result_code") == 0:
        print("✅ 카카오톡 전송 성공! 휴대폰을 확인해 보세요.")
    else:
        # 실패하면 프로그램을 '오류'로 끝낸다 → 5단계에서 GitHub이 실패 알림 메일을 보내줌
        raise SystemExit(f"❌ 전송 실패: {result}")


if __name__ == "__main__":
    send_to_me("👋 안녕하세요! 파이썬에서 보낸 첫 번째 테스트 메시지예요.")
