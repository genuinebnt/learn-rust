use solution::*;

#[test]
fn accented_words() {
    check!(r#""héllo wörld""#, reverse_each_word("héllo wörld"), "olléh dlröw".to_string());
}

#[test]
fn whitespace_kept() {
    check!(r#""  ab\tcd ""#, reverse_each_word("  ab\tcd "), "  ba\tdc ".to_string());
}

#[test]
fn combining_mark_moves_with_letter() {
    check!(r#""e\u{301}x""#, reverse_each_word("e\u{301}x"), "xe\u{301}".to_string());
}

#[test]
fn leetcode_557() {
    check!(r#""Let's take LeetCode contest""#, reverse_each_word("Let's take LeetCode contest"), "s'teL ekat edoCteeL tsetnoc".to_string());
}

#[test]
fn empty() {
    check!(r#""""#, reverse_each_word(""), String::new());
}
