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
