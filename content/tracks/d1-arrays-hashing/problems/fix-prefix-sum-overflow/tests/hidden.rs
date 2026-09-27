use solution::*;

#[test]
fn many_large() {
    check!(r#"nums = [2_000_000_000; 4]"#, max_prefix_sum(&[2_000_000_000; 4]), Some(8_000_000_000));
}

#[test]
fn all_negative() {
    check!(r#"nums = [-5, -1]"#, max_prefix_sum(&[-5, -1]), Some(-5));
}

#[test]
fn single() {
    check!(r#"nums = [7]"#, max_prefix_sum(&[7]), Some(7));
}

#[test]
fn single_negative() {
    check!(r#"nums = [-7]"#, max_prefix_sum(&[-7]), Some(-7));
}

#[test]
fn peak_in_middle() {
    check!(r#"nums = [1, 2, -10, 4]"#, max_prefix_sum(&[1, 2, -10, 4]), Some(3));
}

#[test]
fn zeros() {
    check!(r#"nums = [0, 0]"#, max_prefix_sum(&[0, 0]), Some(0));
}

#[test]
fn below_i32_min() {
    check!(r#"nums = [i32::MIN, i32::MIN]"#, max_prefix_sum(&[i32::MIN, i32::MIN]), Some(i32::MIN as i64));
}

#[test]
fn dips_below_then_recovers() {
    check!(r#"nums = [i32::MIN, -1, i32::MAX, i32::MAX, 5]"#, max_prefix_sum(&[i32::MIN, -1, i32::MAX, i32::MAX, 5]), Some(2_147_483_650));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(16);
    for _ in 0..300 {
        let n = rng.below(8);
        let nums: Vec<i32> = rng.vec(n, i32::MIN as i64, i32::MAX as i64);
        let want = (1..=n).map(|k| nums[..k].iter().map(|&x| x as i64).sum::<i64>()).max();
        check!(format!("nums = {nums:?}"), max_prefix_sum(&nums), want);
    }
}

#[test]
fn scale_200k_max() {
    check!("nums = [i32::MAX; 200000]", max_prefix_sum(&vec![i32::MAX; 200_000]), Some(i32::MAX as i64 * 200_000));
}
