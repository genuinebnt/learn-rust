use solution::*;

#[test]
fn reversed_bounds() {
    let m = std::collections::BTreeMap::from([(5, "b".to_string())]);
    check!(r#"from 9 to 1"#, between(&m, 9, 1), Vec::<&str>::new());
}

#[test]
fn exact_bounds() {
    let m = std::collections::BTreeMap::from([(1, "a".to_string()), (9, "c".to_string())]);
    check!(r#"events at 1 and 9; from 1 to 9"#, between(&m, 1, 9), vec!["a", "c"]);
}
