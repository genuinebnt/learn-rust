use solution::*;

#[test]
fn single() {
    check!(r#"v = [5]"#, is_mirror(&[5]), true);
}

#[test]
fn even() {
    check!(r#"v = [3, 4, 4, 3]"#, is_mirror(&[3, 4, 4, 3]), true);
}

#[test]
fn two_equal() {
    check!(r#"v = [7, 7]"#, is_mirror(&[7, 7]), true);
}

#[test]
fn middle_differs() {
    check!(r#"v = [1, 2, 3, 1]"#, is_mirror(&[1, 2, 3, 1]), false);
}

#[test]
fn ends_differ() {
    check!(r#"v = [1, 5, 5, 2]"#, is_mirror(&[1, 5, 5, 2]), false);
}

#[test]
fn negatives() {
    check!(r#"v = [-1, 0, -1]"#, is_mirror(&[-1, 0, -1]), true);
}

#[test]
fn extremes() {
    check!(r#"v = [i32::MIN, i32::MAX, i32::MIN]"#, is_mirror(&[i32::MIN, i32::MAX, i32::MIN]), true);
}

#[test]
fn extremes_swapped() {
    check!(r#"v = [i32::MIN, i32::MAX]"#, is_mirror(&[i32::MIN, i32::MAX]), false);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(205);
    for _ in 0..300 {
        let n = rng.below(8);
        let mut v: Vec<i32> = rng.vec(n, -2, 2);
        if rng.bool() {
            for i in 0..n / 2 {
                v[n - 1 - i] = v[i];
            }
        }
        let want = v.iter().eq(v.iter().rev());
        check!(format!("v = {v:?}"), is_mirror(&v), want);
    }
}

#[test]
fn scale_200k() {
    let v: Vec<i32> = (0..200_000).map(|i: i32| (i.min(199_999 - i)) % 1000).collect();
    let mut w = v.clone();
    w[100_000] = -1;
    check!("v = a 200000-value mirror, and the same with one middle value changed", (is_mirror(&v), is_mirror(&w)), (true, false));
}
