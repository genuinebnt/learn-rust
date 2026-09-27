use solution::*;

#[test]
fn classic() {
    check!(r#"heights = [1, 8, 6, 2, 5, 4, 8, 3, 7]"#, max_area(&[1, 8, 6, 2, 5, 4, 8, 3, 7]), 49);
}

#[test]
fn two() {
    check!(r#"heights = [1, 1]"#, max_area(&[1, 1]), 1);
}
