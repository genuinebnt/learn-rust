use solution::*;

#[test]
fn empty() {
    check!(r#"v = []"#, dedup_sorted(&mut []), 0);
}

#[test]
fn all_distinct() {
    check!(r#"v = [-3, 0, 7]"#, { let mut v = [-3, 0, 7]; let k = dedup_sorted(&mut v); v[..k].to_vec() }, vec![-3, 0, 7]);
}

#[test]
fn all_same() {
    check!(r#"v = [3, 3, 3, 3, 3]"#, { let mut v = [3; 5]; let k = dedup_sorted(&mut v); (k, v[..k].to_vec()) }, (1, vec![3]));
}

#[test]
fn negatives() {
    check!(r#"v = [-2, -2, -1]"#, { let mut v = [-2, -2, -1]; let k = dedup_sorted(&mut v); (k, v[..k].to_vec()) }, (2, vec![-2, -1]));
}

#[test]
fn extremes() {
    check!(r#"v = [i32::MIN, i32::MIN, i32::MAX]"#, { let mut v = [i32::MIN, i32::MIN, i32::MAX]; let k = dedup_sorted(&mut v); (k, v[..k].to_vec()) }, (2, vec![i32::MIN, i32::MAX]));
}

#[test]
fn run_at_end() {
    check!(r#"v = [1, 2, 2, 2]"#, { let mut v = [1, 2, 2, 2]; let k = dedup_sorted(&mut v); (k, v[..k].to_vec()) }, (2, vec![1, 2]));
}

#[test]
fn two_equal() {
    check!(r#"v = [4, 4]"#, { let mut v = [4, 4]; let k = dedup_sorted(&mut v); (k, v[..k].to_vec()) }, (1, vec![4]));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2307);
    for _ in 0..300 {
        let n = rng.below(12);
        let mut v: Vec<i32> = rng.vec(n, -3, 3);
        v.sort();
        let mut want = v.clone();
        want.dedup();
        let mut got = v.clone();
        let k = dedup_sorted(&mut got);
        check!(format!("v = {v:?}"), (k, got[..k].to_vec()), (want.len(), want));
    }
}

#[test]
fn scale_200k() {
    let mut v: Vec<i32> = (0..200_000).map(|i| i / 2).collect();
    v.extend(vec![100_000; 100_000]);
    let k = dedup_sorted(&mut v);
    check!("v = [0, 0, 1, 1, …, 99999, 99999] then 100000 × 100000", (k, v[k - 1]), (100_001, 100_000));
}
