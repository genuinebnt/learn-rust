use solution::*;

#[test]
fn empty() {
    check!(r#"v = []"#, push_sum(vec![]), vec![0]);
}

#[test]
fn same_buffer() {
    check!(r#"v with capacity 10"#, { let mut v = Vec::with_capacity(10); v.push(5); let p = v.as_ptr(); let out = push_sum(v); out.as_ptr() == p }, true);
}

#[test]
fn single() {
    check!(r#"v = [7]"#, push_sum(vec![7]), vec![7, 7]);
}

#[test]
fn negatives() {
    check!(r#"v = [-5, 2]"#, push_sum(vec![-5, 2]), vec![-5, 2, -3]);
}

#[test]
fn cancels_out() {
    check!(r#"v = [5, -5]"#, push_sum(vec![5, -5]), vec![5, -5, 0]);
}

#[test]
fn beyond_i32() {
    check!(r#"v = [3000000000, 3000000000]"#, push_sum(vec![3_000_000_000, 3_000_000_000]), vec![3_000_000_000, 3_000_000_000, 6_000_000_000]);
}

#[test]
fn near_i64_max() {
    check!(r#"v = [i64::MAX / 2, i64::MAX / 2]"#, push_sum(vec![i64::MAX / 2, i64::MAX / 2]), vec![i64::MAX / 2, i64::MAX / 2, i64::MAX - 1]);
}

#[test]
fn swap_unicode() {
    check!(r#"a = "ünï", b = "日本""#, swap_owned("ünï".into(), "日本".into()), ("日本".to_string(), "ünï".to_string()));
}

#[test]
fn swap_same_buffers() {
    check!(r#"a and b keep their heap buffers"#, { let (a, b) = (String::from("left"), String::from("right")); let (pa, pb) = (a.as_ptr(), b.as_ptr()); let (x, y) = swap_owned(a, b); (x.as_ptr() == pb, y.as_ptr() == pa) }, (true, true));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1104);
    for _ in 0..300 {
        let n = rng.below(20);
        let v: Vec<i64> = rng.vec(n, -1_000_000_000_000, 1_000_000_000_000);
        let mut want = v.clone();
        want.push(v.iter().sum());
        check!(format!("v = {v:?}"), push_sum(v.clone()), want);
    }
}

#[test]
fn long_vec() {
    let v: Vec<i64> = (1..=200_000).collect();
    let out = push_sum(v);
    check!("v = 1..=200000", (out.len(), out[199_999], out[200_000]), (200_001, 200_000, 20_000_100_000));
}
