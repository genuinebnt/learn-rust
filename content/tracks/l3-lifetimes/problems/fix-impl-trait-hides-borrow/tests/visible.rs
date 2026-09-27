use solution::*;

#[test]
fn long_words_example() {
    check!(r#"long_words("a quick brown fox", 3)"#, long_words("a quick brown fox", 3).collect::<Vec<_>>(), vec!["quick".to_string(), "brown".to_string()]);
}

#[test]
fn pairs_example() {
    check!(r#"pairs([1, 2, 3], [10, 20])"#, pairs(&[1, 2, 3], &[10, 20]).collect::<Vec<_>>(), vec![(1, 10), (2, 20)]);
}

#[test]
fn pairs_lifetimes_differ() {
    let a = vec![5u32, 6];
    let got: Vec<(u32, u32)> = {
        let b = vec![7u32];
        pairs(&a, &b).collect()
    };
    check!(r#"pairs(a long-lived slice, a temporary Vec) collected in the temporary's scope"#, got, vec![(5, 7)]);
}

#[test]
fn snapshot_survives_changes() {
    let mut v = vec![3u32, 1, 2];
    let snap = sorted_snapshot(&v);
    v.push(0);
    check!(r#"take a snapshot of [3, 1, 2], then push 0 to v"#, (snap.collect::<Vec<_>>(), v), (vec![1, 2, 3], vec![3, 1, 2, 0]));
}

#[test]
fn long_words_counts_chars() {
    check!(r#"long_words("héllo abc", 4)"#, long_words("héllo abc", 4).collect::<Vec<_>>(), vec!["héllo".to_string()]);
}
