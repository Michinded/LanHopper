import flet as ft

from app import config, i18n


class HomeView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.cfg = config.load()
        i18n.load(self.cfg.get("language", "en"))
        self._build()

    def _build(self):
        self.page.controls.clear()
        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("LanHopper", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text(i18n.t("app_subtitle"), size=16),
                    ft.Divider(),
                    ft.Text(i18n.t("server_stopped"), color=ft.Colors.GREY_500),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            )
        )
        self.page.update()
