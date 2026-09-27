use solution::*;

#[test]
fn middle() {
    let m = std::collections::BTreeMap::from([(1, "a".to_string()), (5, "b".to_string()), (9, "c".to_string())]);
    check!(r#"events at 1, 5, 9; from 2 to 9"#, between(&m, 2, 9), vec!["b", "c"]);
}

#[test]
fn none() {
    let m = std::collections::BTreeMap::from([(1, "a".to_string())]);
    check!(r#"events at 1; from 2 to 3"#, between(&m, 2, 3), Vec::<&str>::new());
}
