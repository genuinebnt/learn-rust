use solution::*;

#[test]
fn single() {
    let l = list(&[9]);
    check!(r#"[9]"#, middle(&l).map(|n| n.val), Some(9));
}

#[test]
fn empty() {
    check!(r#"[]"#, middle(&None).is_none(), true);
}

#[test]
fn two() {
    let l = list(&[1, 2]);
    check!(r#"[1,2]"#, middle(&l).map(|n| n.val), Some(2));
}

#[test]
fn three() {
    let l = list(&[1, 2, 3]);
    check!(r#"[1,2,3]"#, middle(&l).map(|n| n.val), Some(2));
}

#[test]
fn four() {
    let l = list(&[1, 2, 3, 4]);
    check!(r#"[1,2,3,4]"#, middle(&l).map(|n| n.val), Some(3));
}

#[test]
fn rest_is_attached() {
    let l = list(&[1, 2, 3, 4, 5]);
    check!(r#"[1,2,3,4,5]: values from the middle on"#, values(&middle(&l).unwrap().next), vec![4, 5]);
}

#[test]
fn same_node() {
    let l = list(&[5, 5, 5, 5]);
    check!(r#"[5,5,5,5]: the middle is the third node itself"#, std::ptr::eq(middle(&l).unwrap(), l.as_ref().unwrap().next.as_ref().unwrap().next.as_deref().unwrap()), true);
}

#[test]
fn long_even() {
    let l = list(&(0..10_000).collect::<Vec<i32>>());
    check!(r#"10⁴ nodes"#, middle(&l).map(|n| n.val), Some(5_000));
}

/// Drops a long list one node at a time (the default drop recurses once per node).
fn free(mut l: Option<Box<ListNode>>) {
    while let Some(mut n) = l {
        l = n.next.take();
    }
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(504);
    for _ in 0..300 {
        let n = rng.below(12);
        let v: Vec<i32> = rng.vec(n, -9, 9);
        let l = list(&v);
        check!(format!("{v:?}"), middle(&l).map(|m| values(&Some(Box::new(m.clone())))), (n > 0).then(|| v[n / 2..].to_vec()));
    }
}

#[test]
fn scale_200k() {
    let l = list(&(0..200_000).collect::<Vec<i32>>());
    let got = middle(&l).map(|n| n.val);
    free(l);
    check!("0..200000", got, Some(100_000));
}
