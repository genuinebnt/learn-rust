use solution::*;

#[test]
fn accents() {
    check!(r#""héllo wörld""#, reverse_each_word("héllo wörld"), "olléh dlröw".to_string());
}

#[test]
fn ascii() {
    check!(r#""ab cd""#, reverse_each_word("ab cd"), "ba dc".to_string());
}

#[test]
fn leetcode_557_first() {
    check!(r#""Let's take LeetCode contest""#, reverse_each_word("Let's take LeetCode contest"), "s'teL ekat edoCteeL tsetnoc".to_string());
}

#[test]
fn leetcode_557_second() {
    check!(r#""Mr Ding""#, reverse_each_word("Mr Ding"), "rM gniD".to_string());
}

#[test]
fn one_word() {
    check!(r#""hello""#, reverse_each_word("hello"), "olleh".to_string());
}
