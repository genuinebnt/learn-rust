pub fn rotate_right(v: &mut [i32], k: usize) {
    if v.is_empty() {
        return;
    }
    for _ in 0..k % v.len() {
        let last = v[v.len() - 1];
        for i in (1..v.len()).rev() {
            v[i] = v[i - 1];
        }
        v[0] = last;
    }
}
