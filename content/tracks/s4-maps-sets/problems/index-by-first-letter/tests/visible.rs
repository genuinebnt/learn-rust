use solution::*;

#[test]
fn fruit() {
    check!(r#"["banana", "Apple", "avocado"]"#, index(&["banana", "Apple", "avocado"]).into_iter().collect::<Vec<_>>(), vec![('a', vec!["Apple".to_string(), "avocado".to_string()]), ('b', vec!["banana".to_string()])]);
}

#[test]
fn empty_string() {
    check!(r#"[""]"#, index(&[""]).len(), 0);
}
