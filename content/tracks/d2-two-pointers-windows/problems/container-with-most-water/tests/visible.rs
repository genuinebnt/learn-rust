use solution::*;

#[test]
fn classic() {
    check!(r#"heights = [1, 8, 6, 2, 5, 4, 8, 3, 7]"#, max_area(&[1, 8, 6, 2, 5, 4, 8, 3, 7]), 49);
}

#[test]
fn two() {
    check!(r#"heights = [1, 1]"#, max_area(&[1, 1]), 1);
}

#[test]
fn tall_middle() {
    check!(r#"heights = [1, 100, 100, 1]"#, max_area(&[1, 100, 100, 1]), 100);
}

#[test]
fn one_line() {
    check!(r#"heights = [5]"#, max_area(&[5]), 0);
}

#[test]
fn empty() {
    check!(r#"heights = []"#, max_area(&[]), 0);
}
