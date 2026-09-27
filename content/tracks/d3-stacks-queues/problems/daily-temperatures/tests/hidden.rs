use solution::*;

#[test]
fn falling() {
    check!(r#"[60,50,40]"#, daily_temperatures(&[60, 50, 40]), vec![0, 0, 0]);
}

#[test]
fn equal_is_not_warmer() {
    check!(r#"[50,50,51]"#, daily_temperatures(&[50, 50, 51]), vec![2, 1, 0]);
}

#[test]
fn long_wait() {
    let n = 100_000;
    let mut t: Vec<i32> = (0..n as i32).map(|i| 50_000 - i).collect();
    t.push(100_000);
    let ans = daily_temperatures(&t);
    let ok = (0..n).all(|i| ans[i] == n - i) && ans[n] == 0;
    check!(r#"10⁵ falling days, then a hot one"#, ok, true);
}
