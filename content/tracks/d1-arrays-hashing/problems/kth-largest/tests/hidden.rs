use solution::*;

#[test]
fn largest() {
    check!(r#"nums = [7, -1], k = 1"#, kth_largest(&mut [7, -1], 1), 7);
}

#[test]
fn smallest() {
    check!(r#"nums = 0..1000, k = 1000"#, kth_largest(&mut (0..1000).collect::<Vec<_>>(), 1000), 0);
}

#[test]
fn single() {
    check!(r#"nums = [5], k = 1"#, kth_largest(&mut [5], 1), 5);
}

#[test]
fn all_equal() {
    check!(r#"nums = [2, 2, 2], k = 3"#, kth_largest(&mut [2, 2, 2], 3), 2);
}

#[test]
fn repeated_max() {
    check!(r#"nums = [5, 5, 4], k = 2"#, kth_largest(&mut [5, 5, 4], 2), 5);
}

#[test]
fn negatives() {
    check!(r#"nums = [-1, -5, -3], k = 2"#, kth_largest(&mut [-1, -5, -3], 2), -3);
}

#[test]
fn extremes() {
    check!(r#"nums = [i32::MIN, i32::MAX, 0], k = 3"#, kth_largest(&mut [i32::MIN, i32::MAX, 0], 3), i32::MIN);
}

#[test]
fn sorted_descending() {
    check!(r#"nums = [9, 7, 5, 3, 1], k = 4"#, kth_largest(&mut [9, 7, 5, 3, 1], 4), 3);
}

#[test]
fn random_vs_sort() {
    let mut rng = anneal_prelude::Rng::new(20);
    for _ in 0..300 {
        let n = 1 + rng.below(12);
        let nums: Vec<i32> = rng.vec(n, -5, 5);
        let k = 1 + rng.below(n);
        let mut sorted = nums.clone();
        sorted.sort_unstable_by(|a, b| b.cmp(a));
        check!(format!("nums = {nums:?}, k = {k}"), kth_largest(&mut nums.clone(), k), sorted[k - 1]);
    }
}

#[test]
fn scale_200k() {
    let mut rng = anneal_prelude::Rng::new(21);
    let mut nums: Vec<i32> = (0..200_000).collect();
    rng.shuffle(&mut nums);
    check!("nums = 0..200000 shuffled, k = 100000", kth_largest(&mut nums, 100_000), 100_000);
}
