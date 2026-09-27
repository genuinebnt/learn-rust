use solution::*;

#[test]
fn leetcode_rabbit() {
    check!(r#"s = "rabbbit", t = "rabbit""#, num_distinct("rabbbit", "rabbit"), 3);
}

#[test]
fn leetcode_bag() {
    check!(r#"s = "babgbag", t = "bag""#, num_distinct("babgbag", "bag"), 5);
}

#[test]
fn empty_t() {
    check!(r#"s = "abc", t = """#, num_distinct("abc", ""), 1);
}

#[test]
fn empty_s() {
    check!(r#"s = "", t = "a""#, num_distinct("", "a"), 0);
}

#[test]
fn positions_not_letters() {
    check!(r#"s = "aaa", t = "aa""#, num_distinct("aaa", "aa"), 3);
}
