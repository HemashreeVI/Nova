"""Start Nova.

    python main.py            floating desktop robot (default)
    python main.py --terminal chat in the terminal, no window
    python main.py --no-voice skip microphone and speakers
    python main.py --2d       use the simple 2D body
    python main.py --autostart on|off   start Nova whenever you log in (Windows)
    python main.py --shortcut on|off    Nova icon on your desktop and in the Start Menu (Windows)
"""
import argparse
import os
import warnings

# quiet the speech model's download warnings (harmless on Windows)
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("HF_HUB_DISABLE_IMPLICIT_TOKEN", "1")
os.environ.setdefault("HF_HUB_VERBOSITY", "error")
warnings.filterwarnings("ignore", module="huggingface_hub")

import sys  # noqa: E402

# Started from the desktop icon (pythonw): there's no console, so keep Nova's messages in data/nova.log
if sys.stdout is None or sys.stderr is None:
    from pathlib import Path
    _log_path = Path(__file__).resolve().parent / "data" / "nova.log"
    _log_path.parent.mkdir(exist_ok=True)
    sys.stdout = sys.stderr = open(_log_path, "w", encoding="utf-8", errors="replace", buffering=1)

# Only one Nova at a time. Claim that right away, before the slow loading below, so double-clicking
# the icon again while he's still waking up doesn't start (and fight with) a second Nova.
if __name__ == "__main__" and not {"--terminal", "--shortcut", "--autostart", "-h", "--help"} & set(sys.argv):
    from nova.launcher import claim_single_instance
    if not claim_single_instance():
        print("Nova is already running, so I asked him to come back on screen.")
        sys.exit(0)

if sys.version_info >= (3, 15):
    print(f"\nYou're running Python {sys.version.split()[0]}, a preview version many of Nova's packages don't support yet.")
    print("Start Nova with Python 3.14 instead:   py -3.14 main.py   (or double-click start_nova.bat)\n")

try:
    from nova.app import NovaApp  # noqa: E402
    from nova.config import load_settings  # noqa: E402
except ModuleNotFoundError as e:
    print(f"\nNova is missing a package: {e.name}")
    print(f"This Python is: {sys.executable}")
    print("Install everything Nova needs into it with:\n")
    print(f"    py -{sys.version_info.major}.{sys.version_info.minor} -m pip install -r requirements.txt\n")
    print("(Or start Nova with a Python that already has them:   py -3.14 main.py)\n")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Nova, your personal desktop robot")
    parser.add_argument("--terminal", action="store_true", help="chat in the terminal instead of the floating robot")
    parser.add_argument("--no-voice", action="store_true", help="disable microphone and speech")
    parser.add_argument("--2d", dest="flat", action="store_true", help="use the simple 2D body instead of 3D")
    parser.add_argument("--autostart", choices=["on", "off"], help="start Nova when you log in (Windows)")
    parser.add_argument("--shortcut", choices=["on", "off"], help="Nova icon on the desktop and Start Menu (Windows)")
    args = parser.parse_args()

    if args.shortcut:
        from nova.launcher import set_shortcuts
        print(set_shortcuts(args.shortcut == "on"))
        return

    if args.autostart:
        from nova.autostart import set_autostart
        print(set_autostart(args.autostart == "on"))
        return

    settings = load_settings()
    if args.no_voice:
        settings["voice"]["enabled"] = False
    if args.flat:
        settings["buddy"]["style"] = "2d"
    print("Waking Nova up...")
    app = NovaApp(settings, gui=not args.terminal)
    app.startup_report()
    if args.terminal:
        app.run_terminal()
    else:
        import threading
        from nova.launcher import ensure_shortcuts_once, on_show
        on_show(app.bring_back)
        threading.Thread(target=ensure_shortcuts_once, daemon=True, name="shortcuts").start()
        app.run_gui()


if __name__ == "__main__":
    main()
