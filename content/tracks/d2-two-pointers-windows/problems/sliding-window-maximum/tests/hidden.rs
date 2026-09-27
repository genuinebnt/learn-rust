use solution::*;

#[test]
fn whole() {
    check!(r#"nums = [9, 10, 9, -7], k = 4"#, max_sliding_window(&[9, 10, 9, -7], 4), vec![10]);
}

#[test]
fn descending() {
    check!(r#"nums = [5, 4, 3, 2, 1], k = 2"#, max_sliding_window(&[5, 4, 3, 2, 1], 2), vec![5, 4, 3, 2]);
}

#[test]
fn large() {
    check!(r#"nums = 0..100000, k = 1000"#, max_sliding_window(&(0..100_000).collect::<Vec<_>>(), 1000).len(), 99001);
}

#[test]
fn single() {
    check!(r#"nums = [1], k = 1"#, max_sliding_window(&[1], 1), vec![1]);
}

#[test]
fn ascending() {
    check!(r#"nums = [1, 2, 3, 4, 5], k = 2"#, max_sliding_window(&[1, 2, 3, 4, 5], 2), vec![2, 3, 4, 5]);
}

#[test]
fn all_equal() {
    check!(r#"nums = [7, 7, 7, 7], k = 3"#, max_sliding_window(&[7, 7, 7, 7], 3), vec![7, 7]);
}

#[test]
fn max_leaves_window() {
    check!(r#"nums = [9, 1, 1, 1], k = 2"#, max_sliding_window(&[9, 1, 1, 1], 2), vec![9, 1, 1]);
}

#[test]
fn extremes() {
    check!(r#"nums = [i32::MIN, i32::MAX, i32::MIN, i32::MIN], k = 2"#, max_sliding_window(&[i32::MIN, i32::MAX, i32::MIN, i32::MIN], 2), vec![i32::MAX, i32::MAX, i32::MIN]);
}

#[test]
fn negatives() {
    check!(r#"nums = [-7, -8, 7, 5, 7, 1, 6, 0], k = 4"#, max_sliding_window(&[-7, -8, 7, 5, 7, 1, 6, 0], 4), vec![7, 7, 7, 7, 7]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(218);
    for _ in 0..300 {
        let n = 1 + rng.below(14);
        let k = 1 + rng.below(n);
        let nums: Vec<i32> = rng.vec(n, -5, 5);
        let want: Vec<i32> = nums.windows(k).map(|w| *w.iter().max().unwrap()).collect();
        check!(format!("nums = {nums:?}, k = {k}"), max_sliding_window(&nums, k), want);
    }
}

#[test]
fn scale_200k() {
    let nums: Vec<i32> = (0..200_000).rev().collect();
    let want: Vec<i32> = (100_000 - 1..200_000).rev().collect();
    check!("nums = 199999 down to 0, k = 100000", max_sliding_window(&nums, 100_000) == want, true);
}
