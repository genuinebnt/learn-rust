use solution::*;

#[test]
fn middle() {
    check!(r#"n = 5, first bad 4"#, first_bad(5, |v| v >= 4), Some(4));
}

#[test]
fn all_bad() {
    check!(r#"n = 1, first bad 1"#, first_bad(1, |v| v >= 1), Some(1));
}

#[test]
fn nothing_bad() {
    check!(r#"n = 3, none bad"#, first_bad(3, |_| false), None);
}

#[test]
fn no_versions() {
    check!(r#"n = 0"#, first_bad(0, |_| true), None);
}

#[test]
fn only_the_last_is_bad() {
    check!(r#"n = 10, first bad 10"#, first_bad(10, |v| v >= 10), Some(10));
}
