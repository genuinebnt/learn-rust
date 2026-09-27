use solution::*;

#[test]
fn long_existing() {
    check!(r#"v = [5, 5, 5], n = 1"#, { let mut v = vec![5, 5, 5]; push_lengths(&mut v, 1); v }, vec![5, 5, 5, 3]);
}

#[test]
fn thousand() {
    check!(r#"v = [], n = 1000"#, { let mut v = vec![]; push_lengths(&mut v, 1000); (v.len(), v[999]) }, (1000, 999));
}

#[test]
fn called_twice() {
    check!(r#"n = 2, then n = 2"#, { let mut v = vec![]; push_lengths(&mut v, 2); push_lengths(&mut v, 2); v }, vec![0, 1, 2, 3]);
}

#[test]
fn from_ten() {
    check!(r#"v = [0; 10], n = 3"#, { let mut v = vec![0; 10]; push_lengths(&mut v, 3); v[10..].to_vec() }, vec![10, 11, 12]);
}

#[test]
fn values_equal_index() {
    check!(r#"v = [], n = 50"#, { let mut v = vec![]; push_lengths(&mut v, 50); v.iter().enumerate().all(|(i, &x)| i == x) }, true);
}

#[test]
fn large() {
    check!(r#"v = [], n = 200000"#, { let mut v = vec![]; push_lengths(&mut v, 200_000); (v.len(), v[199_999]) }, (200_000, 199_999));
}

#[test]
fn big_values_kept() {
    check!(r#"v = [usize::MAX], n = 1"#, { let mut v = vec![usize::MAX]; push_lengths(&mut v, 1); v }, vec![usize::MAX, 1]);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2013);
    for _ in 0..300 {
        let n0 = rng.below(5);
        let start: Vec<usize> = rng.vec(n0, 0, 9);
        let n = rng.below(6);
        let mut v = start.clone();
        push_lengths(&mut v, n);
        let mut want = start.clone();
        for _ in 0..n {
            want.push(want.len());
        }
        check!(format!("v = {start:?}, n = {n}"), v, want);
    }
}
