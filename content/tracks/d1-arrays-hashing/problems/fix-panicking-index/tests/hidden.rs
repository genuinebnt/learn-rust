use solution::*;

#[test]
fn empty() {
    check!(r#"v = [], i = 0"#, nth_or_zero(&[], 0), 0);
}

#[test]
fn huge_index() {
    check!(r#"v = [1], i = usize::MAX"#, nth_or_zero(&[1], usize::MAX), 0);
}

#[test]
fn first() {
    check!(r#"v = [4, 5, 6], i = 0"#, nth_or_zero(&[4, 5, 6], 0), 4);
}

#[test]
fn last() {
    check!(r#"v = [4, 5, 6], i = 2"#, nth_or_zero(&[4, 5, 6], 2), 6);
}

#[test]
fn negative_value() {
    check!(r#"v = [-9, 3], i = 0"#, nth_or_zero(&[-9, 3], 0), -9);
}

#[test]
fn empty_huge_index() {
    check!(r#"v = [], i = usize::MAX"#, nth_or_zero(&[], usize::MAX), 0);
}

#[test]
fn far_past_the_end() {
    check!(r#"v = [1, 2], i = 100"#, nth_or_zero(&[1, 2], 100), 0);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6);
    for _ in 0..300 {
        let n = rng.below(6);
        let v: Vec<i32> = rng.vec(n, -9, 9);
        let i = rng.below(8);
        let want = if i < v.len() { v[i] } else { 0 };
        check!(format!("v = {v:?}, i = {i}"), nth_or_zero(&v, i), want);
    }
}
