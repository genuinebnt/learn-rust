use solution::*;

#[test]
fn empty() {
    check!(r#"v = [], x = 1"#, find(&[], 1), None);
}

#[test]
fn first() {
    check!(r#"v = [-1, -1], x = -1"#, find(&[-1, -1], -1), Some(0));
}

#[test]
fn last() {
    check!(r#"v = [1, 2, 3], x = 3"#, find(&[1, 2, 3], 3), Some(2));
}

#[test]
fn extremes() {
    check!(r#"v = [i32::MIN, i32::MAX], x = i32::MAX"#, find(&[i32::MIN, i32::MAX], i32::MAX), Some(1));
}

#[test]
fn single_missing() {
    check!(r#"v = [0], x = 1"#, find(&[0], 1), None);
}

#[test]
fn duplicates_give_the_first() {
    check!(r#"v = [2, 5, 5, 5], x = 5"#, find(&[2, 5, 5, 5], 5), Some(1));
}

#[test]
fn minus_one_absent() {
    check!(r#"v = [0, 1], x = -1"#, find(&[0, 1], -1), None);
}

#[test]
fn large_index() {
    let v: Vec<i32> = (0..1_000_000).collect();
    check!(r#"v = 0..10⁶, x = 999999"#, find(&v, 999_999), Some(999_999));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1303);
    for _ in 0..400 {
        let n = rng.below(8);
        let v: Vec<i32> = rng.vec(n, -3, 3);
        let x = rng.int(-4, 4) as i32;
        check!(format!("v = {v:?}, x = {x}"), find(&v, x), v.iter().position(|&y| y == x));
    }
}
