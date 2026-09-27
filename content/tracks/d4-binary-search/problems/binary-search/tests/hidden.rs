use solution::*;

#[test]
fn empty() {
    check!(r#"[], 1"#, search(&[], 1), None);
}

#[test]
fn ends() {
    check!(r#"[1,2,3], 1 and 3"#, (search(&[1, 2, 3], 1), search(&[1, 2, 3], 3)), (Some(0), Some(2)));
}

#[test]
fn below_all() {
    check!(r#"[5], 1"#, search(&[5], 1), None);
}

#[test]
fn million() {
    let v: Vec<i32> = (0..1_000_000).map(|i| i * 2).collect();
    check!(r#"0..10⁶ evens, 777_778"#, search(&v, 777_778), Some(388_889));
}

#[test]
fn extremes() {
    let v = [i32::MIN, 0, i32::MAX];
    check!(r#"[i32::MIN, 0, i32::MAX], each value"#, (search(&v, i32::MIN), search(&v, 0), search(&v, i32::MAX)), (Some(0), Some(1), Some(2)));
}

#[test]
fn two_elements() {
    check!(r#"[4,8], 4, 8 and 6"#, (search(&[4, 8], 4), search(&[4, 8], 8), search(&[4, 8], 6)), (Some(0), Some(1), None));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(401);
    for _ in 0..400 {
        let n = rng.below(12);
        let mut nums: Vec<i32> = rng.vec(n, -30, 30);
        nums.sort_unstable();
        nums.dedup();
        let target = rng.int(-32, 32) as i32;
        let want = nums.iter().position(|&x| x == target);
        check!(format!("nums = {nums:?}, target = {target}"), search(&nums, target), want);
    }
}

#[test]
fn scale_100k_queries() {
    let v: Vec<i32> = (0..100_000).map(|i| i * 3).collect();
    let hits = (0..300_000).filter(|&t| search(&v, t).is_some_and(|i| v[i] == t)).count();
    check!("nums = 0, 3, …, 299997; every target in 0..300000", hits, 100_000);
}
