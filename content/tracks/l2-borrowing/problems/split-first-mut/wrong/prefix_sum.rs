pub fn add_head_to_rest(v: &mut [i32]) {
    for i in 1..v.len() {
        v[i] += v[i - 1];
    }
}
