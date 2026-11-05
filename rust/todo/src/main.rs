mod due;
mod store;
mod tui;

use clap::{Parser, Subcommand};
use std::io::{self, IsTerminal};
use std::path::PathBuf;
use std::process::ExitCode;
use store::{Priority, Store};

/// A small, fast todo manager for the terminal.
#[derive(Parser)]
#[command(name = "ferrodo", version, about)]
struct Cli {
    /// Path to the todo file (default: $FERRODO_FILE or ~/.ferrodo.json)
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
        /// Due date: today, tomorrow, fri, 3d, 2w, dec 24, 2026-12-24
        #[arg(short, long)]
        due: Option<String>,
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
    /// Set or clear a task's due date (e.g. `todo due 3 fri`, `todo due 3 none`)
    Due {
        id: u32,
        #[arg(required = true, num_args = 1..)]
        when: Vec<String>,
    },
    /// Delete all finished tasks
    Clear,
    /// Open the full-screen app (also the default with no command)
    Ui,
}

fn default_path() -> PathBuf {
    if let Some(p) = std::env::var_os("FERRODO_FILE") {
        return PathBuf::from(p);
    }
    let home = std::env::var_os("HOME")
        .or_else(|| std::env::var_os("USERPROFILE"))
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."));
    home.join(".ferrodo.json")
}

fn print_list(store: &Store, all: bool) {
    let today = due::today();
    let tasks = store.sorted_on(all, today);
    if tasks.is_empty() {
        println!("Nothing to do. Add a task with: ferrodo add <text>");
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
        let due = t.due.map(|d| {
            let (label, urgency) = due::label(d, today);
            match urgency {
                _ if t.done => format!("  ({label})"),
                due::Urgency::Overdue | due::Urgency::Today => format!("  ({label}!)"),
                _ => format!("  ({label})"),
            }
        });
        println!(
            "{:>width$}  {check} {pri} {}{}",
            t.id,
            t.text,
            due.unwrap_or_default()
        );
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
        Command::Add {
            text,
            priority,
            due,
        } => {
            let due = match due.map(|d| due::parse(&d, due::today())).transpose() {
                Ok(d) => d.flatten(),
                Err(e) => {
                    eprintln!("{e}");
                    return Ok(false);
                }
            };
            let id = store.add(text.join(" "), priority);
            store.get_mut(id).expect("just added").due = due;
            println!("Added task {id}");
            true
        }
        Command::Due { id, when } => match due::parse(&when.join(" "), due::today()) {
            Err(e) => {
                eprintln!("{e}");
                return Ok(false);
            }
            Ok(date) => match store.get_mut(id) {
                Some(t) => {
                    t.due = date;
                    true
                }
                None => warn_missing(&[id]),
            },
        },
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
