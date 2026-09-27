use solution::*;

#[test]
fn all_same() {
    check!(r#"[7,7,7,7]"#, values(&dedup_sorted(list(&[7, 7, 7, 7]))), vec![7]);
}

#[test]
fn empty() {
    check!(r#"[]"#, dedup_sorted(None), None);
}

#[test]
fn long() {
    let v: Vec<i32> = (0..10_000).map(|i| i / 2).collect();
    check!(r#"10⁴ values, each twice"#, values(&dedup_sorted(list(&v))).len(), 5_000);
}

#[test]
fn single() {
    check!(r#"[3]"#, values(&dedup_sorted(list(&[3]))), vec![3]);
}

#[test]
fn dup_at_end() {
    check!(r#"[1,2,2]"#, values(&dedup_sorted(list(&[1, 2, 2]))), vec![1, 2]);
}

#[test]
fn negatives() {
    check!(r#"[-3,-3,-1,0,0]"#, values(&dedup_sorted(list(&[-3, -3, -1, 0, 0]))), vec![-3, -1, 0]);
}

#[test]
fn extremes() {
    check!(r#"[MIN,MIN,MAX,MAX]"#, values(&dedup_sorted(list(&[i32::MIN, i32::MIN, i32::MAX, i32::MAX]))), vec![i32::MIN, i32::MAX]);
}

#[test]
fn runs_of_three() {
    check!(r#"[1,1,1,2,2,2,3]"#, values(&dedup_sorted(list(&[1, 1, 1, 2, 2, 2, 3]))), vec![1, 2, 3]);
}

/// Drops a long list one node at a time (the default drop recurses once per node).
fn free(mut l: Option<Box<ListNode>>) {
    while let Some(mut n) = l {
        l = n.next.take();
    }
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(503);
    for _ in 0..300 {
        let n = rng.below(12);
        let mut v: Vec<i32> = rng.vec(n, -4, 4);
        v.sort();
        let mut want = v.clone();
        want.dedup();
        check!(format!("{v:?}"), values(&dedup_sorted(list(&v))), want);
    }
}

#[test]
fn scale_200k() {
    let v: Vec<i32> = (0..200_000).collect();
    let l = dedup_sorted(list(&v));
    let got = values(&l);
    free(l);
    check!("0..200000 (no duplicates)", got == v, true);
}
