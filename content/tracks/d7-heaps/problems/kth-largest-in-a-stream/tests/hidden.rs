use solution::*;

#[test]
fn empty_start_k_one() {
    let mut s = KthLargest::new(1, &[]);
    check!(r#"k = 1, nums = []; add -4, -9"#, [-4, -9].map(|v| s.add(v)), [Some(-4), Some(-4)]);
}

#[test]
fn small_value_changes_nothing() {
    let mut s = KthLargest::new(2, &[10, 20, 30]);
    check!(r#"k = 2, nums = [10, 20, 30]; add 1, 1, 1"#, [1, 1, 1].map(|v| s.add(v)), [Some(20), Some(20), Some(20)]);
}

#[test]
fn one_short_of_k() {
    let mut s = KthLargest::new(3, &[1]);
    check!(r#"k = 3, nums = [1]; add 2, 3"#, [2, 3].map(|v| s.add(v)), [None, Some(1)]);
}

#[test]
fn extremes() {
    let mut s = KthLargest::new(2, &[i32::MAX, i32::MIN]);
    check!(r#"k = 2, nums = [i32::MAX, i32::MIN]; add i32::MIN, i32::MAX"#, [i32::MIN, i32::MAX].map(|v| s.add(v)), [Some(i32::MIN), Some(i32::MAX)]);
}

#[test]
fn all_equal() {
    let mut s = KthLargest::new(3, &[4, 4, 4, 4]);
    check!(r#"k = 3, nums = [4, 4, 4, 4]; add 4, 5"#, [4, 5].map(|v| s.add(v)), [Some(4), Some(4)]);
}

#[test]
fn each_new_maximum() {
    let mut s = KthLargest::new(2, &[1, 2]);
    check!(r#"k = 2, nums = [1, 2]; add 3, 4, 5"#, [3, 4, 5].map(|v| s.add(v)), [Some(2), Some(3), Some(4)]);
}

#[test]
fn k_larger_than_everything() {
    let mut s = KthLargest::new(5, &[9, 8]);
    check!(r#"k = 5, nums = [9, 8]; add 7, 6, 5, 4"#, [7, 6, 5, 4].map(|v| s.add(v)), [None, None, Some(5), Some(5)]);
}

#[test]
fn two_streams_are_independent() {
    let mut a = KthLargest::new(1, &[1]);
    let mut b = KthLargest::new(1, &[100]);
    check!(r#"a: k = 1, nums = [1]; b: k = 1, nums = [100]; a.add(2), b.add(3)"#, (a.add(2), b.add(3)), (Some(2), Some(100)));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(701);
    for _ in 0..300 {
        let k = 1 + rng.below(5);
        let n = rng.below(8);
        let nums: Vec<i32> = rng.vec(n, -10, 10);
        let adds_len = rng.below(10);
        let adds: Vec<i32> = rng.vec(adds_len, -10, 10);
        let mut s = KthLargest::new(k, &nums);
        let mut seen = nums.clone();
        let mut got = Vec::new();
        let mut want = Vec::new();
        for &v in &adds {
            got.push(s.add(v));
            seen.push(v);
            let mut sorted = seen.clone();
            sorted.sort_unstable_by(|a, b| b.cmp(a));
            want.push(sorted.get(k - 1).copied());
        }
        check!(format!("k = {k}, nums = {nums:?}; add {adds:?}"), got, want);
    }
}

#[test]
fn scale_100k_adds() {
    let mut rng = anneal_prelude::Rng::new(702);
    let mut nums: Vec<i32> = (0..100_000).collect();
    rng.shuffle(&mut nums);
    let mut s = KthLargest::new(50_000, &nums);
    // Even steps add a new maximum, odd steps a value far below the k-th largest.
    let mut first_wrong = None;
    for i in 0..100_000 {
        let v = if i % 2 == 0 { 100_000 + i / 2 } else { -1 - i };
        if s.add(v) != Some(50_001 + i / 2) && first_wrong.is_none() {
            first_wrong = Some(i);
        }
    }
    check!("k = 50000, nums = 0..100000 shuffled; add 100000, -2, 100001, -4, … (100000 adds); first add with a wrong answer", first_wrong, None);
}
