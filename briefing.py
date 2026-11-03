"""
[매일 아침 실행할 메인 프로그램] 날씨·뉴스를 모아서 내 카톡으로 보내고, 요약 페이지도 만든다.

실행 방법:
  python briefing.py --dry-run   → 카톡으로 보내지 않고 화면 + 요약 페이지 파일만 만듦 (테스트용)
  python briefing.py             → 실제로 카톡 전송
"""
import sys
from datetime import datetime, timedelta, timezone

from kakao_send import send_to_me
from news import format_news, get_headlines
from page import make_page
from weather import get_weather_text

KST = timezone(timedelta(hours=9))  # 한국 시간 (GitHub 서버는 다른 나라 시간이라 직접 지정)
DAYS = "월화수목금토일"
LIMIT = 200  # 카톡 텍스트 메시지 최대 글자 수


def log(text):
    """화면에 시간과 함께 기록을 남긴다. (5단계에서 GitHub 실행 기록에 그대로 남음)"""
    print(f"[{datetime.now(KST):%H:%M:%S}] {text}")


def safe(name, get_data, fallback):
    """한 부분(날씨/뉴스)이 실패해도 멈추지 않고, 대신할 값(fallback)을 쓴다."""
    try:
        data = get_data()
        log(f"{name} 가져오기 성공")
        return data
    except Exception as error:
        log(f"⚠️ {name} 가져오기 실패: {error}")
        return fallback


dry_run = "--dry-run" in sys.argv

today = datetime.now(KST)
date_text = f"{today.month}/{today.day}({DAYS[today.weekday()]})"

# 1) 재료 모으기 (한 번만 가져와서 카톡과 페이지에 같이 씀)
weather = safe("날씨", get_weather_text, "⚠️ 오늘은 날씨 정보를 못 가져왔어요.")
top_news = safe("주요 뉴스", lambda: get_headlines("주요"), [])
economy_news = safe("경제 뉴스", lambda: get_headlines("경제"), [])

# 2) 요약 페이지 만들기 (뉴스 전체 + 링크)
page_path = make_page(f"{date_text} 아침 브리핑", weather, [
    ("📰 주요 뉴스", top_news),
    ("💰 경제 뉴스", economy_news),
])
log(f"요약 페이지 생성: {page_path}")

# 3) 카톡 메시지 만들기
message1 = f"☀️ 좋은 아침! {date_text}\n\n{weather}\n\n"
message1 += format_news("주요", "📰", top_news, LIMIT - len(message1))
message2 = format_news("경제", "💰", economy_news, LIMIT)

for number, message in enumerate([message1, message2], start=1):
    log(f"메시지 {number} ({len(message)}자 / 최대 {LIMIT}자):\n{message}")
    if len(message) > LIMIT:
        raise SystemExit(f"❌ 메시지 {number}이 {LIMIT}자를 넘어서 보낼 수 없어요.")

if dry_run:
    log("🧪 미리보기 모드라서 전송하지 않았어요.")
else:
    send_to_me(message1)
    send_to_me(message2)
