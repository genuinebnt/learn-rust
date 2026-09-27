use solution::*;

#[test]
fn swaps() {
    check!(r#"["a", "b", "c"], 0 ↔ 2"#, { let mut v = ["a", "b", "c"].map(String::from); swap_items(&mut v, 0, 2); v }, ["c", "b", "a"].map(String::from));
}

#[test]
fn adjacent() {
    check!(r#"["x", "y"], 0 ↔ 1"#, { let mut v = ["x", "y"].map(String::from); swap_items(&mut v, 0, 1); v }, ["y", "x"].map(String::from));
}

#[test]
fn unicode() {
    check!(r#"["é", "ß"], 0 ↔ 1"#, { let mut v = ["é", "ß"].map(String::from); swap_items(&mut v, 0, 1); v }, ["ß", "é"].map(String::from));
}

#[test]
fn same_index() {
    check!(r#"1 ↔ 1"#, { let mut v = ["a", "b"].map(String::from); swap_items(&mut v, 1, 1); v }, ["a", "b"].map(String::from));
}

#[test]
fn reversed() {
    check!(r#"2 ↔ 0"#, { let mut v = ["a", "b", "c"].map(String::from); swap_items(&mut v, 2, 0); v }, ["c", "b", "a"].map(String::from));
}
