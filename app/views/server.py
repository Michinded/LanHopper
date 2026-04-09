import flet as ft
from flet.controls.services.clipboard import Clipboard

import app.server as server
from app import config, i18n


class ServerView(ft.Column):
    def __init__(self):
        super().__init__(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=24,
        )
        self._running = server.is_running()
        self._build()

    # ----------------------------------------------------------------- build

    def _build(self):
        self._status_icon = ft.Icon(
            ft.Icons.CIRCLE,
            color=ft.Colors.GREEN_500 if self._running else ft.Colors.GREY_400,
            size=14,
        )
        self._status_label = ft.Text(
            i18n.t("server_running") if self._running else i18n.t("server_stopped"),
            size=13,
            color=ft.Colors.GREEN_700 if self._running else ft.Colors.GREY_500,
        )

        self._url_field = ft.TextField(
            label=i18n.t("server_url"),
            value=server.get_url() or "",
            read_only=True,
            width=320,
            visible=self._running,
            suffix=ft.IconButton(
                icon=ft.Icons.COPY_OUTLINED,
                tooltip="Copy",
                on_click=self._copy_url,
            ),
        )

        self._password_field = ft.TextField(
            label=i18n.t("session_password"),
            value=server.session.get("password") or "",
            read_only=True,
            width=320,
            password=True,
            can_reveal_password=True,
            visible=self._running,
        )

        self._toggle_btn = ft.FilledButton(
            content=i18n.t("stop_server") if self._running else i18n.t("start_server"),
            icon=ft.Icons.STOP_CIRCLE_OUTLINED if self._running else ft.Icons.PLAY_CIRCLE_OUTLINED,
            on_click=self._toggle_server,
        )

        self.controls = [
            ft.Row(
                controls=[self._status_icon, self._status_label],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            self._toggle_btn,
            self._url_field,
            self._password_field,
            # QR placeholder — implemented in a future iteration
            ft.Container(
                content=ft.Icon(ft.Icons.QR_CODE, size=80, color=ft.Colors.GREY_300),
                visible=self._running,
                tooltip="QR code — coming soon",
            ),
        ]

    # ------------------------------------------------------------ interactions

    def _toggle_server(self, _):
        if server.is_running():
            server.stop()
            self._refresh(running=False)
        else:
            cfg = config.load()
            port = cfg.get("port", 8080)
            try:
                server.start(port)
                self._refresh(running=True)
            except Exception as e:
                self.page.show_dialog(ft.SnackBar(
                    content=ft.Text(i18n.t("server_start_error").format(error=str(e))),
                    bgcolor=ft.Colors.RED_700,
                ))

    def _refresh(self, running: bool):
        self._running = running

        self._status_icon.color = ft.Colors.GREEN_500 if running else ft.Colors.GREY_400
        self._status_label.value = i18n.t("server_running") if running else i18n.t("server_stopped")
        self._status_label.color = ft.Colors.GREEN_700 if running else ft.Colors.GREY_500

        self._url_field.value = server.get_url() or ""
        self._url_field.visible = running

        self._password_field.value = server.session.get("password") or ""
        self._password_field.visible = running

        self._toggle_btn.content = i18n.t("stop_server") if running else i18n.t("start_server")
        self._toggle_btn.icon = ft.Icons.STOP_CIRCLE_OUTLINED if running else ft.Icons.PLAY_CIRCLE_OUTLINED

        self.controls[-1].visible = running  # QR placeholder
        self.update()

    async def _copy_url(self, _):
        url = server.get_url()
        if url:
            await Clipboard().set(url)
            self.page.show_dialog(ft.SnackBar(
                content=ft.Text("URL copied to clipboard"),
                bgcolor=ft.Colors.GREEN_700,
            ))
