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

#[test]
fn single() {
    check!(r#"v = [5]"#, is_mirror(&[5]), true);
}

#[test]
fn even() {
    check!(r#"v = [3, 4, 4, 3]"#, is_mirror(&[3, 4, 4, 3]), true);
}
