use solution::*;

#[test]
fn one() {
    check!(r#"nums = [7]"#, concat_twice(&[7]), vec![7, 7]);
}

#[test]
fn length() {
    check!(r#"nums = 0..1000"#, concat_twice(&(0..1000).collect::<Vec<_>>()).len(), 2000);
}

#[test]
fn negatives() {
    check!(r#"nums = [-1, -2]"#, concat_twice(&[-1, -2]), vec![-1, -2, -1, -2]);
}

#[test]
fn duplicates() {
    check!(r#"nums = [4, 4, 5]"#, concat_twice(&[4, 4, 5]), vec![4, 4, 5, 4, 4, 5]);
}

#[test]
fn single_zero() {
    check!(r#"nums = [0]"#, concat_twice(&[0]), vec![0, 0]);
}

#[test]
fn extremes() {
    check!(r#"nums = [i32::MIN, i32::MAX]"#, concat_twice(&[i32::MIN, i32::MAX]), vec![i32::MIN, i32::MAX, i32::MIN, i32::MAX]);
}

#[test]
fn order_kept() {
    check!(r#"nums = [3, 1, 2]"#, concat_twice(&[3, 1, 2]), vec![3, 1, 2, 3, 1, 2]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2);
    for _ in 0..200 {
        let n = rng.below(12);
        let nums: Vec<i32> = rng.vec(n, -50, 50);
        let mut want = nums.clone();
        want.extend(nums.iter().copied());
        check!(format!("nums = {nums:?}"), concat_twice(&nums), want);
    }
}

#[test]
fn scale_200k() {
    let nums: Vec<i32> = (0..200_000).collect();
    let out = concat_twice(&nums);
    check!("nums = 0..200000", (out.len(), out[199_999], out[200_000], out[399_999]), (400_000, 199_999, 0, 199_999));
}
