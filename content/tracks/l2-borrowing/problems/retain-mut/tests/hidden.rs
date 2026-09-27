use solution::*;

#[test]
fn no_zeros() {
    check!(r#"[8, 6]"#, { let mut v = vec![8, 6]; drop_zeros_and_halve(&mut v); v }, vec![4, 3]);
}

#[test]
fn odd() {
    check!(r#"[7]"#, { let mut v = vec![7]; drop_zeros_and_halve(&mut v); v }, vec![3]);
}

#[test]
fn i32_min() {
    check!(r#"[i32::MIN]"#, { let mut v = vec![i32::MIN]; drop_zeros_and_halve(&mut v); v }, vec![-1_073_741_824]);
}

#[test]
fn i32_max() {
    check!(r#"[i32::MAX]"#, { let mut v = vec![i32::MAX]; drop_zeros_and_halve(&mut v); v }, vec![1_073_741_823]);
}

#[test]
fn minus_one() {
    check!(r#"[-1]"#, { let mut v = vec![-1]; drop_zeros_and_halve(&mut v); v }, vec![0]);
}

#[test]
fn zeros_between() {
    check!(r#"[0, 2, 0, 0, 4, 0]"#, { let mut v = vec![0, 2, 0, 0, 4, 0]; drop_zeros_and_halve(&mut v); v }, vec![1, 2]);
}

#[test]
fn single_zero() {
    check!(r#"[0]"#, { let mut v = vec![0]; drop_zeros_and_halve(&mut v); v }, Vec::<i32>::new());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2017);
    for _ in 0..300 {
        let n = rng.below(10);
        let v: Vec<i32> = rng.vec(n, -5, 5);
        let want: Vec<i32> = v.iter().filter(|&&x| x != 0).map(|&x| x / 2).collect();
        let mut got = v.clone();
        drop_zeros_and_halve(&mut got);
        check!(format!("v = {v:?}"), got, want);
    }
}

#[test]
fn scale_800k_zeros_first() {
    let mut v = vec![0; 400_000];
    v.resize(800_000, 6);
    drop_zeros_and_halve(&mut v);
    check!("400000 zeros then 400000 sixes", (v.len(), v[0], v[399_999]), (400_000, 3, 3));
}
