pub fn push_sum(v: Vec<i64>) -> Vec<i64> {
    let mut out = Vec::with_capacity(v.len() + 1);
    out.extend_from_slice(&v);
    out.push(v.iter().sum());
    out
}

pub fn swap_owned(a: String, b: String) -> (String, String) {
    (b, a)
}
