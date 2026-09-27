use solution::*;

#[test]
fn rotated() {
    check!(r#"[3,4,5,1,2]"#, find_min(&[3, 4, 5, 1, 2]), Some(1));
}

#[test]
fn longer() {
    check!(r#"[4,5,6,7,0,1,2]"#, find_min(&[4, 5, 6, 7, 0, 1, 2]), Some(0));
}
