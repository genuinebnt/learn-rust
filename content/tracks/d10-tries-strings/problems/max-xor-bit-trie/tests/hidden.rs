use solution::*;

#[test]
fn zero_and_max() {
    check!(r#"nums = [0, u32::MAX]"#, find_maximum_xor(&[0, u32::MAX]), u32::MAX);
}

#[test]
fn adjacent_maxes() {
    check!(r#"nums = [u32::MAX, u32::MAX - 1]"#, find_maximum_xor(&[u32::MAX, u32::MAX - 1]), 1);
}

#[test]
fn powers_of_two() {
    check!(r#"nums = [1, 2, 4, 8]"#, find_maximum_xor(&[1, 2, 4, 8]), 12);
}

#[test]
fn all_zero() {
    check!(r#"nums = [0, 0, 0]"#, find_maximum_xor(&[0, 0, 0]), 0);
}

#[test]
fn duplicates() {
    check!(r#"nums = [5, 5]"#, find_maximum_xor(&[5, 5]), 0);
}

#[test]
fn both_sides_of_the_top_bit() {
    check!(r#"nums = [2³¹, 2³¹ - 1]"#, find_maximum_xor(&[1 << 31, (1 << 31) - 1]), u32::MAX);
}

#[test]
fn large_values() {
    check!(r#"nums = [3000000000, 1500000000, 123]"#, find_maximum_xor(&[3_000_000_000, 1_500_000_000, 123]), 3954733312);
}

#[test]
fn two_numbers() {
    check!(r#"nums = [10, 5]"#, find_maximum_xor(&[10, 5]), 15);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1020);
    for _ in 0..400 {
        let n = rng.below(10);
        let nums: Vec<u32> = if rng.bool() { rng.vec(n, 0, 15) } else { rng.vec(n, 0, u32::MAX as i64) };
        let mut want = 0;
        for i in 0..nums.len() {
            for j in i + 1..nums.len() {
                want = want.max(nums[i] ^ nums[j]);
            }
        }
        check!(format!("nums = {nums:?}"), find_maximum_xor(&nums), want);
    }
}

#[test]
fn scale_131k() {
    // 0..2¹⁷ in shuffled order, then 2³¹: the best pair is 2³¹ with 2¹⁷ − 1, found only at the very end.
    let mut nums: Vec<u32> = (0..1u32 << 17).map(|i| i.wrapping_mul(40_503) % (1 << 17)).collect();
    nums.push(1 << 31);
    check!("nums = 0..131072 shuffled, then 2147483648", find_maximum_xor(&nums), (1 << 31) | ((1 << 17) - 1));
}
