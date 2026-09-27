use solution::*;

#[test]
fn empty() {
    check!(r#"nums = []"#, delete_and_earn(&[]), 0);
}

#[test]
fn single() {
    check!(r#"nums = [5]"#, delete_and_earn(&[5]), 5);
}

#[test]
fn run() {
    check!(r#"nums = [1, 2, 3]"#, delete_and_earn(&[1, 2, 3]), 4);
}

#[test]
fn largest_values() {
    check!(r#"nums = [100000, 99999]"#, delete_and_earn(&[100_000, 99_999]), 100_000);
}

#[test]
fn unsorted_repeats() {
    check!(r#"nums = [3, 3, 3, 4, 2]"#, delete_and_earn(&[3, 3, 3, 4, 2]), 9);
}

#[test]
fn mixed_ten() {
    check!(r#"nums = [8, 10, 4, 9, 1, 3, 5, 9, 4, 10]"#, delete_and_earn(&[8, 10, 4, 9, 1, 3, 5, 9, 4, 10]), 37);
}

#[test]
fn mixed_ten_again() {
    check!(r#"nums = [1, 6, 3, 3, 8, 4, 8, 10, 1, 3]"#, delete_and_earn(&[1, 6, 3, 3, 8, 4, 8, 10, 1, 3]), 43);
}

#[test]
fn past_u32() {
    check!(r#"nums = [100000; 200000]"#, delete_and_earn(&vec![100_000; 200_000]), 20_000_000_000);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1209);
    for _ in 0..300 {
        let n = rng.below(12);
        let nums: Vec<u32> = rng.vec(n, 1, 9);
        let mut want = 0u64;
        // Choose a set of values with no two consecutive; take every copy of each.
        for mask in 0u32..(1 << 10) {
            if mask & (mask >> 1) == 0 {
                let earned = nums.iter().filter(|&&x| mask >> x & 1 == 1).map(|&x| x as u64).sum();
                want = want.max(earned);
            }
        }
        check!(format!("nums = {nums:?}"), delete_and_earn(&nums), want);
    }
}

#[test]
fn scale_200k() {
    let nums: Vec<u32> = (0..200_000u64).map(|i| (i * 7919 % 100_000 + 1) as u32).collect();
    check!("nums[i] = (7919·i) % 100000 + 1, 200000 values", delete_and_earn(&nums), 5_000_100_000);
}
