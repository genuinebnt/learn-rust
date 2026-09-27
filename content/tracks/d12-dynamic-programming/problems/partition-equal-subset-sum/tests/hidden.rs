use solution::*;

#[test]
fn empty() {
    check!(r#"nums = []"#, can_partition(&[]), true);
}

#[test]
fn odd_total() {
    check!(r#"nums = [1, 2, 4]"#, can_partition(&[1, 2, 4]), false);
}

#[test]
fn each_number_once() {
    check!(r#"nums = [2, 2, 3, 5]"#, can_partition(&[2, 2, 3, 5]), false);
}

#[test]
fn max_pair() {
    check!(r#"nums = [100, 100]"#, can_partition(&[100, 100]), true);
}

#[test]
fn five_numbers() {
    check!(r#"nums = [3, 3, 3, 4, 5]"#, can_partition(&[3, 3, 3, 4, 5]), true);
}

#[test]
fn one_to_seven() {
    check!(r#"nums = [1, 2, 3, 4, 5, 6, 7]"#, can_partition(&[1, 2, 3, 4, 5, 6, 7]), true);
}

#[test]
fn one_big() {
    check!(r#"nums = [1, 1, 1, 100]"#, can_partition(&[1, 1, 1, 100]), false);
}

#[test]
fn two_hundred() {
    check!(r#"nums[i] = (7919·i) % 100 + 1, 200 numbers"#, can_partition(&(0..200u32).map(|i| i * 7919 % 100 + 1).collect::<Vec<_>>()), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1231);
    for _ in 0..300 {
        let n = rng.below(13);
        let nums: Vec<u32> = rng.vec(n, 1, 12);
        let total: u32 = nums.iter().sum();
        let want = (0u32..(1 << n)).any(|mask| 2 * (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| nums[i]).sum::<u32>() == total);
        check!(format!("nums = {nums:?}"), can_partition(&nums), want);
    }
}

#[test]
fn scale_all_twos() {
    // Half of 202 is 101, which no set of 2s can hit; plain recursion tries every subset.
    check!("nums = [2; 101]", can_partition(&vec![2; 101]), false);
}
