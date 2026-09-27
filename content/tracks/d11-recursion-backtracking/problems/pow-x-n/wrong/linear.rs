pub fn my_pow(x: f64, n: i32) -> f64 {
    let mut p = 1.0;
    for _ in 0..n.unsigned_abs() {
        p *= x;
    }
    if n < 0 { 1.0 / p } else { p }
}
