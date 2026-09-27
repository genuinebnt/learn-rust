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
fn two_pick_larger() {
    check!(r#"nums = [2, 1]"#, rob(&[2, 1]), 2);
}

#[test]
fn gap_of_two() {
    check!(r#"nums = [5, 1, 1, 5]"#, rob(&[5, 1, 1, 5]), 10);
}

#[test]
fn zeros() {
    check!(r#"nums = [0, 0, 0]"#, rob(&[0, 0, 0]), 0);
}

#[test]
fn middle_wins() {
    check!(r#"nums = [1, 3, 1]"#, rob(&[1, 3, 1]), 3);
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
    let mut rng = anneal_prelude::Rng::new(1206);
    for _ in 0..300 {
        let n = rng.below(13);
        let nums: Vec<u32> = rng.vec(n, 0, 30);
        let mut want = 0u64;
        for mask in 0u32..(1 << n) {
            if mask & (mask >> 1) == 0 {
                want = want.max((0..n).filter(|&i| mask >> i & 1 == 1).map(|i| nums[i] as u64).sum());
            }
        }
        check!(format!("nums = {nums:?}"), rob(&nums), want);
    }
}

#[test]
fn scale_200k() {
    let nums: Vec<u32> = (0..200_000u32).map(|i| (i * 37) % 1000).collect();
    check!("nums[i] = (37·i) % 1000, 200000 houses", rob(&nums), 51_666_800);
}
