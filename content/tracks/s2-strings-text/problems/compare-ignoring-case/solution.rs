/// Does `input`, ignoring surrounding whitespace, name `command`, ignoring ASCII case? No allocation.
pub fn is_command(input: &str, command: &str) -> bool {
    input.trim().eq_ignore_ascii_case(command)
}

/// Lower-cases an HTTP header name in place. Only ASCII letters change. No allocation.
pub fn normalize_header(name: &mut String) {
    name.make_ascii_lowercase();
}

/// Each whitespace-separated word with its first character in upper case and the rest in lower case,
/// by the full Unicode rules. Words are joined by single spaces.
pub fn title_case(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for word in s.split_whitespace() {
        if !out.is_empty() {
            out.push(' ');
        }
        let mut chars = word.chars();
        if let Some(first) = chars.next() {
            out.extend(first.to_uppercase());
            out.push_str(&chars.as_str().to_lowercase());
        }
    }
    out
}
