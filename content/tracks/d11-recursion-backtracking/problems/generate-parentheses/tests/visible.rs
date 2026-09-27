use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn leetcode_three() {
    check!(r#"n = 3"#, sorted(generate_parenthesis(3)), vec!["((()))", "(()())", "(())()", "()(())", "()()()"]);
}

#[test]
fn leetcode_one() {
    check!(r#"n = 1"#, generate_parenthesis(1), vec!["()"]);
}

#[test]
fn zero_pairs() {
    check!(r#"n = 0 (one answer: the empty string)"#, generate_parenthesis(0), vec![String::new()]);
}

#[test]
fn two() {
    check!(r#"n = 2"#, sorted(generate_parenthesis(2)), vec!["(())", "()()"]);
}

#[test]
fn five_has_42() {
    check!(r#"n = 5"#, generate_parenthesis(5).len(), 42);
}
