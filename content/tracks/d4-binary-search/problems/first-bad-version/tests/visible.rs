use solution::*;

#[test]
fn middle() {
    check!(r#"n = 5, first bad 4"#, first_bad(5, |v| v >= 4), Some(4));
}

#[test]
fn all_bad() {
    check!(r#"n = 1, first bad 1"#, first_bad(1, |v| v >= 1), Some(1));
}
