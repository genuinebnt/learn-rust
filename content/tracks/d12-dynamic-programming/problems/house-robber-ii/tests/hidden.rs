use solution::*;

#[test]
fn empty() {
    check!(r#"nums = []"#, rob(&[]), 0);
}

#[test]
fn single() {
    check!(r#"nums = [7]"#, rob(&[7]), 7);
}

#[test]
fn two() {
    check!(r#"nums = [2, 1]"#, rob(&[2, 1]), 2);
}

#[test]
fn zeros() {
    check!(r#"nums = [0, 0, 0]"#, rob(&[0, 0, 0]), 0);
}

#[test]
fn five_equal() {
    check!(r#"nums = [10000; 5]"#, rob(&[10_000; 5]), 20_000);
}

#[test]
fn line_answer_uses_both_ends() {
    check!(r#"nums = [2, 7, 9, 3, 1]"#, rob(&[2, 7, 9, 3, 1]), 11);
}

#[test]
fn skip_two() {
    check!(r#"nums = [2, 1, 1, 2]"#, rob(&[2, 1, 1, 2]), 3);
}

#[test]
fn mixed() {
    check!(r#"nums = [4, 1, 2, 7, 5, 3, 1]"#, rob(&[4, 1, 2, 7, 5, 3, 1]), 14);
}

#[test]
fn past_u32() {
    check!(r#"nums = [10000; 1000000]"#, rob(&vec![10_000; 1_000_000]), 5_000_000_000);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1207);
    for _ in 0..300 {
        let n = rng.below(13);
        let nums: Vec<u32> = rng.vec(n, 0, 30);
        let mut want = 0u64;
        for mask in 0u32..(1 << n) {
            let wraps = n > 1 && mask & 1 == 1 && mask >> (n - 1) & 1 == 1;
            if mask & (mask >> 1) == 0 && !wraps {
                want = want.max((0..n).filter(|&i| mask >> i & 1 == 1).map(|i| nums[i] as u64).sum());
            }
        }
        check!(format!("nums = {nums:?}"), rob(&nums), want);
    }
}

#[test]
fn scale_200k() {
    let mut nums: Vec<u32> = (0..200_000u32).map(|i| (i * 37) % 1000).collect();
    nums[0] = 10_000;
    nums[199_999] = 10_000;
    check!("nums[i] = (37·i) % 1000 with 10000 at both ends, 200000 houses", rob(&nums), 51_676_282);
}
