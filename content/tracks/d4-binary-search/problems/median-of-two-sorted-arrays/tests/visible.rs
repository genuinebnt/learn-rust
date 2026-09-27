use solution::*;

#[test]
fn odd() {
    check!(r#"[1,3], [2]"#, median(&[1, 3], &[2]), Some(2.0));
}

#[test]
fn even() {
    check!(r#"[1,2], [3,4]"#, median(&[1, 2], &[3, 4]), Some(2.5));
}

#[test]
fn second_empty() {
    check!(r#"[1,2,3], []"#, median(&[1, 2, 3], &[]), Some(2.0));
}

#[test]
fn nothing_at_all() {
    check!(r#"[], []"#, median(&[], &[]), None);
}

#[test]
fn same_values_in_both() {
    check!(r#"[1,2], [1,2]"#, median(&[1, 2], &[1, 2]), Some(1.5));
}
