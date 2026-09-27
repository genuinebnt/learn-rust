use solution::*;

#[test]
fn leetcode_pair() {
    check!(r#"s = "()""#, check_valid_string("()"), true);
}

#[test]
fn leetcode_star_as_nothing() {
    check!(r#"s = "(*)""#, check_valid_string("(*)"), true);
}

#[test]
fn leetcode_star_as_open() {
    check!(r#"s = "(*))""#, check_valid_string("(*))"), true);
}

#[test]
fn empty() {
    check!(r#"s = """#, check_valid_string(""), true);
}

#[test]
fn star_cannot_close_a_later_open() {
    check!(r#"s = "*(""#, check_valid_string("*("), false);
}

#[test]
fn not_enough_stars() {
    check!(r#"s = "((*""#, check_valid_string("((*"), false);
}
