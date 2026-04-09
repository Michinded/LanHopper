from datetime import datetime, timezone
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
            spacing=20,
        )
        self._running = server.is_running()
        self._build()

    # ---------------------------------------------------- lifecycle

    def did_mount(self):
        server.set_qr_callback(self._on_qr_rotated)
        # If server is already running when we navigate here, load the current QR
        if self._running and server.session.get("qr_token"):
            self._update_qr(server.session["qr_token"], server.session["qr_expires_at"])

    def will_unmount(self):
        server.set_qr_callback(None)

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

        self._qr_image = ft.Image(
            "",
            width=180,
            height=180,
            fit=ft.BoxFit.CONTAIN,
            visible=False,
        )

        self._qr_expires_label = ft.Text(
            "",
            size=12,
            color=ft.Colors.GREY_500,
            italic=True,
            visible=False,
        )

        self._regen_btn = ft.OutlinedButton(
            content=i18n.t("regenerate_qr"),
            icon=ft.Icons.REFRESH,
            on_click=self._on_regenerate,
            visible=False,
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
            self._qr_image,
            self._qr_expires_label,
            self._regen_btn,
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

    def _on_regenerate(self, _):
        server.regenerate_qr()

    def _on_qr_rotated(self, token: str, expires_at: datetime):
        """Called from the background thread — must use page.run_task for UI updates."""
        if self.page:
            self.page.run_task(self._update_qr_async, token, expires_at)

    async def _update_qr_async(self, token: str, expires_at: datetime):
        self._update_qr(token, expires_at)

    def _update_qr(self, token: str, expires_at: datetime):
        b64 = server.build_qr_base64(token)
        self._qr_image.src_base64 = b64
        self._qr_image.visible = True

        local_exp = expires_at.astimezone()
        self._qr_expires_label.value = i18n.t("qr_expires_at").format(
            time=local_exp.strftime("%d/%m/%Y %H:%M:%S")
        )
        self._qr_expires_label.visible = True
        self._regen_btn.visible = True
        self.update()

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

        if not running:
            self._qr_image.visible = False
            self._qr_expires_label.visible = False
            self._regen_btn.visible = False

        self.update()

    async def _copy_url(self, _):
        url = server.get_url()
        if url:
            await Clipboard().set(url)
            self.page.show_dialog(ft.SnackBar(
                content=ft.Text("URL copied to clipboard"),
                bgcolor=ft.Colors.GREEN_700,
            ))
