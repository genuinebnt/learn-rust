use solution::*;

#[test]
fn classic() {
    check!(r#"words = ["wrt", "wrf", "er", "ett", "rftt"]"#, alien_order(&["wrt", "wrf", "er", "ett", "rftt"]), Some("wertf".to_string()));
}

#[test]
fn prefix_after_word() {
    check!(r#"words = ["abc", "ab"]"#, alien_order(&["abc", "ab"]), None);
}
