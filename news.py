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
MAX_TITLE = 45  # 카톡에서는 제목이 너무 길면 이 글자 수에서 자르고 "…" 붙임


def get_headlines(topic, count=10):
    """분야(topic)의 최신 뉴스를 [{제목, 링크, 언론사}, ...] 목록으로 가져온다."""
    response = requests.get(FEEDS[topic], timeout=10)
    response.raise_for_status()  # 사이트가 오류를 돌려주면 여기서 멈춤
    root = ET.fromstring(response.content)

    items = []
    for item in root.iter("item"):
        source = item.findtext("source", "").strip()
        title = item.findtext("title", "").strip()
        if source and title.endswith(f" - {source}"):
            title = title[: -len(f" - {source}")]  # 끝의 " - 언론사명" 제거
        if title:
            items.append({"title": title, "link": item.findtext("link", ""), "source": source})
        if len(items) == count:
            break
    if not items:
        raise ValueError("뉴스 제목을 하나도 못 찾았어요")
    return items


def format_news(topic, emoji, items, max_chars):
    """카톡용: 뉴스 제목들을 max_chars 글자 안에 들어가는 만큼만 담아 글로 만든다."""
    if not items:
        return f"⚠️ 오늘은 {topic} 뉴스를 못 가져왔어요."
    text = f"{emoji} {topic} 뉴스"
    for item in items:
        title = item["title"]
        if len(title) > MAX_TITLE:
            title = title[:MAX_TITLE - 1] + "…"
        line = f"\n• {title}"
        if len(text) + len(line) > max_chars:
            break  # 더 넣으면 넘치니까 여기서 멈춤
        text += line
    return text


if __name__ == "__main__":
    print(format_news("주요", "📰", get_headlines("주요"), 130))
    print()
    print(format_news("경제", "💰", get_headlines("경제"), 200))
