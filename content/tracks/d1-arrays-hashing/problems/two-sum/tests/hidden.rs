use solution::*;

#[test]
fn negatives() {
    check!(r#"nums = [-3, 4, 3, 90], target = 0"#, two_sum(&[-3, 4, 3, 90], 0), Some((0, 2)));
}

#[test]
fn large_input() {
    check!(r#"nums = 0..10000, target = 19997"#, two_sum(&(0..10_000).collect::<Vec<i32>>(), 19_997), Some((9998, 9999)));
}

#[test]
fn zeros() {
    check!(r#"nums = [0, 4, 3, 0], target = 0"#, two_sum(&[0, 4, 3, 0], 0), Some((0, 3)));
}

#[test]
fn ends() {
    check!(r#"nums = [5, 1, 2, 7], target = 12"#, two_sum(&[5, 1, 2, 7], 12), Some((0, 3)));
}

#[test]
fn negative_target() {
    check!(r#"nums = [-1, -2, -3, -4, -5], target = -8"#, two_sum(&[-1, -2, -3, -4, -5], -8), Some((2, 4)));
}

#[test]
fn bounds() {
    check!(r#"nums = [1000000000, -1000000000, 7], target = -999999993"#, two_sum(&[1_000_000_000, -1_000_000_000, 7], -999_999_993), Some((1, 2)));
}

#[test]
fn far_apart_bounds() {
    check!(r#"nums = [-1000000000, 3, -1000000000], target = -2000000000"#, two_sum(&[-1_000_000_000, 3, -1_000_000_000], -2_000_000_000), Some((0, 2)));
}

#[test]
fn half_target_once() {
    check!(r#"nums = [3, 2, 4], target = 6 (3 must not pair with itself)"#, two_sum(&[3, 2, 4], 6), Some((1, 2)));
}

#[test]
fn two_elements_no_pair() {
    check!(r#"nums = [1, 1], target = 3"#, two_sum(&[1, 1], 3), None);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(3);
    let mut tried = 0;
    while tried < 300 {
        let n = 2 + rng.below(10);
        let nums: Vec<i32> = rng.vec(n, -20, 20);
        let target = rng.int(-40, 40) as i32;
        let pairs: Vec<(usize, usize)> = (0..n).flat_map(|i| (i + 1..n).map(move |j| (i, j))).filter(|&(i, j)| nums[i] + nums[j] == target).collect();
        // The problem promises at most one pair.
        if pairs.len() > 1 {
            continue;
        }
        tried += 1;
        check!(format!("nums = {nums:?}, target = {target}"), two_sum(&nums, target), pairs.first().copied());
    }
}

#[test]
fn scale_100k() {
    let nums: Vec<i32> = (0..100_000).collect();
    check!("nums = 0..100000, target = 199997", two_sum(&nums, 199_997), Some((99_998, 99_999)));
}
