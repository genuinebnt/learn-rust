use solution::*;

#[test]
fn empty_tree() {
    check!(r#"n = 0"#, num_trees(0), 1);
}

#[test]
fn five() {
    check!(r#"n = 5"#, num_trees(5), 42);
}

#[test]
fn ten() {
    check!(r#"n = 10"#, num_trees(10), 16_796);
}

#[test]
fn leetcode_max() {
    check!(r#"n = 19"#, num_trees(19), 1_767_263_190);
}

#[test]
fn past_u32() {
    check!(r#"n = 20"#, num_trees(20), 6_564_120_420);
}

#[test]
fn thirty_five() {
    check!(r#"n = 35"#, num_trees(35), 3_116_285_494_907_301_262);
}

#[test]
fn largest() {
    check!(r#"n = 36"#, num_trees(36), 11_959_798_385_860_453_492);
}

#[test]
fn random_vs_brute_force() {
    fn count(k: usize) -> u64 {
        if k == 0 { 1 } else { (0..k).map(|l| count(l) * count(k - 1 - l)).sum() }
    }
    let mut rng = anneal_prelude::Rng::new(1240);
    for _ in 0..200 {
        let n = rng.below(13);
        check!(format!("n = {n}"), num_trees(n as u32), count(n));
    }
}

#[test]
fn every_n_up_to_36() {
    // Catalan numbers also satisfy C(k + 1) = C(k) · 2(2k + 1) / (k + 2).
    let mut c: u128 = 1;
    for k in 0..=36u32 {
        check!(format!("n = {k}"), num_trees(k) as u128, c);
        c = c * 2 * (2 * k as u128 + 1) / (k as u128 + 2);
    }
}

#[test]
fn scale_36_repeated() {
    // Without the table, splitting on every root is about 3^36 calls.
    check!("n = 36, called 1000 times", (0..1000).map(|_| num_trees(36)).min(), Some(11_959_798_385_860_453_492));
}
