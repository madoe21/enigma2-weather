# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime

from .wmo import map_weather_code


class WeatherService(object):
    def __init__(self, api_client):
        self.api_client = api_client

    def search_city_candidates(self, query):
        raw_items = self.api_client.search_cities(query, count=12, language="en")
        cities = []
        for item in raw_items:
            name = item.get("name", "")
            country = item.get("country", "")
            admin1 = item.get("admin1", "")
            lat = item.get("latitude")
            lon = item.get("longitude")
            timezone = item.get("timezone", "auto")
            if lat is None or lon is None:
                continue
            cities.append(
                {
                    "name": name,
                    "country": country,
                    "admin1": admin1,
                    "latitude": float(lat),
                    "longitude": float(lon),
                    "timezone": timezone,
                    "label": self._city_label(name, admin1, country),
                }
            )
        return cities

    def build_city_weather(self, city):
        payload = self.api_client.fetch_forecast(city.latitude, city.longitude, city.timezone)

        current = payload.get("current") if isinstance(payload, dict) else {}
        hourly = payload.get("hourly") if isinstance(payload, dict) else {}
        daily = payload.get("daily") if isinstance(payload, dict) else {}
        current = current or {}
        hourly = hourly or {}
        daily = daily or {}

        current_temp = current.get("temperature_2m")
        current_code = current.get("weather_code")
        current_time = current.get("time")
        current_icon, current_text = map_weather_code(current_code)

        next_hours = self._collect_next_hours(hourly, current_time)
        next_days = self._collect_next_days(daily, limit=5)

        return {
            "city": city.display_name(),
            "temperature": self._fmt_temp(current_temp),
            "feels_like": self._fmt_temp(current.get("apparent_temperature")),
            "humidity": self._fmt_percent(current.get("relative_humidity_2m")),
            "wind": self._fmt_wind(
                current.get("wind_speed_10m"),
                current.get("wind_direction_10m"),
            ),
            "precipitation": self._fmt_precip(current.get("precipitation")),
            "condition": current_text,
            "condition_icon": current_icon,
            "hours": next_hours,
            "days": next_days,
        }

    def _collect_next_hours(self, hourly, current_time):
        times = hourly.get("time") if isinstance(hourly, dict) else []
        temps = hourly.get("temperature_2m") if isinstance(hourly, dict) else []
        codes = hourly.get("weather_code") if isinstance(hourly, dict) else []
        probs = hourly.get("precipitation_probability") if isinstance(hourly, dict) else []

        if not isinstance(times, list) or not isinstance(temps, list) or not isinstance(codes, list):
            return []
        if not isinstance(probs, list):
            probs = []

        start_index = 0
        if current_time and current_time in times:
            start_index = times.index(current_time) + 1

        rows = []
        idx = start_index
        while idx < len(times) and len(rows) < 4:
            icon, label = map_weather_code(codes[idx] if idx < len(codes) else None)
            rows.append(
                {
                    "time": self._fmt_hour(times[idx]),
                    "temp": self._fmt_temp(temps[idx] if idx < len(temps) else None),
                    "condition": label,
                    "icon": icon,
                    "precip_prob": self._fmt_percent(probs[idx] if idx < len(probs) else None),
                }
            )
            idx += 1
        return rows

    def _collect_next_days(self, daily, limit=5):
        dates = daily.get("time") if isinstance(daily, dict) else []
        maxes = daily.get("temperature_2m_max") if isinstance(daily, dict) else []
        mins = daily.get("temperature_2m_min") if isinstance(daily, dict) else []
        codes = daily.get("weather_code") if isinstance(daily, dict) else []
        precs = daily.get("precipitation_sum") if isinstance(daily, dict) else []
        probs = daily.get("precipitation_probability_max") if isinstance(daily, dict) else []
        winds = daily.get("wind_speed_10m_max") if isinstance(daily, dict) else []

        if not isinstance(dates, list) or not isinstance(maxes, list) or not isinstance(mins, list) or not isinstance(codes, list):
            return []
        if not isinstance(precs, list):
            precs = []
        if not isinstance(probs, list):
            probs = []
        if not isinstance(winds, list):
            winds = []

        rows = []
        for idx, date_text in enumerate(dates):
            if len(rows) >= int(limit):
                break
            icon, label = map_weather_code(codes[idx] if idx < len(codes) else None)
            rows.append(
                {
                    "day": self._fmt_day_label(date_text, idx == 0),
                    "condition": label,
                    "icon": icon,
                    "temp_min": self._fmt_temp(mins[idx] if idx < len(mins) else None),
                    "temp_max": self._fmt_temp(maxes[idx] if idx < len(maxes) else None),
                    "precip_prob": self._fmt_percent(probs[idx] if idx < len(probs) else None),
                    "precip_sum": self._fmt_precip(precs[idx] if idx < len(precs) else None),
                    "wind": self._fmt_wind_simple(winds[idx] if idx < len(winds) else None),
                }
            )
        return rows

    def _fmt_temp(self, value):
        if value is None:
            return u"-"
        try:
            return u"%d\u00b0C" % int(round(float(value)))
        except Exception:
            return u"-"

    def _fmt_percent(self, value):
        if value is None:
            return u"-"
        try:
            return u"%d%%" % int(round(float(value)))
        except Exception:
            return u"-"

    def _fmt_precip(self, value):
        if value is None:
            return u"-"
        try:
            v = float(value)
        except Exception:
            return u"-"
        if v <= 0:
            return u"0 mm"
        if v < 1:
            return u"%.1f mm" % v
        return u"%d mm" % int(round(v))

    def _fmt_wind(self, speed, direction):
        speed_text = self._fmt_wind_simple(speed)
        if speed_text == u"-":
            return speed_text
        arrow = self._wind_arrow(direction)
        if arrow:
            return u"%s %s" % (arrow, speed_text)
        return speed_text

    def _fmt_wind_simple(self, speed):
        if speed is None:
            return u"-"
        try:
            return u"%d km/h" % int(round(float(speed)))
        except Exception:
            return u"-"

    def _wind_arrow(self, direction):
        if direction is None:
            return u""
        try:
            deg = float(direction) % 360.0
        except Exception:
            return u""
        labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        idx = int((deg + 22.5) // 45) % 8
        return labels[idx]

    def _fmt_hour(self, timestamp):
        if not timestamp:
            return "--:--"
        try:
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M")
            return dt.strftime("%H:%M")
        except Exception:
            return str(timestamp)[-5:]

    def _fmt_day_label(self, date_text, is_today):
        if is_today:
            return "Today"
        try:
            dt = datetime.strptime(date_text, "%Y-%m-%d")
            return dt.strftime("%A")
        except Exception:
            return date_text

    def _city_label(self, name, admin1, country):
        parts = [name]
        if admin1:
            parts.append(admin1)
        if country:
            parts.append(country)
        return ", ".join([part for part in parts if part])
