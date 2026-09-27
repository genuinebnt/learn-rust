use solution::*;

#[test]
fn length_in_bytes() {
    check!(r#"["é", "ab"]"#, group_by_len(&["é", "ab"]), std::collections::HashMap::from([(2, vec!["é", "ab"])]));
}

#[test]
fn duplicates() {
    check!(r#"["a", "a"]"#, group_by_len(&["a", "a"]), std::collections::HashMap::from([(1, vec!["a", "a"])]));
}

#[test]
fn borrows_the_words() {
    check!(r#"one word, compared by address"#, { let s = String::from("xyz"); let g = group_by_len(&[s.as_str()]); std::ptr::eq(g[&3][0], s.as_str()) }, true);
}

#[test]
fn long_word() {
    check!(r#"a 1000-byte word"#, { let w = "x".repeat(1000); group_by_len(&[w.as_str()]).keys().copied().collect::<Vec<_>>() }, vec![1000]);
}

#[test]
fn many() {
    check!(r#"10000 words of lengths 0..10"#, { let ws: Vec<String> = (0..10_000).map(|i| "a".repeat(i % 10)).collect(); let refs: Vec<&str> = ws.iter().map(|w| w.as_str()).collect(); let g = group_by_len(&refs); (g.len(), g[&0].len(), g[&9].len()) }, (10, 1000, 1000));
}

#[test]
fn three_groups() {
    check!(r#"["a", "bbb", "cc", "d"]"#, group_by_len(&["a", "bbb", "cc", "d"]), std::collections::HashMap::from([(1, vec!["a", "d"]), (2, vec!["cc"]), (3, vec!["bbb"])]));
}

#[test]
fn spaces_count() {
    check!(r#"[" ", "  "]"#, group_by_len(&[" ", "  "]), std::collections::HashMap::from([(1, vec![" "]), (2, vec!["  "])]));
}

#[test]
fn scale_many_distinct_lengths() {
    let big = "a".repeat(50_000);
    let refs: Vec<&str> = (0..200_000).map(|i| &big[..i % 50_000]).collect();
    let g = group_by_len(&refs);
    check!(r#"200000 slices of one string, 50000 distinct lengths"#, (g.len(), g[&0].len(), g[&49_999].len(), std::ptr::eq(g[&49_999][3], &big[..49_999])), (50_000, 4, 4, true));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(4002);
    for _ in 0..300 {
        let n = rng.below(10);
        let words: Vec<String> = (0..n).map(|_| { let l = rng.below(4); rng.string(l, "aé") }).collect();
        let refs: Vec<&str> = words.iter().map(|w| w.as_str()).collect();
        let mut want: std::collections::HashMap<usize, Vec<&str>> = std::collections::HashMap::new();
        for &w in &refs {
            let group = want.entry(w.len()).or_default();
            group.push(w);
        }
        check!(format!("words = {refs:?}"), group_by_len(&refs), want);
    }
}
