use solution::*;

#[test]
fn classic() {
    check!(r#"heights = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]"#, trap(&[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]), 6);
}

#[test]
fn bowl() {
    check!(r#"heights = [4, 2, 0, 3, 2, 5]"#, trap(&[4, 2, 0, 3, 2, 5]), 9);
}
