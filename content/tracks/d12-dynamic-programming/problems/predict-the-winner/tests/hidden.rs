use solution::*;

#[test]
fn single_zero() {
    check!(r#"nums = [0]"#, predict_the_winner(&[0]), true);
}

#[test]
fn middle_is_big() {
    check!(r#"nums = [1, 3, 1]"#, predict_the_winner(&[1, 3, 1]), false);
}

#[test]
fn five() {
    check!(r#"nums = [2, 4, 55, 6, 8]"#, predict_the_winner(&[2, 4, 55, 6, 8]), false);
}

#[test]
fn take_the_small_end() {
    check!(r#"nums = [1, 2, 99]"#, predict_the_winner(&[1, 2, 99]), true);
}

#[test]
fn four_greedy_loses() {
    check!(r#"nums = [3, 9, 1, 2]"#, predict_the_winner(&[3, 9, 1, 2]), true);
}

#[test]
fn seven() {
    check!(r#"nums = [0, 0, 7, 6, 5, 6, 1]"#, predict_the_winner(&[0, 0, 7, 6, 5, 6, 1]), false);
}

#[test]
fn twenty() {
    check!(r#"nums = [10, 17, 11, 16, 17, 9, 14, 17, 18, 13, 11, 4, 17, 18, 15, 3, 13, 9, 11, 7]"#, predict_the_winner(&[10, 17, 11, 16, 17, 9, 14, 17, 18, 13, 11, 4, 17, 18, 15, 3, 13, 9, 11, 7]), true);
}

#[test]
fn big_values() {
    check!(r#"nums = [10⁷; 999]"#, predict_the_winner(&[10_000_000; 999]), true);
}

#[test]
fn random_vs_brute_force() {
    fn lead(nums: &[u32]) -> i64 {
        match nums {
            [] => 0,
            [x] => *x as i64,
            [first, .., last] => (*first as i64 - lead(&nums[1..])).max(*last as i64 - lead(&nums[..nums.len() - 1])),
        }
    }
    let mut rng = anneal_prelude::Rng::new(1241);
    for _ in 0..300 {
        let n = rng.below(12);
        let nums: Vec<u32> = rng.vec(n, 0, 20);
        check!(format!("nums = {nums:?}"), predict_the_winner(&nums), lead(&nums) >= 0);
    }
}

#[test]
fn scale_1000() {
    let nums: Vec<u32> = (0..1000u32).map(|i| i * 7919 % 1000).collect();
    check!("nums[i] = (7919·i) % 1000, 1000 numbers", predict_the_winner(&nums), true);
}

#[test]
fn scale_999_loses() {
    let nums: Vec<u32> = (0..999u64).map(|i| (i * 104_729 % 997) as u32).collect();
    check!("nums[i] = (104729·i) % 997, 999 numbers", predict_the_winner(&nums), false);
}
