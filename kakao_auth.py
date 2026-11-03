"""
[처음 한 번만 실행] 카카오 로그인을 해서 '토큰'을 받아 저장하는 프로그램.

토큰 = "이 프로그램이 내 카톡으로 메시지를 보내도 된다"는 출입증.
- access_token(액세스 토큰): 실제로 쓰는 출입증. 약 12시간 뒤 만료.
- refresh_token(리프레시 토큰): 출입증 재발급용 카드. 약 2개월 유효.

흐름:
1) 브라우저로 카카오 로그인 페이지를 연다
2) 로그인 + 동의하면, 카카오가 내 컴퓨터(localhost:5000)로 '인가 코드'를 보내준다
3) 그 코드를 토큰으로 바꿔서 kakao_token.json 파일에 저장한다
"""
import json
import os
import secrets
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode, urlparse, parse_qs

import requests
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 비밀 정보를 읽어온다

REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback"  # 카카오 개발자 사이트에 등록한 주소와 똑같아야 함
TOKEN_FILE = "kakao_token.json"

if not REST_API_KEY or not CLIENT_SECRET:
    raise SystemExit("❌ .env 파일에 KAKAO_REST_API_KEY 와 KAKAO_CLIENT_SECRET 을 먼저 넣어주세요.")

state = secrets.token_urlsafe(16)  # 보안용 임의 문자열 (다른 사람이 끼어들지 못하게)
received = {}


class CallbackHandler(BaseHTTPRequestHandler):
    """카카오가 로그인 후 돌려보내는 주소(localhost:5000/callback)를 받아주는 작은 서버."""

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        received["code"] = query.get("code", [None])[0]
        received["state"] = query.get("state", [None])[0]
        received["error"] = query.get("error_description", query.get("error", [None]))[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("<h2>완료! 이 창을 닫고 프로그램 화면으로 돌아가세요.</h2>".encode("utf-8"))

    def log_message(self, *args):  # 서버 기록 메시지는 화면에 안 보이게
        pass


auth_url = "https://kauth.kakao.com/oauth/authorize?" + urlencode({
    "response_type": "code",
    "client_id": REST_API_KEY,
    "redirect_uri": REDIRECT_URI,
    "scope": "talk_message",  # '카카오톡 메시지 전송' 권한을 요청
    "state": state,
})

print("🌐 브라우저에서 카카오 로그인 창을 엽니다. 로그인하고 '동의하고 계속하기'를 눌러주세요.")
webbrowser.open(auth_url)

server = HTTPServer(("localhost", 5000), CallbackHandler)
server.handle_request()  # 카카오가 돌려보내는 요청 1번을 기다린다

if received.get("error"):
    raise SystemExit(f"❌ 로그인 실패: {received['error']}")
if received.get("state") != state or not received.get("code"):
    raise SystemExit("❌ 올바른 응답을 받지 못했어요. 다시 실행해 주세요.")

# 인가 코드를 토큰으로 바꾸기
response = requests.post("https://kauth.kakao.com/oauth/token", data={
    "grant_type": "authorization_code",
    "client_id": REST_API_KEY,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI,
    "code": received["code"],
})
tokens = response.json()

if "access_token" not in tokens:
    raise SystemExit(f"❌ 토큰 받기 실패: {tokens}")

with open(TOKEN_FILE, "w", encoding="utf-8") as f:
    json.dump(tokens, f, ensure_ascii=False, indent=2)

print(f"✅ 토큰을 {TOKEN_FILE} 에 저장했어요. (이 파일도 비밀이에요!)")
