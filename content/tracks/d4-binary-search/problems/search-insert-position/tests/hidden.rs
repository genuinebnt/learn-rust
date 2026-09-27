use solution::*;

#[test]
fn after_all() {
    check!(r#"[1,3,5,6], 7"#, insert_position(&[1, 3, 5, 6], 7), 4);
}

#[test]
fn before_all() {
    check!(r#"[1,3,5,6], 0"#, insert_position(&[1, 3, 5, 6], 0), 0);
}

#[test]
fn empty() {
    check!(r#"[], 3"#, insert_position(&[], 3), 0);
}

#[test]
fn single() {
    check!(r#"[1], 0, 1 and 2"#, (insert_position(&[1], 0), insert_position(&[1], 1), insert_position(&[1], 2)), (0, 0, 1));
}

#[test]
fn negatives() {
    check!(r#"[-9,-4,-1], -4 and -5"#, (insert_position(&[-9, -4, -1], -4), insert_position(&[-9, -4, -1], -5)), (1, 1));
}

#[test]
fn extremes() {
    let v = [i32::MIN, i32::MAX];
    check!(r#"[i32::MIN, i32::MAX], i32::MIN, 0 and i32::MAX"#, (insert_position(&v, i32::MIN), insert_position(&v, 0), insert_position(&v, i32::MAX)), (0, 1, 1));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(402);
    for _ in 0..400 {
        let n = rng.below(12);
        let mut nums: Vec<i32> = rng.vec(n, -30, 30);
        nums.sort_unstable();
        nums.dedup();
        let target = rng.int(-32, 32) as i32;
        let want = nums.iter().filter(|&&x| x < target).count();
        check!(format!("nums = {nums:?}, target = {target}"), insert_position(&nums, target), want);
    }
}

#[test]
fn scale_100k_queries() {
    let v: Vec<i32> = (0..100_000).map(|i| i * 2).collect();
    let total: usize = (0..200_000).map(|t| insert_position(&v, t)).sum();
    check!("nums = 0, 2, …, 199998; sum of answers for every target in 0..200000", total, 10_000_000_000usize);
}
