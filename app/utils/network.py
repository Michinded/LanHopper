import socket
from dataclasses import dataclass


@dataclass
class PortStatus:
    available: bool
    pid: int | None = None
    process_name: str | None = None


def check_port(port: int) -> PortStatus:
    """Return availability status of a TCP port, including the owning process if busy."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("0.0.0.0", port))
            return PortStatus(available=True)
        except OSError:
            pass

    try:
        import psutil
        for conn in psutil.net_connections(kind="inet"):
            if conn.laddr.port == port and conn.pid:
                try:
                    name = psutil.Process(conn.pid).name()
                except psutil.NoSuchProcess:
                    name = None
                return PortStatus(available=False, pid=conn.pid, process_name=name)
    except Exception:
        pass

    return PortStatus(available=False)


def kill_process(pid: int) -> None:
    """Terminate a process by PID. Raises PermissionError or ProcessLookupError."""
    import psutil
    psutil.Process(pid).terminate()
