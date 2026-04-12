# -*- coding: utf-8 -*-
from __future__ import absolute_import

WMO_MAP = {
    0: ("clear", "Sunny"),
    1: ("partly_cloudy", "Mainly clear"),
    2: ("partly_cloudy", "Partly cloudy"),
    3: ("cloudy", "Overcast"),
    45: ("fog", "Fog"),
    48: ("fog", "Rime fog"),
    51: ("drizzle", "Light drizzle"),
    53: ("drizzle", "Moderate drizzle"),
    55: ("drizzle", "Dense drizzle"),
    56: ("drizzle", "Freezing drizzle"),
    57: ("drizzle", "Heavy freezing drizzle"),
    61: ("rain", "Slight rain"),
    63: ("rain", "Rain"),
    65: ("rain", "Heavy rain"),
    66: ("rain", "Freezing rain"),
    67: ("rain", "Heavy freezing rain"),
    71: ("snow", "Slight snow"),
    73: ("snow", "Snow"),
    75: ("snow", "Heavy snow"),
    77: ("snow", "Snow grains"),
    80: ("rain", "Rain showers"),
    81: ("rain", "Rain showers"),
    82: ("rain", "Violent rain showers"),
    85: ("snow", "Snow showers"),
    86: ("snow", "Heavy snow showers"),
    95: ("thunder", "Thunderstorm"),
    96: ("thunder", "Thunderstorm with hail"),
    99: ("thunder", "Strong thunderstorm with hail"),
}


def map_weather_code(code):
    try:
        code = int(code)
    except Exception:
        return "unknown", "Unknown"
    return WMO_MAP.get(code, ("unknown", "Unknown"))
