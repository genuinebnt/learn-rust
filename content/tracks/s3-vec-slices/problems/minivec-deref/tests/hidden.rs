use solution::*;

#[test]
fn empty_slice() {
    check!(r#"new MiniVec"#, MiniVec::<String>::new().as_slice().len(), 0);
}

#[test]
fn range_index() {
    check!(r#"push 10, 20, 30"#, { let mut v = MiniVec::new(); v.push(10); v.push(20); v.push(30); v[1..].to_vec() }, vec![20, 30]);
}

#[test]
fn mutate_through_slice() {
    check!(r#"push 1, 2"#, { let mut v = MiniVec::new(); v.push(1); v.push(2); for x in v.iter_mut() { *x *= 5; } v.as_slice().to_vec() }, vec![5, 10]);
}

#[test]
fn empty_mut_slice() {
    check!(r#"new MiniVec"#, MiniVec::<u8>::new().as_mut_slice().len(), 0);
}

#[test]
fn contains_and_search() {
    check!(r#"push 1, 3, 5"#, { let mut v = MiniVec::new(); for x in [1, 3, 5] { v.push(x); } (v.contains(&3), v.contains(&4), v.binary_search(&5)) }, (true, false, Ok(2)));
}

#[test]
fn first_last() {
    check!(r#"push "a", "b", "c""#, { let mut v = MiniVec::new(); for s in ["a", "b", "c"] { v.push(s.to_string()); } (v.first().cloned(), v.last().cloned()) }, (Some("a".to_string()), Some("c".to_string())));
}

#[test]
fn reverse() {
    check!(r#"push 1, 2, 3, then reverse"#, { let mut v = MiniVec::new(); for x in 1..=3 { v.push(x); } v.reverse(); v.to_vec() }, vec![3, 2, 1]);
}

#[test]
fn windows_through_deref() {
    check!(r#"push 1, 2, 3"#, { let mut v = MiniVec::new(); for x in 1..=3 { v.push(x); } v.windows(2).map(|w| w[0] + w[1]).collect::<Vec<_>>() }, vec![3, 5]);
}

#[test]
fn after_pop() {
    check!(r#"push 1, 2, 3, pop"#, { let mut v = MiniVec::new(); for x in 1..=3 { v.push(x); } v.pop(); v.to_vec() }, vec![1, 2]);
}

#[test]
fn random_vs_vec() {
    let mut rng = anneal_prelude::Rng::new(2316);
    for _ in 0..200 {
        let n = rng.below(20);
        let values: Vec<i32> = rng.vec(n, -50, 50);
        let mut v = MiniVec::new();
        for &x in &values {
            v.push(x);
        }
        let mut want = values.clone();
        want.sort();
        v.sort();
        check!(format!("push {values:?}, then sort"), (v.to_vec(), v.len()), (want, n));
    }
}

#[test]
fn scale_200k_sort() {
    let mut v = MiniVec::new();
    for i in 0..200_000u32 {
        v.push(i.wrapping_mul(2_654_435_761));
    }
    v.sort_unstable();
    check!("200000 values, sorted through DerefMut", (v.len(), v.windows(2).all(|w| w[0] <= w[1])), (200_000, true));
}
