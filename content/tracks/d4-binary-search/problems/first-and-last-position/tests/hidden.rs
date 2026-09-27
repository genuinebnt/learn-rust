use solution::*;

#[test]
fn empty() {
    check!(r#"[], 0"#, search_range(&[], 0), None);
}

#[test]
fn outside_both_ends() {
    check!(r#"[2,3,3], 1 and 4"#, (search_range(&[2, 3, 3], 1), search_range(&[2, 3, 3], 4)), (None, None));
}

#[test]
fn negatives() {
    check!(r#"[-5,-5,-3,0], -5"#, search_range(&[-5, -5, -3, 0], -5), Some((0, 1)));
}

#[test]
fn extremes() {
    let v = [i32::MIN, i32::MIN, i32::MAX];
    check!(r#"[i32::MIN, i32::MIN, i32::MAX], i32::MIN and i32::MAX"#, (search_range(&v, i32::MIN), search_range(&v, i32::MAX)), (Some((0, 1)), Some((2, 2))));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(405);
    for _ in 0..400 {
        let n = rng.below(14);
        let mut nums: Vec<i32> = rng.vec(n, -5, 5);
        nums.sort_unstable();
        let target = rng.int(-6, 6) as i32;
        let first = nums.iter().position(|&x| x == target);
        let last = nums.iter().rposition(|&x| x == target);
        let want = first.zip(last);
        check!(format!("nums = {nums:?}, target = {target}"), search_range(&nums, target), want);
    }
}

#[test]
fn scale_long_runs() {
    // Four runs of 500000; 200000 lookups. Walking outward from a hit costs a whole run each time.
    let v: Vec<i32> = (0..2_000_000).map(|i| i / 500_000).collect();
    let total: usize = (0..200_000).map(|q| search_range(&v, q % 4).map_or(0, |(a, b)| b - a + 1)).sum();
    check!("nums = 500000 × 0, 1, 2, 3; 200000 lookups", total, 100_000_000_000usize);
}

#[test]
fn all_same() {
    check!(r#"[2,2,2], 2"#, search_range(&[2, 2, 2], 2), Some((0, 2)));
}

#[test]
fn big_run() {
    let mut v = vec![0; 10];
    v.extend(std::iter::repeat(1).take(1_000_000));
    v.extend([2, 2]);
    check!(r#"10⁶ copies of 1 between 0s and 2s"#, search_range(&v, 1), Some((10, 1_000_009)));
}
