use solution::*;

#[test]
fn out_of_reach() {
    check!(r#"nums = [1, 2], target = 4"#, find_target_sum_ways(&[1, 2], 4), 0);
}

#[test]
fn out_of_reach_below() {
    check!(r#"nums = [1], target = -2"#, find_target_sum_ways(&[1], -2), 0);
}

#[test]
fn wrong_parity() {
    check!(r#"nums = [1, 1], target = 1"#, find_target_sum_ways(&[1, 1], 1), 0);
}

#[test]
fn one_zero() {
    check!(r#"nums = [1, 0], target = 1"#, find_target_sum_ways(&[1, 0], 1), 2);
}

#[test]
fn balanced() {
    check!(r#"nums = [2, 3, 5], target = 0"#, find_target_sum_ways(&[2, 3, 5], 0), 2);
}

#[test]
fn small_mixed() {
    check!(r#"nums = [1, 2, 1], target = 0"#, find_target_sum_ways(&[1, 2, 1], 0), 2);
}

#[test]
fn forty_ones() {
    check!(r#"nums = [1; 40], target = 0"#, find_target_sum_ways(&[1; 40], 0), 137_846_528_820);
}

#[test]
fn sixty_zeros() {
    check!(r#"nums = [0; 60], target = 0"#, find_target_sum_ways(&[0; 60], 0), 1 << 60);
}

#[test]
fn far_target() {
    check!(r#"nums = [1000], target = -1000"#, find_target_sum_ways(&[1000], -1000), 1);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1232);
    for _ in 0..300 {
        let n = rng.below(12);
        let nums: Vec<u32> = rng.vec(n, 0, 5);
        let target = rng.int(-12, 12) as i32;
        let want = (0u32..(1 << n))
            .filter(|mask| (0..n).map(|i| if mask >> i & 1 == 1 { nums[i] as i32 } else { -(nums[i] as i32) }).sum::<i32>() == target)
            .count() as u64;
        check!(format!("nums = {nums:?}, target = {target}"), find_target_sum_ways(&nums, target), want);
    }
}

#[test]
fn scale_sixty() {
    // 2⁶⁰ sign choices for plain recursion.
    let nums: Vec<u32> = (0..60u32).map(|i| i * 7919 % 16 + 1).collect();
    check!("nums[i] = (7919·i) % 16 + 1, 60 numbers, target = 10", find_target_sum_ways(&nums, 10), 11_765_817_607_280_003);
}
