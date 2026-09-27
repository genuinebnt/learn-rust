use solution::*;

#[test]
fn leetcode_open_first() {
    check!(r#"s = "(()""#, longest_valid_parentheses("(()"), 2);
}

#[test]
fn leetcode_middle() {
    check!(r#"s = ")()())""#, longest_valid_parentheses(")()())"), 4);
}

#[test]
fn leetcode_empty() {
    check!(r#"s = """#, longest_valid_parentheses(""), 0);
}

#[test]
fn must_be_contiguous() {
    check!(r#"s = "()(()""#, longest_valid_parentheses("()(()"), 2);
}

#[test]
fn nested_after_pair() {
    check!(r#"s = "()(())""#, longest_valid_parentheses("()(())"), 6);
}
