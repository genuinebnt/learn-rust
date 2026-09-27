pub fn my_pow(x: f64, n: i32) -> f64 {
    fn power(x: f64, n: u32) -> f64 {
        if n == 0 {
            return 1.0;
        }
        let half = power(x, n / 2);
        if n % 2 == 0 { half * half } else { half * half * x }
    }
    power(x, n.unsigned_abs())
}
