import flet as ft

from app import config
from app.views.home import HomeView

_THEME_MAP = {
    "dark":   ft.ThemeMode.DARK,
    "light":  ft.ThemeMode.LIGHT,
    "system": ft.ThemeMode.SYSTEM,
}


def main(page: ft.Page):
    page.title = "LanHopper"
    page.window.width = 900
    page.window.height = 650
    page.window.resizable = False

    saved_theme = config.load().get("theme", "dark")
    page.theme_mode = _THEME_MAP.get(saved_theme, ft.ThemeMode.DARK)

    HomeView(page)


ft.run(main, assets_dir="assets")
