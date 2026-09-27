use solution::*;

#[test]
fn long_words_none() {
    check!(r#"long_words("a b", 5)"#, long_words("a b", 5).count(), 0);
}

#[test]
fn long_words_strict() {
    check!(r#"long_words("abcd abcde", 4)"#, long_words("abcd abcde", 4).collect::<Vec<_>>(), vec!["abcde".to_string()]);
}

#[test]
fn long_words_whitespace() {
    check!(r#"long_words("\tlong\nwords  ", 0)"#, long_words("\tlong\nwords  ", 0).collect::<Vec<_>>(), vec!["long".to_string(), "words".to_string()]);
}

#[test]
fn pairs_empty() {
    check!(r#"pairs([], [1])"#, pairs(&[], &[1]).count(), 0);
}

#[test]
fn pairs_first_shorter() {
    check!(r#"pairs([1], [2, 3])"#, pairs(&[1], &[2, 3]).collect::<Vec<_>>(), vec![(1, 2)]);
}

#[test]
fn snapshot_empty() {
    check!(r#"sorted_snapshot([])"#, sorted_snapshot(&vec![]).count(), 0);
}

#[test]
fn snapshot_duplicates() {
    check!(r#"sorted_snapshot([2, 2, 1])"#, sorted_snapshot(&vec![2, 2, 1]).collect::<Vec<_>>(), vec![1, 2, 2]);
}

#[test]
fn snapshot_outlives_v() {
    check!(r#"snapshot, then drop v"#, { let s = { let v = vec![9u32, 8]; sorted_snapshot(&v) }; s.collect::<Vec<_>>() }, vec![8, 9]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6305);
    for _ in 0..300 {
        let (n, m) = (rng.below(6), rng.below(6));
        let a: Vec<u32> = rng.vec(n, 0, 9);
        let b: Vec<u32> = rng.vec(m, 0, 9);
        let want: Vec<(u32, u32)> = a.iter().copied().zip(b.iter().copied()).collect();
        check!(format!("pairs({a:?}, {b:?})"), pairs(&a, &b).collect::<Vec<_>>(), want);
        let mut v = a.clone();
        let snap = sorted_snapshot(&v);
        v.clear();
        let mut want = a.clone();
        want.sort();
        check!(format!("sorted_snapshot({a:?})"), snap.collect::<Vec<_>>(), want);
        let len = rng.below(12);
        let text = rng.string(len, "ab é");
        let min = rng.below(3);
        let want: Vec<String> = text.split_whitespace().filter(|w| w.chars().count() > min).map(String::from).collect();
        check!(format!("long_words({text:?}, {min})"), long_words(&text, min).collect::<Vec<_>>(), want);
    }
}
