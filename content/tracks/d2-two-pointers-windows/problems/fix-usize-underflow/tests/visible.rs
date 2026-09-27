use solution::*;

#[test]
fn odd() {
    check!(r#"v = [1, 2, 1]"#, is_mirror(&[1, 2, 1]), true);
}

#[test]
fn not_mirror() {
    check!(r#"v = [1, 2]"#, is_mirror(&[1, 2]), false);
}

#[test]
fn empty() {
    check!(r#"v = []"#, is_mirror(&[]), true);
}
