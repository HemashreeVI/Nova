"""Nova as a desktop app: a Nova icon on the desktop and in the Start Menu, and only one Nova at a time.

Double-clicking the icon starts Nova. If Nova is already running, it brings him back on screen instead
of starting a second copy.
"""
import os
import platform
import socket
import subprocess
import sys
import threading
from pathlib import Path

from nova.config import ROOT

ICON = ROOT / "assets" / "nova.ico"
PORT = 47613                       # local-only "bring Nova back" doorbell
MARKER = ROOT / "data" / ".shortcut_made"


# one Nova at a time
_on_show = None


def ring_running_nova() -> bool:
    """If a Nova is already running, ask it to show itself and return True.
    Only counts if Nova itself answers, so another program on the same port can't block him."""
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=1) as s:
            s.sendall(b"show\n")
            s.settimeout(3)
            return s.recv(8).startswith(b"nova")
    except OSError:
        return False


def claim_single_instance() -> bool:
    """Call first thing, before anything slow. True: this is the one running Nova.
    False: another Nova answered and was asked to show itself, so this launch should quit."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        srv.bind(("127.0.0.1", PORT))
    except OSError:
        srv.close()
        return not ring_running_nova()  # port taken by something that isn't Nova: start anyway
    srv.listen(4)

    def loop():
        while True:
            try:
                conn, _ = srv.accept()
                with conn:
                    conn.settimeout(1)
                    if conn.recv(16).startswith(b"show"):
                        conn.sendall(b"nova\n")
                        if _on_show:  # still starting up? He'll appear by himself in a moment.
                            _on_show()
            except Exception as e:
                print("[nova] doorbell:", e)

    threading.Thread(target=loop, daemon=True, name="doorbell").start()
    return True


def on_show(fn):
    """What to do when Nova's icon is double-clicked while he's running."""
    global _on_show
    _on_show = fn


# app icon
def make_icon() -> Path:
    if not ICON.exists():
        from nova.tray import _icon_image
        ICON.parent.mkdir(parents=True, exist_ok=True)
        _icon_image(256).save(ICON, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    return ICON


def _gui_python() -> Path:
    """pythonw.exe runs Nova without a black console window."""
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    return pythonw if pythonw.exists() else Path(sys.executable)


def _ps_quote(value) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def set_shortcuts(enabled: bool) -> str:
    """Add (or remove) the Nova icon on the desktop and in the Start Menu."""
    if platform.system() != "Windows":
        return "Desktop shortcuts are only set up for Windows right now."
    if enabled:
        icon = make_icon()
        body = (
            f"$t = {_ps_quote(_gui_python())}; $a = {_ps_quote(chr(34) + str(ROOT / 'main.py') + chr(34))}; "
            f"$w = {_ps_quote(ROOT)}; $i = {_ps_quote(icon)}; "
            "$sh = New-Object -ComObject WScript.Shell; "
            "foreach ($d in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) { "
            "  $l = $sh.CreateShortcut((Join-Path $d 'Nova.lnk')); $l.TargetPath = $t; $l.Arguments = $a; "
            "  $l.WorkingDirectory = $w; $l.IconLocation = $i; $l.Description = 'Nova, your desktop robot'; $l.Save() }"
        )
    else:
        body = ("foreach ($d in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) { "
                "  Remove-Item -ErrorAction SilentlyContinue (Join-Path $d 'Nova.lnk') }")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", body],
                           capture_output=True, text=True, timeout=30,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except Exception as e:
        return f"Couldn't update the Nova shortcuts ({e})."
    if r.returncode != 0:
        detail = (r.stderr or r.stdout or "").strip().splitlines()
        return f"Couldn't update the Nova shortcuts: {detail[0] if detail else 'PowerShell error ' + str(r.returncode)}"
    if not enabled:
        MARKER.unlink(missing_ok=True)
        return "Removed the Nova icon from your desktop and Start Menu."
    return "Nova is now on your desktop and in the Start Menu. Double-click him anytime!"


def ensure_shortcuts_once():
    """The first time Nova runs on Windows, put his icon on the desktop. Never again after that,
    so deleting the icon sticks."""
    if platform.system() != "Windows" or MARKER.exists():
        return
    msg = set_shortcuts(True)
    print("[nova]", msg)
    if msg.startswith("Couldn't"):
        return  # try again next time
    try:
        MARKER.parent.mkdir(parents=True, exist_ok=True)
        MARKER.write_text("1", encoding="utf-8")
    except OSError:
        pass
