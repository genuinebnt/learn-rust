use solution::*;

#[test]
fn leetcode_one_close() {
    check!(r#"s = "())""#, min_add_to_make_valid("())"), 1);
}

#[test]
fn leetcode_three_open() {
    check!(r#"s = "(((""#, min_add_to_make_valid("((("), 3);
}

#[test]
fn empty() {
    check!(r#"s = """#, min_add_to_make_valid(""), 0);
}

#[test]
fn balanced() {
    check!(r#"s = "()()""#, min_add_to_make_valid("()()"), 0);
}

#[test]
fn counts_match_order_wrong() {
    check!(r#"s = ")(""#, min_add_to_make_valid(")("), 2);
}

#[test]
fn both_kinds() {
    check!(r#"s = "()))((""#, min_add_to_make_valid("()))(("), 4);
}
