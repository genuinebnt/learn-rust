use solution::*;

#[test]
fn big() {
    check!(r#"v = 0..1000"#, { let mut v: Vec<i32> = (0..1000).collect(); double_up(&mut v); (v.len(), v[1000], v[1999]) }, (2000, 0, 999));
}

#[test]
fn negatives() {
    check!(r#"v = [-1, -2]"#, { let mut v = vec![-1, -2]; double_up(&mut v); v }, vec![-1, -2, -1, -2]);
}

#[test]
fn extremes() {
    check!(r#"v = [i32::MIN, i32::MAX]"#, { let mut v = vec![i32::MIN, i32::MAX]; double_up(&mut v); v }, vec![i32::MIN, i32::MAX, i32::MIN, i32::MAX]);
}

#[test]
fn twice() {
    check!(r#"v = [1, 2], double_up twice"#, { let mut v = vec![1, 2]; double_up(&mut v); double_up(&mut v); v }, vec![1, 2, 1, 2, 1, 2, 1, 2]);
}

#[test]
fn order_kept() {
    check!(r#"v = [3, 1, 2]"#, { let mut v = vec![3, 1, 2]; double_up(&mut v); v }, vec![3, 1, 2, 3, 1, 2]);
}

#[test]
fn single_zero() {
    check!(r#"v = [0]"#, { let mut v = vec![0]; double_up(&mut v); v }, vec![0, 0]);
}

#[test]
fn first_half_untouched() {
    check!(r#"v = [9, 8, 7, 6]"#, { let mut v = vec![9, 8, 7, 6]; double_up(&mut v); v[..4].to_vec() }, vec![9, 8, 7, 6]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2312);
    for _ in 0..300 {
        let n = rng.below(10);
        let v: Vec<i32> = rng.vec(n, -9, 9);
        let want = [&v[..], &v[..]].concat();
        let mut got = v.clone();
        double_up(&mut got);
        check!(format!("v = {v:?}"), got, want);
    }
}

#[test]
fn scale_200k() {
    let mut v: Vec<i32> = (0..200_000).collect();
    double_up(&mut v);
    check!("v = 0..200000", (v.len(), v[199_999], v[200_000], v[399_999]), (400_000, 199_999, 0, 199_999));
}
