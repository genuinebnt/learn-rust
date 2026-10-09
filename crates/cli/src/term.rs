//! Terminal output for the learner's commands: colour only on a terminal (and never under `NO_COLOR`), a spinner on stderr while cargo
//! compiles, and the cleaning of libtest's panic text into the lines that tell a learner what went wrong.

use std::io::IsTerminal;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::Duration;

use indicatif::{ProgressBar, ProgressStyle};

/// Set by the learner's `test` command; `verify` and the other authoring commands leave it off so their output stays plain.
static SHOW_PROGRESS: AtomicBool = AtomicBool::new(false);

pub fn enable_progress() {
    SHOW_PROGRESS.store(true, Ordering::SeqCst);
}

/// Does stdout take colour? A terminal, and `NO_COLOR` unset or empty (https://no-color.org).
pub fn color_on() -> bool {
    std::io::stdout().is_terminal() && std::env::var_os("NO_COLOR").is_none_or(|v| v.is_empty())
}

fn paint(code: &str, text: &str) -> String {
    if color_on() { format!("\x1b[{code}m{text}\x1b[0m") } else { text.to_owned() }
}

pub fn green(t: &str) -> String {
    paint("32", t)
}
pub fn red(t: &str) -> String {
    paint("31", t)
}
pub fn dim(t: &str) -> String {
    paint("2", t)
}
pub fn bold(t: &str) -> String {
    paint("1", t)
}

/// A spinner with a message while `f` runs: shown on stderr, only when stderr is a terminal and progress is enabled.
pub fn with_spinner<T>(message: &str, f: impl FnOnce() -> T) -> T {
    if !SHOW_PROGRESS.load(Ordering::SeqCst) || !std::io::stderr().is_terminal() {
        return f();
    }
    let bar = ProgressBar::new_spinner();
    bar.set_style(ProgressStyle::with_template("{spinner} {msg} {elapsed}").unwrap_or_else(|_| ProgressStyle::default_spinner()));
    bar.set_message(message.to_owned());
    bar.enable_steady_tick(Duration::from_millis(90));
    let out = f();
    bar.finish_and_clear();
    out
}

/// `anneal ... | head` closes the pipe while we are still printing, and `println!` panics on that. A CLI should stop quietly instead (the usual
/// Unix behaviour); every other panic still reports as before.
pub fn quiet_broken_pipe() {
    let default = std::panic::take_hook();
    std::panic::set_hook(Box::new(move |info| {
        let text = info.to_string();
        if text.contains("Broken pipe") {
            std::process::exit(141); // 128 + SIGPIPE, what a shell reports for a process killed by the signal
        }
        default(info);
    }));
}

/// The lines of a failure worth showing: libtest's `thread '...' (id) panicked at file:line:col:` becomes `at file:line:col`, the
/// `RUST_BACKTRACE` note is dropped, and blank lines go.
pub fn clean_detail(detail: &str) -> Vec<String> {
    let mut out = Vec::new();
    for line in detail.lines() {
        let t = line.trim();
        if t.is_empty() || t.starts_with("note: run with `RUST_BACKTRACE") {
            continue;
        }
        if t.starts_with("thread '")
            && let Some((_, rest)) = t.split_once(" panicked at ")
        {
            out.push(format!("at {}", rest.trim_end_matches(':')));
            continue;
        }
        out.push(t.to_owned());
    }
    out
}

/// The part of a cleaned failure that says *what* went wrong, without the location: used to spot failures that repeat.
pub fn reason(lines: &[String]) -> String {
    lines.iter().filter(|l| !l.starts_with("at ")).cloned().collect::<Vec<_>>().join("\n")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_panic_header_becomes_a_location() {
        let d = "thread 's1a_01_x' (46799829) panicked at src/storage/disk/disk_manager.rs:19:5:\nnot yet implemented: 1a-01: slot offset\nnote: run with `RUST_BACKTRACE=1` environment variable to display a backtrace\n";
        assert_eq!(clean_detail(d), vec!["at src/storage/disk/disk_manager.rs:19:5", "not yet implemented: 1a-01: slot offset"]);
    }

    #[test]
    fn assertion_lines_are_kept() {
        let d = "thread 't' (1) panicked at tests/a.rs:3:5:\nassertion `left == right` failed\n  left: 1\n right: 2\n";
        let c = clean_detail(d);
        assert_eq!(c.len(), 4);
        assert_eq!(reason(&c), "assertion `left == right` failed\nleft: 1\nright: 2");
    }

    #[test]
    fn the_same_reason_at_different_places_is_the_same_reason() {
        let a = clean_detail("thread 'a' (1) panicked at src/x.rs:1:1:\nboom\n");
        let b = clean_detail("thread 'b' (2) panicked at src/y.rs:9:9:\nboom\n");
        assert_eq!(reason(&a), reason(&b));
    }

    #[test]
    fn no_spinner_or_colour_when_not_a_terminal() {
        // tests run with piped output
        assert!(!color_on());
        assert_eq!(green("x"), "x");
        assert_eq!(with_spinner("m", || 5), 5);
    }
}
