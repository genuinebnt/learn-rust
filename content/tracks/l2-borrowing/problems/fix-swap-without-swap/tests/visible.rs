use solution::*;

#[test]
fn swaps() {
    check!(r#"["a", "b", "c"], 0 ↔ 2"#, { let mut v = ["a", "b", "c"].map(String::from); swap_items(&mut v, 0, 2); v }, ["c", "b", "a"].map(String::from));
}

#[test]
fn adjacent() {
    check!(r#"["x", "y"], 0 ↔ 1"#, { let mut v = ["x", "y"].map(String::from); swap_items(&mut v, 0, 1); v }, ["y", "x"].map(String::from));
}
