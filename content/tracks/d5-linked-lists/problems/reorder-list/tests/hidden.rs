use solution::*;

#[test]
fn short() {
    let mut l = list(&[1, 2]);
    check!(r#"[1,2]"#, { reorder(&mut l); values(&l) }, vec![1, 2]);
}

#[test]
fn empty() {
    let mut l = None;
    check!(r#"[]"#, { reorder(&mut l); l }, None);
}

#[test]
fn long() {
    let mut l = list(&(0..10_000).collect::<Vec<_>>());
    check!(r#"10⁴ nodes: first and last swap in"#, { reorder(&mut l); values(&l)[..4].to_vec() }, vec![0, 9_999, 1, 9_998]);
}

#[test]
fn single() {
    let mut l = list(&[1]);
    check!(r#"[1]"#, { reorder(&mut l); values(&l) }, vec![1]);
}

#[test]
fn six() {
    let mut l = list(&[1, 2, 3, 4, 5, 6]);
    check!(r#"[1..=6]"#, { reorder(&mut l); values(&l) }, vec![1, 6, 2, 5, 3, 4]);
}

#[test]
fn seven() {
    let mut l = list(&[1, 2, 3, 4, 5, 6, 7]);
    check!(r#"[1..=7]"#, { reorder(&mut l); values(&l) }, vec![1, 7, 2, 6, 3, 5, 4]);
}

#[test]
fn duplicates() {
    let mut l = list(&[2, 2, 1, 1]);
    check!(r#"[2,2,1,1]"#, { reorder(&mut l); values(&l) }, vec![2, 1, 2, 1]);
}

#[test]
fn extremes() {
    let mut l = list(&[i32::MIN, 0, i32::MAX]);
    check!(r#"[i32::MIN, 0, i32::MAX]"#, { reorder(&mut l); values(&l) }, vec![i32::MIN, i32::MAX, 0]);
}

/// Drops a long list one node at a time (the default drop recurses once per node).
fn free(mut l: Option<Box<ListNode>>) {
    while let Some(mut n) = l {
        l = n.next.take();
    }
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(507);
    for _ in 0..300 {
        let n = rng.below(12);
        let v: Vec<i32> = rng.vec(n, -9, 9);
        let mut want = Vec::new();
        let (mut i, mut j) = (0, n);
        while i < j {
            want.push(v[i]);
            i += 1;
            if i < j {
                j -= 1;
                want.push(v[j]);
            }
        }
        let mut l = list(&v);
        reorder(&mut l);
        check!(format!("{v:?}"), values(&l), want);
    }
}

#[test]
fn scale_200k() {
    let mut l = list(&(0..200_000).collect::<Vec<i32>>());
    reorder(&mut l);
    let got = values(&l);
    free(l);
    check!("0..200000", (got.len(), got[0], got[1], got[199_998], got[199_999]), (200_000, 0, 199_999, 99_999, 100_000));
}
