use solution::*;

#[test]
fn keys_sorted() {
    check!(r#"["z", "m", "a"]"#, index(&["z", "m", "a"]).keys().copied().collect::<Vec<_>>(), vec!['a', 'm', 'z']);
}
