use solution::*;

#[test]
fn egg_add() {
    check!(r#"s = "egg", t = "add""#, is_isomorphic("egg", "add"), true);
}

#[test]
fn foo_bar() {
    check!(r#"s = "foo", t = "bar""#, is_isomorphic("foo", "bar"), false);
}

#[test]
fn paper_title() {
    check!(r#"s = "paper", t = "title""#, is_isomorphic("paper", "title"), true);
}

#[test]
fn two_letters_to_one() {
    check!(r#"s = "ab", t = "aa""#, is_isomorphic("ab", "aa"), false);
}

#[test]
fn empty() {
    check!(r#"s = "", t = """#, is_isomorphic("", ""), true);
}
