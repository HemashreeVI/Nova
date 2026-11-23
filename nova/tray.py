"""Nova's icon in the taskbar's system tray (needs: pip install pystray).

Left-click the icon to show or hide Nova. Right-click it for everything else:
moves, mute, voice, quiet time, starting with Windows, and turning Nova off.
"""
import platform

from PIL import Image, ImageDraw, ImageFilter


def _icon_image(size: int = 64) -> Image.Image:
    """Nova's armored helmet: purple armor, dark visor, glowing eyes. Drawn big, then shrunk for smooth edges."""
    S = 256
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # helmet with a lighter top edge
    d.rounded_rectangle((28, 22, 228, 238), radius=72, fill=(30, 11, 74, 255))
    d.rounded_rectangle((36, 26, 220, 226), radius=66, fill=(76, 29, 149, 255))
    d.rounded_rectangle((52, 34, 204, 120), radius=50, fill=(124, 58, 237, 255))
    d.rounded_rectangle((44, 60, 212, 226), radius=60, fill=(76, 29, 149, 255))
    d.rounded_rectangle((116, 6, 140, 60), radius=12, fill=(42, 15, 99, 255))  # crest
    # visor
    d.rounded_rectangle((52, 90, 204, 182), radius=30, fill=(5, 6, 13, 255))
    # glowing eyes
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for x in (100, 156):
        gd.ellipse((x - 22, 112, x + 22, 162), fill=(91, 224, 255, 255))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
    for x in (100, 156):
        d.ellipse((x - 15, 118, x + 15, 156), fill=(160, 240, 255, 255))
    d.rounded_rectangle((96, 198, 160, 214), radius=8, fill=(30, 11, 74, 255))  # jaw vent
    return img.resize((size, size), Image.LANCZOS)


def start_tray(app):
    try:
        import pystray
    except ImportError:
        print("[nova] no tray icon: run  pip install pystray")
        return None

    def item(text, fn, **kw):
        return pystray.MenuItem(text, lambda icon, _item: fn(), **kw)

    def muted() -> bool:
        return bool(getattr(app, "speaker", None) and app.speaker.muted)

    def move(name):
        return lambda: (app.body_do("show"), app.body_do("perform", name))

    entries = [
        item("Show / hide Nova", app.toggle_visible, default=True),  # left-click
        item("Bring Nova back to his corner", lambda: (app.body_do("show"), app.body_do("home"))),
        item("Talk to Nova", app.listen_now),
        pystray.MenuItem("Moves", pystray.Menu(
            item("🚀 Fly", move("fly")),
            item("👋 Wave", move("wave")),
            item("👍 Thumbs up", move("thumbs")),
            item("🦸 Hero pose", move("hero")),
            item("💃 Dance", move("dance")),
            item("🌈 Cheer me up", move("cheer")),
        )),
        pystray.MenuItem("Size", pystray.Menu(
            item("➕ Bigger", lambda: app.resize(+15)),
            item("➖ Smaller", lambda: app.resize(-15)),
            item("Reset size", lambda: app.resize(reset=True)),
        )),
        pystray.Menu.SEPARATOR,
        item("Mute voice", app._toggle_mute, checked=lambda _item: muted()),
        item("Change voice", app.next_voice),
        pystray.MenuItem("Quiet time", pystray.Menu(
            item("Quiet for 1 hour", lambda: app.set_quiet(60)),
            item("Quiet until I say", lambda: app.set_quiet(24 * 60)),
            item("Wake up (end quiet)", lambda: app.set_quiet(0)),
        )),
    ]
    if platform.system() == "Windows":
        from nova.autostart import LAUNCHER, set_autostart
        from nova.launcher import set_shortcuts
        entries.append(item("Put Nova on my desktop", lambda: print("[nova]", set_shortcuts(True))))
        entries.append(item("Start Nova when I log in", lambda: print("[nova]", set_autostart(not LAUNCHER.exists())),
                            checked=lambda _item: LAUNCHER.exists()))
    entries += [pystray.Menu.SEPARATOR, item("Turn off Nova", app.shutdown)]

    icon = pystray.Icon("Nova", _icon_image(), "Nova: click to show or hide", pystray.Menu(*entries))
    icon.run_detached()
    return icon
