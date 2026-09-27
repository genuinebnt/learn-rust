use solution::*;

#[test]
fn not_rotated() {
    check!(r#"[11,13,15,17]"#, find_min(&[11, 13, 15, 17]), Some(11));
}

#[test]
fn single() {
    check!(r#"[1]"#, find_min(&[1]), Some(1));
}

#[test]
fn empty() {
    check!(r#"[]"#, find_min(&[]), None);
}

#[test]
fn two() {
    check!(r#"[2,1]"#, find_min(&[2, 1]), Some(1));
}
