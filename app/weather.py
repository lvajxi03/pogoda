import httpx

URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: ("Bezchmurnie", "☀️"),
    1: ("Przeważnie pogodnie", "🌤️"),
    2: ("Częściowe zachmurzenie", "⛅"),
    3: ("Pochmurno", "☁️"),
    45: ("Mgła", "🌫️"),
    48: ("Mgła osadzająca szadź", "🌫️"),
    51: ("Lekka mżawka", "🌦️"),
    53: ("Mżawka", "🌦️"),
    55: ("Gęsta mżawka", "🌧️"),
    61: ("Lekki deszcz", "🌧️"),
    63: ("Deszcz", "🌧️"),
    65: ("Silny deszcz", "🌧️"),
    71: ("Lekki śnieg", "🌨️"),
    73: ("Śnieg", "🌨️"),
    75: ("Silny śnieg", "❄️"),
    80: ("Przelotny deszcz", "🌦️"),
    81: ("Przelotny deszcz", "🌧️"),
    82: ("Silna ulewa", "⛈️"),
    95: ("Burza", "⛈️"),
    96: ("Burza z gradem", "⛈️"),
    99: ("Silna burza z gradem", "⛈️"),
}


def describe_weather(code: int):
    return WEATHER_CODES.get(code, ("Nieznana pogoda", "🌡️"))


def weather_icon(code: int):
    return WEATHER_CODES.get(code, ("", "🌡️"))[1]


async def get_weather(city):
    params = {
        "latitude": city.latitude,
        "longitude": city.longitude,

        "current": ",".join([
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "weather_code",
            "wind_speed_10m",
        ]),

        "daily": ",".join([
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "wind_speed_10m_max",
        ]),

        "forecast_days": 5,
        "timezone": "auto",
    }

    async with httpx.AsyncClient(timeout=8) as client:
        r = await client.get(URL, params=params)
        r.raise_for_status()
        return r.json()
