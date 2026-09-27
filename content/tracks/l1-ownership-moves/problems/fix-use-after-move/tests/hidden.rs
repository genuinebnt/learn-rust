use solution::*;

#[test]
fn hash_label() {
    check!(r##"id 7, label "#ops", items ["x"]"##, describe(Batch { id: 7, label: Some("#ops".to_string()), items: vec!["x".to_string()] }).0, "#ops: 1 items (0 long), longest x");
}

#[test]
fn empty_label() {
    check!(r#"id 7, label "", items ["abc"]"#, describe(Batch { id: 7, label: Some("".to_string()), items: vec!["abc".to_string()] }).0, ": 1 items (0 long), longest abc");
}

#[test]
fn exactly_three_bytes() {
    check!(r#"id 7, label "l", items ["abc", "abcd"]"#, describe(Batch { id: 7, label: Some("l".to_string()), items: vec!["abc".to_string(), "abcd".to_string()] }).0, "l: 2 items (1 long), longest abcd");
}

#[test]
fn longest_last() {
    check!(r#"id 9, label None, items ["a", "bb", "ccc"]"#, describe(Batch { id: 9, label: None, items: vec!["a".to_string(), "bb".to_string(), "ccc".to_string()] }).0, "#9: 3 items (0 long), longest ccc [unlabelled]");
}

#[test]
fn three_way_tie() {
    check!(r#"id 7, label "tie", items ["aa", "bb", "cc"]"#, describe(Batch { id: 7, label: Some("tie".to_string()), items: vec!["aa".to_string(), "bb".to_string(), "cc".to_string()] }).0, "tie: 3 items (0 long), longest aa");
}

#[test]
fn unicode_bytes() {
    check!(r#"id 7, label "u", items ["ab", "é日"]"#, describe(Batch { id: 7, label: Some("u".to_string()), items: vec!["ab".to_string(), "é日".to_string()] }).0, "u: 2 items (1 long), longest é日");
}

#[test]
fn unlabelled_empty() {
    check!(r#"id 0, label None, items []"#, describe(Batch { id: 0, label: None, items: vec![] }).0, "#0: 0 items (0 long), longest - [unlabelled]");
}

#[test]
fn items_unchanged() {
    check!(r#"items ["b", "a", "b"] come back in order"#, describe(Batch { id: 2, label: None, items: vec!["b".into(), "a".into(), "b".into()] }).1, vec!["b", "a", "b"]);
}

#[test]
fn dash_item() {
    check!(r#"an item that is "-""#, describe(Batch { id: 3, label: Some("d".into()), items: vec!["-".into()] }).0, "d: 1 items (0 long), longest -");
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6101);
    for _ in 0..300 {
        let n = rng.below(6);
        let mut items = Vec::new();
        for _ in 0..n {
            let len = rng.below(6);
            items.push(rng.string(len, "ab#é"));
        }
        let label = if rng.bool() { Some(rng.string(2, "#x")) } else { None };
        let id = rng.below(100) as u32;
        let mut best: Option<&str> = None;
        for it in &items {
            if best.map_or(true, |b| it.len() > b.len()) {
                best = Some(it);
            }
        }
        let long = items.iter().filter(|i| i.len() > 3).count();
        let name = label.clone().unwrap_or(format!("#{id}"));
        let mut want = format!("{name}: {} items ({long} long), longest {}", items.len(), best.unwrap_or("-"));
        if label.is_none() {
            want.push_str(" [unlabelled]");
        }
        let input = format!("id {id}, label {label:?}, items {items:?}");
        let (line, back) = describe(Batch { id, label, items: items.clone() });
        check!(input, (line, back), (want, items));
    }
}

#[test]
fn many_items() {
    let items: Vec<String> = (0..100_000).map(|i| if i == 77_777 { "longest!".to_string() } else { "ab".to_string() }).collect();
    let ptr = items.as_ptr();
    let (line, back) = describe(Batch { id: 1, label: Some("big".into()), items });
    check!("100000 items, one of 8 bytes", (line, back.as_ptr() == ptr), ("big: 100000 items (1 long), longest longest!".to_string(), true));
}
