mod store;
mod tui;

use clap::{Parser, Subcommand};
use std::io::{self, IsTerminal};
use std::path::PathBuf;
use std::process::ExitCode;
use store::{Priority, Store};

/// A small, fast todo manager for the terminal.
#[derive(Parser)]
#[command(name = "todo", version, about)]
struct Cli {
    /// Path to the todo file (default: $TODO_FILE or ~/.todo.json)
    #[arg(long, global = true)]
    file: Option<PathBuf>,

    #[command(subcommand)]
    command: Option<Command>,
}

#[derive(Subcommand)]
enum Command {
    /// Add a new task
    Add {
        /// Task text
        #[arg(required = true, num_args = 1..)]
        text: Vec<String>,
        /// Priority of the task
        #[arg(short, long, value_enum, default_value_t = Priority::Medium)]
        priority: Priority,
    },
    /// List tasks (open ones by default)
    #[command(alias = "ls")]
    List {
        /// Include finished tasks
        #[arg(short, long)]
        all: bool,
    },
    /// Mark one or more tasks as done
    Done { ids: Vec<u32> },
    /// Mark one or more tasks as not done
    Undo { ids: Vec<u32> },
    /// Delete one or more tasks
    #[command(alias = "rm")]
    Remove { ids: Vec<u32> },
    /// Change the text of a task
    Edit {
        id: u32,
        #[arg(required = true, num_args = 1..)]
        text: Vec<String>,
    },
    /// Delete all finished tasks
    Clear,
    /// Open the full-screen app (also the default with no command)
    Ui,
}

fn default_path() -> PathBuf {
    if let Some(p) = std::env::var_os("TODO_FILE") {
        return PathBuf::from(p);
    }
    let home = std::env::var_os("HOME")
        .or_else(|| std::env::var_os("USERPROFILE"))
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."));
    home.join(".todo.json")
}

fn print_list(store: &Store, all: bool) {
    let tasks = store.sorted(all);
    if tasks.is_empty() {
        println!("Nothing to do. Add a task with: todo add <text>");
        return;
    }
    let width = tasks
        .iter()
        .map(|t| t.id.to_string().len())
        .max()
        .unwrap_or(1);
    for t in &tasks {
        let check = if t.done { "[x]" } else { "[ ]" };
        let pri = match t.priority {
            Priority::High => "!!",
            Priority::Medium => "! ",
            Priority::Low => "  ",
        };
        println!("{:>width$}  {check} {pri} {}", t.id, t.text);
    }
    let open = store.tasks.iter().filter(|t| !t.done).count();
    println!("\n{open} open, {} done", store.tasks.len() - open);
}

fn warn_missing(missing: &[u32]) -> bool {
    for id in missing {
        eprintln!("No task with id {id}");
    }
    missing.is_empty()
}

fn run(cli: Cli) -> io::Result<bool> {
    let path = cli.file.unwrap_or_else(default_path);
    let mut store = Store::load(&path)?;
    let command = match cli.command {
        Some(c) => c,
        // No subcommand in an interactive terminal: open the full-screen app.
        None if io::stdout().is_terminal() && io::stdin().is_terminal() => {
            tui::run(store, path)?;
            return Ok(true);
        }
        None => Command::List { all: false },
    };

    let ok = match command {
        Command::List { all } => {
            print_list(&store, all);
            return Ok(true);
        }
        Command::Add { text, priority } => {
            let id = store.add(text.join(" "), priority);
            println!("Added task {id}");
            true
        }
        Command::Done { ids } => warn_missing(&store.set_done(&ids, true)),
        Command::Undo { ids } => warn_missing(&store.set_done(&ids, false)),
        Command::Remove { ids } => warn_missing(&store.remove(&ids)),
        Command::Edit { id, text } => match store.get_mut(id) {
            Some(t) => {
                t.text = text.join(" ");
                true
            }
            None => warn_missing(&[id]),
        },
        Command::Ui => {
            tui::run(store, path)?;
            return Ok(true);
        }
        Command::Clear => {
            println!("Removed {} finished task(s)", store.clear_done());
            true
        }
    };
    store.save(&path)?;
    Ok(ok)
}

fn main() -> ExitCode {
    match run(Cli::parse()) {
        Ok(true) => ExitCode::SUCCESS,
        Ok(false) => ExitCode::from(1),
        Err(e) => {
            eprintln!("error: {e}");
            ExitCode::from(2)
        }
    }
}
