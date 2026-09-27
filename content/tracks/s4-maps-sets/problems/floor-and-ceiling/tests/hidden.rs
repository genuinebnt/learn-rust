use solution::*;

#[test]
fn zero() {
    check!(r#"prices = {0}, x = 0"#, nearest(&std::collections::BTreeSet::from([0]), 0), (Some(0), Some(0)));
}

#[test]
fn max_in_set() {
    check!(r#"prices = {5, u32::MAX}, x = u32::MAX"#, nearest(&std::collections::BTreeSet::from([5, u32::MAX]), u32::MAX), (Some(u32::MAX), Some(u32::MAX)));
}

#[test]
fn max_not_in_set() {
    check!(r#"prices = {5}, x = u32::MAX"#, nearest(&std::collections::BTreeSet::from([5]), u32::MAX), (Some(5), None));
}

#[test]
fn zero_not_in_set() {
    check!(r#"prices = {5}, x = 0"#, nearest(&std::collections::BTreeSet::from([5]), 0), (None, Some(5)));
}

#[test]
fn single_equal() {
    check!(r#"prices = {7}, x = 7"#, nearest(&std::collections::BTreeSet::from([7]), 7), (Some(7), Some(7)));
}

#[test]
fn adjacent() {
    check!(r#"prices = {1, 2}, x = 1"#, nearest(&std::collections::BTreeSet::from([1, 2]), 1), (Some(1), Some(1)));
}

#[test]
fn just_above_one() {
    check!(r#"prices = {10, 20, 30}, x = 11"#, nearest(&std::collections::BTreeSet::from([10, 20, 30]), 11), (Some(10), Some(20)));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4009);
    for _ in 0..300 {
        let n = rng.below(8);
        let prices: std::collections::BTreeSet<u32> = (0..n).map(|_| rng.below(20) as u32).collect();
        let x = rng.below(21) as u32;
        let want = (prices.iter().copied().filter(|&p| p <= x).max(), prices.iter().copied().filter(|&p| p >= x).min());
        check!(format!("prices = {prices:?}, x = {x}"), nearest(&prices, x), want);
    }
}

#[test]
fn scale_100k_queries() {
    let prices: std::collections::BTreeSet<u32> = (0..200_000u32).map(|i| i * 2).collect();
    let mut total = 0u64;
    for q in 0..100_000u32 {
        let (f, c) = nearest(&prices, q * 2 + 1);
        total += u64::from(f.unwrap_or(0)) + u64::from(c.unwrap_or(0));
    }
    check!("200000 even prices; 100000 odd queries", total, 20_000_000_000);
}
