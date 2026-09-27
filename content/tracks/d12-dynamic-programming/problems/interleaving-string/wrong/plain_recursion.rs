fn can(a: &[u8], b: &[u8], c: &[u8]) -> bool {
    match c {
        [] => a.is_empty() && b.is_empty(),
        [x, rest @ ..] => (a.first() == Some(x) && can(&a[1..], b, rest)) || (b.first() == Some(x) && can(a, &b[1..], rest)),
    }
}

pub fn is_interleave(s1: &str, s2: &str, s3: &str) -> bool {
    can(s1.as_bytes(), s2.as_bytes(), s3.as_bytes())
}
