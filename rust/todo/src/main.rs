use clap::{Parser, Subcommand, ValueEnum};
use serde::{Deserialize, Serialize};
use std::fs;
use std::io;
use std::path::PathBuf;
use std::process::ExitCode;
use std::time::{SystemTime, UNIX_EPOCH};

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
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, ValueEnum)]
#[serde(rename_all = "lowercase")]
enum Priority {
    High,
    Medium,
    Low,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
struct Task {
    id: u32,
    text: String,
    done: bool,
    priority: Priority,
    created: u64,
}

#[derive(Debug, Default, Serialize, Deserialize)]
struct Store {
    next_id: u32,
    tasks: Vec<Task>,
}

impl Store {
    fn load(path: &PathBuf) -> io::Result<Store> {
        match fs::read_to_string(path) {
            Ok(s) if s.trim().is_empty() => Ok(Store::default()),
            Ok(s) => serde_json::from_str(&s).map_err(|e| {
                io::Error::new(
                    io::ErrorKind::InvalidData,
                    format!("{}: {e}", path.display()),
                )
            }),
            Err(e) if e.kind() == io::ErrorKind::NotFound => Ok(Store::default()),
            Err(e) => Err(e),
        }
    }

    fn save(&self, path: &PathBuf) -> io::Result<()> {
        if let Some(dir) = path.parent()
            && !dir.as_os_str().is_empty()
        {
            fs::create_dir_all(dir)?;
        }
        // Write to a temp file then rename so a crash never corrupts the list.
        let tmp = path.with_extension("json.tmp");
        fs::write(&tmp, serde_json::to_string_pretty(self)?)?;
        fs::rename(tmp, path)
    }

    fn add(&mut self, text: String, priority: Priority) -> u32 {
        self.next_id = self
            .next_id
            .max(self.tasks.iter().map(|t| t.id).max().unwrap_or(0))
            + 1;
        let id = self.next_id;
        let created = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_secs())
            .unwrap_or(0);
        self.tasks.push(Task {
            id,
            text,
            done: false,
            priority,
            created,
        });
        id
    }

    fn get_mut(&mut self, id: u32) -> Option<&mut Task> {
        self.tasks.iter_mut().find(|t| t.id == id)
    }

    /// Returns the ids that did not exist.
    fn set_done(&mut self, ids: &[u32], done: bool) -> Vec<u32> {
        ids.iter()
            .copied()
            .filter(|&id| match self.get_mut(id) {
                Some(t) => {
                    t.done = done;
                    false
                }
                None => true,
            })
            .collect()
    }

    /// Returns the ids that did not exist.
    fn remove(&mut self, ids: &[u32]) -> Vec<u32> {
        let missing: Vec<u32> = ids
            .iter()
            .copied()
            .filter(|id| !self.tasks.iter().any(|t| t.id == *id))
            .collect();
        self.tasks.retain(|t| !ids.contains(&t.id));
        missing
    }

    fn clear_done(&mut self) -> usize {
        let before = self.tasks.len();
        self.tasks.retain(|t| !t.done);
        before - self.tasks.len()
    }

    fn sorted(&self, all: bool) -> Vec<&Task> {
        let mut v: Vec<&Task> = self.tasks.iter().filter(|t| all || !t.done).collect();
        v.sort_by_key(|t| (t.done, t.priority, t.id));
        v
    }
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
    let command = cli.command.unwrap_or(Command::List { all: false });

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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn add_assigns_increasing_ids() {
        let mut s = Store::default();
        assert_eq!(s.add("a".into(), Priority::Low), 1);
        assert_eq!(s.add("b".into(), Priority::Low), 2);
        s.remove(&[2]);
        // ids are never reused, even after deletion
        assert_eq!(s.add("c".into(), Priority::Low), 3);
    }

    #[test]
    fn done_undo_and_missing_ids() {
        let mut s = Store::default();
        let id = s.add("a".into(), Priority::Medium);
        assert_eq!(s.set_done(&[id, 99], true), vec![99]);
        assert!(s.tasks[0].done);
        assert!(s.set_done(&[id], false).is_empty());
        assert!(!s.tasks[0].done);
    }

    #[test]
    fn sorting_and_clear() {
        let mut s = Store::default();
        let low = s.add("low".into(), Priority::Low);
        let high = s.add("high".into(), Priority::High);
        let med = s.add("med".into(), Priority::Medium);
        s.set_done(&[high], true);
        let ids: Vec<u32> = s.sorted(true).iter().map(|t| t.id).collect();
        assert_eq!(ids, vec![med, low, high]);
        assert_eq!(s.sorted(false).len(), 2);
        assert_eq!(s.clear_done(), 1);
        assert_eq!(s.tasks.len(), 2);
    }

    #[test]
    fn save_and_load_roundtrip() {
        let dir = std::env::temp_dir().join(format!("todo-test-{}", std::process::id()));
        let path = dir.join("todo.json");
        let mut s = Store::default();
        s.add("persist me".into(), Priority::High);
        s.save(&path).unwrap();
        let loaded = Store::load(&path).unwrap();
        assert_eq!(loaded.tasks, s.tasks);
        fs::remove_dir_all(dir).unwrap();
    }
}
