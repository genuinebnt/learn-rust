use solution::*;

#[test]
fn none() {
    check!(r#"nums = [5, 5], k = 3"#, subarray_sum(&[5, 5], 3), 0);
}

#[test]
fn all_zero() {
    check!(r#"nums = [0; 100], k = 0"#, subarray_sum(&[0; 100], 0), 5050);
}

#[test]
fn single_match() {
    check!(r#"nums = [5], k = 5"#, subarray_sum(&[5], 5), 1);
}

#[test]
fn single_miss() {
    check!(r#"nums = [5], k = -5"#, subarray_sum(&[5], -5), 0);
}

#[test]
fn negative_k() {
    check!(r#"nums = [-1, -1, 1], k = -1"#, subarray_sum(&[-1, -1, 1], -1), 3);
}

#[test]
fn alternating_zero() {
    check!(r#"nums = [1, -1, 1, -1], k = 0"#, subarray_sum(&[1, -1, 1, -1], 0), 4);
}

#[test]
fn whole_array() {
    check!(r#"nums = [3, 4, 7], k = 14"#, subarray_sum(&[3, 4, 7], 14), 1);
}

#[test]
fn bounds() {
    check!(r#"nums = [1000, -1000, 1000], k = 1000"#, subarray_sum(&[1000, -1000, 1000], 1000), 3);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(14);
    for _ in 0..300 {
        let n = 1 + rng.below(12);
        let nums: Vec<i32> = rng.vec(n, -3, 3);
        let k = rng.int(-4, 4) as i32;
        let want = (0..n).flat_map(|i| (i + 1..=n).map(move |j| (i, j))).filter(|&(i, j)| nums[i..j].iter().sum::<i32>() == k).count();
        check!(format!("nums = {nums:?}, k = {k}"), subarray_sum(&nums, k), want);
    }
}

#[test]
fn scale_200k_zeros() {
    check!("nums = [0; 200000], k = 0", subarray_sum(&vec![0; 200_000], 0), 20_000_100_000);
}
