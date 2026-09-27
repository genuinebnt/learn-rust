use solution::*;

#[test]
fn flat_route() {
    check!(r#"a 5×5 grid with a flat winding path"#, minimum_effort(&[vec![1, 2, 1, 1, 1], vec![1, 2, 1, 2, 1], vec![1, 2, 1, 2, 1], vec![1, 2, 1, 2, 1], vec![1, 1, 1, 2, 1]]), 0);
}

#[test]
fn single_cell() {
    check!(r#"heights = [[7]]"#, minimum_effort(&[vec![7]]), 0);
}

#[test]
fn big_drop() {
    check!(r#"heights = [[0, 1000000]]"#, minimum_effort(&[vec![0, 1_000_000]]), 1_000_000);
}
