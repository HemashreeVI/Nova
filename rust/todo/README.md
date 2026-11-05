# ferrodo

A fast, friendly todo manager for the terminal, written in Rust.
Open it full-screen and tick things off with the keyboard, or use one-off commands in scripts.

```
 ferrodo   5 open · 0 done · 1 overdue
╭──────────────────────────────────────────────────╮
│  ○ !  Pay electricity bill  ◷ overdue 4d         │
│  ○ !  Call mom  ◷ today                          │
│▌ ○ !! Finish Rust project  ◷ tomorrow            │
│  ○ !  Read a book                                │
│  ○    Buy gifts  ◷ Dec 24                        │
╰──────────────────────────────────────────────────╯
 a add   space done   e edit   t due date   d delete   q quit
```

## Features

- **Full-screen app** built with [ratatui](https://ratatui.rs), driven entirely by the keyboard.
- **Due dates you can type naturally:** `today`, `tomorrow`, `fri`, `3d`, `2w`, `1m`, `dec 24`, `2026-12-24`.
- **Smart order:** overdue and due-today tasks rise to the top, then by priority and nearest date.
- **Priorities:** high (`!!`), medium (`!`) and low.
- **Saved instantly** to a JSON file, written safely so a crash never corrupts it.
- **Scriptable commands** for everything the app can do.

## Install

You need [Rust](https://rustup.rs).

```bash
cargo install --git https://github.com/HemashreeVI/ferrodo
```

Or from a clone:

```bash
cargo build --release
```

The program is then at `target/release/ferrodo`.

## Full-screen app

Run `ferrodo` with no arguments (or `ferrodo ui`).

| Key | Action |
| --- | --- |
| `↑` `↓` / `j` `k` | Move (`g` / `G` jump to top / bottom) |
| `a` | Add a task |
| `space` / `enter` / `x` | Mark done / not done |
| `e` | Edit the selected task |
| `t` | Set the due date (leave empty to clear it) |
| `d` | Delete (confirm with `y`) |
| `+` / `-` | Raise / lower priority |
| `h` | Hide or show finished tasks |
| `c` | Delete all finished tasks |
| `q` / `esc` | Quit |

## Commands

```bash
ferrodo add Buy milk
ferrodo add -p high -d fri Finish the report
ferrodo ls          # open tasks
ferrodo ls -a       # include finished tasks
ferrodo done 1 3
ferrodo undo 1
ferrodo edit 2 Finish the quarterly report
ferrodo due 2 tomorrow
ferrodo due 2 none  # clear the due date
ferrodo rm 2
ferrodo clear       # delete all finished tasks
```

When the output is not a terminal (a pipe or a script), plain `ferrodo` prints the list instead of opening the app.

## Where tasks are stored

In `~/.ferrodo.json`. Set `FERRODO_FILE` or pass `--file <path>` to use another file.

## License

MIT
