use solution::*;

#[test]
fn leetcode_horse() {
    check!(r#"a = "horse", b = "ros""#, edit_distance("horse", "ros"), 3);
}

#[test]
fn leetcode_intention() {
    check!(r#"a = "intention", b = "execution""#, edit_distance("intention", "execution"), 5);
}

#[test]
fn empty_to_word() {
    check!(r#"a = "", b = "abc""#, edit_distance("", "abc"), 3);
}

#[test]
fn word_to_empty() {
    check!(r#"a = "abc", b = """#, edit_distance("abc", ""), 3);
}

#[test]
fn same() {
    check!(r#"a = "same", b = "same""#, edit_distance("same", "same"), 0);
}

#[test]
fn unicode_is_one_edit() {
    check!(r#"a = "café", b = "cafe""#, edit_distance("café", "cafe"), 1);
}
