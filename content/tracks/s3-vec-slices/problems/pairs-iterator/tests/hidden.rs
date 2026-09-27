use solution::*;

#[test]
fn len() {
    check!(r#"v = [0; 7]"#, pairs(&[0; 7]).len(), 3);
}

#[test]
fn empty() {
    check!(r#"v = []"#, pairs::<u8>(&[]).next(), None);
}

#[test]
fn len_after_next() {
    check!(r#"v = [0; 7], one next()"#, { let mut it = pairs(&[0; 7]); it.next(); it.len() }, 2);
}

#[test]
fn size_hint_exact() {
    check!(r#"v = [0; 6]"#, pairs(&[0; 6]).size_hint(), (3, Some(3)));
}

#[test]
fn two() {
    check!(r#"v = [8, 9]"#, pairs(&[8, 9]).map(|(a, b)| (*a, *b)).collect::<Vec<_>>(), vec![(8, 9)]);
}

#[test]
fn strings() {
    check!(r#"v = ["a", "b", "c", "d", "e"]"#, pairs(&["a", "b", "c", "d", "e"]).map(|(a, b)| format!("{a}{b}")).collect::<Vec<_>>(), vec!["ab", "cd"]);
}

#[test]
fn next_after_end() {
    check!(r#"v = [1, 2]"#, { let mut it = pairs(&[1, 2]); it.next(); (it.next(), it.next(), it.len()) }, (None, None, 0));
}

#[test]
fn refs_point_into_v() {
    let v = [1, 2];
    check!(r#"v = [1, 2]"#, { let (a, b) = pairs(&v).next().unwrap(); (std::ptr::eq(a, &v[0]), std::ptr::eq(b, &v[1])) }, (true, true));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2319);
    for _ in 0..300 {
        let n = rng.below(10);
        let v: Vec<i32> = rng.vec(n, -9, 9);
        let want: Vec<(i32, i32)> = (0..n / 2).map(|i| (v[2 * i], v[2 * i + 1])).collect();
        let it = pairs(&v);
        let len = it.len();
        check!(format!("v = {v:?}"), (len, it.map(|(a, b)| (*a, *b)).collect::<Vec<_>>()), (n / 2, want));
    }
}

#[test]
fn scale_200k() {
    let v: Vec<u32> = (0..200_001).collect();
    let sum: u64 = pairs(&v).map(|(a, b)| (*a + *b) as u64).sum();
    check!("v = 0..200001", (pairs(&v).len(), sum), (100_000, 19_999_900_000));
}
