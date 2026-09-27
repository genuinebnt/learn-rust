use solution::*;

#[test]
fn empty() {
    check!(r#"[]"#, reverse(None), None);
}

#[test]
fn long() {
    let v: Vec<i32> = (0..10_000).collect();
    check!(r#"10⁴ nodes"#, values(&reverse(list(&v))) == v.iter().rev().copied().collect::<Vec<_>>(), true);
}

#[test]
fn single() {
    check!(r#"[7]"#, values(&reverse(list(&[7]))), vec![7]);
}

#[test]
fn three() {
    check!(r#"[1,2,3]"#, values(&reverse(list(&[1, 2, 3]))), vec![3, 2, 1]);
}

#[test]
fn extremes() {
    check!(r#"[i32::MIN, 0, i32::MAX]"#, values(&reverse(list(&[i32::MIN, 0, i32::MAX]))), vec![i32::MAX, 0, i32::MIN]);
}

#[test]
fn all_same() {
    check!(r#"[4,4,4]"#, values(&reverse(list(&[4, 4, 4]))), vec![4, 4, 4]);
}

#[test]
fn twice_is_identity() {
    check!(r#"[3,1,2] reversed twice"#, values(&reverse(reverse(list(&[3, 1, 2])))), vec![3, 1, 2]);
}

#[test]
fn negatives() {
    check!(r#"[-1,-2,-3,-4]"#, values(&reverse(list(&[-1, -2, -3, -4]))), vec![-4, -3, -2, -1]);
}

/// Drops a long list one node at a time (the default drop recurses once per node).
fn free(mut l: Option<Box<ListNode>>) {
    while let Some(mut n) = l {
        l = n.next.take();
    }
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(501);
    for _ in 0..300 {
        let n = rng.below(12);
        let v: Vec<i32> = rng.vec(n, -9, 9);
        let want: Vec<i32> = v.iter().rev().copied().collect();
        check!(format!("{v:?}"), values(&reverse(list(&v))), want);
    }
}

#[test]
fn scale_100k() {
    let v: Vec<i32> = (0..100_000).collect();
    let r = reverse(list(&v));
    let got = values(&r);
    free(r);
    check!("0..100000", (got.len(), got[0], got[99_999]), (100_000, 99_999, 0));
}
