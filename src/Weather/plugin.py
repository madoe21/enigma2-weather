# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import sys

from Plugins.Plugin import PluginDescriptor
from Tools.Directories import SCOPE_PLUGINS, resolveFilename

from . import _

USE_ASPECT_ICON_VARIANTS = True
_APP = None


def _log(message):
    try:
        sys.stderr.write("[Weather] %s\n" % message)
    except Exception:
        pass


class AppContext(object):
    def __init__(self):
        from .core.api_client import OpenMeteoApiClient
        from .core.service import WeatherService
        from .store import WeatherStore

        self.store = WeatherStore()
        self.api = OpenMeteoApiClient()
        self.service = WeatherService(self.api)

    def list_cities(self):
        return self.store.list_cities()

    def first_city(self):
        return self.store.first_city()

    def add_city_from_candidate(self, candidate):
        from .core.models import City

        city = City(
            name=candidate.get("name", ""),
            country=candidate.get("country", ""),
            admin1=candidate.get("admin1", ""),
            latitude=candidate.get("latitude", 0.0),
            longitude=candidate.get("longitude", 0.0),
            timezone=candidate.get("timezone", "auto"),
        )
        return self.store.add_city(city)

    def remove_city(self, index):
        return self.store.remove_city(index)

    def move_city_up(self, index):
        return self.store.move_up(index)

    def move_city_down(self, index):
        return self.store.move_down(index)


class ScreenAppAdapter(object):
    def __init__(self, app_context):
        self.app = app_context


def _get_app():
    global _APP
    if _APP is None:
        _APP = AppContext()
    return _APP


def main(session, **kwargs):
    try:
        from .screens import WeatherMainScreen
    except Exception as exc:
        _log("import WeatherMainScreen failed: %s" % exc)
        return

    try:
        app = _get_app()
    except Exception as exc:
        _log("AppContext init failed: %s" % exc)
        return

    try:
        session.open(WeatherMainScreen, ScreenAppAdapter(app))
    except Exception as exc:
        _log("session.open WeatherMainScreen failed: %s" % exc)


def _icon_file_for_aspect_ratio():
    try:
        from enigma import getDesktop

        size = getDesktop(0).size()
        width = int(size.width())
        height = int(size.height())
        if height > 0:
            ratio = float(width) / float(height)
            if ratio < 1.5:
                return "plugin_4x3.png"
            if ratio < 1.7:
                return "plugin_16x10.png"
            return "plugin_16x9.png"
    except Exception:
        pass
    return "plugin_16x9.png"


def _resolve_plugin_icon_path():
    fallback = resolveFilename(SCOPE_PLUGINS, "Extensions/Weather/res/plugin.png")
    if not USE_ASPECT_ICON_VARIANTS:
        return fallback

    icon_name = _icon_file_for_aspect_ratio()
    icon_path = resolveFilename(SCOPE_PLUGINS, "Extensions/Weather/res/%s" % icon_name)
    if os.path.exists(icon_path):
        return icon_path
    return fallback


def Plugins(**kwargs):
    plugin_icon = _resolve_plugin_icon_path()
    return [
        PluginDescriptor(
            name=_("Weather"),
            description=_("Weather"),
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon=plugin_icon,
            fnc=main,
        )
    ]
