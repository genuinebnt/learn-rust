use solution::*;

#[test]
fn two_zeros() {
    check!(r#"nums = [0, 4, 0]"#, product_except_self(&[0, 4, 0]), vec![0, 0, 0]);
}

#[test]
fn pair() {
    check!(r#"nums = [3, 5]"#, product_except_self(&[3, 5]), vec![5, 3]);
}

#[test]
fn all_negative() {
    check!(r#"nums = [-1, -2, -3]"#, product_except_self(&[-1, -2, -3]), vec![6, 3, 2]);
}

#[test]
fn zero_first() {
    check!(r#"nums = [0, 1, 2, 3]"#, product_except_self(&[0, 1, 2, 3]), vec![6, 0, 0, 0]);
}

#[test]
fn zero_last() {
    check!(r#"nums = [2, 3, 0]"#, product_except_self(&[2, 3, 0]), vec![0, 0, 6]);
}

#[test]
fn pair_with_zero() {
    check!(r#"nums = [0, 5]"#, product_except_self(&[0, 5]), vec![5, 0]);
}

#[test]
fn ones() {
    check!(r#"nums = [1, 1, 1, 1]"#, product_except_self(&[1, 1, 1, 1]), vec![1, 1, 1, 1]);
}

#[test]
fn near_i32_max() {
    check!(r#"nums = [46340, 46340, 1]"#, product_except_self(&[46_340, 46_340, 1]), vec![46_340, 46_340, 2_147_395_600]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(13);
    for _ in 0..300 {
        let n = 2 + rng.below(7);
        let nums: Vec<i32> = rng.vec(n, -3, 3);
        let want: Vec<i32> = (0..n).map(|i| (0..n).filter(|&j| j != i).map(|j| nums[j]).product()).collect();
        check!(format!("nums = {nums:?}"), product_except_self(&nums), want);
    }
}

#[test]
fn scale_100k() {
    let nums: Vec<i32> = (0..100_000).map(|i| if i % 3 == 0 { -1 } else { 1 }).collect();
    let out = product_except_self(&nums);
    // 33334 factors of -1: the total is 1, so out[i] is 1 / nums[i] = nums[i].
    check!("nums = [-1, 1, 1, -1, 1, 1, …] (100000 values)", out == nums, true);
}
