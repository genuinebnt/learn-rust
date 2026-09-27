use solution::*;

#[test]
fn left_part() {
    check!(r#"[4,5,6,7,0,1,2], 5"#, search_rotated(&[4, 5, 6, 7, 0, 1, 2], 5), Some(1));
}

#[test]
fn single_miss() {
    check!(r#"[1], 0"#, search_rotated(&[1], 0), None);
}

#[test]
fn empty() {
    check!(r#"[], 1"#, search_rotated(&[], 1), None);
}

#[test]
fn not_rotated() {
    check!(r#"[1,3,5], 5"#, search_rotated(&[1, 3, 5], 5), Some(2));
}

#[test]
fn target_equals_last() {
    check!(r#"[4,5,6,7,0,1,2], 2"#, search_rotated(&[4, 5, 6, 7, 0, 1, 2], 2), Some(6));
}

#[test]
fn target_equals_first() {
    check!(r#"[4,5,6,7,0,1,2], 4"#, search_rotated(&[4, 5, 6, 7, 0, 1, 2], 4), Some(0));
}

#[test]
fn extremes() {
    let v = [i32::MAX, i32::MIN, 0];
    check!(r#"[i32::MAX, i32::MIN, 0], each value"#, (search_rotated(&v, i32::MAX), search_rotated(&v, i32::MIN), search_rotated(&v, 0)), (Some(0), Some(1), Some(2)));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(407);
    for _ in 0..400 {
        let n = rng.below(12);
        let mut nums: Vec<i32> = rng.vec(n, -30, 30);
        nums.sort_unstable();
        nums.dedup();
        let k = if nums.is_empty() { 0 } else { rng.below(nums.len()) };
        nums.rotate_left(k);
        let target = rng.int(-32, 32) as i32;
        check!(format!("nums = {nums:?}, target = {target}"), search_rotated(&nums, target), nums.iter().position(|&x| x == target));
    }
}

#[test]
fn scale_every_rotation() {
    let n = 100_000;
    let doubled: Vec<i32> = (0..2 * n).map(|i| (i % n) as i32).collect();
    // In rotation k, value v sits at (v - k) mod n.
    let bad = (0..n).filter(|&k| { let t = ((k * 7 + 3) % n) as i32; search_rotated(&doubled[k..k + n], t) != Some((t as usize + n - k) % n) }).count();
    check!("all 100000 rotations of 0..100000, one lookup each: how many are wrong", bad, 0);
}
