pub fn my_pow(x: f64, n: i32) -> f64 {
    // x^n for n ≥ 0: square the answer for n / 2, times x once more when n is odd.
    fn power(x: f64, n: u32) -> f64 {
        if n == 0 {
            return 1.0;
        }
        let half = power(x, n / 2);
        if n % 2 == 0 { half * half } else { half * half * x }
    }
    // `unsigned_abs` is exact for i32::MIN, where `-n` would overflow.
    let p = power(x, n.unsigned_abs());
    if n < 0 { 1.0 / p } else { p }
}
