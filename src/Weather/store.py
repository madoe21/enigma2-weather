# -*- coding: utf-8 -*-
from __future__ import absolute_import

import json
import os

from .core.models import City

STORE_FILE = "/etc/enigma2/weather.json"


class WeatherStore(object):
    def __init__(self, path=STORE_FILE):
        self.path = path

    def _read(self):
        try:
            with open(self.path, "r") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                return data
            return {}
        except Exception:
            return {}

    def _write(self, data):
        folder = os.path.dirname(self.path)
        if folder and not os.path.isdir(folder):
            os.makedirs(folder)
        with open(self.path, "w") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)

    def list_cities(self):
        data = self._read()
        raw = data.get("cities", [])
        if not isinstance(raw, list):
            return []
        cities = []
        for item in raw:
            try:
                cities.append(City.from_dict(item))
            except Exception:
                continue
        return cities

    def save_cities(self, cities):
        payload = {"cities": [city.to_dict() for city in (cities or [])]}
        self._write(payload)

    def add_city(self, city):
        cities = self.list_cities()
        key = self._city_key(city)
        existing = [self._city_key(entry) for entry in cities]
        if key in existing:
            return False
        cities.append(city)
        self.save_cities(cities)
        return True

    def remove_city(self, index):
        cities = self.list_cities()
        try:
            index = int(index)
        except Exception:
            return False
        if index < 0 or index >= len(cities):
            return False
        del cities[index]
        self.save_cities(cities)
        return True

    def move_up(self, index):
        cities = self.list_cities()
        try:
            index = int(index)
        except Exception:
            return False
        if index <= 0 or index >= len(cities):
            return False
        cities[index - 1], cities[index] = cities[index], cities[index - 1]
        self.save_cities(cities)
        return True

    def move_down(self, index):
        cities = self.list_cities()
        try:
            index = int(index)
        except Exception:
            return False
        if index < 0 or index >= len(cities) - 1:
            return False
        cities[index + 1], cities[index] = cities[index], cities[index + 1]
        self.save_cities(cities)
        return True

    def first_city(self):
        cities = self.list_cities()
        if not cities:
            return None
        return cities[0]

    def _city_key(self, city):
        return "%s|%s|%.4f|%.4f" % (
            city.name.strip().lower(),
            city.country.strip().lower(),
            float(city.latitude),
            float(city.longitude),
        )
