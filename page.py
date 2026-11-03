"""
카톡 [자세히 보기] 버튼이 열 '오늘의 요약 페이지'(웹페이지)를 만드는 프로그램.

만든 파일: site/index.html
5단계에서 GitHub Pages(무료 웹사이트)에 올려서 휴대폰으로 볼 수 있게 함.
⚠️ 이 페이지는 누구나 볼 수 있는 공개 페이지이므로 개인적인 내용은 넣지 말 것!
"""
import os
from html import escape

SITE_DIR = "site"


def make_page(title, weather_text, sections, ai_summary=None):
    """
    title: 페이지 제목 (예: "11/3(화) 아침 브리핑")
    weather_text: 날씨 글
    sections: [("📰 주요 뉴스", [뉴스, ...]), ("💰 경제 뉴스", [...])]
    ai_summary: AI 3줄 요약 (실패했으면 None → 칸을 안 보여줌)
    """
    ai_block = ""
    if ai_summary:
        ai_lines = "".join(f"<li>{escape(line)}</li>" for line in ai_summary.splitlines())
        ai_block = (
            f'<section class="ai"><h2>🤖 AI 요약</h2><ul>{ai_lines}</ul>'
            f'<p class="note">AI가 아래 기사 제목들을 보고 쓴 요약이라 틀릴 수 있어요. 자세한 내용은 원문을 확인하세요.</p></section>'
        )

    blocks = []
    for heading, items in sections:
        if items:
            rows = "".join(
                f'<li><a href="{escape(i["link"])}" target="_blank" rel="noopener">{escape(i["title"])}</a>'
                f'<span class="src">{escape(i["source"])}</span></li>'
                for i in items
            )
            blocks.append(f"<section><h2>{escape(heading)}</h2><ol>{rows}</ol></section>")
        else:
            blocks.append(f"<section><h2>{escape(heading)}</h2><p>⚠️ 오늘은 뉴스를 못 가져왔어요.</p></section>")

    weather_html = escape(weather_text).replace("\n", "<br>")

    html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{escape(title)}</title>
<style>
  :root {{ --bg:#f6f7f9; --card:#fff; --text:#1d1f23; --sub:#6b7280; --accent:#2563eb; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#111317; --card:#1b1e24; --text:#e8eaed; --sub:#9aa0a6; --accent:#7ab0ff; }}
  }}
  body {{ margin:0; background:var(--bg); color:var(--text);
         font-family:-apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; line-height:1.55; }}
  main {{ max-width:640px; margin:0 auto; padding:20px 16px 40px; }}
  h1 {{ font-size:1.4rem; margin:4px 0 16px; }}
  h2 {{ font-size:1.1rem; margin:0 0 10px; }}
  section {{ background:var(--card); border-radius:14px; padding:16px 18px; margin-bottom:14px; }}
  ol {{ margin:0; padding-left:1.3em; }}
  li {{ margin:0 0 10px; }}
  a {{ color:var(--text); text-decoration:none; }}
  a:hover {{ color:var(--accent); text-decoration:underline; }}
  .src {{ display:block; font-size:.8rem; color:var(--sub); }}
  footer {{ text-align:center; font-size:.8rem; color:var(--sub); }}
  .ai {{ border:2px solid var(--accent); }}
  .ai ul {{ list-style:none; margin:0; padding:0; }}
  .ai li {{ margin:0 0 8px; font-size:1.02rem; }}
  .note {{ margin:8px 0 0; font-size:.78rem; color:var(--sub); }}
</style>
</head>
<body>
<main>
  <h1>☀️ {escape(title)}</h1>
  {ai_block}
  <section><h2>오늘의 날씨</h2><p style="margin:0">{weather_html}</p></section>
  {"".join(blocks)}
  <footer>제목을 누르면 기사 원문으로 이동해요 · 출처: Open-Meteo, Google 뉴스 · 요약: Claude</footer>
</main>
</body>
</html>
"""
    os.makedirs(SITE_DIR, exist_ok=True)
    path = os.path.join(SITE_DIR, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
