use chrono::NaiveDate;
use clap::ValueEnum;
use serde::{Deserialize, Serialize};
use std::fs;
use std::io;
use std::path::Path;
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Copy, Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, ValueEnum)]
#[serde(rename_all = "lowercase")]
pub enum Priority {
    High,
    Medium,
    Low,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Task {
    pub id: u32,
    pub text: String,
    pub done: bool,
    pub priority: Priority,
    pub created: u64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub due: Option<NaiveDate>,
}

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct Store {
    pub next_id: u32,
    pub tasks: Vec<Task>,
}

impl Store {
    pub fn load(path: &Path) -> io::Result<Store> {
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

    pub fn save(&self, path: &Path) -> io::Result<()> {
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

    pub fn add(&mut self, text: String, priority: Priority) -> u32 {
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
            due: None,
        });
        id
    }

    pub fn get_mut(&mut self, id: u32) -> Option<&mut Task> {
        self.tasks.iter_mut().find(|t| t.id == id)
    }

    /// Returns the ids that did not exist.
    pub fn set_done(&mut self, ids: &[u32], done: bool) -> Vec<u32> {
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
    pub fn remove(&mut self, ids: &[u32]) -> Vec<u32> {
        let missing: Vec<u32> = ids
            .iter()
            .copied()
            .filter(|id| !self.tasks.iter().any(|t| t.id == *id))
            .collect();
        self.tasks.retain(|t| !ids.contains(&t.id));
        missing
    }

    pub fn clear_done(&mut self) -> usize {
        let before = self.tasks.len();
        self.tasks.retain(|t| !t.done);
        before - self.tasks.len()
    }

    /// Moves a priority one step: `up` goes Low -> Medium -> High.
    pub fn bump_priority(&mut self, id: u32, up: bool) {
        if let Some(t) = self.get_mut(id) {
            t.priority = match (t.priority, up) {
                (Priority::Low, true) | (Priority::High, false) => Priority::Medium,
                (Priority::Medium, true) | (Priority::High, true) => Priority::High,
                (Priority::Medium, false) | (Priority::Low, false) => Priority::Low,
            };
        }
    }

    pub fn sorted(&self, all: bool) -> Vec<&Task> {
        self.sorted_on(all, crate::due::today())
    }

    /// Open tasks first; among them, anything due today or overdue comes first,
    /// then by priority, then the nearest due date, then oldest.
    pub fn sorted_on(&self, all: bool, today: NaiveDate) -> Vec<&Task> {
        let mut v: Vec<&Task> = self.tasks.iter().filter(|t| all || !t.done).collect();
        v.sort_by_key(|t| {
            let pressing = t.due.is_some_and(|d| d <= today);
            (t.done, !pressing, t.priority, t.due.is_none(), t.due, t.id)
        });
        v
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

        // A low-priority task due today jumps above a high-priority one.
        let today = NaiveDate::from_ymd_opt(2026, 11, 5).unwrap();
        let urgent = s.add("urgent".into(), Priority::Low);
        s.add("big".into(), Priority::High);
        s.get_mut(urgent).unwrap().due = Some(today);
        assert_eq!(s.sorted_on(false, today)[0].id, urgent);
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
