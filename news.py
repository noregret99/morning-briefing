"""
구글 뉴스에서 헤드라인(뉴스 제목)을 가져오는 프로그램. (가입·키 필요 없음)

RSS = 뉴스 사이트가 "최신 글 목록"을 프로그램이 읽기 쉬운 형태로 제공하는 것.
"""
import xml.etree.ElementTree as ET

import requests

FEEDS = {
    "주요": "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
    "경제": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko",
}
MAX_TITLE = 45  # 제목이 너무 길면 이 글자 수에서 자르고 "…" 붙임


def get_headlines(topic, count=5):
    """분야(topic)의 최신 뉴스 제목 목록을 가져온다."""
    response = requests.get(FEEDS[topic], timeout=10)
    response.raise_for_status()  # 사이트가 오류를 돌려주면 여기서 멈춤
    root = ET.fromstring(response.content)

    titles = []
    for item in root.iter("item"):
        title = item.findtext("title", "").rsplit(" - ", 1)[0].strip()  # 끝의 " - 언론사명" 제거
        if title:
            titles.append(title)
        if len(titles) == count:
            break
    if not titles:
        raise ValueError("뉴스 제목을 하나도 못 찾았어요")
    return titles


def get_news_text(topic, emoji, max_chars):
    """뉴스 제목들을 max_chars 글자 안에 들어가는 만큼만 담아 글로 만든다."""
    text = f"{emoji} {topic} 뉴스"
    for title in get_headlines(topic):
        if len(title) > MAX_TITLE:
            title = title[:MAX_TITLE - 1] + "…"
        line = f"\n• {title}"
        if len(text) + len(line) > max_chars:
            break  # 더 넣으면 넘치니까 여기서 멈춤
        text += line
    return text


if __name__ == "__main__":
    print(get_news_text("주요", "📰", 130))
    print()
    print(get_news_text("경제", "💰", 200))
