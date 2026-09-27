pub fn add_halves(v: &mut [i32]) {
    let n = v.len();
    for i in 0..n / 2 {
        v[n - 1 - i] += v[i];
    }
}
