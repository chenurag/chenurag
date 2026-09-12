import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

LATITUDE = 6.9271
LONGITUDE = 79.8612
API = "https://api.open-meteo.com/v1/forecast?"
PARAMS = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
    "daily": "temperature_2m_max,temperature_2m_min",
    "forecast_days": 5,
    "timezone": "Asia/Colombo",
}

WEATHER = {
    0: "CLEAR SKY", 1: "MAINLY CLEAR", 2: "PARTLY CLOUDY", 3: "OVERCAST",
    45: "FOGGY", 48: "RIME FOG", 51: "LIGHT DRIZZLE", 53: "DRIZZLE",
    55: "HEAVY DRIZZLE", 61: "LIGHT RAIN", 63: "RAIN", 65: "HEAVY RAIN",
    71: "LIGHT SNOW", 73: "SNOW", 75: "HEAVY SNOW", 80: "RAIN SHOWERS",
    81: "RAIN SHOWERS", 82: "HEAVY SHOWERS", 95: "THUNDERSTORM",
    96: "THUNDERSTORM", 99: "THUNDERSTORM",
}


def fetch_weather():
    url = API + urllib.parse.urlencode(PARAMS)
    request = urllib.request.Request(url, headers={"User-Agent": "chenurag-profile-weather/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def esc(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def dashboard(data):
    current = data["current"]
    daily = data["daily"]
    days = []
    for date, high, low in zip(
        daily["time"], daily["temperature_2m_max"], daily["temperature_2m_min"]
    ):
        day = datetime.fromisoformat(date).strftime("%a").upper()
        days.append(f'<text x="{len(days) * 92}" y="170">{day} {round(high)}°/{round(low)}°</text>')
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    condition = WEATHER.get(current["weather_code"], "CHANGEABLE")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 240" width="100%" role="img" aria-labelledby="title desc">
  <title id="title">Dynamic weather operations dashboard</title>
  <desc id="desc">Live Colombo, Sri Lanka weather refreshed hourly from Open-Meteo.</desc>
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#061326"/><stop offset="1" stop-color="#102b4a"/></linearGradient>
    <linearGradient id="line" x1="0" x2="1"><stop stop-color="#53b8ff"/><stop offset="1" stop-color="#7cf6d2"/></linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <style>.pulse{{animation:p 3s ease-in-out infinite}}.scan{{animation:s 5s linear infinite}}@keyframes p{{50%{{opacity:.45}}}}@keyframes s{{from{{transform:translateX(-1200px)}}to{{transform:translateX(1200px)}}}}</style>
  </defs>
  <rect width="1200" height="240" rx="12" fill="url(#bg)"/><rect x="1" y="1" width="1198" height="238" rx="12" fill="none" stroke="#53b8ff" opacity=".35"/>
  <rect class="scan" width="1200" height="2" fill="#7cf6d2" opacity=".16"/>
  <g font-family="ui-monospace, SFMono-Regular, Consolas, monospace">
    <text x="38" y="38" fill="#7cf6d2" font-size="13" letter-spacing="3">WEATHER OPERATIONS / LIVE TELEMETRY</text>
    <circle class="pulse" cx="1154" cy="33" r="6" fill="#7cf6d2" filter="url(#glow)"/><text x="1170" y="38" fill="#9db6cf" font-size="11" text-anchor="end">ONLINE</text>
    <rect x="38" y="63" width="300" height="135" rx="9" fill="#071b31" stroke="#23567a"/>
    <text x="60" y="91" fill="#9db6cf" font-size="12">COLOMBO, LK / 6.93° N</text>
    <text x="60" y="145" fill="#eaf7ff" font-size="48">{round(current["temperature_2m"])}°</text><text x="177" y="141" fill="#7cf6d2" font-size="14">{esc(condition)}</text>
    <text x="60" y="175" fill="#9db6cf" font-size="12">HUMIDITY {round(current["relative_humidity_2m"])}%   WIND {round(current["wind_speed_10m"])} KM/H</text>
    <g transform="translate(380 70)"><text x="0" y="18" fill="#9db6cf" font-size="12">5-DAY OUTLOOK</text>
      <g transform="translate(0 35)" fill="none" stroke="url(#line)" stroke-width="2"><path d="M0 60 C50 28 95 56 145 23 S238 40 292 10 S390 45 445 20" opacity=".8"/><path d="M0 93 C55 72 100 94 145 61 S240 84 292 54 S390 91 445 68" stroke="#4f7899" opacity=".8"/></g>
      <g fill="#dff7ff" font-size="12">{''.join(days)}</g>
    </g>
    <text x="1138" y="218" fill="#527b9b" font-size="10" text-anchor="end">OPEN-METEO // UPDATED {esc(updated)}</text>
  </g>
</svg>
'''


if __name__ == "__main__":
    Path("assets/weather-ops.svg").write_text(dashboard(fetch_weather()), encoding="utf-8")
