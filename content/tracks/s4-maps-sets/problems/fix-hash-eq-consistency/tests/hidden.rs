use solution::*;

#[test]
fn many_cases() {
    check!(r#"["ADMIN", "admin", "Admin", "aDmIn"]"#, distinct(&["ADMIN", "admin", "Admin", "aDmIn"]), 1);
}

#[test]
fn empty() {
    check!(r#"[]"#, distinct(&[]), 0);
}
