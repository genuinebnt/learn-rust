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

#[test]
fn single_point() {
    let m = std::collections::BTreeMap::from([(4, "a".to_string()), (5, "b".to_string()), (6, "c".to_string())]);
    check!(r#"events at 4, 5, 6; from 5 to 5"#, between(&m, 5, 5), vec!["b"]);
}
