use solution::*;

#[test]
fn classic() {
    check!(r#"s = "ADOBECODEBANC", t = "ABC""#, min_window("ADOBECODEBANC", "ABC"), "BANC");
}

#[test]
fn single() {
    check!(r#"s = "a", t = "a""#, min_window("a", "a"), "a");
}

#[test]
fn impossible() {
    check!(r#"s = "a", t = "aa""#, min_window("a", "aa"), "");
}
