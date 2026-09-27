use solution::*;

#[test]
fn hit() {
    check!(r#"nums = [1, 1, 1, 0], target = 3"#, three_sum_closest(&[1, 1, 1, 0], 3), 3);
}

#[test]
fn negative_target() {
    check!(r#"nums = [4, 0, 5, -5, 3, 3, 0, -4, -5], target = -2"#, three_sum_closest(&[4, 0, 5, -5, 3, 3, 0, -4, -5], -2), -2);
}

#[test]
fn exactly_three() {
    check!(r#"nums = [1, 2, 3], target = 100"#, three_sum_closest(&[1, 2, 3], 100), 6);
}

#[test]
fn all_negative() {
    check!(r#"nums = [-5, -4, -3, -2], target = -100"#, three_sum_closest(&[-5, -4, -3, -2], -100), -12);
}

#[test]
fn far_value_unused() {
    check!(r#"nums = [-1, 0, 1, 1, 55], target = 3"#, three_sum_closest(&[-1, 0, 1, 1, 55], 3), 2);
}

#[test]
fn needs_the_big_value() {
    check!(r#"nums = [1, 6, 9, 14, 16, 70], target = 81"#, three_sum_closest(&[1, 6, 9, 14, 16, 70], 81), 80);
}

#[test]
fn duplicates() {
    check!(r#"nums = [-1000, -5, -5, -5, -5, -5, -5, -1, -1, -1], target = -14"#, three_sum_closest(&[-1000, -5, -5, -5, -5, -5, -5, -1, -1, -1], -14), -15);
}

#[test]
fn bounds() {
    check!(r#"nums = [10000, 10000, 10000, -10000], target = 100000"#, three_sum_closest(&[10_000, 10_000, 10_000, -10_000], 100_000), 30000);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(210);
    let mut tried = 0;
    while tried < 300 {
        let n = 3 + rng.below(8);
        let nums: Vec<i32> = rng.vec(n, -20, 20);
        let target = rng.int(-70, 70) as i32;
        let mut sums = Vec::new();
        for i in 0..n {
            for j in i + 1..n {
                for k in j + 1..n {
                    sums.push(nums[i] + nums[j] + nums[k]);
                }
            }
        }
        let d = sums.iter().map(|s| s.abs_diff(target)).min().unwrap();
        let mut closest: Vec<i32> = sums.into_iter().filter(|s| s.abs_diff(target) == d).collect();
        closest.dedup();
        closest.sort();
        closest.dedup();
        // The problem promises exactly one closest sum.
        if closest.len() > 1 {
            continue;
        }
        tried += 1;
        check!(format!("nums = {nums:?}, target = {target}"), three_sum_closest(&nums, target), closest[0]);
    }
}

#[test]
fn scale_5000() {
    let nums: Vec<i32> = (0..5000).map(|i| (i * 7919 % 20_001) - 10_000).collect();
    let mut top = nums.clone();
    top.sort();
    let want: i32 = top[4997..].iter().sum();
    check!("nums[i] = i * 7919 % 20001 - 10000 for i in 0..5000, target = 100000", three_sum_closest(&nums, 100_000), want);
}
