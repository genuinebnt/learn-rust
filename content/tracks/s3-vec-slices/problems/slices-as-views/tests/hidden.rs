use solution::*;

#[test]
fn middle_of_empty() {
    check!(r#"v = []"#, middle(&[]), &[][..]);
}

#[test]
fn trim_all_zero() {
    check!(r#"v = [0, 0]"#, trim_zeros(&[0, 0]), &[][..]);
}

#[test]
fn middle_of_two() {
    check!(r#"v = [1, 2]"#, middle(&[1, 2]), &[][..]);
}
