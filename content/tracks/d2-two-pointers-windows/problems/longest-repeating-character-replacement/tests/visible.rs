use solution::*;

#[test]
fn abab() {
    check!(r#"s = "ABAB", k = 2"#, character_replacement("ABAB", 2), 4);
}

#[test]
fn aababba() {
    check!(r#"s = "AABABBA", k = 1"#, character_replacement("AABABBA", 1), 4);
}

#[test]
fn empty() {
    check!(r#"s = "", k = 3"#, character_replacement("", 3), 0);
}

#[test]
fn zero_k() {
    check!(r#"s = "ABBB", k = 0"#, character_replacement("ABBB", 0), 3);
}

#[test]
fn k_past_length() {
    check!(r#"s = "AB", k = 5"#, character_replacement("AB", 5), 2);
}
