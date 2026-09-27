/// The longer of `a` and `b`; `a` on a tie.
pub fn longest(a: &str, b: &str) -> &str {
    if b.len() > a.len() {
        b
    } else {
        a
    }
}

/// The longest of `words` (the first on a tie), or None if there are none.
pub fn longest_of(words: &[&str]) -> Option<&str> {
    let mut best: Option<&str> = None;
    for &w in words {
        if best.map_or(true, |b| w.len() > b.len()) {
            best = Some(w);
        }
    }
    best
}

/// Makes `best` point at `line` if `line` is longer. Returns whether it did.
pub fn keep_longest(best: &mut &str, line: &str) -> bool {
    if line.len() > best.len() {
        *best = line;
        true
    } else {
        false
    }
}
