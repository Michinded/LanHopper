import flet as ft
from flet.controls.services.url_launcher import UrlLauncher

from app import i18n, meta


class AboutView(ft.Column):
    def __init__(self):
        super().__init__(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        self.controls = [
            ft.Container(
                content=ft.Column(
                    spacing=0,
                    controls=[
                        _header(),
                        _divider(),
                        _section(
                            i18n.t("about"),
                            ft.Text(i18n.t("about_description"), size=14, color=ft.Colors.GREY_600),
                        ),
                        _divider(),
                        _section(
                            i18n.t("developer"),
                            ft.Text(meta.DEVELOPER, size=14, weight=ft.FontWeight.W_500),
                        ),
                        _divider(),
                        _section(
                            i18n.t("open_source"),
                            ft.Column(
                                spacing=14,
                                controls=[
                                    ft.Text(i18n.t("open_source_desc"), size=14, color=ft.Colors.GREY_600),
                                    ft.OutlinedButton(
                                        content=i18n.t("view_on_github"),
                                        icon=ft.Icons.OPEN_IN_NEW,
                                        on_click=_open_github,
                                    ),
                                ],
                            ),
                        ),
                        _divider(),
                        _section(
                            i18n.t("privacy"),
                            ft.Text(i18n.t("privacy_desc"), size=14, color=ft.Colors.GREY_600),
                        ),
                        _divider(),
                        _section(
                            i18n.t("built_with"),
                            ft.Text(meta.TECH_STACK, size=13, color=ft.Colors.GREY_500,
                                    font_family="monospace"),
                        ),
                        _divider(),
                        _section(
                            i18n.t("license"),
                            ft.Text(meta.LICENSE, size=14, weight=ft.FontWeight.W_500),
                        ),
                        ft.Container(height=32),
                    ],
                ),
                padding=ft.Padding(left=40, right=40, top=32, bottom=0),
                expand=True,
            )
        ]


# ------------------------------------------------------------------ helpers

async def _open_github(_):
    await UrlLauncher().launch_url(meta.GITHUB_URL)


def _header() -> ft.Container:
    return ft.Container(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=10,
            controls=[
                ft.Row(
                    spacing=14,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "LanHopper",
                            size=30,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(
                            content=ft.Text(
                                f"v{meta.APP_VERSION}",
                                size=12,
                                weight=ft.FontWeight.W_600,
                                color=ft.Colors.WHITE,
                            ),
                            bgcolor=ft.Colors.BLUE_700,
                            border_radius=20,
                            padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                        ),
                    ],
                ),
                ft.Text(
                    i18n.t("app_subtitle"),
                    size=14,
                    color=ft.Colors.GREY_500,
                    italic=True,
                ),
            ],
        ),
        padding=ft.Padding(left=0, right=0, top=0, bottom=24),
    )


def _divider() -> ft.Divider:
    return ft.Divider(height=1, color=ft.Colors.GREY_200)


def _section(title: str, content: ft.Control) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text(
                    title.upper(),
                    size=11,
                    weight=ft.FontWeight.W_700,
                    color=ft.Colors.GREY_500,
                    style=ft.TextStyle(letter_spacing=1.2),
                ),
                content,
            ],
        ),
        padding=ft.Padding(left=0, right=0, top=20, bottom=20),
    )
