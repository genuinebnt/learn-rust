pub fn median(a: &[i32], b: &[i32]) -> Option<f64> {
    let mut all: Vec<i64> = a.iter().chain(b).map(|&x| i64::from(x)).collect();
    all.sort_unstable();
    let k = all.len();
    (k > 0).then(|| if k % 2 == 1 { all[k / 2] as f64 } else { (all[k / 2 - 1] + all[k / 2]) as f64 / 2.0 })
}
