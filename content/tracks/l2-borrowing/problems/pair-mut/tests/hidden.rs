use solution::*;

#[test]
fn out_of_bounds() {
    check!(r#"j = 5"#, pair_mut(&mut [1, 2], 0, 5).is_none(), true);
}

#[test]
fn empty_slice() {
    check!(r#"v = [], i = 0, j = 1"#, pair_mut::<i32>(&mut [], 0, 1).is_none(), true);
}

#[test]
fn both_out_equal() {
    check!(r#"v = [1, 2], i = j = 5"#, pair_mut(&mut [1, 2], 5, 5).is_none(), true);
}

#[test]
fn j_is_len() {
    check!(r#"v = [1, 2, 3], i = 0, j = 3"#, pair_mut(&mut [1, 2, 3], 0, 3).is_none(), true);
}

#[test]
fn strings() {
    check!(r#"v = ["a", "b"], push to both"#, { let mut v = vec!["a".to_string(), "b".to_string()]; if let Some((a, b)) = pair_mut(&mut v, 1, 0) { a.push('1'); b.push('0'); } v }, vec!["a0".to_string(), "b1".to_string()]);
}

#[test]
fn last_and_first() {
    check!(r#"v = 0..10, i = 9, j = 0"#, { let mut v: Vec<i32> = (0..10).collect(); let (a, b) = pair_mut(&mut v, 9, 0).unwrap(); (*a, *b) }, (9, 0));
}

#[test]
fn usize_max() {
    check!(r#"i = usize::MAX"#, pair_mut(&mut [1, 2], usize::MAX, 0).is_none(), true);
}

#[test]
fn writes_land() {
    check!(r#"v = [0, 0, 0], set v[1] = 7, v[2] = 8"#, { let mut v = [0, 0, 0]; let (a, b) = pair_mut(&mut v, 1, 2).unwrap(); *a = 7; *b = 8; v }, [0, 7, 8]);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2023);
    for _ in 0..300 {
        let n = rng.below(6);
        let v0: Vec<i32> = rng.vec(n, 0, 99);
        let i = rng.below(n + 2);
        let j = rng.below(n + 2);
        let mut v = v0.clone();
        let got = pair_mut(&mut v, i, j).map(|(a, b)| {
            let r = (*a, *b);
            *a = -1;
            *b = -2;
            r
        });
        let mut want_v = v0.clone();
        let want = if i != j && i < n && j < n {
            want_v[i] = -1;
            want_v[j] = -2;
            Some((v0[i], v0[j]))
        } else {
            None
        };
        check!(format!("v = {v0:?}, i = {i}, j = {j}"), (got, v), (want, want_v));
    }
}
