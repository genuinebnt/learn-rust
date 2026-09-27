use solution::*;

#[test]
fn four() {
    check!(r#"nums = [100, 4, 200, 1, 3, 2]"#, longest_consecutive(&[100, 4, 200, 1, 3, 2]), 4);
}

#[test]
fn nine() {
    check!(r#"nums = [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]"#, longest_consecutive(&[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]), 9);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, longest_consecutive(&[]), 0);
}
