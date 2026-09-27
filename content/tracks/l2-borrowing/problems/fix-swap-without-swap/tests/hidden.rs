use solution::*;

#[test]
fn same_index() {
    check!(r#"1 ↔ 1"#, { let mut v = ["a", "b"].map(String::from); swap_items(&mut v, 1, 1); v }, ["a", "b"].map(String::from));
}

#[test]
fn reversed() {
    check!(r#"2 ↔ 0"#, { let mut v = ["a", "b", "c"].map(String::from); swap_items(&mut v, 2, 0); v }, ["c", "b", "a"].map(String::from));
}
