use solution::*;

#[test]
fn one_empty() {
    check!(r#"[], [5]"#, median(&[], &[5]), Some(5.0));
}

#[test]
fn both_empty() {
    check!(r#"[], []"#, median(&[], &[]), None);
}

#[test]
fn extremes() {
    check!(r#"[i32::MIN], [i32::MAX]"#, median(&[i32::MIN], &[i32::MAX]), Some(-0.5));
}

#[test]
fn interleaved() {
    let odd: Vec<i32> = (0..100_000).filter(|x| x % 2 == 1).collect();
    let even: Vec<i32> = (0..100_000).filter(|x| x % 2 == 0).collect();
    check!(r#"odds and evens up to 10⁵"#, median(&odd, &even), Some(49_999.5));
}

#[test]
fn disjoint() {
    check!(r#"[1,2,3], [10,11,12,13]"#, median(&[1, 2, 3], &[10, 11, 12, 13]), Some(10.0));
}

#[test]
fn both_max() {
    check!(r#"[i32::MAX], [i32::MAX]"#, median(&[i32::MAX], &[i32::MAX]), Some(2_147_483_647.0));
}

#[test]
fn negatives() {
    check!(r#"[-5,-3], [-4]"#, median(&[-5, -3], &[-4]), Some(-4.0));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(411);
    for _ in 0..400 {
        let (m, n) = (rng.below(7), rng.below(7));
        let mut a: Vec<i32> = rng.vec(m, -20, 20);
        let mut b: Vec<i32> = rng.vec(n, -20, 20);
        a.sort_unstable();
        b.sort_unstable();
        let mut all: Vec<i64> = a.iter().chain(&b).map(|&x| i64::from(x)).collect();
        all.sort_unstable();
        let k = all.len();
        let want = (k > 0).then(|| if k % 2 == 1 { all[k / 2] as f64 } else { (all[k / 2 - 1] + all[k / 2]) as f64 / 2.0 });
        check!(format!("a = {a:?}, b = {b:?}"), median(&a, &b), want);
    }
}

#[test]
fn scale_100k_queries() {
    // a = evens, b = odds, each 200000 long; 100000 medians of prefixes a[..i], b[..j] with i, j ≥ 100000.
    let a: Vec<i32> = (0..200_000).map(|x| 2 * x).collect();
    let b: Vec<i32> = (0..200_000).map(|x| 2 * x + 1).collect();
    let bad = (0..100_000usize).filter(|&q| {
        let (i, j) = (100_000 + q * 7919 % 100_000, 100_000 + q * 104_729 % 100_000);
        // The k-th smallest of the union, from 0: 0, 1, 2, … up to 2·min(i, j), then every other value of the longer prefix.
        let m = i.min(j);
        let kth = |k: usize| (if k < 2 * m { k } else { 2 * m + 2 * (k - 2 * m) + usize::from(j > i) }) as f64;
        let t = i + j;
        let want = if t % 2 == 1 { kth(t / 2) } else { (kth(t / 2 - 1) + kth(t / 2)) / 2.0 };
        median(&a[..i], &b[..j]) != Some(want)
    }).count();
    check!("100000 medians of long prefixes of the evens and the odds: how many are wrong", bad, 0);
}
