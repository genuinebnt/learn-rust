use solution::*;

#[test]
fn single_negative() {
    check!(r#"nums = [-7]"#, max_subarray(&[-7]), Some(-7));
}

#[test]
fn i32_min() {
    check!(r#"nums = [-2147483648]"#, max_subarray(&[i32::MIN]), Some(-2_147_483_648));
}

#[test]
fn zeros() {
    check!(r#"nums = [0, 0]"#, max_subarray(&[0, 0]), Some(0));
}

#[test]
fn zero_among_negatives() {
    check!(r#"nums = [-1, 0, -2]"#, max_subarray(&[-1, 0, -2]), Some(0));
}

#[test]
fn dip_worth_keeping() {
    check!(r#"nums = [3, -2, 5]"#, max_subarray(&[3, -2, 5]), Some(6));
}

#[test]
fn dip_not_worth_keeping() {
    check!(r#"nums = [2, -5, 3]"#, max_subarray(&[2, -5, 3]), Some(3));
}

#[test]
fn best_at_end() {
    check!(r#"nums = [8, -19, 5, -4, 20]"#, max_subarray(&[8, -19, 5, -4, 20]), Some(21));
}

#[test]
fn min_values() {
    check!(r#"nums = [i32::MIN; 3]"#, max_subarray(&[i32::MIN; 3]), Some(-2_147_483_648));
}

#[test]
fn big_total() {
    check!(r#"nums = [100000; 200000]"#, max_subarray(&vec![100_000; 200_000]), Some(20_000_000_000));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(805);
    for _ in 0..400 {
        let n = rng.below(16);
        let nums: Vec<i32> = rng.vec(n, -20, 20);
        let mut want: Option<i64> = None;
        for i in 0..n {
            for j in i..n {
                let s: i64 = nums[i..=j].iter().map(|&x| x as i64).sum();
                want = Some(want.map_or(s, |w| w.max(s)));
            }
        }
        check!(format!("nums = {nums:?}"), max_subarray(&nums), want);
    }
}

#[test]
fn scale_200k() {
    let nums: Vec<i32> = (0..200_000).map(|i| if i % 2 == 0 { 1_000_000_000 } else { -999_999_999 }).collect();
    check!("nums = [10⁹, -(10⁹ - 1), …] (200000 values)", max_subarray(&nums), Some(1_000_099_999));
}
