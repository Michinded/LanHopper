import flet as ft

from app.views.home import HomeView


def main(page: ft.Page):
    page.title = "LanHopper"
    page.window.width = 900
    page.window.height = 650
    page.window.resizable = False
    HomeView(page)


ft.run(main, assets_dir="assets")
