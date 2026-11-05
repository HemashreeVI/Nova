# todo

A small, fast todo manager for the terminal, written in Rust.

## Build

```bash
cargo build --release
```

The binary is at `target/release/todo`.

## Full-screen app

Run `todo` with no arguments (or `todo ui`) to open the full-screen app.

| Key | Action |
| --- | --- |
| `↑` `↓` / `j` `k` | Move (`g` / `G` jump to top / bottom) |
| `a` | Add a task |
| `space` / `enter` / `x` | Mark done / not done |
| `e` | Edit the selected task |
| `d` | Delete (asks to confirm with `y`) |
| `+` / `-` | Raise / lower priority |
| `h` | Hide or show finished tasks |
| `c` | Delete all finished tasks |
| `q` / `esc` | Quit |

Every change is saved immediately.

## Commands

The same list can be managed with one-off commands, which is handy in scripts:

```bash
todo add Buy milk
todo add -p high Finish the report
todo ls         # list open tasks
todo ls -a      # include finished tasks
todo done 1 3
todo undo 1
todo edit 2 Finish the quarterly report
todo rm 2
todo clear      # delete all finished tasks
```

Tasks are sorted by priority (`high`, `medium`, `low`). They are saved to `~/.todo.json`;
set `TODO_FILE` or pass `--file <path>` to use another file.
