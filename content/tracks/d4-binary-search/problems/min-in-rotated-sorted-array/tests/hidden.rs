use solution::*;

#[test]
fn not_rotated() {
    check!(r#"[11,13,15,17]"#, find_min(&[11, 13, 15, 17]), Some(11));
}

#[test]
fn single() {
    check!(r#"[1]"#, find_min(&[1]), Some(1));
}

#[test]
fn empty() {
    check!(r#"[]"#, find_min(&[]), None);
}

#[test]
fn two() {
    check!(r#"[2,1]"#, find_min(&[2, 1]), Some(1));
}

#[test]
fn extremes() {
    check!(r#"[i32::MAX, i32::MIN, 0]"#, find_min(&[i32::MAX, i32::MIN, 0]), Some(i32::MIN));
}

#[test]
fn negatives() {
    check!(r#"[-1,-10,-7,-4]"#, find_min(&[-1, -10, -7, -4]), Some(-10));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(406);
    for _ in 0..400 {
        let n = rng.below(12);
        let mut nums: Vec<i32> = rng.vec(n, -50, 50);
        nums.sort_unstable();
        nums.dedup();
        let k = if nums.is_empty() { 0 } else { rng.below(nums.len()) };
        nums.rotate_left(k);
        check!(format!("nums = {nums:?}"), find_min(&nums), nums.iter().copied().min());
    }
}

#[test]
fn scale_every_rotation() {
    // Every rotation of 0..100000, as a window into the doubled slice.
    let n = 100_000;
    let doubled: Vec<i32> = (0..2 * n).map(|i| (i % n) as i32).collect();
    let bad = (0..n).filter(|&k| find_min(&doubled[k..k + n]) != Some(0)).count();
    check!("all 100000 rotations of 0..100000: how many give a minimum other than 0", bad, 0);
}
