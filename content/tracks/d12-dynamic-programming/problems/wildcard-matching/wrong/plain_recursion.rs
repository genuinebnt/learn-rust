fn matches(s: &[char], p: &[char]) -> bool {
    match p.split_first() {
        None => s.is_empty(),
        Some(('*', rest)) => (0..=s.len()).any(|k| matches(&s[k..], rest)),
        Some((&q, rest)) => !s.is_empty() && (q == '?' || q == s[0]) && matches(&s[1..], rest),
    }
}

pub fn is_match(s: &str, p: &str) -> bool {
    let s: Vec<char> = s.chars().collect();
    let p: Vec<char> = p.chars().collect();
    matches(&s, &p)
}
