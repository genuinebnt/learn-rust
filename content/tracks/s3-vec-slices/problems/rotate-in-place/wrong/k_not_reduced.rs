pub fn rotate_right(v: &mut [i32], k: usize) {
    if v.is_empty() || k > v.len() {
        return;
    }
    let k = k % v.len();
    v.reverse();
    v[..k].reverse();
    v[k..].reverse();
}
