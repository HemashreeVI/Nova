//! Due dates: reading what people type ("fri", "3d", "dec 24") and showing
//! dates relative to today ("tomorrow", "overdue 2d").

use chrono::{Datelike, Days, Local, Months, NaiveDate, Weekday};

pub const HELP: &str = "today, tomorrow, fri, 3d, 2w, 1m, dec 24, 2026-12-24 (empty clears)";

pub fn today() -> NaiveDate {
    Local::now().date_naive()
}

/// Parses a due date relative to `today`. `Ok(None)` means "no due date".
pub fn parse(input: &str, today: NaiveDate) -> Result<Option<NaiveDate>, String> {
    let s = input.trim().to_lowercase();
    let s = s.strip_prefix("in ").unwrap_or(&s).trim();
    let err = || format!("Can't read \"{}\" as a date. Try: {HELP}", input.trim());

    let date = match s {
        "" | "none" | "clear" | "-" => return Ok(None),
        "today" | "tod" | "now" => today,
        "tomorrow" | "tmr" | "tom" => today + Days::new(1),
        "yesterday" => today - Days::new(1),
        "next week" => today + Days::new(7),
        _ => {
            if let Ok(day) = s.parse::<Weekday>() {
                // The next one after today (so "fri" on a Friday means next Friday).
                let ahead =
                    (day.num_days_from_monday() + 7 - today.weekday().num_days_from_monday()) % 7;
                today + Days::new(if ahead == 0 { 7 } else { ahead as u64 })
            } else if let Some(d) = relative(s, today) {
                d
            } else if let Ok(d) = NaiveDate::parse_from_str(s, "%Y-%m-%d") {
                d
            } else if let Some(d) = month_day(s, today) {
                d
            } else {
                return Err(err());
            }
        }
    };
    Ok(Some(date))
}

/// "3d", "+3d", "3 days", "2w", "1m".
fn relative(s: &str, today: NaiveDate) -> Option<NaiveDate> {
    let s = s.strip_prefix('+').unwrap_or(s);
    let split = s.find(|c: char| !c.is_ascii_digit())?;
    let n: u32 = s[..split].parse().ok()?;
    match s[split..].trim() {
        "d" | "day" | "days" => today.checked_add_days(Days::new(n.into())),
        "w" | "wk" | "week" | "weeks" => today.checked_add_days(Days::new(u64::from(n) * 7)),
        "m" | "mo" | "month" | "months" => today.checked_add_months(Months::new(n)),
        _ => None,
    }
}

/// "dec 24", "24 dec", "december 24": the next time that day comes round.
fn month_day(s: &str, today: NaiveDate) -> Option<NaiveDate> {
    // chrono reads "dec" but not "december", so shorten month words.
    let s: Vec<String> = s
        .split_whitespace()
        .map(|w| {
            w.chars()
                .take(if w.chars().all(char::is_alphabetic) {
                    3
                } else {
                    w.len()
                })
                .collect()
        })
        .collect();
    let s = s.join(" ");
    for year in [today.year(), today.year() + 1] {
        for fmt in ["%b %d %Y", "%d %b %Y"] {
            if let Ok(d) = NaiveDate::parse_from_str(&format!("{s} {year}"), fmt)
                && d >= today
            {
                return Some(d);
            }
        }
    }
    None
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Urgency {
    Overdue,
    Today,
    Soon,
    Later,
}

/// A short label such as "today", "Fri", "Dec 24" or "overdue 2d".
pub fn label(due: NaiveDate, today: NaiveDate) -> (String, Urgency) {
    let days = (due - today).num_days();
    match days {
        ..=-2 => (format!("overdue {}d", -days), Urgency::Overdue),
        -1 => ("yesterday".into(), Urgency::Overdue),
        0 => ("today".into(), Urgency::Today),
        1 => ("tomorrow".into(), Urgency::Soon),
        2..=6 => (due.format("%a").to_string(), Urgency::Soon),
        _ if due.year() == today.year() => (due.format("%b %-d").to_string(), Urgency::Later),
        _ => (due.format("%b %-d %Y").to_string(), Urgency::Later),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    // A Thursday.
    fn day() -> NaiveDate {
        NaiveDate::from_ymd_opt(2026, 11, 5).unwrap()
    }

    fn p(s: &str) -> NaiveDate {
        parse(s, day()).unwrap().unwrap()
    }

    #[test]
    fn parses_words_and_offsets() {
        assert_eq!(p("today"), day());
        assert_eq!(p("Tomorrow"), NaiveDate::from_ymd_opt(2026, 11, 6).unwrap());
        assert_eq!(p("fri"), NaiveDate::from_ymd_opt(2026, 11, 6).unwrap());
        assert_eq!(
            p("thursday"),
            NaiveDate::from_ymd_opt(2026, 11, 12).unwrap()
        );
        assert_eq!(p("3d"), NaiveDate::from_ymd_opt(2026, 11, 8).unwrap());
        assert_eq!(
            p("in 2 weeks"),
            NaiveDate::from_ymd_opt(2026, 11, 19).unwrap()
        );
        assert_eq!(p("1m"), NaiveDate::from_ymd_opt(2026, 12, 5).unwrap());
        assert_eq!(
            p("2027-01-02"),
            NaiveDate::from_ymd_opt(2027, 1, 2).unwrap()
        );
    }

    #[test]
    fn month_names_roll_to_next_year() {
        assert_eq!(p("dec 24"), NaiveDate::from_ymd_opt(2026, 12, 24).unwrap());
        assert_eq!(p("3 march"), NaiveDate::from_ymd_opt(2027, 3, 3).unwrap());
    }

    #[test]
    fn empty_clears_and_junk_errors() {
        assert_eq!(parse("", day()), Ok(None));
        assert_eq!(parse("none", day()), Ok(None));
        assert!(parse("someday", day()).is_err());
    }

    #[test]
    fn labels() {
        let l = |d: &str| label(p(d), day());
        assert_eq!(l("today"), ("today".into(), Urgency::Today));
        assert_eq!(l("tomorrow"), ("tomorrow".into(), Urgency::Soon));
        assert_eq!(l("mon"), ("Mon".into(), Urgency::Soon));
        assert_eq!(l("dec 24"), ("Dec 24".into(), Urgency::Later));
        assert_eq!(l("2027-01-02"), ("Jan 2 2027".into(), Urgency::Later));
        assert_eq!(l("2026-11-01"), ("overdue 4d".into(), Urgency::Overdue));
    }
}
