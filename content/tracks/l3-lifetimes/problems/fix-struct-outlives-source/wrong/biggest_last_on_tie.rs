use std::cmp::Reverse;

#[derive(Debug, PartialEq)]
pub struct Excerpt<'a> {
    pub title: &'a str,
    pub first_line: &'a str,
}

impl<'a> Excerpt<'a> {
    /// The title is the document's first line, trimmed. `first_line` is the first non-blank line after it,
    /// trimmed ("" if there's none). Lines may end in "\n" or "\r\n".
    pub fn of(doc: &'a str) -> Self {
        let mut lines = doc.lines().map(str::trim);
        let title = lines.next().unwrap_or("");
        let first_line = lines.find(|l| !l.is_empty()).unwrap_or("");
        Excerpt { title, first_line }
    }
}

/// Every document's title, longest first (in document order on a tie).
pub fn titles(docs: &[String]) -> Vec<&str> {
    let ex = excerpts(docs);
    let mut t: Vec<&str> = ex.iter().map(|e| e.title).collect();
    t.sort_by_key(|s| Reverse(s.len()));
    t
}

/// The excerpt of every document, in order.
pub fn excerpts(docs: &[String]) -> Vec<Excerpt<'_>> {
    docs.iter().map(|d| Excerpt::of(d)).collect()
}

/// The excerpt of what follows the first "---" line in `raw`, or of all of `raw` if there's no such line.
pub fn body_excerpt(raw: &str) -> Excerpt<'_> {
    let body = match raw.split_once("---\n") {
        Some((_, rest)) => rest,
        None => raw,
    };
    Excerpt::of(body)
}

/// The excerpt of the document with the most lines (the first on a tie), or None if there are none.
pub fn biggest(docs: &[String]) -> Option<Excerpt<'_>> {
    let mut best: Option<&String> = None;
    for d in docs {
        if best.map_or(true, |b| d.lines().count() >= b.lines().count()) {
            best = Some(d);
        }
    }
    Some(Excerpt::of(best?))
}
