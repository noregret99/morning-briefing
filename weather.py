"""
오늘 날씨를 가져오는 프로그램. (Open-Meteo: 가입·키 없이 쓰는 무료 날씨 서비스)
"""
import requests

CITY_NAME = "김해"
LATITUDE = 35.2285   # 위도 (김해시청)
LONGITUDE = 128.8894  # 경도

# Open-Meteo는 날씨를 숫자 코드로 알려줌 → 사람이 읽는 말로 바꾸는 표
WEATHER_CODES = {
    0: "☀️ 맑음", 1: "🌤️ 대체로 맑음", 2: "⛅ 구름 조금", 3: "☁️ 흐림",
    45: "🌫️ 안개", 48: "🌫️ 짙은 안개",
    51: "🌦️ 약한 이슬비", 53: "🌦️ 이슬비", 55: "🌦️ 강한 이슬비",
    56: "🌧️ 어는 이슬비", 57: "🌧️ 어는 이슬비",
    61: "🌧️ 약한 비", 63: "🌧️ 비", 65: "🌧️ 강한 비",
    66: "🌧️ 어는 비", 67: "🌧️ 어는 비",
    71: "🌨️ 약한 눈", 73: "🌨️ 눈", 75: "❄️ 강한 눈", 77: "🌨️ 싸락눈",
    80: "🌦️ 소나기", 81: "🌦️ 소나기", 82: "⛈️ 강한 소나기",
    85: "🌨️ 눈 소나기", 86: "🌨️ 강한 눈 소나기",
    95: "⛈️ 뇌우", 96: "⛈️ 우박 동반 뇌우", 99: "⛈️ 우박 동반 뇌우",
}


def get_weather_text():
    """오늘 날씨를 짧은 글로 만들어 돌려준다."""
    response = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "Asia/Seoul",
        "forecast_days": 1,
    }, timeout=10)
    data = response.json()

    now = round(data["current"]["temperature_2m"])
    daily = data["daily"]
    sky = WEATHER_CODES.get(daily["weather_code"][0], "날씨 정보 없음")
    high = round(daily["temperature_2m_max"][0])
    low = round(daily["temperature_2m_min"][0])
    rain = daily["precipitation_probability_max"][0]

    text = f"📍{CITY_NAME} {sky}\n🌡️ 지금 {now}° (최저 {low}° / 최고 {high}°)\n☔ 강수확률 {rain}%"
    if rain is not None and rain >= 50:
        text += " → 우산 챙기세요!"
    return text


if __name__ == "__main__":
    print(get_weather_text())
