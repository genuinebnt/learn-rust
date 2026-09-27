use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn leetcode_aab() {
    check!(r#"s = "aab""#, sorted(partition("aab")), vec![vec!["a", "a", "b"], vec!["aa", "b"]]);
}

#[test]
fn leetcode_single() {
    check!(r#"s = "a""#, partition("a"), vec![vec!["a"]]);
}

#[test]
fn empty_has_one_split() {
    check!(r#"s = "" (one split with no pieces)"#, partition(""), vec![Vec::<&str>::new()]);
}

#[test]
fn no_long_palindromes() {
    check!(r#"s = "abc""#, partition("abc"), vec![vec!["a", "b", "c"]]);
}

#[test]
fn odd_palindrome() {
    check!(r#"s = "aba""#, sorted(partition("aba")), vec![vec!["a", "b", "a"], vec!["aba"]]);
}
