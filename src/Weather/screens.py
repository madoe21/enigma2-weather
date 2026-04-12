# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import sys
import threading

from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.ScrollLabel import ScrollLabel
from Components.Sources.StaticText import StaticText
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import SCOPE_PLUGINS, resolveFilename

try:
    from enigma import eTimer
except Exception:
    eTimer = None

try:
    from Screens.VirtualKeyBoard import VirtualKeyBoard
except Exception:
    VirtualKeyBoard = None

from . import _


def _log(message):
    try:
        sys.stderr.write("[Weather] %s\n" % message)
    except Exception:
        pass


def _make_timer(callback):
    if eTimer is None:
        return None
    timer = eTimer()
    try:
        timer_conn = timer.timeout.connect(callback)
        timer._conn = timer_conn
    except Exception:
        try:
            timer.callback.append(callback)
        except Exception:
            return None
    return timer


def _set_pixmap_file(widget, path):
    if widget is None or not path:
        return False
    try:
        instance = getattr(widget, "instance", None)
        if instance is None:
            return False
        instance.setPixmapFromFile(path)
        return True
    except Exception as exc:
        _log("pixmap load failed %s: %s" % (path, exc))
        return False


HOUR_COUNT = 4
DAY_COUNT = 5

_TRANSLATABLE_DAYS = (
    _("Monday"), _("Tuesday"), _("Wednesday"),
    _("Thursday"), _("Friday"), _("Saturday"), _("Sunday"),
)


class WeatherMainScreen(Screen):
    skin = """
        <screen name="WeatherMainScreen" position="center,center" size="1280,700" title="Weather">
            <widget source="title" render="Label" position="20,10" size="900,40" font="Regular;32" foregroundColor="#ffffff" transparent="1" />
            <widget source="city" render="Label" position="20,58" size="1240,32" font="Regular;26" foregroundColor="#cccccc" transparent="1" />
            <widget source="status" render="Label" position="20,92" size="1240,26" font="Regular;22" foregroundColor="#aaaaaa" transparent="1" />

            <widget name="current_icon" position="30,130" size="140,140" alphatest="blend" scale="1" />
            <widget source="current_temp" render="Label" position="190,130" size="500,70" font="Regular;58" foregroundColor="#ffffff" transparent="1" />
            <widget source="current_cond" render="Label" position="190,204" size="500,32" font="Regular;26" foregroundColor="#cccccc" transparent="1" />

            <widget source="stat_feels" render="Label" position="720,138" size="540,30" font="Regular;24" foregroundColor="#ffffff" transparent="1" />
            <widget source="stat_humidity" render="Label" position="720,174" size="540,30" font="Regular;24" foregroundColor="#ffffff" transparent="1" />
            <widget source="stat_wind" render="Label" position="720,210" size="540,30" font="Regular;24" foregroundColor="#ffffff" transparent="1" />
            <widget source="stat_precip" render="Label" position="720,246" size="540,30" font="Regular;24" foregroundColor="#ffffff" transparent="1" />

            <widget source="hours_head" render="Label" position="20,292" size="1240,26" font="Regular;22" foregroundColor="#888888" transparent="1" />

            <widget name="h0_icon" position="34,322" size="72,72" alphatest="blend" scale="1" />
            <widget source="h0_time" render="Label" position="120,320" size="200,28" font="Regular;24" foregroundColor="#ffffff" transparent="1" />
            <widget source="h0_temp" render="Label" position="120,350" size="200,28" font="Regular;22" foregroundColor="#cccccc" transparent="1" />
            <widget source="h0_cond" render="Label" position="120,378" size="200,22" font="Regular;18" foregroundColor="#888888" transparent="1" />

            <widget name="h1_icon" position="344,322" size="72,72" alphatest="blend" scale="1" />
            <widget source="h1_time" render="Label" position="430,320" size="200,28" font="Regular;24" foregroundColor="#ffffff" transparent="1" />
            <widget source="h1_temp" render="Label" position="430,350" size="200,28" font="Regular;22" foregroundColor="#cccccc" transparent="1" />
            <widget source="h1_cond" render="Label" position="430,378" size="200,22" font="Regular;18" foregroundColor="#888888" transparent="1" />

            <widget name="h2_icon" position="654,322" size="72,72" alphatest="blend" scale="1" />
            <widget source="h2_time" render="Label" position="740,320" size="200,28" font="Regular;24" foregroundColor="#ffffff" transparent="1" />
            <widget source="h2_temp" render="Label" position="740,350" size="200,28" font="Regular;22" foregroundColor="#cccccc" transparent="1" />
            <widget source="h2_cond" render="Label" position="740,378" size="200,22" font="Regular;18" foregroundColor="#888888" transparent="1" />

            <widget name="h3_icon" position="964,322" size="72,72" alphatest="blend" scale="1" />
            <widget source="h3_time" render="Label" position="1050,320" size="200,28" font="Regular;24" foregroundColor="#ffffff" transparent="1" />
            <widget source="h3_temp" render="Label" position="1050,350" size="200,28" font="Regular;22" foregroundColor="#cccccc" transparent="1" />
            <widget source="h3_cond" render="Label" position="1050,378" size="200,22" font="Regular;18" foregroundColor="#888888" transparent="1" />

            <widget source="days_head" render="Label" position="20,434" size="1240,26" font="Regular;22" foregroundColor="#888888" transparent="1" />

            <widget source="d0_day" render="Label" position="20,462" size="250,28" font="Regular;22" halign="center" foregroundColor="#ffffff" transparent="1" />
            <widget name="d0_icon" position="97,494" size="96,96" alphatest="blend" scale="1" />
            <widget source="d0_temp" render="Label" position="20,596" size="250,28" font="Regular;22" halign="center" foregroundColor="#ffffff" transparent="1" />
            <widget source="d0_precip" render="Label" position="20,622" size="250,22" font="Regular;18" halign="center" foregroundColor="#888888" transparent="1" />

            <widget source="d1_day" render="Label" position="270,462" size="250,28" font="Regular;22" halign="center" foregroundColor="#ffffff" transparent="1" />
            <widget name="d1_icon" position="347,494" size="96,96" alphatest="blend" scale="1" />
            <widget source="d1_temp" render="Label" position="270,596" size="250,28" font="Regular;22" halign="center" foregroundColor="#ffffff" transparent="1" />
            <widget source="d1_precip" render="Label" position="270,622" size="250,22" font="Regular;18" halign="center" foregroundColor="#888888" transparent="1" />

            <widget source="d2_day" render="Label" position="520,462" size="250,28" font="Regular;22" halign="center" foregroundColor="#ffffff" transparent="1" />
            <widget name="d2_icon" position="597,494" size="96,96" alphatest="blend" scale="1" />
            <widget source="d2_temp" render="Label" position="520,596" size="250,28" font="Regular;22" halign="center" foregroundColor="#ffffff" transparent="1" />
            <widget source="d2_precip" render="Label" position="520,622" size="250,22" font="Regular;18" halign="center" foregroundColor="#888888" transparent="1" />

            <widget source="d3_day" render="Label" position="770,462" size="250,28" font="Regular;22" halign="center" foregroundColor="#ffffff" transparent="1" />
            <widget name="d3_icon" position="847,494" size="96,96" alphatest="blend" scale="1" />
            <widget source="d3_temp" render="Label" position="770,596" size="250,28" font="Regular;22" halign="center" foregroundColor="#ffffff" transparent="1" />
            <widget source="d3_precip" render="Label" position="770,622" size="250,22" font="Regular;18" halign="center" foregroundColor="#888888" transparent="1" />

            <widget source="d4_day" render="Label" position="1020,462" size="240,28" font="Regular;22" halign="center" foregroundColor="#ffffff" transparent="1" />
            <widget name="d4_icon" position="1092,494" size="96,96" alphatest="blend" scale="1" />
            <widget source="d4_temp" render="Label" position="1020,596" size="240,28" font="Regular;22" halign="center" foregroundColor="#ffffff" transparent="1" />
            <widget source="d4_precip" render="Label" position="1020,622" size="240,22" font="Regular;18" halign="center" foregroundColor="#888888" transparent="1" />

            <ePixmap pixmap="skin_default/buttons/red.png" position="20,648" size="295,28" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="325,648" size="295,28" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="630,648" size="295,28" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/blue.png" position="935,648" size="325,28" alphatest="on" />
            <widget source="key_red" render="Label" position="20,648" size="295,28" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget source="key_green" render="Label" position="325,648" size="295,28" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget source="key_yellow" render="Label" position="630,648" size="295,28" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget source="key_blue" render="Label" position="935,648" size="325,28" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget source="support" render="Label" position="20,678" size="1240,20" font="Regular;16" foregroundColor="#666666" transparent="1" />
        </screen>
    """

    def __init__(self, session, app_adapter):
        Screen.__init__(self, session)
        self.app = app_adapter.app

        self["title"] = StaticText(_("Weather"))
        self["city"] = StaticText("")
        self["status"] = StaticText("")
        self["current_temp"] = StaticText("")
        self["current_cond"] = StaticText("")
        self["stat_feels"] = StaticText("")
        self["stat_humidity"] = StaticText("")
        self["stat_wind"] = StaticText("")
        self["stat_precip"] = StaticText("")
        self["hours_head"] = StaticText(_("Next 4 hours"))
        self["days_head"] = StaticText(_("Daily forecast"))

        self["current_icon"] = Pixmap()
        for i in range(HOUR_COUNT):
            self["h%d_icon" % i] = Pixmap()
            self["h%d_time" % i] = StaticText("")
            self["h%d_temp" % i] = StaticText("")
            self["h%d_cond" % i] = StaticText("")
        for i in range(DAY_COUNT):
            self["d%d_icon" % i] = Pixmap()
            self["d%d_day" % i] = StaticText("")
            self["d%d_temp" % i] = StaticText("")
            self["d%d_precip" % i] = StaticText("")

        self["key_red"] = StaticText(_("Close"))
        self["key_green"] = StaticText(_("Refresh"))
        self["key_yellow"] = StaticText(_("Settings"))
        self["key_blue"] = StaticText(_("Information"))
        self["support"] = StaticText("Buy me a coffee: https://buymeacoffee.com/madoe21")

        self["actions"] = ActionMap(
            ["ColorActions", "OkCancelActions"],
            {
                "cancel": self.close,
                "red": self.close,
                "ok": self._trigger_refresh,
                "green": self._trigger_refresh,
                "yellow": self._open_settings,
                "blue": self._open_info,
            },
            -1,
        )

        self._worker = None
        self._worker_result = None
        self._worker_error = None
        self._poll_timer = _make_timer(self._poll_worker)
        self._bootstrap_timer = _make_timer(self._bootstrap)

        self.onShow.append(self._on_show)
        self._bootstrapped = False

    def _on_show(self):
        if self._bootstrapped:
            return
        self._bootstrapped = True
        if self._bootstrap_timer is not None:
            self._bootstrap_timer.start(150, True)
        else:
            self._bootstrap()

    def _bootstrap(self):
        try:
            city = self.app.first_city()
        except Exception as exc:
            _log("first_city failed: %s" % exc)
            city = None

        if city is None:
            self["city"].setText("")
            self["status"].setText(_("No city configured"))
            return

        self._trigger_refresh()

    def _trigger_refresh(self):
        try:
            city = self.app.first_city()
        except Exception as exc:
            _log("first_city failed: %s" % exc)
            self["status"].setText(_("Could not load weather data"))
            return

        if city is None:
            self["status"].setText(_("No city configured"))
            return

        if self._worker is not None and self._worker.is_alive():
            return

        self["status"].setText(_("Loading..."))
        self._worker_result = None
        self._worker_error = None

        worker = threading.Thread(target=self._run_worker, args=(city,))
        worker.daemon = True
        self._worker = worker
        try:
            worker.start()
        except Exception as exc:
            _log("thread start failed: %s" % exc)
            self["status"].setText(_("Could not load weather data"))
            return

        if self._poll_timer is not None:
            self._poll_timer.start(200, True)
        else:
            worker.join(timeout=15)
            self._poll_worker()

    def _run_worker(self, city):
        try:
            self._worker_result = self.app.service.build_city_weather(city)
        except Exception as exc:
            _log("build_city_weather failed: %s" % exc)
            self._worker_error = str(exc) or "error"

    def _poll_worker(self):
        worker = self._worker
        if worker is not None and worker.is_alive():
            if self._poll_timer is not None:
                self._poll_timer.start(200, True)
            return

        self._worker = None

        if self._worker_error is not None or self._worker_result is None:
            self["status"].setText(_("Could not load weather data"))
            return

        try:
            self._render(self._worker_result)
            self["status"].setText("")
        except Exception as exc:
            _log("render failed: %s" % exc)
            self["status"].setText(_("Could not load weather data"))

    def _render(self, view):
        self["city"].setText(view.get("city", "") or "")
        self["current_temp"].setText(view.get("temperature", "-") or "-")
        self["current_cond"].setText(_(view.get("condition", "Unknown")))

        self["stat_feels"].setText(u"%s: %s" % (_("Feels like"), view.get("feels_like", "-") or "-"))
        self["stat_humidity"].setText(u"%s: %s" % (_("Humidity"), view.get("humidity", "-") or "-"))
        self["stat_wind"].setText(u"%s: %s" % (_("Wind"), view.get("wind", "-") or "-"))
        self["stat_precip"].setText(u"%s: %s" % (_("Precipitation"), view.get("precipitation", "-") or "-"))

        self._apply_icon("current_icon", view.get("condition_icon", "unknown"))

        hours = view.get("hours", []) or []
        for idx in range(HOUR_COUNT):
            if idx < len(hours):
                row = hours[idx]
                self["h%d_time" % idx].setText(row.get("time", "--:--") or "--:--")
                self["h%d_temp" % idx].setText(row.get("temp", "-") or "-")
                self["h%d_cond" % idx].setText(_(row.get("condition", "Unknown")))
                self._apply_icon("h%d_icon" % idx, row.get("icon", "unknown"))
            else:
                self["h%d_time" % idx].setText("")
                self["h%d_temp" % idx].setText("")
                self["h%d_cond" % idx].setText("")
                self._apply_icon("h%d_icon" % idx, "unknown")

        days = view.get("days", []) or []
        for idx in range(DAY_COUNT):
            if idx < len(days):
                row = days[idx]
                day_label = row.get("day", "") or ""
                if day_label == "Today":
                    day_label = _("Today")
                else:
                    day_label = _(day_label)
                self["d%d_day" % idx].setText(day_label)
                self["d%d_temp" % idx].setText(
                    u"%s / %s" % (row.get("temp_min", "-") or "-", row.get("temp_max", "-") or "-")
                )
                prob = row.get("precip_prob", "-") or "-"
                psum = row.get("precip_sum", "-") or "-"
                if prob == "-" and psum == "-":
                    precip_text = ""
                elif prob == "-":
                    precip_text = psum
                else:
                    precip_text = u"%s \u00b7 %s" % (prob, psum)
                self["d%d_precip" % idx].setText(precip_text)
                self._apply_icon("d%d_icon" % idx, row.get("icon", "unknown"))
            else:
                self["d%d_day" % idx].setText("")
                self["d%d_temp" % idx].setText("")
                self["d%d_precip" % idx].setText("")
                self._apply_icon("d%d_icon" % idx, "unknown")

    def _apply_icon(self, widget_key, icon_name):
        if widget_key not in self:
            return
        res_dir = os.path.join(os.path.dirname(__file__), "res", "weather")
        path = os.path.join(res_dir, "%s.png" % (icon_name or "unknown"))
        if not os.path.exists(path):
            path = os.path.join(res_dir, "unknown.png")
        if os.path.exists(path):
            _set_pixmap_file(self[widget_key], path)

    def _open_settings(self):
        try:
            self.session.openWithCallback(
                self._on_settings_closed, WeatherCitiesScreen, self.app
            )
        except Exception as exc:
            _log("open settings failed: %s" % exc)

    def _on_settings_closed(self, *args):
        self._trigger_refresh()

    def _open_info(self):
        try:
            self.session.open(WeatherInfoScreen)
        except Exception as exc:
            _log("open info failed: %s" % exc)


class WeatherCitiesScreen(Screen):
    skin = """
        <screen name="WeatherCitiesScreen" position="center,center" size="900,520" title="Manage cities">
            <widget source="title" render="Label" position="20,10" size="860,36" font="Regular;30" transparent="1" />
            <widget source="hint" render="Label" position="20,50" size="860,26" font="Regular;20" foregroundColor="#aaaaaa" transparent="1" />
            <widget name="city_list" position="20,86" size="860,374" scrollbarMode="showOnDemand" />

            <ePixmap pixmap="skin_default/buttons/red.png" position="20,478" size="205,28" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="235,478" size="205,28" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="450,478" size="205,28" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/blue.png" position="665,478" size="215,28" alphatest="on" />
            <widget source="key_red" render="Label" position="20,478" size="205,28" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget source="key_green" render="Label" position="235,478" size="205,28" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget source="key_yellow" render="Label" position="450,478" size="205,28" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget source="key_blue" render="Label" position="665,478" size="215,28" font="Regular;20" halign="center" valign="center" transparent="1" />
        </screen>
    """

    def __init__(self, session, app):
        Screen.__init__(self, session)
        self.app = app
        self._rows = []
        self._worker = None
        self._worker_result = None
        self._worker_error = None
        self._poll_timer = _make_timer(self._poll_worker)

        self["title"] = StaticText(_("Manage cities"))
        self["hint"] = StaticText(_("Search city") + " / " + _("Remove city") + " / " + _("Move up") + " / " + _("Move down"))
        self["city_list"] = MenuList([])

        self["key_red"] = StaticText(_("Remove city"))
        self["key_green"] = StaticText(_("Move up"))
        self["key_yellow"] = StaticText(_("Move down"))
        self["key_blue"] = StaticText(_("Search city"))

        self["actions"] = ActionMap(
            ["ColorActions", "OkCancelActions"],
            {
                "cancel": self.close,
                "ok": self.close,
                "red": self._remove,
                "green": self._move_up,
                "yellow": self._move_down,
                "blue": self._search,
            },
            -1,
        )

        self.onShow.append(self._reload)

    def _reload(self):
        try:
            cities = self.app.list_cities()
        except Exception as exc:
            _log("list_cities failed: %s" % exc)
            cities = []

        rows = []
        for idx, city in enumerate(cities):
            prefix = "* " if idx == 0 else "  "
            rows.append((idx, "%s%d. %s" % (prefix, idx + 1, city.display_name())))
        self._rows = rows

        if rows:
            self["city_list"].setList([row[1] for row in rows])
        else:
            self["city_list"].setList([_("No city configured")])

    def _selected_index(self):
        if not self._rows:
            return None
        try:
            pos = int(self["city_list"].getSelectionIndex())
        except Exception:
            pos = 0
        if pos < 0 or pos >= len(self._rows):
            return None
        return self._rows[pos][0]

    def _remove(self):
        idx = self._selected_index()
        if idx is None:
            return
        try:
            self.app.remove_city(idx)
        except Exception as exc:
            _log("remove_city failed: %s" % exc)
        self._reload()

    def _move_up(self):
        idx = self._selected_index()
        if idx is None:
            return
        try:
            if self.app.move_city_up(idx):
                self._reload()
        except Exception as exc:
            _log("move_up failed: %s" % exc)

    def _move_down(self):
        idx = self._selected_index()
        if idx is None:
            return
        try:
            if self.app.move_city_down(idx):
                self._reload()
        except Exception as exc:
            _log("move_down failed: %s" % exc)

    def _search(self):
        if VirtualKeyBoard is None:
            self.session.open(MessageBox, _("Enter city name"), MessageBox.TYPE_INFO, timeout=4)
            return
        try:
            self.session.openWithCallback(
                self._on_query_entered,
                VirtualKeyBoard,
                title=_("Enter city name"),
                text="",
            )
        except Exception as exc:
            _log("keyboard open failed: %s" % exc)

    def _on_query_entered(self, text=None):
        query = (text or "").strip()
        if not query:
            return

        self._worker_result = None
        self._worker_error = None

        worker = threading.Thread(target=self._run_search, args=(query,))
        worker.daemon = True
        self._worker = worker
        try:
            worker.start()
        except Exception as exc:
            _log("search thread start failed: %s" % exc)
            self.session.open(MessageBox, _("No city matches found"), MessageBox.TYPE_ERROR, timeout=4)
            return

        if self._poll_timer is not None:
            self._poll_timer.start(200, True)
        else:
            worker.join(timeout=15)
            self._poll_worker()

    def _run_search(self, query):
        try:
            self._worker_result = self.app.service.search_city_candidates(query)
        except Exception as exc:
            _log("search_city_candidates failed: %s" % exc)
            self._worker_error = str(exc) or "error"

    def _poll_worker(self):
        worker = self._worker
        if worker is not None and worker.is_alive():
            if self._poll_timer is not None:
                self._poll_timer.start(200, True)
            return

        self._worker = None

        if self._worker_error is not None:
            self.session.open(MessageBox, _("No city matches found"), MessageBox.TYPE_ERROR, timeout=4)
            return

        candidates = self._worker_result or []
        if not candidates:
            self.session.open(MessageBox, _("No city matches found"), MessageBox.TYPE_INFO, timeout=4)
            return

        choice_rows = []
        for item in candidates:
            label = item.get("label") if isinstance(item, dict) else None
            choice_rows.append((label or "?", item))

        try:
            self.session.openWithCallback(
                self._on_city_chosen, ChoiceBox, title=_("Add city"), list=choice_rows
            )
        except Exception as exc:
            _log("choicebox open failed: %s" % exc)

    def _on_city_chosen(self, choice=None):
        if not choice:
            return
        try:
            self.app.add_city_from_candidate(choice[1])
        except Exception as exc:
            _log("add_city_from_candidate failed: %s" % exc)
        self._reload()


class WeatherInfoScreen(Screen):
    skin = """
        <screen name="WeatherInfoScreen" position="center,90" size="1000,620" title="Weather Info">
            <widget source="title" render="Label" position="20,10" size="960,35" font="Regular;30" />
            <widget name="body" position="20,55" size="690,500" font="Regular;24" scrollbarMode="showOnDemand" />
            <widget name="qr" position="740,100" size="240,240" alphatest="blend" />
            <widget source="support" render="Label" position="20,560" size="960,24" font="Regular;20" foregroundColor="#666666" />
            <ePixmap pixmap="skin_default/buttons/red.png" position="20,585" size="220,30" alphatest="on" />
            <widget source="key_red" render="Label" position="20,585" size="220,30" font="Regular;22" halign="center" valign="center" transparent="1" />
        </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self["title"] = StaticText(_("Information"))
        self["key_red"] = StaticText(_("Close"))
        self["support"] = StaticText("Buy me a coffee: https://buymeacoffee.com/madoe21")
        self["body"] = ScrollLabel(self._info_text())
        self["qr"] = Pixmap()
        self.onLayoutFinish.append(self._load_qr)

        self["actions"] = ActionMap(
            ["OkCancelActions", "DirectionActions", "ColorActions"],
            {
                "cancel": self.close,
                "ok": self.close,
                "red": self.close,
                "up": self["body"].pageUp,
                "down": self["body"].pageDown,
                "left": self["body"].pageUp,
                "right": self["body"].pageDown,
            },
            -1,
        )

    def _info_text(self):
        lines = [
            "Weather Plugin",
            "",
            _("Data source") + ": Open-Meteo API",
            "https://open-meteo.com",
            "",
            _("Controls") + ":",
            u"  OK / Gr\u00fcn  \u2192 " + _("Refresh"),
            u"  Rot        \u2192 " + _("Close"),
            u"  Gelb       \u2192 " + _("Settings"),
            u"  Blau       \u2192 " + _("Information"),
            "",
            "Buy me a coffee: https://buymeacoffee.com/madoe21",
            "GitHub: https://github.com/madoe21/enigma2-weather",
        ]
        return "\n".join(lines)

    def _load_qr(self):
        for path in [
            resolveFilename(SCOPE_PLUGINS, "Extensions/Weather/res/qr_buymeacoffee.png"),
            os.path.join(os.path.dirname(__file__), "res", "qr_buymeacoffee.png"),
        ]:
            if os.path.exists(path):
                try:
                    self["qr"].instance.setPixmapFromFile(path)
                    return
                except Exception:
                    pass
