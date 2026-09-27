use solution::*;

#[test]
fn leetcode_aab() {
    check!(r#"s = "aab""#, min_cut("aab"), 1);
}

#[test]
fn leetcode_a() {
    check!(r#"s = "a""#, min_cut("a"), 0);
}

#[test]
fn leetcode_ab() {
    check!(r#"s = "ab""#, min_cut("ab"), 1);
}

#[test]
fn empty() {
    check!(r#"s = """#, min_cut(""), 0);
}

#[test]
fn already_a_palindrome() {
    check!(r#"s = "aba""#, min_cut("aba"), 0);
}

#[test]
fn longest_first_is_a_trap() {
    check!(r#"s = "bbab" ("b" | "bab")"#, min_cut("bbab"), 1);
}
