use solution::*;

#[test]
fn rotated() {
    check!(r#"[3,4,5,1,2]"#, find_min(&[3, 4, 5, 1, 2]), Some(1));
}

#[test]
fn longer() {
    check!(r#"[4,5,6,7,0,1,2]"#, find_min(&[4, 5, 6, 7, 0, 1, 2]), Some(0));
}

#[test]
fn not_rotated_at_all() {
    check!(r#"[11,13,15,17]"#, find_min(&[11, 13, 15, 17]), Some(11));
}

#[test]
fn empty_slice() {
    check!(r#"[]"#, find_min(&[]), None);
}

#[test]
fn minimum_last() {
    check!(r#"[2,3,4,5,1]"#, find_min(&[2, 3, 4, 5, 1]), Some(1));
}
