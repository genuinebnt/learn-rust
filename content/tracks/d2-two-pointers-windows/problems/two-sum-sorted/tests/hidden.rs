use solution::*;

#[test]
fn empty() {
    check!(r#"nums = [], target = 0"#, two_sum_sorted(&[], 0), None);
}

#[test]
fn extremes() {
    check!(r#"nums = [i32::MIN, 0, i32::MAX], target = -1"#, two_sum_sorted(&[i32::MIN, 0, i32::MAX], -1), Some((0, 2)));
}

#[test]
fn single() {
    check!(r#"nums = [5], target = 10"#, two_sum_sorted(&[5], 10), None);
}

#[test]
fn no_self_pair() {
    check!(r#"nums = [3, 4], target = 6"#, two_sum_sorted(&[3, 4], 6), None);
}

#[test]
fn equal_values() {
    check!(r#"nums = [1, 3, 3, 8], target = 6"#, two_sum_sorted(&[1, 3, 3, 8], 6), Some((1, 2)));
}

#[test]
fn negatives() {
    check!(r#"nums = [-8, -5, -3, 1, 7], target = -8"#, two_sum_sorted(&[-8, -5, -3, 1, 7], -8), Some((1, 2)));
}

#[test]
fn last_two() {
    check!(r#"nums = [1, 2, 3, 4, 5], target = 9"#, two_sum_sorted(&[1, 2, 3, 4, 5], 9), Some((3, 4)));
}

#[test]
fn sum_past_i32_max() {
    check!(r#"nums = [1, i32::MAX], target = i32::MIN"#, two_sum_sorted(&[1, i32::MAX], i32::MIN), None);
}

#[test]
fn sum_below_i32_min() {
    check!(r#"nums = [i32::MIN, -1, 5], target = 4"#, two_sum_sorted(&[i32::MIN, -1, 5], 4), Some((1, 2)));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(206);
    let mut tried = 0;
    while tried < 300 {
        let n = rng.below(10);
        let mut nums: Vec<i32> = rng.vec(n, -20, 20);
        nums.sort();
        let target = rng.int(-40, 40) as i32;
        let pairs: Vec<(usize, usize)> = (0..n).flat_map(|i| (i + 1..n).map(move |j| (i, j))).filter(|&(i, j)| nums[i] + nums[j] == target).collect();
        // Keep inputs with at most one answer, so any correct method agrees.
        if pairs.len() > 1 {
            continue;
        }
        tried += 1;
        check!(format!("nums = {nums:?}, target = {target}"), two_sum_sorted(&nums, target), pairs.first().copied());
    }
}

#[test]
fn scale_200k() {
    let nums: Vec<i32> = (0..200_000).collect();
    check!("nums = 0..200000, target = 399997 / -1", (two_sum_sorted(&nums, 399_997), two_sum_sorted(&nums, -1)), (Some((199_998, 199_999)), None));
}
