pub fn my_pow(x: f64, n: i32) -> f64 {
    if n < 0 {
        return 1.0 / my_pow(x, -n);
    }
    if n == 0 {
        return 1.0;
    }
    let half = my_pow(x, n / 2);
    if n % 2 == 0 { half * half } else { half * half * x }
}
