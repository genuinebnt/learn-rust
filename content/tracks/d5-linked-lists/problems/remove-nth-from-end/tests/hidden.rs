use solution::*;

#[test]
fn last() {
    check!(r#"[1,2], n = 1"#, values(&remove_nth_from_end(list(&[1, 2]), 1)), vec![1]);
}

#[test]
fn first() {
    check!(r#"[1,2], n = 2"#, values(&remove_nth_from_end(list(&[1, 2]), 2)), vec![2]);
}

#[test]
fn out_of_range() {
    check!(r#"[1,2], n = 3 and 0"#, (values(&remove_nth_from_end(list(&[1, 2]), 3)), values(&remove_nth_from_end(list(&[1, 2]), 0))), (vec![1, 2], vec![1, 2]));
}

#[test]
fn empty() {
    check!(r#"[], n = 1"#, remove_nth_from_end(None, 1), None);
}

#[test]
fn head_of_long() {
    check!(r#"[1..=5], n = 5"#, values(&remove_nth_from_end(list(&[1, 2, 3, 4, 5]), 5)), vec![2, 3, 4, 5]);
}

#[test]
fn last_of_long() {
    check!(r#"[1..=5], n = 1"#, values(&remove_nth_from_end(list(&[1, 2, 3, 4, 5]), 1)), vec![1, 2, 3, 4]);
}

#[test]
fn huge_n() {
    check!(r#"[1,2,3], n = usize::MAX"#, values(&remove_nth_from_end(list(&[1, 2, 3]), usize::MAX)), vec![1, 2, 3]);
}

#[test]
fn duplicates() {
    check!(r#"[7,7,7], n = 2"#, values(&remove_nth_from_end(list(&[7, 7, 7]), 2)), vec![7, 7]);
}

/// Drops a long list one node at a time (the default drop recurses once per node).
fn free(mut l: Option<Box<ListNode>>) {
    while let Some(mut n) = l {
        l = n.next.take();
    }
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(506);
    for _ in 0..300 {
        let len = rng.below(8);
        let v: Vec<i32> = (0..len as i32).collect();
        let n = rng.below(10);
        let mut want = v.clone();
        if n >= 1 && n <= len {
            want.remove(len - n);
        }
        check!(format!("{v:?}, n = {n}"), values(&remove_nth_from_end(list(&v), n)), want);
    }
}

#[test]
fn scale_200k() {
    let v: Vec<i32> = (0..200_000).collect();
    let l = remove_nth_from_end(list(&v), 1);
    let got = values(&l);
    free(l);
    check!("0..200000, n = 1", (got.len(), got[199_998]), (199_999, 199_998));
}
