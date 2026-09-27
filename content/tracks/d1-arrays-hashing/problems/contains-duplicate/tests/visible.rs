use solution::*;

#[test]
fn has_duplicate() {
    check!(r#"nums = [1, 2, 3, 1]"#, contains_duplicate(&[1, 2, 3, 1]), true);
}

#[test]
fn all_distinct() {
    check!(r#"nums = [1, 2, 3, 4]"#, contains_duplicate(&[1, 2, 3, 4]), false);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, contains_duplicate(&[]), false);
}

#[test]
fn single() {
    check!(r#"nums = [1]"#, contains_duplicate(&[1]), false);
}

#[test]
fn repeat_far_apart() {
    check!(r#"nums = [5, 1, 2, 3, 5]"#, contains_duplicate(&[5, 1, 2, 3, 5]), true);
}

#[test]
fn leetcode_many_repeats() {
    check!(r#"nums = [1, 1, 1, 3, 3, 4, 3, 2, 4, 2]"#, contains_duplicate(&[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]), true);
}
