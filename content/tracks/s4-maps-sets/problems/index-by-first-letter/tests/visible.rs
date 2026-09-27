use solution::*;

#[test]
fn fruit() {
    check!(r#"["banana", "Apple", "avocado"]"#, index(&["banana", "Apple", "avocado"]).into_iter().collect::<Vec<_>>(), vec![('a', vec!["Apple".to_string(), "avocado".to_string()]), ('b', vec!["banana".to_string()])]);
}

#[test]
fn empty_string() {
    check!(r#"[""]"#, index(&[""]).len(), 0);
}

#[test]
fn keys_sorted() {
    check!(r#"["z", "m", "a"]"#, index(&["z", "m", "a"]).keys().copied().collect::<Vec<_>>(), vec!['a', 'm', 'z']);
}

#[test]
fn case_merged_words_kept() {
    check!(r#"["Bob", "ann", "Al"]"#, index(&["Bob", "ann", "Al"]).into_iter().collect::<Vec<_>>(), vec![('a', vec!["Al".to_string(), "ann".to_string()]), ('b', vec!["Bob".to_string()])]);
}

#[test]
fn lists_sorted() {
    check!(r#"["b2", "b10", "b1"]"#, index(&["b2", "b10", "b1"])[&'b'].clone(), vec!["b1".to_string(), "b10".to_string(), "b2".to_string()]);
}
