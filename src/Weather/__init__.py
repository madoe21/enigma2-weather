# -*- coding: utf-8 -*-
from __future__ import absolute_import

import gettext

from Components.Language import language
from Tools.Directories import SCOPE_PLUGINS, resolveFilename

PLUGIN_DOMAIN = "Weather"
PLUGIN_PATH = "Extensions/Weather/locale"

_DE_FALLBACK = {
    "Weather": "Wetter",
    "Current weather": "Aktuelles Wetter",
    "Next 4 hours": "Nächste 4 Stunden",
    "Daily forecast": "Tagesvorhersage",
    "Settings": "Einstellungen",
    "Refresh": "Aktualisieren",
    "Close": "Schließen",
    "Back": "Zurück",
    "Manage cities": "Städte verwalten",
    "Search city": "Stadt suchen",
    "Add city": "Stadt hinzufügen",
    "Remove city": "Stadt entfernen",
    "Move up": "Nach oben",
    "Move down": "Nach unten",
    "No city configured": "Keine Stadt konfiguriert",
    "Please add at least one city": "Bitte mindestens eine Stadt hinzufügen",
    "Enter city name": "Stadtname eingeben",
    "No city matches found": "Keine passenden Städte gefunden",
    "Could not load weather data": "Wetterdaten konnten nicht geladen werden",
    "Today": "Heute",
    "Information": "Information",
    "Sunny": "Sonnig",
    "Mainly clear": "Überwiegend klar",
    "Partly cloudy": "Teilweise bewölkt",
    "Overcast": "Bedeckt",
    "Fog": "Nebel",
    "Rime fog": "Raureifnebel",
    "Light drizzle": "Leichter Nieselregen",
    "Moderate drizzle": "Mäßiger Nieselregen",
    "Dense drizzle": "Dichter Nieselregen",
    "Freezing drizzle": "Gefrierender Nieselregen",
    "Heavy freezing drizzle": "Starker gefrierender Nieselregen",
    "Slight rain": "Leichter Regen",
    "Rain": "Regen",
    "Heavy rain": "Starker Regen",
    "Freezing rain": "Gefrierender Regen",
    "Heavy freezing rain": "Starker gefrierender Regen",
    "Slight snow": "Leichter Schneefall",
    "Snow": "Schneefall",
    "Heavy snow": "Starker Schneefall",
    "Snow grains": "Schneegriesel",
    "Rain showers": "Regenschauer",
    "Violent rain showers": "Heftige Regenschauer",
    "Snow showers": "Schneeschauer",
    "Heavy snow showers": "Starke Schneeschauer",
    "Thunderstorm": "Gewitter",
    "Thunderstorm with hail": "Gewitter mit Hagel",
    "Strong thunderstorm with hail": "Starkes Gewitter mit Hagel",
    "Unknown": "Unbekannt",
}


def localeInit():
    gettext.bindtextdomain(PLUGIN_DOMAIN, resolveFilename(SCOPE_PLUGINS, PLUGIN_PATH))
    try:
        gettext.bind_textdomain_codeset(PLUGIN_DOMAIN, "UTF-8")
    except Exception:
        pass


def _(txt):
    translated = gettext.dgettext(PLUGIN_DOMAIN, txt)
    if translated != txt:
        return translated

    try:
        lang = language.getLanguage()[:2]
    except Exception:
        lang = "en"

    if lang == "de":
        return _DE_FALLBACK.get(txt, txt)
    return txt


localeInit()
try:
    language.addCallback(localeInit)
except Exception:
    pass
