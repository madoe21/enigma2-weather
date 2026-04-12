# -*- coding: utf-8 -*-
from __future__ import absolute_import


class City(object):
    def __init__(self, name, country, latitude, longitude, timezone, admin1=""):
        self.name = name or ""
        self.country = country or ""
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.timezone = timezone or "auto"
        self.admin1 = admin1 or ""

    def display_name(self):
        parts = [self.name]
        if self.admin1:
            parts.append(self.admin1)
        if self.country:
            parts.append(self.country)
        return ", ".join([part for part in parts if part])

    def to_dict(self):
        return {
            "name": self.name,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "admin1": self.admin1,
        }

    @staticmethod
    def from_dict(data):
        data = data or {}
        return City(
            name=data.get("name", ""),
            country=data.get("country", ""),
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            timezone=data.get("timezone", "auto"),
            admin1=data.get("admin1", ""),
        )
