pub fn normalize(s: &mut String) {
    let trimmed = s.trim().to_lowercase();
    *s = trimmed;
}

pub fn same_after_normalizing(a: &mut String, b: &mut String) -> bool {
    normalize(a);
    normalize(b);
    a == b
}
