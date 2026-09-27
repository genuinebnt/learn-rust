use solution::*;

#[test]
fn before_all() {
    check!(r#"[[5]], 1"#, search_matrix(&[vec![5]], 1), false);
}

#[test]
fn last_cell() {
    check!(r#"[[1,2],[3,4]], 4"#, search_matrix(&[vec![1, 2], vec![3, 4]], 4), true);
}

#[test]
fn empty() {
    check!(r#"[]"#, search_matrix(&[], 1), false);
}
