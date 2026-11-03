"""
[매일 아침 실행할 메인 프로그램] 날씨(+ 나중에 뉴스)를 모아서 내 카톡으로 보낸다.

실행 방법:
  python briefing.py --dry-run   → 카톡으로 보내지 않고 화면에만 미리 보여줌 (테스트용)
  python briefing.py             → 실제로 카톡 전송
"""
import sys
from datetime import datetime, timedelta, timezone

from kakao_send import send_to_me
from news import get_news_text
from weather import get_weather_text

KST = timezone(timedelta(hours=9))  # 한국 시간 (GitHub 서버는 다른 나라 시간이라 직접 지정)
DAYS = "월화수목금토일"


def log(text):
    """화면에 시간과 함께 기록을 남긴다. (5단계에서 GitHub 실행 기록에 그대로 남음)"""
    print(f"[{datetime.now(KST):%H:%M:%S}] {text}")


def safe(name, get_text):
    """한 부분(날씨/뉴스)이 실패해도 멈추지 않고, 실패했다는 문구로 대신한다."""
    try:
        text = get_text()
        log(f"{name} 가져오기 성공")
        return text
    except Exception as error:
        log(f"⚠️ {name} 가져오기 실패: {error}")
        return f"⚠️ 오늘은 {name} 정보를 못 가져왔어요."


dry_run = "--dry-run" in sys.argv
LIMIT = 200  # 카톡 텍스트 메시지 최대 글자 수

today = datetime.now(KST)
header = f"☀️ 좋은 아침! {today.month}/{today.day}({DAYS[today.weekday()]})"

# 메시지 1: 날씨 + 주요 뉴스 (날씨를 넣고 남은 글자 수만큼 뉴스를 채움)
message1 = f"{header}\n\n{safe('날씨', get_weather_text)}\n\n"
room = LIMIT - len(message1)
message1 += safe("주요 뉴스", lambda: get_news_text("주요", "📰", room))

# 메시지 2: 경제 뉴스
message2 = safe("경제 뉴스", lambda: get_news_text("경제", "💰", LIMIT))

for number, message in enumerate([message1, message2], start=1):
    log(f"메시지 {number} ({len(message)}자 / 최대 {LIMIT}자):\n{message}")
    if len(message) > LIMIT:
        raise SystemExit(f"❌ 메시지 {number}이 {LIMIT}자를 넘어서 보낼 수 없어요.")

if dry_run:
    log("🧪 미리보기 모드라서 전송하지 않았어요.")
else:
    send_to_me(message1)
    send_to_me(message2)
