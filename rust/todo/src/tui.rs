//! Full-screen terminal interface built with ratatui.

use crate::store::{Priority, Store, Task};
use ratatui::crossterm::event::{self, Event, KeyCode, KeyEvent, KeyEventKind, KeyModifiers};
use ratatui::layout::{Constraint, Layout, Rect};
use ratatui::style::{Color, Modifier, Style, Stylize};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, BorderType, Clear, List, ListItem, ListState, Paragraph};
use ratatui::{DefaultTerminal, Frame};
use std::io;
use std::path::PathBuf;

const ACCENT: Color = Color::Cyan;

/// Runs the app until the user quits. Restores the terminal even on error or panic.
pub fn run(store: Store, path: PathBuf) -> io::Result<()> {
    let mut terminal = ratatui::init();
    let result = App::new(store, path).run(&mut terminal);
    ratatui::restore();
    result
}

#[derive(Debug, PartialEq)]
enum Mode {
    Normal,
    /// Typing a new task, or editing the task with this id.
    Input {
        editing: Option<u32>,
        text: String,
        cursor: usize,
    },
    ConfirmDelete(u32),
}

pub struct App {
    store: Store,
    path: PathBuf,
    selected: usize,
    hide_done: bool,
    mode: Mode,
    status: Option<String>,
    quit: bool,
}

impl App {
    pub fn new(store: Store, path: PathBuf) -> App {
        App {
            store,
            path,
            selected: 0,
            hide_done: false,
            mode: Mode::Normal,
            status: None,
            quit: false,
        }
    }

    fn run(&mut self, terminal: &mut DefaultTerminal) -> io::Result<()> {
        while !self.quit {
            terminal.draw(|f| self.draw(f))?;
            if let Event::Key(key) = event::read()?
                && key.kind == KeyEventKind::Press
            {
                self.on_key(key);
            }
        }
        Ok(())
    }

    fn visible(&self) -> Vec<&Task> {
        self.store.sorted(!self.hide_done)
    }

    fn selected_id(&self) -> Option<u32> {
        self.visible().get(self.selected).map(|t| t.id)
    }

    fn select_id(&mut self, id: u32) {
        if let Some(i) = self.visible().iter().position(|t| t.id == id) {
            self.selected = i;
        }
    }

    fn clamp_selection(&mut self) {
        self.selected = self.selected.min(self.visible().len().saturating_sub(1));
    }

    fn save(&mut self) {
        self.clamp_selection();
        if let Err(e) = self.store.save(&self.path) {
            self.status = Some(format!("Could not save: {e}"));
        }
    }

    pub fn on_key(&mut self, key: KeyEvent) {
        if key.modifiers.contains(KeyModifiers::CONTROL) && key.code == KeyCode::Char('c') {
            self.quit = true;
            return;
        }
        self.status = None;
        match &mut self.mode {
            Mode::Normal => self.on_normal_key(key.code),
            Mode::ConfirmDelete(id) => {
                let id = *id;
                if matches!(
                    key.code,
                    KeyCode::Char('y') | KeyCode::Char('d') | KeyCode::Enter
                ) {
                    self.store.remove(&[id]);
                    self.save();
                    self.status = Some("Task deleted".into());
                }
                self.mode = Mode::Normal;
            }
            Mode::Input {
                editing,
                text,
                cursor,
            } => {
                let byte = |s: &str, c: usize| s.char_indices().nth(c).map_or(s.len(), |(i, _)| i);
                match key.code {
                    KeyCode::Esc => self.mode = Mode::Normal,
                    KeyCode::Enter => {
                        let value = text.trim().to_string();
                        let editing = *editing;
                        self.mode = Mode::Normal;
                        if value.is_empty() {
                            return;
                        }
                        let id = match editing {
                            Some(id) => {
                                if let Some(t) = self.store.get_mut(id) {
                                    t.text = value;
                                }
                                id
                            }
                            None => self.store.add(value, Priority::Medium),
                        };
                        self.save();
                        self.select_id(id);
                    }
                    KeyCode::Char(c) => {
                        text.insert(byte(text, *cursor), c);
                        *cursor += 1;
                    }
                    KeyCode::Backspace if *cursor > 0 => {
                        *cursor -= 1;
                        text.remove(byte(text, *cursor));
                    }
                    KeyCode::Delete if *cursor < text.chars().count() => {
                        text.remove(byte(text, *cursor));
                    }
                    KeyCode::Left => *cursor = cursor.saturating_sub(1),
                    KeyCode::Right => *cursor = (*cursor + 1).min(text.chars().count()),
                    KeyCode::Home => *cursor = 0,
                    KeyCode::End => *cursor = text.chars().count(),
                    _ => {}
                }
            }
        }
    }

    fn on_normal_key(&mut self, code: KeyCode) {
        let len = self.visible().len();
        let id = self.selected_id();
        match code {
            KeyCode::Char('q') | KeyCode::Esc => self.quit = true,
            KeyCode::Down | KeyCode::Char('j') => {
                self.selected = (self.selected + 1).min(len.saturating_sub(1))
            }
            KeyCode::Up | KeyCode::Char('k') => self.selected = self.selected.saturating_sub(1),
            KeyCode::Home | KeyCode::Char('g') => self.selected = 0,
            KeyCode::End | KeyCode::Char('G') => self.selected = len.saturating_sub(1),
            KeyCode::Char('a') | KeyCode::Char('n') => {
                self.mode = Mode::Input {
                    editing: None,
                    text: String::new(),
                    cursor: 0,
                };
            }
            KeyCode::Char('e') | KeyCode::Char('i') => {
                if let Some(t) = id.and_then(|id| self.store.get_mut(id)) {
                    let text = t.text.clone();
                    let cursor = text.chars().count();
                    self.mode = Mode::Input {
                        editing: Some(t.id),
                        text,
                        cursor,
                    };
                }
            }
            // Toggling keeps the cursor on the same row, so you can tick off tasks one after another.
            KeyCode::Char(' ') | KeyCode::Enter | KeyCode::Char('x') => {
                if let Some(t) = id.and_then(|id| self.store.get_mut(id)) {
                    t.done = !t.done;
                    self.save();
                }
            }
            KeyCode::Char('d') | KeyCode::Delete => {
                if let Some(id) = id {
                    self.mode = Mode::ConfirmDelete(id);
                }
            }
            KeyCode::Char('+') | KeyCode::Char('=') | KeyCode::Char('-') => {
                if let Some(id) = id {
                    self.store.bump_priority(id, code != KeyCode::Char('-'));
                    self.save();
                    self.select_id(id);
                }
            }
            KeyCode::Char('h') => {
                self.hide_done = !self.hide_done;
                self.clamp_selection();
                if let Some(id) = id {
                    self.select_id(id);
                }
            }
            KeyCode::Char('c') => {
                let n = self.store.clear_done();
                self.save();
                self.status = Some(format!("Removed {n} finished task(s)"));
            }
            _ => {}
        }
    }

    pub fn draw(&self, frame: &mut Frame) {
        let [header, body, footer] = Layout::vertical([
            Constraint::Length(1),
            Constraint::Min(1),
            Constraint::Length(1),
        ])
        .areas(frame.area());

        let open = self.store.tasks.iter().filter(|t| !t.done).count();
        let done = self.store.tasks.len() - open;
        let filter = if self.hide_done {
            "  (finished hidden)"
        } else {
            ""
        };
        frame.render_widget(
            Line::from(vec![
                " todo ".bold().fg(Color::Black).bg(ACCENT),
                format!("  {open} open · {done} done{filter}").dark_gray(),
            ]),
            header,
        );

        self.draw_list(frame, body);
        self.draw_footer(frame, footer);

        if let Mode::Input {
            editing,
            text,
            cursor,
        } = &self.mode
        {
            let title = if editing.is_some() {
                " Edit task "
            } else {
                " New task "
            };
            draw_input(frame, title, text, *cursor);
        }
    }

    fn draw_list(&self, frame: &mut Frame, area: Rect) {
        let block = Block::bordered()
            .border_type(BorderType::Rounded)
            .border_style(Style::new().dark_gray());
        let tasks = self.visible();
        if tasks.is_empty() {
            let msg = if self.store.tasks.is_empty() {
                "Nothing to do yet. Press  a  to add your first task."
            } else {
                "All done! Press  h  to show finished tasks."
            };
            let inner = block.inner(area);
            frame.render_widget(block, area);
            let [_, mid, _] = Layout::vertical([
                Constraint::Fill(1),
                Constraint::Length(1),
                Constraint::Fill(1),
            ])
            .areas(inner);
            frame.render_widget(Paragraph::new(msg).dark_gray().centered(), mid);
            return;
        }

        let items: Vec<ListItem> = tasks.iter().map(|t| task_item(t)).collect();
        let list = List::new(items)
            .block(block)
            .highlight_style(
                Style::new()
                    .bg(Color::DarkGray)
                    .add_modifier(Modifier::BOLD),
            )
            .highlight_symbol("▌ ");
        let mut state = ListState::default().with_selected(Some(self.selected));
        frame.render_stateful_widget(list, area, &mut state);
    }

    fn draw_footer(&self, frame: &mut Frame, area: Rect) {
        let line = if let Some(msg) = &self.status {
            Line::from(format!(" {msg}")).fg(ACCENT)
        } else {
            let keys: &[(&str, &str)] = match &self.mode {
                Mode::Normal => &[
                    ("a", "add"),
                    ("space", "done"),
                    ("e", "edit"),
                    ("d", "delete"),
                    ("q", "quit"),
                    ("+/-", "priority"),
                    ("h", "hide done"),
                    ("c", "clear done"),
                ],
                Mode::Input { .. } => &[("enter", "save"), ("esc", "cancel")],
                Mode::ConfirmDelete(_) => &[("y", "delete"), ("any key", "cancel")],
            };
            let mut spans = vec![Span::raw(" ")];
            if matches!(self.mode, Mode::ConfirmDelete(_)) {
                spans.push("Delete this task? ".red().bold());
            }
            for (k, label) in keys {
                spans.push(k.bold().fg(ACCENT));
                spans.push(format!(" {label}   ").dark_gray());
            }
            Line::from(spans)
        };
        frame.render_widget(line, area);
    }
}

fn task_item(t: &Task) -> ListItem<'static> {
    let (mark, mark_style) = match t.priority {
        Priority::High => ("!! ", Style::new().red().bold()),
        Priority::Medium => ("!  ", Style::new().yellow()),
        Priority::Low => ("   ", Style::new()),
    };
    let (check, text_style) = if t.done {
        ("✔ ", Style::new().green().add_modifier(Modifier::DIM))
    } else {
        ("○ ", Style::new())
    };
    let text = if t.done {
        Span::styled(t.text.clone(), Style::new().dark_gray().crossed_out())
    } else {
        Span::styled(t.text.clone(), text_style)
    };
    ListItem::new(Line::from(vec![
        Span::styled(
            check,
            if t.done {
                text_style
            } else {
                Style::new().dark_gray()
            },
        ),
        Span::styled(mark, mark_style),
        text,
    ]))
}

fn draw_input(frame: &mut Frame, title: &str, text: &str, cursor: usize) {
    let area = frame.area();
    let width = area.width.saturating_sub(4).min(70);
    let [row] = Layout::vertical([Constraint::Length(3)])
        .flex(ratatui::layout::Flex::Center)
        .areas(area);
    let [popup] = Layout::horizontal([Constraint::Length(width)])
        .flex(ratatui::layout::Flex::Center)
        .areas(row);

    let block = Block::bordered()
        .border_type(BorderType::Rounded)
        .border_style(Style::new().fg(ACCENT))
        .title(title.bold());
    let inner = block.inner(popup);

    // Scroll horizontally so the cursor always stays visible.
    let room = (inner.width as usize).saturating_sub(1);
    let skip = cursor.saturating_sub(room);
    let shown: String = text.chars().skip(skip).take(inner.width as usize).collect();

    frame.render_widget(Clear, popup);
    frame.render_widget(Paragraph::new(shown).block(block), popup);
    frame.set_cursor_position((inner.x + (cursor - skip) as u16, inner.y));
}

#[cfg(test)]
mod tests {
    use super::*;
    use ratatui::Terminal;
    use ratatui::backend::TestBackend;

    fn app() -> (App, PathBuf) {
        let dir = std::env::temp_dir().join(format!(
            "todo-tui-{}-{:?}",
            std::process::id(),
            std::thread::current().id()
        ));
        let path = dir.join("todo.json");
        let mut store = Store::default();
        store.add("first".into(), Priority::Medium);
        store.add("second".into(), Priority::Low);
        (App::new(store, path), dir)
    }

    fn press(app: &mut App, keys: &str) {
        for c in keys.chars() {
            let code = match c {
                '\n' => KeyCode::Enter,
                '\x08' => KeyCode::Backspace,
                c => KeyCode::Char(c),
            };
            app.on_key(KeyEvent::new(code, KeyModifiers::NONE));
        }
    }

    #[test]
    fn add_edit_toggle_delete() {
        let (mut app, dir) = app();
        press(&mut app, "aMilkx\x08\n");
        assert_eq!(app.store.tasks[2].text, "Milk");
        assert_eq!(app.selected_id(), Some(3));

        press(&mut app, "e!\n");
        assert_eq!(app.store.tasks[2].text, "Milk!");

        press(&mut app, "g ");
        assert!(app.store.get_mut(1).unwrap().done);

        press(&mut app, "gdn");
        assert_eq!(app.store.tasks.len(), 3, "any other key cancels delete");
        press(&mut app, "dy");
        assert_eq!(app.store.tasks.len(), 2);

        // Changes were written to disk.
        assert_eq!(Store::load(&app.path).unwrap().tasks.len(), 2);
        std::fs::remove_dir_all(dir).unwrap();
    }

    #[test]
    fn priority_hide_and_clear() {
        let (mut app, dir) = app();
        press(&mut app, "j++");
        assert_eq!(app.store.get_mut(2).unwrap().priority, Priority::High);
        assert_eq!(app.selected_id(), Some(2), "selection follows the task");

        press(&mut app, " h");
        assert_eq!(app.visible().len(), 1);
        press(&mut app, "hc");
        assert_eq!(app.store.tasks.len(), 1);
        std::fs::remove_dir_all(dir).unwrap();
    }

    #[test]
    fn renders_tasks_and_popup() {
        let (mut app, _) = app();
        let mut term = Terminal::new(TestBackend::new(60, 10)).unwrap();
        term.draw(|f| app.draw(f)).unwrap();
        let screen = format!("{:?}", term.backend().buffer());
        assert!(screen.contains("first") && screen.contains("2 open"));

        press(&mut app, "a");
        term.draw(|f| app.draw(f)).unwrap();
        assert!(format!("{:?}", term.backend().buffer()).contains("New task"));
    }
}
