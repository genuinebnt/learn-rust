/// The longer of `a` and `b`; `a` on a tie.
pub fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
    if b.len() > a.len() {
        b
    } else {
        a
    }
}

/// The longest of `words` (the first on a tie), or None if there are none.
pub fn longest_of<'a>(words: &[&'a str]) -> Option<&'a str> {
    let mut best: Option<&'a str> = None;
    for &w in words {
        if best.map_or(true, |b| w.len() >= b.len()) {
            best = Some(w);
        }
    }
    best
}

/// Makes `best` point at `line` if `line` is longer. Returns whether it did.
pub fn keep_longest<'a>(best: &mut &'a str, line: &'a str) -> bool {
    if line.len() > best.len() {
        *best = line;
        true
    } else {
        false
    }
}
