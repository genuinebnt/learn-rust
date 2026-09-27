use solution::*;

#[test]
fn tail_past_end() {
    check!(r#"v = [1], at = 5"#, { let mut v = vec![1]; let t = take_tail(&mut v, 5); (v, t) }, (vec![1], vec![]));
}

#[test]
fn splice_insert() {
    check!(r#"v = [1, 4], replace 1..1 with [2, 3]"#, { let mut v = vec![1, 4]; let r = replace_range(&mut v, 1, 1, &[2, 3]); (v, r) }, (vec![1, 2, 3, 4], vec![]));
}

#[test]
fn tail_of_empty() {
    check!(r#"v = [], at = 0"#, { let mut v: Vec<i32> = vec![]; let t = take_tail(&mut v, 0); (v, t) }, (vec![], vec![]));
}

#[test]
fn tail_huge_at() {
    check!(r#"v = [1, 2], at = usize::MAX"#, { let mut v = vec![1, 2]; let t = take_tail(&mut v, usize::MAX); (v, t) }, (vec![1, 2], vec![]));
}

#[test]
fn splice_whole() {
    check!(r#"v = [1, 2, 3], replace 0..3 with [7]"#, { let mut v = vec![1, 2, 3]; let r = replace_range(&mut v, 0, 3, &[7]); (v, r) }, (vec![7], vec![1, 2, 3]));
}

#[test]
fn splice_longer() {
    check!(r#"v = [1, 2], replace 0..1 with [5, 6, 7]"#, { let mut v = vec![1, 2]; let r = replace_range(&mut v, 0, 1, &[5, 6, 7]); (v, r) }, (vec![5, 6, 7, 2], vec![1]));
}

#[test]
fn splice_at_end() {
    check!(r#"v = [1], replace 1..1 with [2]"#, { let mut v = vec![1]; let r = replace_range(&mut v, 1, 1, &[2]); (v, r) }, (vec![1, 2], vec![]));
}

#[test]
fn splice_empty_vec() {
    check!(r#"v = [], replace 0..0 with [1, 2]"#, { let mut v = vec![]; let r = replace_range(&mut v, 0, 0, &[1, 2]); (v, r) }, (vec![1, 2], vec![]));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2309);
    for _ in 0..300 {
        let n = rng.below(8);
        let v: Vec<i32> = rng.vec(n, 0, 9);
        let at = rng.below(10);
        let start = rng.below(n + 1);
        let end = start + rng.below(n - start + 1);
        let wl = rng.below(4);
        let with: Vec<i32> = rng.vec(wl, 10, 19);
        let cut = at.min(n);
        let want_tail = (v[..cut].to_vec(), v[cut..].to_vec());
        let want_splice = ([&v[..start], &with[..], &v[end..]].concat(), v[start..end].to_vec());
        let (mut a, mut b) = (v.clone(), v.clone());
        let t = take_tail(&mut a, at);
        let r = replace_range(&mut b, start, end, &with);
        check!(format!("v = {v:?}, at = {at}, replace {start}..{end} with {with:?}"), ((a, t), (b, r)), (want_tail, want_splice));
    }
}

#[test]
fn scale_200k() {
    let mut v: Vec<i32> = (0..200_000).collect();
    let r = replace_range(&mut v, 1, 199_999, &[-1]);
    let t = take_tail(&mut v, 1);
    check!("v = 0..200000, replace 1..199999 with [-1], then take_tail(1)", (v, t, r.len()), (vec![0], vec![-1, 199_999], 199_998));
}
