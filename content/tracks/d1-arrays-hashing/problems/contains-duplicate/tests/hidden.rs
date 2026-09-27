use solution::*;

#[test]
fn many_repeats() {
    check!(r#"nums = [1, 1, 1, 3, 3, 4, 3, 2, 4, 2]"#, contains_duplicate(&[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]), true);
}

#[test]
fn large_distinct() {
    check!(r#"nums = 0..100000"#, contains_duplicate(&(0..100_000).collect::<Vec<_>>()), false);
}

#[test]
fn single() {
    check!(r#"nums = [1]"#, contains_duplicate(&[1]), false);
}

#[test]
fn pair() {
    check!(r#"nums = [2, 2]"#, contains_duplicate(&[2, 2]), true);
}

#[test]
fn negatives() {
    check!(r#"nums = [-3, 1, -3]"#, contains_duplicate(&[-3, 1, -3]), true);
}

#[test]
fn zero_and_negative_zero() {
    check!(r#"nums = [0, -0]"#, contains_duplicate(&[0, -0]), true);
}

#[test]
fn extremes_distinct() {
    check!(r#"nums = [i32::MIN, i32::MAX, 0]"#, contains_duplicate(&[i32::MIN, i32::MAX, 0]), false);
}

#[test]
fn extremes_repeated() {
    check!(r#"nums = [i32::MIN, 5, i32::MIN]"#, contains_duplicate(&[i32::MIN, 5, i32::MIN]), true);
}

#[test]
fn far_apart() {
    check!(r#"nums = [1, 2, 3, 4, 5, 6, 7, 1]"#, contains_duplicate(&[1, 2, 3, 4, 5, 6, 7, 1]), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4);
    for _ in 0..300 {
        let n = rng.below(12);
        let nums: Vec<i32> = rng.vec(n, -15, 15);
        let want = (0..n).any(|i| (i + 1..n).any(|j| nums[i] == nums[j]));
        check!(format!("nums = {nums:?}"), contains_duplicate(&nums), want);
    }
}

#[test]
fn scale_200k_last_repeats_first() {
    let mut nums: Vec<i32> = (0..200_000).map(|i| i * 7).collect();
    nums.push(0);
    check!("nums = [0, 7, 14, …, 1399993, 0]", contains_duplicate(&nums), true);
}
