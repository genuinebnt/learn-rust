use solution::*;

#[test]
fn leetcode_three() {
    check!(r#"n = 3"#, num_trees(3), 5);
}

#[test]
fn leetcode_one() {
    check!(r#"n = 1"#, num_trees(1), 1);
}

#[test]
fn empty_tree() {
    check!(r#"n = 0"#, num_trees(0), 1);
}

#[test]
fn two() {
    check!(r#"n = 2"#, num_trees(2), 2);
}

#[test]
fn four() {
    check!(r#"n = 4"#, num_trees(4), 14);
}
