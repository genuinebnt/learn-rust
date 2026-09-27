use solution::*;

#[test]
fn cycle() {
    check!(r#"words = ["z", "x", "z"]"#, alien_order(&["z", "x", "z"]), None);
}

#[test]
fn unconstrained_letters() {
    check!(r#"words = ["ba", "bc"]"#, alien_order(&["ba", "bc"]), Some("abc".to_string()));
}

#[test]
fn single_word() {
    check!(r#"words = ["zy"]"#, alien_order(&["zy"]), Some("yz".to_string()));
}
