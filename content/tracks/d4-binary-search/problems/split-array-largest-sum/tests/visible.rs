use solution::*;

#[test]
fn two_parts() {
    check!(r#"[7,2,5,10,8], k = 2"#, split_array(&[7, 2, 5, 10, 8], 2), 18);
}

#[test]
fn even() {
    check!(r#"[1,2,3,4,5], k = 2"#, split_array(&[1, 2, 3, 4, 5], 2), 9);
}

#[test]
fn every_value_alone() {
    check!(r#"[1,4,4], k = 3"#, split_array(&[1, 4, 4], 3), 4);
}

#[test]
fn one_part_is_the_total() {
    check!(r#"[1,2,3], k = 1"#, split_array(&[1, 2, 3], 1), 6);
}

#[test]
fn zeros_count_as_parts() {
    check!(r#"[0,0,5], k = 2"#, split_array(&[0, 0, 5], 2), 5);
}
