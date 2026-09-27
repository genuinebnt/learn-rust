pub fn middle(v: &[i32]) -> &[i32] {
    v.get(1..v.len().saturating_sub(1)).unwrap_or(&[])
}

pub fn trim_zeros(v: &[i32]) -> &[i32] {
    let start = v.iter().position(|&x| x != 0).unwrap_or(v.len());
    let end = v.iter().rposition(|&x| x != 0).unwrap_or(start);
    &v[start..end.max(start)]
}
