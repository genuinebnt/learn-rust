use solution::*;

#[test]
fn middle_of_four() {
    check!(r#"v = [1, 2, 3, 4]"#, middle(&[1, 2, 3, 4]), &[2, 3][..]);
}

#[test]
fn middle_of_one() {
    check!(r#"v = [1]"#, middle(&[1]), &[][..]);
}

#[test]
fn trim() {
    check!(r#"v = [0, 0, 5, 0, 7, 0]"#, trim_zeros(&[0, 0, 5, 0, 7, 0]), &[5, 0, 7][..]);
}

#[test]
fn middle_of_three() {
    check!(r#"v = [1, 2, 3]"#, middle(&[1, 2, 3]), &[2][..]);
}

#[test]
fn trim_nothing_to_trim() {
    check!(r#"v = [1, 2]"#, trim_zeros(&[1, 2]), &[1, 2][..]);
}
