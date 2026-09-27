use solution::*;

#[test]
fn abab() {
    check!(r#"s = "ABAB", k = 2"#, character_replacement("ABAB", 2), 4);
}

#[test]
fn aababba() {
    check!(r#"s = "AABABBA", k = 1"#, character_replacement("AABABBA", 1), 4);
}
