import asyncio
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import flet as ft

import app.server as server
from app import config, i18n, meta
from app.views.about import AboutView
from app.views.server import ServerView, _fmt_uptime
from app.views.settings import SettingsView

_QUOTE_EXECUTOR = ThreadPoolExecutor(max_workers=1)


def _fetch_quote_sync() -> dict | None:
    try:
        req = urllib.request.Request(
            "https://programming-quotesapi.vercel.app/api/random",
            headers={"User-Agent": "LanHopper/1.0"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


class HomeView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.cfg = config.load()
        i18n.load(self.cfg.get("language", "en"))

        self._current_index = 0
        self._content = ft.Column(expand=True)

        self._build()
        self._navigate(0)

    # ------------------------------------------------------------------ layout

    def _build(self):
        self.page.padding = 0

        rail = ft.NavigationRail(
            selected_index=self._current_index,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=80,
            group_alignment=-1.0,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label=i18n.t("home"),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.WIFI_OUTLINED,
                    selected_icon=ft.Icons.WIFI,
                    label=i18n.t("server"),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label=i18n.t("settings"),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.INFO_OUTLINED,
                    selected_icon=ft.Icons.INFO,
                    label=i18n.t("about"),
                ),
            ],
            on_change=lambda e: self._navigate(e.control.selected_index),
        )

        self.page.add(
            ft.Row(
                controls=[
                    rail,
                    ft.VerticalDivider(width=1),
                    self._content,
                ],
                expand=True,
                spacing=0,
            )
        )

    # --------------------------------------------------------------- navigation

    def _navigate(self, index: int):
        self._current_index = index
        self._content.controls.clear()

        if index == 0:
            self._content.controls.append(_HomeScreen())
        elif index == 1:
            self._content.controls.append(ServerView())
        elif index == 2:
            self._content.controls.append(SettingsView())
        elif index == 3:
            self._content.controls.append(AboutView())

        self.page.update()


# ---------------------------------------------------------------- Home screen

class _HomeScreen(ft.Column):
    def __init__(self):
        super().__init__(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )
        self._running = False

        # ── app identity ──────────────────────────────────────────────
        welcome_line = ft.Text(
            f'{i18n.t("welcome_greeting")} {meta.APP_NAME}',
            size=14, color=ft.Colors.GREY_500,
        )
        app_title_row = ft.Row(
            controls=[
                ft.Text(
                    meta.APP_NAME,
                    size=34,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(
                    content=ft.Text(
                        f"v{meta.APP_VERSION}",
                        size=11,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.WHITE,
                    ),
                    bgcolor=ft.Colors.BLUE_700,
                    border_radius=20,
                    padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        app_subtitle = ft.Text(
            i18n.t("app_subtitle"),
            size=13,
            color=ft.Colors.GREY_500,
            italic=True,
        )

        # ── clock ─────────────────────────────────────────────────────
        self._greeting_label = ft.Text(
            "", size=14, color=ft.Colors.GREY_500,
        )
        self._time_label = ft.Text(
            "", size=52, weight=ft.FontWeight.BOLD, font_family="monospace",
        )
        self._date_label = ft.Text(
            "", size=13, color=ft.Colors.GREY_500,
        )

        # ── server status (plain text, no pill) ───────────────────────
        running = server.is_running()
        self._status_dot = ft.Container(
            width=7, height=7,
            bgcolor=ft.Colors.GREEN_500 if running else ft.Colors.GREY_400,
            border_radius=4,
        )
        self._status_label = ft.Text(
            i18n.t("server_running") if running else i18n.t("server_stopped"),
            size=13,
            color=ft.Colors.GREEN_700 if running else ft.Colors.GREY_500,
        )
        self._status_row = ft.Row(
            controls=[self._status_dot, self._status_label],
            spacing=7,
            tight=True,
        )
        self._uptime_label = ft.Text(
            "", size=11, color=ft.Colors.GREY_400, italic=True, visible=False,
        )
        self._start_hint = ft.Text(
            i18n.t("server_start_hint"),
            size=11, color=ft.Colors.GREY_400, italic=True,
            visible=not running,
        )

        # ── quote card ────────────────────────────────────────────────
        self._quote_text = ft.Text(
            "", size=13, color=ft.Colors.GREY_600, italic=True,
            text_align=ft.TextAlign.CENTER,
        )
        self._quote_author = ft.Text(
            "", size=12, color=ft.Colors.GREY_400, weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER,
        )
        self._quote_card = ft.Container(
            content=ft.Column(
                controls=[self._quote_text, self._quote_author],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.GREY_100,
            border_radius=12,
            padding=ft.Padding(left=28, right=28, top=16, bottom=16),
            width=460,
            visible=False,
        )

        self.controls = [
            welcome_line,
            ft.Container(height=4),
            app_title_row,
            app_subtitle,
            ft.Container(height=32),
            self._greeting_label,
            ft.Container(height=2),
            self._time_label,
            self._date_label,
            ft.Container(height=28),
            self._status_row,
            self._uptime_label,
            self._start_hint,
            ft.Container(height=28),
            self._quote_card,
        ]

    def did_mount(self):
        self._running = True
        self.page.run_task(self._clock_loop)
        self.page.run_task(self._load_quote)

    def will_unmount(self):
        self._running = False

    async def _clock_loop(self):
        while self._running:
            now = datetime.now()
            h = now.hour

            if 5 <= h < 12:
                greeting = i18n.t("greeting_morning")
            elif 12 <= h < 19:
                greeting = i18n.t("greeting_afternoon")
            elif 19 <= h < 24:
                greeting = i18n.t("greeting_evening")
            else:
                greeting = i18n.t("greeting_dawn")

            self._greeting_label.value = greeting
            self._time_label.value = now.strftime("%H:%M:%S")
            self._date_label.value = now.strftime("%A, %b %d · %Y")

            running = server.is_running()
            self._status_dot.bgcolor = ft.Colors.GREEN_500 if running else ft.Colors.GREY_400
            self._status_label.value = i18n.t("server_running") if running else i18n.t("server_stopped")
            self._status_label.color = ft.Colors.GREEN_700 if running else ft.Colors.GREY_500

            if running:
                start = server.session.get("start_time")
                if start:
                    elapsed = int((datetime.now(timezone.utc) - start).total_seconds())
                    self._uptime_label.value = f"{i18n.t('uptime')}: {_fmt_uptime(elapsed)}"
                    self._uptime_label.visible = True
                self._start_hint.visible = False
            else:
                self._uptime_label.visible = False
                self._start_hint.visible = True

            if self.page:
                self.page.update()
            await asyncio.sleep(1)

    async def _load_quote(self):
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(_QUOTE_EXECUTOR, _fetch_quote_sync)
        if data and self._running and self.page:
            self._quote_text.value = f'"{data.get("quote", "")}"'
            self._quote_author.value = f'— {data.get("author", "")}'
            self._quote_card.visible = True
            self.page.update()
