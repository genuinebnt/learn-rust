/// Centers `s` in a field `width` characters wide, padding with `fill`.
/// Odd padding puts the extra character on the right. Text of `width` characters or more is returned as is.
pub fn center(s: &str, width: usize, fill: char) -> String {
    let len = s.chars().count();
    if len >= width {
        return s.to_string();
    }
    let left = (width - len) / 2;
    let right = width - len - left;
    let mut out = String::new();
    out.extend(std::iter::repeat(fill).take(left));
    out.push_str(s);
    out.extend(std::iter::repeat(fill).take(right));
    out
}

/// The number of whitespace characters at the start of `line`.
pub fn indent(line: &str) -> usize {
    line.chars().take_while(|c| c.is_whitespace()).count()
}

/// Greedy word wrap. Words are the whitespace-separated pieces of `text`. Each line holds as many words
/// as fit in `width` characters, separated by single spaces; a word longer than `width` gets a line to itself.
pub fn wrap(text: &str, width: usize) -> Vec<String> {
    let mut lines = Vec::new();
    let mut line = String::new();
    let mut used = 0;
    for word in text.split_whitespace() {
        let w = word.chars().count();
        if used > 0 && used + 1 + w > width {
            lines.push(std::mem::take(&mut line));
            used = 0;
        }
        if used > 0 {
            line.push(' ');
            used += 1;
        }
        line.push_str(word);
        used += w;
    }
    if !line.is_empty() {
        lines.push(line);
    }
    lines
}
