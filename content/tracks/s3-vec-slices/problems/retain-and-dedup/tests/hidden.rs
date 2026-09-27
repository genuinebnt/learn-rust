use solution::*;

#[test]
fn non_adjacent() {
    check!(r#"v = [2, 1, 2]"#, { let mut v = vec![2, 1, 2]; clean(&mut v); v }, vec![2, 1, 2]);
}

#[test]
fn all_negative() {
    check!(r#"v = [-1, -1]"#, { let mut v = vec![-1, -1]; clean(&mut v); v }, Vec::<i32>::new());
}

#[test]
fn single() {
    check!(r#"v = [5]"#, { let mut v = vec![5]; clean(&mut v); v }, vec![5]);
}

#[test]
fn single_negative() {
    check!(r#"v = [-5]"#, { let mut v = vec![-5]; clean(&mut v); v }, Vec::<i32>::new());
}

#[test]
fn negative_between_equals() {
    check!(r#"v = [5, -1, 5]"#, { let mut v = vec![5, -1, 5]; clean(&mut v); v }, vec![5]);
}

#[test]
fn extremes() {
    check!(r#"v = [i32::MIN, i32::MAX, i32::MAX, i32::MIN]"#, { let mut v = vec![i32::MIN, i32::MAX, i32::MAX, i32::MIN]; clean(&mut v); v }, vec![i32::MAX]);
}

#[test]
fn order_kept() {
    check!(r#"v = [3, 1, 2, 2, 1]"#, { let mut v = vec![3, 1, 2, 2, 1]; clean(&mut v); v }, vec![3, 1, 2, 1]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2302);
    for _ in 0..300 {
        let n = rng.below(12);
        let v: Vec<i32> = rng.vec(n, -2, 2);
        let mut want: Vec<i32> = Vec::new();
        for &x in &v {
            if x >= 0 && want.last() != Some(&x) {
                want.push(x);
            }
        }
        let mut got = v.clone();
        clean(&mut got);
        check!(format!("v = {v:?}"), got, want);
    }
}

#[test]
fn scale_200k() {
    let mut v: Vec<i32> = (0..200_000).map(|i| if i % 2 == 0 { -1 } else { i / 1000 }).collect();
    clean(&mut v);
    check!("v = [-1, 0, -1, 0, …, -1, 199] (200000 values)", (v.len(), v[0], v[199]), (200, 0, 199));
}
