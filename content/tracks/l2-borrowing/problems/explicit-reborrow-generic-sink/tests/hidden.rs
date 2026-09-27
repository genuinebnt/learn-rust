use solution::*;

#[test]
fn negatives() {
    check!(r#"xs = [-1, i32::MIN]"#, { let mut v = vec![]; emit_twice(&mut v, &[-1, i32::MIN]); v }, vec![-1, i32::MIN, -1, i32::MIN]);
}

#[test]
fn duplicates() {
    check!(r#"xs = [2, 2]"#, { let mut v = vec![]; emit_twice(&mut v, &[2, 2]); v }, vec![2, 2, 2, 2]);
}

#[test]
fn existing_kept() {
    check!(r#"sink = [9, 9], xs = [1]"#, { let mut v = vec![9, 9]; emit_twice(&mut v, &[1]); v }, vec![9, 9, 1, 1]);
}

#[test]
fn large() {
    check!(r#"xs = 0..10000"#, { let xs: Vec<i32> = (0..10_000).collect(); let mut v = vec![]; emit_twice(&mut v, &xs); (v.len(), v[9_999], v[10_000]) }, (20_000, 9_999, 0));
}

#[test]
fn max() {
    check!(r#"xs = [i32::MAX]"#, { let mut v = vec![]; emit_twice(&mut v, &[i32::MAX]); v }, vec![i32::MAX, i32::MAX]);
}

#[test]
fn called_twice() {
    check!(r#"xs = [4], twice"#, { let mut v = vec![]; emit_twice(&mut v, &[4]); emit_twice(&mut v, &[4]); v }, vec![4, 4, 4, 4]);
}

#[test]
fn two_distinct() {
    check!(r#"xs = [1, 2]"#, { let mut v = vec![0]; emit_twice(&mut v, &[1, 2]); v }, vec![0, 1, 2, 1, 2]);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2015);
    for _ in 0..300 {
        let n0 = rng.below(4);
        let start: Vec<i32> = rng.vec(n0, -9, 9);
        let n = rng.below(6);
        let xs: Vec<i32> = rng.vec(n, -100, 100);
        let mut v = start.clone();
        emit_twice(&mut v, &xs);
        let want: Vec<i32> = start.iter().chain(&xs).chain(&xs).copied().collect();
        check!(format!("sink = {start:?}, xs = {xs:?}"), v, want);
    }
}
