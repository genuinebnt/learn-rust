fn matches(s: &[char], p: &[char]) -> bool {
    if p.is_empty() {
        return s.is_empty();
    }
    let first = !s.is_empty() && (p[0] == '.' || p[0] == s[0]);
    if p.len() >= 2 && p[1] == '*' {
        matches(s, &p[2..]) || (first && matches(&s[1..], p))
    } else {
        first && matches(&s[1..], &p[1..])
    }
}

pub fn is_match(s: &str, p: &str) -> bool {
    let s: Vec<char> = s.chars().collect();
    let p: Vec<char> = p.chars().collect();
    matches(&s, &p)
}
