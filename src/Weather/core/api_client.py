# -*- coding: utf-8 -*-
from __future__ import absolute_import

import json

try:
    from urllib import urlencode
    from urllib2 import Request, URLError, urlopen
except ImportError:
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen
    from urllib.error import URLError


class OpenMeteoApiClient(object):
    GEOCODE_ENDPOINT = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_ENDPOINT = "https://api.open-meteo.com/v1/forecast"

    def _get_json(self, base_url, params, timeout=12):
        query = urlencode(params)
        url = "%s?%s" % (base_url, query)
        req = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "enigma2-openmeteo-weather/1.0",
            },
        )
        response = urlopen(req, timeout=timeout)
        raw = response.read()
        if not isinstance(raw, str):
            raw = raw.decode("utf-8")
        return json.loads(raw)

    def search_cities(self, name, count=10, language="en"):
        query = (name or "").strip()
        if not query:
            return []

        params = {
            "name": query,
            "count": int(count),
            "language": language,
            "format": "json",
        }

        try:
            payload = self._get_json(self.GEOCODE_ENDPOINT, params)
        except URLError as exc:
            raise Exception("Network error: %s" % exc)
        except Exception as exc:
            raise Exception("Geocoding failed: %s" % exc)

        results = payload.get("results") if isinstance(payload, dict) else None
        if not isinstance(results, list):
            return []
        return results

    def fetch_forecast(self, latitude, longitude, timezone="auto"):
        params = {
            "latitude": "%.6f" % float(latitude),
            "longitude": "%.6f" % float(longitude),
            "current": ",".join([
                "temperature_2m",
                "apparent_temperature",
                "relative_humidity_2m",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "precipitation",
                "is_day",
            ]),
            "hourly": ",".join([
                "temperature_2m",
                "weather_code",
                "precipitation_probability",
            ]),
            "daily": ",".join([
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
            ]),
            "wind_speed_unit": "kmh",
            "timezone": timezone or "auto",
            "forecast_days": 7,
        }

        try:
            return self._get_json(self.FORECAST_ENDPOINT, params)
        except URLError as exc:
            raise Exception("Network error: %s" % exc)
        except Exception as exc:
            raise Exception("Forecast request failed: %s" % exc)
