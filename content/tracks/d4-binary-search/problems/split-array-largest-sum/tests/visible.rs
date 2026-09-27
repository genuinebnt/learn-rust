use solution::*;

#[test]
fn two_parts() {
    check!(r#"[7,2,5,10,8], k = 2"#, split_array(&[7, 2, 5, 10, 8], 2), 18);
}

#[test]
fn even() {
    check!(r#"[1,2,3,4,5], k = 2"#, split_array(&[1, 2, 3, 4, 5], 2), 9);
}
