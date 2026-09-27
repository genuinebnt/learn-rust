use std::io::{self, BufRead};

/// Counts runs of consecutive lines with the same key. A line's key is the text before its first ':', or the
/// whole line (without its line ending) when it has none. Returns each run's key and length, in order.
pub fn key_runs<R: BufRead>(mut input: R) -> io::Result<Vec<(String, usize)>> {
    let mut runs: Vec<(String, usize)> = Vec::new();
    let mut buf = String::new();
    let mut prev: Option<String> = None;
    let mut count = 0;
    loop {
        buf.clear();
        if input.read_line(&mut buf)? == 0 {
            break;
        }
        let line = buf.trim_end_matches('\n');
        let key = line.split(':').next().unwrap_or(line);
        if prev.as_deref() == Some(key) {
            count += 1;
        } else {
            if let Some(p) = prev.replace(key.to_string()) {
                runs.push((p, count));
            }
            count = 1;
        }
    }
    if let Some(p) = prev {
        runs.push((p, count));
    }
    Ok(runs)
}
