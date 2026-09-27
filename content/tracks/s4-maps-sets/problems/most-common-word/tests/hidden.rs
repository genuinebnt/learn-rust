use solution::*;

#[test]
fn tie_alphabetical() {
    check!(r#""b a b a", banned = []"#, most_common_word("b a b a", &[]), "a");
}

#[test]
fn all_banned() {
    check!(r#""x y", banned = ["x", "y"]"#, most_common_word("x y", &["x", "y"]), "");
}
