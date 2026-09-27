use std::collections::HashMap;
use std::io::{self, Read};

/// Word counts, most frequent first; ties in byte order of the word.
/// Generic, so it's compiled once per reader type: keep it to one line.
pub fn word_counts<R: Read>(mut reader: R) -> io::Result<Vec<(String, usize)>> {
    word_counts_dyn(&mut reader)
}

/// The worker. It isn't generic, so it's compiled once, whatever readers callers use.
pub fn word_counts_dyn(reader: &mut dyn Read) -> io::Result<Vec<(String, usize)>> {
    let mut bytes = Vec::new();
    let mut buf = [0u8; 4096];
    loop {
        let n = reader.read(&mut buf)?;
        if n == 0 {
            break;
        }
        bytes.extend_from_slice(&buf[..n]);
    }
    let text = String::from_utf8(bytes).map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))?;
    let mut counts: HashMap<String, usize> = HashMap::new();
    for w in text.split_whitespace() {
        *counts.entry(w.to_string()).or_insert(0) += 1;
    }
    let mut out: Vec<(String, usize)> = counts.into_iter().collect();
    out.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));
    Ok(out)
}
