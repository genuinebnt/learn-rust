use solution::*;

#[test]
fn insert_front_and_back() {
    check!(r#"v = [5], x = 1 then 9"#, { let mut v = vec![5]; insert_sorted(&mut v, 1); insert_sorted(&mut v, 9); v }, vec![1, 5, 9]);
}

#[test]
fn empty_range() {
    check!(r#"v = [1, 2, 3], lo = 5, hi = 1"#, count_in_range(&[1, 2, 3], 5, 1), 0);
}

#[test]
fn insert_into_empty() {
    check!(r#"v = [], x = 4"#, { let mut v = vec![]; insert_sorted(&mut v, 4); v }, vec![4]);
}

#[test]
fn count_on_empty() {
    check!(r#"v = [], lo = 0, hi = 9"#, count_in_range(&[], 0, 9), 0);
}

#[test]
fn lo_equals_hi() {
    check!(r#"v = [1, 2, 2, 3], lo = 2, hi = 2"#, count_in_range(&[1, 2, 2, 3], 2, 2), 2);
}

#[test]
fn negatives() {
    check!(r#"v = [-5, -3, 0], lo = -4, hi = 0"#, count_in_range(&[-5, -3, 0], -4, 0), 2);
}

#[test]
fn extremes() {
    check!(r#"v = [i32::MIN, 0, i32::MAX], lo = i32::MIN, hi = i32::MAX"#, count_in_range(&[i32::MIN, 0, i32::MAX], i32::MIN, i32::MAX), 3);
}

#[test]
fn insert_extremes() {
    check!(r#"v = [0], x = i32::MAX then i32::MIN"#, { let mut v = vec![0]; insert_sorted(&mut v, i32::MAX); insert_sorted(&mut v, i32::MIN); v }, vec![i32::MIN, 0, i32::MAX]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2314);
    for _ in 0..300 {
        let n = rng.below(10);
        let mut v: Vec<i32> = rng.vec(n, -5, 5);
        v.sort();
        let x = rng.int(-6, 6) as i32;
        let (lo, hi) = (rng.int(-6, 6) as i32, rng.int(-6, 6) as i32);
        let want_count = v.iter().filter(|&&y| lo <= y && y <= hi).count();
        let mut want_v = v.clone();
        want_v.push(x);
        want_v.sort();
        let mut got_v = v.clone();
        insert_sorted(&mut got_v, x);
        check!(format!("v = {v:?}, x = {x}, lo = {lo}, hi = {hi}"), (got_v, count_in_range(&v, lo, hi)), (want_v, want_count));
    }
}

#[test]
fn scale_200k_queries() {
    let v: Vec<i32> = (0..200_000).map(|i| i * 2).collect();
    let total: usize = (0..200_000).map(|q| count_in_range(&v, q, q + 10)).sum();
    check!("v = [0, 2, 4, …, 399998], 200000 queries lo = q, hi = q + 10", total, 1_100_000);
}
