import asyncio
from datetime import datetime, timezone

import flet as ft

import app.server as server
from app import config, i18n
from app.views.about import AboutView
from app.views.server import ServerView, _fmt_uptime
from app.views.settings import SettingsView


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
                    label=i18n.t("app_title"),
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
            spacing=24,
        )
        running = server.is_running()
        self._uptime_running = False

        self._status_icon = ft.Icon(
            ft.Icons.CIRCLE,
            color=ft.Colors.GREEN_500 if running else ft.Colors.GREY_400,
            size=18,
        )
        self._status_label = ft.Text(
            i18n.t("server_running") if running else i18n.t("server_stopped"),
            color=ft.Colors.GREEN_700 if running else ft.Colors.GREY_500,
            size=14,
        )
        self._uptime_label = ft.Text(
            "",
            size=12,
            color=ft.Colors.GREY_500,
            italic=True,
            visible=running,
        )

        self.controls = [
            ft.Text(
                i18n.t("app_title"),
                size=36,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                i18n.t("app_subtitle"),
                size=15,
                color=ft.Colors.GREY_600,
            ),
            ft.Container(height=8),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[self._status_icon, self._status_label],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        self._uptime_label,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                ),
                bgcolor=ft.Colors.GREY_100,
                border_radius=12,
                padding=ft.Padding(left=24, right=24, top=12, bottom=12),
            ),
        ]

    def did_mount(self):
        if server.is_running():
            self._uptime_running = True
            self.page.run_task(self._uptime_loop)

    def will_unmount(self):
        self._uptime_running = False

    async def _uptime_loop(self):
        while self._uptime_running and server.is_running():
            start = server.session.get("start_time")
            if start and self.page:
                elapsed = int((datetime.now(timezone.utc) - start).total_seconds())
                self._uptime_label.value = f"{i18n.t('uptime')}: {_fmt_uptime(elapsed)}"
                self._uptime_label.visible = True
                self._uptime_label.update()
            await asyncio.sleep(1)
