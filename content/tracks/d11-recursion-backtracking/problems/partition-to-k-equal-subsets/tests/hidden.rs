use solution::*;

#[test]
fn single() {
    check!(r#"nums = [7], k = 1"#, can_partition_k_subsets(&[7], 1), true);
}

#[test]
fn leetcode_fives() {
    check!(r#"nums = [2, 2, 2, 2, 3, 4, 5], k = 4"#, can_partition_k_subsets(&[2, 2, 2, 2, 3, 4, 5], 4), false);
}

#[test]
fn leetcode_thirties() {
    check!(r#"nums = [10, 10, 10, 7, 7, 7, 7, 7, 7, 6, 6, 6], k = 3"#, can_partition_k_subsets(&[10, 10, 10, 7, 7, 7, 7, 7, 7, 6, 6, 6], 3), true);
}

#[test]
fn leetcode_mixed() {
    check!(r#"nums = [4, 15, 1, 1, 1, 1, 3, 11, 1, 10], k = 3"#, can_partition_k_subsets(&[4, 15, 1, 1, 1, 1, 3, 11, 1, 10], 3), true);
}

#[test]
fn leetcode_nine_groups() {
    check!(r#"nums = [3, 2, 1, 3, 6, 1, 4, 8, 10, 8, 9, 1, 7, 9, 8, 1], k = 9"#, can_partition_k_subsets(&[3, 2, 1, 3, 6, 1, 4, 8, 10, 8, 9, 1, 7, 9, 8, 1], 9), false);
}

#[test]
fn first_fit_fails() {
    check!(r#"nums = [6, 4, 6, 2, 5, 3], k = 2 (6+4+3 and 6+5+2)"#, can_partition_k_subsets(&[6, 4, 6, 2, 5, 3], 2), true);
}

#[test]
fn pairs() {
    check!(r#"nums = [1, 1, 1, 1, 2, 2, 2, 2], k = 4"#, can_partition_k_subsets(&[1, 1, 1, 1, 2, 2, 2, 2], 4), true);
}

#[test]
fn twenty_ones() {
    check!(r#"nums = [1; 20], k = 20"#, can_partition_k_subsets(&[1; 20], 20), true);
}

#[test]
fn big_values() {
    check!(r#"nums = [10⁴; 20], k = 5"#, can_partition_k_subsets(&[10_000; 20], 5), true);
}

#[test]
fn not_divisible() {
    check!(r#"nums = [1; 20], k = 3"#, can_partition_k_subsets(&[1; 20], 3), false);
}

/// Every way to give each number one of the k groups.
fn brute(nums: &[u32], k: usize) -> bool {
    (0..k.pow(nums.len() as u32)).any(|mut code| {
        let mut sums = vec![0u32; k];
        for &x in nums {
            sums[code % k] += x;
            code /= k;
        }
        sums.iter().all(|&s| s == sums[0])
    })
}

#[test]
fn random_vs_every_assignment() {
    let mut rng = anneal_prelude::Rng::new(1135);
    for _ in 0..300 {
        let n = rng.int(1, 8) as usize;
        let hi = if rng.bool() { 4 } else { 9 };
        let nums: Vec<u32> = rng.vec(n, 1, hi);
        let k = rng.int(1, n.min(4) as i64) as usize;
        check!(format!("nums = {nums:?}, k = {k}"), can_partition_k_subsets(&nums, k), brute(&nums, k));
    }
}

#[test]
fn scale_repeats_and_parity() {
    // Groups of 9 each need one of the two 1s, and there are four groups.
    let nums = [vec![2; 17], vec![1, 1]].concat();
    check!("nums = [2; 17] + [1, 1], k = 4", can_partition_k_subsets(&nums, 4), false);
}

#[test]
fn scale_twenty_distinct() {
    let nums: Vec<u32> = (1..=20).collect();
    check!("nums = 1..=20, k = 7", can_partition_k_subsets(&nums, 7), true);
}
