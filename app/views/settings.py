import threading
import flet as ft

import app.server as server
from app import config, i18n
from app.utils.network import check_port, kill_process
from app.utils.paths import normalize_path, pick_folder


class SettingsView(ft.Column):
    def __init__(self):
        super().__init__(expand=True, scroll=ft.ScrollMode.AUTO)
        self._cfg = config.load()

        raw_folder = self._cfg.get("shared_folder", {})
        if isinstance(raw_folder, str):
            raw_folder = {"type": "local", "path": raw_folder}
        self._folder = raw_folder

        self._build()

    # ----------------------------------------------------------------- build

    def _build(self):
        self._field_device = ft.TextField(
            label=i18n.t("device_name"),
            value=self._cfg.get("device_name", ""),
            expand=True,
        )

        self._field_port = ft.TextField(
            label=i18n.t("port"),
            hint_text=i18n.t("port_hint"),
            value=str(self._cfg.get("port", 8080)),
            width=140,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self._folder_type_dropdown = ft.Dropdown(
            label=i18n.t("folder_type"),
            value=self._folder.get("type", "local"),
            width=180,
            options=[
                ft.dropdown.Option(key="local", text=i18n.t("folder_type_local")),
                ft.dropdown.Option(key="network", text=i18n.t("folder_type_network")),
            ],
            on_select=self._on_folder_type_change,
        )

        is_local = self._folder.get("type", "local") == "local"

        self._field_path = ft.TextField(
            label=i18n.t("folder_path"),
            value=self._folder.get("path", ""),
            expand=True,
            read_only=is_local,
            hint_text="" if is_local else i18n.t("folder_path_hint_network"),
        )

        self._btn_browse = ft.IconButton(
            icon=ft.Icons.FOLDER_OPEN_OUTLINED,
            tooltip=i18n.t("browse"),
            on_click=self._on_browse,
            visible=is_local,
        )

        self._btn_validate_path = ft.IconButton(
            icon=ft.Icons.WIFI_FIND_OUTLINED,
            tooltip=i18n.t("validate_path"),
            on_click=self._on_validate_path,
        )

        self._lang_dropdown = ft.Dropdown(
            label=i18n.t("language"),
            value=self._cfg.get("language", "en"),
            width=180,
            options=[
                ft.dropdown.Option(key="en", text="English"),
                ft.dropdown.Option(key="es", text="Español"),
            ],
        )

        self._port_dialog = ft.AlertDialog(modal=True, title=ft.Text(" "))

        self.controls = [
            ft.Container(
                content=ft.Column(
                    spacing=28,
                    controls=[
                        _section_title(i18n.t("device_name")),
                        self._field_device,

                        _section_title(i18n.t("port")),
                        ft.Row(
                            controls=[
                                self._field_port,
                                ft.IconButton(
                                    icon=ft.Icons.SEARCH,
                                    tooltip=i18n.t("check_port"),
                                    on_click=self._on_check_port,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),

                        _section_title(i18n.t("shared_folder")),
                        self._folder_type_dropdown,
                        ft.Row(
                            controls=[self._field_path, self._btn_browse, self._btn_validate_path],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),

                        _section_title(i18n.t("language")),
                        self._lang_dropdown,
                        ft.Text(
                            i18n.t("language_restart_hint"),
                            size=12,
                            color=ft.Colors.AMBER_700,
                            italic=True,
                        ),

                        ft.Container(height=8),
                        ft.Text(
                            i18n.t("settings_server_running_hint"),
                            size=12,
                            color=ft.Colors.RED_400,
                            italic=True,
                            visible=server.is_running(),
                        ),
                        ft.FilledButton(
                            content=i18n.t("save"),
                            icon=ft.Icons.SAVE_OUTLINED,
                            on_click=self._save,
                            disabled=server.is_running(),
                        ),
                    ],
                ),
                padding=ft.Padding(left=32, right=32, top=28, bottom=32),
            ),
        ]

    # ---------------------------------------------------- lifecycle

    def did_mount(self):
        self.page.overlay.append(self._port_dialog)

    def will_unmount(self):
        self.page.overlay.remove(self._port_dialog)

    # ------------------------------------------------------------ interactions

    def _on_folder_type_change(self, e):
        is_local = e.control.value == "local"
        self._field_path.read_only = is_local
        self._field_path.hint_text = "" if is_local else i18n.t("folder_path_hint_network")
        self._btn_browse.visible = is_local
        self._field_path.value = self._folder.get("path", "") if is_local else ""
        self.update()

    def _on_browse(self, _):
        def run():
            path = pick_folder()
            if path:
                self._field_path.value = path
                self._field_path.update()
        threading.Thread(target=run, daemon=True).start()

    def _on_validate_path(self, _):
        from pathlib import Path
        raw = self._field_path.value.strip()
        if not raw:
            self._show_snack(i18n.t("invalid_path"), error=True)
            return
        try:
            accessible = Path(raw).expanduser().exists()
        except Exception:
            accessible = False

        if accessible:
            self._show_snack(i18n.t("path_ok"))
        else:
            self._show_snack(i18n.t("path_not_found"), error=True)

    def _on_check_port(self, _):
        port_str = self._field_port.value.strip()
        try:
            port = int(port_str)
            assert 1024 <= port <= 65535
        except (ValueError, AssertionError):
            self._field_port.error_text = i18n.t("invalid_port")
            self._field_port.update()
            return

        self._field_port.error_text = None
        self._field_port.update()

        status = check_port(port)
        if status.available:
            self._show_snack(i18n.t("port_available").format(port=port))
        else:
            self._show_port_dialog(port, status.pid, status.process_name)

    def _show_port_dialog(self, port: int, pid: int | None, process_name: str | None):
        name = process_name or i18n.t("port_in_use_unknown")
        body = i18n.t("port_in_use_body").format(name=name, pid=pid) if pid else name

        def on_kill(_):
            self._port_dialog.open = False
            self.page.update()
            try:
                kill_process(pid)
                self._show_snack(i18n.t("kill_success").format(port=port))
            except PermissionError:
                self._show_snack(i18n.t("kill_error_permission"), error=True)
            except Exception:
                self._show_snack(i18n.t("kill_error_generic"), error=True)

        def on_close(_):
            self._port_dialog.open = False
            self.page.update()

        self._port_dialog.title = ft.Text(i18n.t("port_in_use_title").format(port=port))
        self._port_dialog.content = ft.Text(body)
        self._port_dialog.actions = [
            ft.TextButton(content=i18n.t("close"), on_click=on_close),
            ft.FilledButton(
                content=i18n.t("kill_process"),
                icon=ft.Icons.STOP_CIRCLE_OUTLINED,
                on_click=on_kill,
                visible=pid is not None,
            ),
        ]
        self._port_dialog.open = True
        self.page.update()

    def _show_snack(self, message: str, error: bool = False):
        self.page.show_dialog(ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_700 if error else ft.Colors.GREEN_700,
        ))

    def _save(self, _):
        if not self._validate():
            return

        self._cfg["device_name"] = self._field_device.value.strip()
        self._cfg["port"] = int(self._field_port.value.strip())
        self._cfg["shared_folder"] = {
            "type": self._folder_type_dropdown.value,
            "path": normalize_path(self._field_path.value.strip(), self._folder_type_dropdown.value),
        }
        self._cfg["language"] = self._lang_dropdown.value
        config.save(self._cfg)
        self._show_snack(i18n.t("settings_saved"))

    def _validate(self) -> bool:
        port_str = self._field_port.value.strip()
        try:
            port = int(port_str)
            assert 1024 <= port <= 65535
            self._field_port.error_text = None
        except (ValueError, AssertionError):
            self._field_port.error_text = i18n.t("invalid_port")
            self._field_port.update()
            return False

        if not self._field_path.value.strip():
            self._field_path.error_text = i18n.t("invalid_path")
            self._field_path.update()
            return False

        self._field_path.error_text = None
        return True


# ------------------------------------------------------------------- helpers

def _section_title(text: str) -> ft.Text:
    return ft.Text(text, size=13, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_700)
