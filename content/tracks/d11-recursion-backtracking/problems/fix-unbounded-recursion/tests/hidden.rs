use solution::*;

#[test]
fn single_negative() {
    check!(r#"nums = [-9]"#, split_sum(&[-9]), -9);
}

#[test]
fn single_zero() {
    check!(r#"nums = [0]"#, split_sum(&[0]), 0);
}

#[test]
fn two() {
    check!(r#"nums = [4, 6]"#, split_sum(&[4, 6]), 10);
}

#[test]
fn cancels_out() {
    check!(r#"nums = [5, -5, 5, -5, 1]"#, split_sum(&[5, -5, 5, -5, 1]), 1);
}

#[test]
fn near_max() {
    check!(r#"nums = [i64::MAX - 1, 1]"#, split_sum(&[i64::MAX - 1, 1]), i64::MAX);
}

#[test]
fn near_min() {
    check!(r#"nums = [i64::MIN + 5, -5]"#, split_sum(&[i64::MIN + 5, -5]), i64::MIN);
}

#[test]
fn large_values() {
    check!(r#"nums = [10¹⁵; 1000]"#, split_sum(&vec![1_000_000_000_000_000; 1000]), 1_000_000_000_000_000_000);
}

#[test]
fn empty_again() {
    check!(r#"nums = []"#, split_sum(&[]), 0);
}

#[test]
fn random_vs_loop() {
    let mut rng = anneal_prelude::Rng::new(1107);
    for _ in 0..300 {
        let n = rng.below(40);
        let nums: Vec<i64> = rng.vec(n, -1_000_000_000, 1_000_000_000);
        let mut want = 0;
        for &x in &nums {
            want += x;
        }
        check!(format!("nums = {nums:?}"), split_sum(&nums), want);
    }
}

#[test]
fn scale_200k() {
    let nums: Vec<i64> = (1..=200_000).collect();
    check!("nums = 1..=200000", split_sum(&nums), 20_000_100_000);
}
