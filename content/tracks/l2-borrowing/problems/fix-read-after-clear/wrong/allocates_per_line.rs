use std::io::{self, BufRead};

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
        let line = buf.trim_end_matches(['\n', '\r']);
        let key = line.split(':').next().unwrap_or(line).to_string();
        if prev.as_ref() == Some(&key) {
            count += 1;
        } else {
            if let Some(p) = prev.take() {
                runs.push((p, count));
            }
            count = 1;
        }
        prev = Some(key);
    }
    if let Some(p) = prev {
        runs.push((p, count));
    }
    Ok(runs)
}
