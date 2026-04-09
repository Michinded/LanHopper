import flet as ft

from app import i18n


class SettingsView(ft.Column):
    def __init__(self):
        super().__init__(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.controls = [
            ft.Icon(ft.Icons.SETTINGS_OUTLINED, size=48, color=ft.Colors.GREY_400),
            ft.Container(height=8),
            ft.Text(i18n.t("settings"), size=20, color=ft.Colors.GREY_500),
        ]
