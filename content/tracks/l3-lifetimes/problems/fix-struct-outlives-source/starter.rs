pub struct Excerpt<'a> {
    pub text: &'a str,
}

/// The first line of each document, after trimming the document.
pub fn first_lines(docs: &[String]) -> Vec<String> {
    let mut excerpts = Vec::new();
    for d in docs {
        let trimmed = d.trim().to_string();
        excerpts.push(Excerpt { text: trimmed.lines().next().unwrap_or("") });
    }
    excerpts.iter().map(|e| e.text.to_string()).collect()
}
