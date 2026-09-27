use solution::*;

#[test]
fn zero_k() {
    check!(r#"s = "ABBB", k = 0"#, character_replacement("ABBB", 0), 3);
}

#[test]
fn empty() {
    check!(r#"s = "", k = 3"#, character_replacement("", 3), 0);
}
