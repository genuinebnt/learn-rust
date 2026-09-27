use solution::*;

#[test]
fn classic() {
    check!(r#"words = ["wrt", "wrf", "er", "ett", "rftt"]"#, alien_order(&["wrt", "wrf", "er", "ett", "rftt"]), Some("wertf".to_string()));
}

#[test]
fn prefix_after_word() {
    check!(r#"words = ["abc", "ab"]"#, alien_order(&["abc", "ab"]), None);
}

#[test]
fn two_words() {
    check!(r#"words = ["z", "x"]"#, alien_order(&["z", "x"]), Some("zx".to_string()));
}

#[test]
fn contradiction() {
    check!(r#"words = ["z", "x", "z"]"#, alien_order(&["z", "x", "z"]), None);
}

#[test]
fn ties_go_alphabetically() {
    check!(r#"words = ["cb", "ca"]"#, alien_order(&["cb", "ca"]), Some("bac".to_string()));
}
