use solution::*;

#[test]
fn labelled() {
    check!(r#"id 7, label "nightly", items ["build", "api", "ship"]"#, describe(Batch { id: 7, label: Some("nightly".to_string()), items: vec!["build".to_string(), "api".to_string(), "ship".to_string()] }).0, "nightly: 3 items (2 long), longest build");
}

#[test]
fn unlabelled() {
    check!(r#"id 7, label None, items ["a", "bbbb"]"#, describe(Batch { id: 7, label: None, items: vec!["a".to_string(), "bbbb".to_string()] }).0, "#7: 2 items (1 long), longest bbbb [unlabelled]");
}

#[test]
fn no_items() {
    check!(r#"id 7, label "empty", items []"#, describe(Batch { id: 7, label: Some("empty".to_string()), items: vec![] }).0, "empty: 0 items (0 long), longest -");
}

#[test]
fn tie_first_wins() {
    check!(r#"id 7, label "t", items ["abcd", "wxyz"]"#, describe(Batch { id: 7, label: Some("t".to_string()), items: vec!["abcd".to_string(), "wxyz".to_string()] }).0, "t: 2 items (2 long), longest abcd");
}

#[test]
fn items_come_back() {
    let b = Batch { id: 1, label: None, items: vec!["x".to_string(), "yy".to_string()] };
    let ptr = b.items.as_ptr();
    let (_, items) = describe(b);
    let items_ptr = items.as_ptr();
    check!(r#"the returned items are the batch's own Vec"#, (items, items_ptr == ptr), (vec!["x".to_string(), "yy".to_string()], true));
}
