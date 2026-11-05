# todo

A small, fast todo manager for the terminal, written in Rust.

## Build

```bash
cargo build --release
```

The binary is at `target/release/todo`.

## Use

```bash
todo add Buy milk
todo add -p high Finish the report
todo            # list open tasks (same as `todo ls`)
todo ls -a      # include finished tasks
todo done 1 3
todo undo 1
todo edit 2 Finish the quarterly report
todo rm 2
todo clear      # delete all finished tasks
```

Tasks are sorted by priority (`high`, `medium`, `low`). They are saved to `~/.todo.json`;
set `TODO_FILE` or pass `--file <path>` to use another file.
