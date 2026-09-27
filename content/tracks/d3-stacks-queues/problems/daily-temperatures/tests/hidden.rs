use solution::*;

#[test]
fn single() {
    check!(r#"[50]"#, daily_temperatures(&[50]), vec![0]);
}

#[test]
fn empty() {
    check!(r#"[]"#, daily_temperatures(&[]), Vec::<usize>::new());
}

#[test]
fn all_equal() {
    check!(r#"[5,5,5]"#, daily_temperatures(&[5, 5, 5]), vec![0, 0, 0]);
}

#[test]
fn negatives() {
    check!(r#"[-5,-10,-3]"#, daily_temperatures(&[-5, -10, -3]), vec![2, 1, 0]);
}

#[test]
fn extremes() {
    check!(r#"[i32::MIN, i32::MAX]"#, daily_temperatures(&[i32::MIN, i32::MAX]), vec![1, 0]);
}

#[test]
fn valley() {
    check!(r#"[3,1,2,4]"#, daily_temperatures(&[3, 1, 2, 4]), vec![3, 1, 1, 0]);
}

#[test]
fn peak_later() {
    check!(r#"[1,5,2,3,4,6]"#, daily_temperatures(&[1, 5, 2, 3, 4, 6]), vec![1, 4, 1, 1, 1, 0]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(3006);
    for _ in 0..300 {
        let n = rng.below(12);
        let t: Vec<i32> = rng.vec(n, 30, 40);
        let want: Vec<usize> = (0..n).map(|i| (i + 1..n).find(|&j| t[j] > t[i]).map_or(0, |j| j - i)).collect();
        check!(format!("temps = {t:?}"), daily_temperatures(&t), want);
    }
}

#[test]
fn scale_200k_falling() {
    let mut t: Vec<i32> = (0..200_000).map(|i| 300_000 - i).collect();
    t.push(1_000_000);
    let ans = daily_temperatures(&t);
    check!("200000 falling days, then a hot one", (ans[0], ans[199_999], ans[200_000]), (200_000, 1, 0));
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
