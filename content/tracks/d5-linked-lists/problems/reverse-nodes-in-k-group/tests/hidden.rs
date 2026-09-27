use solution::*;

#[test]
fn k1() {
    check!(r#"[1,2,3], k = 1"#, values(&reverse_k_group(list(&[1, 2, 3]), 1)), vec![1, 2, 3]);
}

#[test]
fn k0() {
    check!(r#"[1,2,3], k = 0"#, values(&reverse_k_group(list(&[1, 2, 3]), 0)), vec![1, 2, 3]);
}

#[test]
fn empty() {
    check!(r#"[], k = 2"#, reverse_k_group(None, 2), None);
}

#[test]
fn exact_multiple() {
    check!(r#"[1..=6], k = 2"#, values(&reverse_k_group(list(&[1, 2, 3, 4, 5, 6]), 2)), vec![2, 1, 4, 3, 6, 5]);
}

#[test]
fn short_tail_kept() {
    check!(r#"[1..=8], k = 3"#, values(&reverse_k_group(list(&[1, 2, 3, 4, 5, 6, 7, 8]), 3)), vec![3, 2, 1, 6, 5, 4, 7, 8]);
}

#[test]
fn k_len_minus_one() {
    check!(r#"[1,2,3,4], k = 3"#, values(&reverse_k_group(list(&[1, 2, 3, 4]), 3)), vec![3, 2, 1, 4]);
}

/// Drops a long list one node at a time (the default drop recurses once per node).
fn free(mut l: Option<Box<ListNode>>) {
    while let Some(mut n) = l {
        l = n.next.take();
    }
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(513);
    for _ in 0..300 {
        let n = rng.below(12);
        let v: Vec<i32> = (0..n as i32).collect();
        let k = rng.below(6);
        let mut want = v.clone();
        if k >= 2 {
            for chunk in want.chunks_exact_mut(k) {
                chunk.reverse();
            }
        }
        check!(format!("{v:?}, k = {k}"), values(&reverse_k_group(list(&v), k)), want);
    }
}

#[test]
fn scale_200k_pairs() {
    let l = reverse_k_group(list(&(0..200_000).collect::<Vec<i32>>()), 2);
    let got = values(&l);
    free(l);
    check!("0..200000, k = 2", (got.len(), got[0], got[1], got[199_998], got[199_999]), (200_000, 1, 0, 199_999, 199_998));
}

#[test]
fn whole() {
    check!(r#"[1,2,3], k = 3"#, values(&reverse_k_group(list(&[1, 2, 3]), 3)), vec![3, 2, 1]);
}

#[test]
fn too_long() {
    check!(r#"[1,2], k = 3"#, values(&reverse_k_group(list(&[1, 2]), 3)), vec![1, 2]);
}

#[test]
fn long() {
    check!(r#"10⁴ nodes, k = 100"#, { let v = values(&reverse_k_group(list(&(0..10_000).collect::<Vec<i32>>()), 100)); (v[0], v[99], v[100], v.len()) }, (99, 0, 199, 10_000));
}
