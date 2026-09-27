fn walk(t: &[Vec<i32>], r: usize, c: usize) -> i64 {
    let here = t[r][c] as i64;
    if r + 1 == t.len() { here } else { here + walk(t, r + 1, c).min(walk(t, r + 1, c + 1)) }
}

pub fn minimum_total(triangle: &[Vec<i32>]) -> i64 {
    walk(triangle, 0, 0)
}
