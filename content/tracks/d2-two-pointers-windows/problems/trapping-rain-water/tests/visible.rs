use solution::*;

#[test]
fn classic() {
    check!(r#"heights = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]"#, trap(&[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]), 6);
}

#[test]
fn bowl() {
    check!(r#"heights = [4, 2, 0, 3, 2, 5]"#, trap(&[4, 2, 0, 3, 2, 5]), 9);
}

#[test]
fn empty() {
    check!(r#"heights = []"#, trap(&[]), 0);
}

#[test]
fn monotonic() {
    check!(r#"heights = [1, 2, 3, 4]"#, trap(&[1, 2, 3, 4]), 0);
}

#[test]
fn lower_wall_decides() {
    check!(r#"heights = [3, 0, 1]"#, trap(&[3, 0, 1]), 1);
}
