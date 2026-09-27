use solution::*;

#[test]
fn empty() {
    check!(r#"[]"#, index(&[]).len(), 0);
}

#[test]
fn duplicates() {
    check!(r#"["a", "a"]"#, index(&["a", "a"])[&'a'].clone(), vec!["a".to_string(), "a".to_string()]);
}

#[test]
fn keeps_original_case() {
    check!(r#"["Zed"]"#, index(&["Zed"]).into_iter().collect::<Vec<_>>(), vec![('z', vec!["Zed".to_string()])]);
}

#[test]
fn non_letters() {
    check!(r#"["1abc", "_x"]"#, index(&["1abc", "_x"]).keys().copied().collect::<Vec<_>>(), vec!['1', '_']);
}

#[test]
fn non_ascii_not_folded() {
    check!(r#"["école", "Émile"]"#, index(&["école", "Émile"]).keys().copied().collect::<Vec<_>>(), vec!['É', 'é']);
}

#[test]
fn mixed_empties() {
    check!(r#"["", "a", ""]"#, index(&["", "a", ""]).len(), 1);
}

#[test]
fn upper_sorts_first() {
    check!(r#"["apple", "Apple"]"#, index(&["apple", "Apple"])[&'a'].clone(), vec!["Apple".to_string(), "apple".to_string()]);
}

#[test]
fn many() {
    check!(r#"10000 words over 26 letters"#, { let ws: Vec<String> = (0..10_000u32).map(|i| format!("{}{}", char::from(b'a' + (i % 26) as u8), i)).collect(); let refs: Vec<&str> = ws.iter().map(|w| w.as_str()).collect(); let idx = index(&refs); (idx.len(), idx[&'a'].len(), idx[&'z'][0].clone()) }, (26, 385, "z1013".to_string()));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(4004);
    for _ in 0..300 {
        let n = rng.below(8);
        let words: Vec<String> = (0..n).map(|_| { let l = rng.below(3); rng.string(l, "abAB") }).collect();
        let refs: Vec<&str> = words.iter().map(|w| w.as_str()).collect();
        let mut want: std::collections::BTreeMap<char, Vec<String>> = std::collections::BTreeMap::new();
        for w in &words {
            if let Some(c) = w.chars().next() {
                want.entry(c.to_ascii_lowercase()).or_default().push(w.clone());
            }
        }
        want.values_mut().for_each(|l| l.sort());
        check!(format!("words = {refs:?}"), index(&refs), want);
    }
}
