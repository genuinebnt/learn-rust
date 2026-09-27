use solution::*;

#[test]
fn found() {
    check!(r#"[-1,0,3,5,9,12], 9"#, search(&[-1, 0, 3, 5, 9, 12], 9), Some(4));
}

#[test]
fn missing() {
    check!(r#"[-1,0,3,5,9,12], 2"#, search(&[-1, 0, 3, 5, 9, 12], 2), None);
}

#[test]
fn empty_slice() {
    check!(r#"[], 0"#, search(&[], 0), None);
}

#[test]
fn single_found() {
    check!(r#"[5], 5"#, search(&[5], 5), Some(0));
}

#[test]
fn outside_both_ends() {
    check!(r#"[1,3], 0 and 4"#, (search(&[1, 3], 0), search(&[1, 3], 4)), (None, None));
}
