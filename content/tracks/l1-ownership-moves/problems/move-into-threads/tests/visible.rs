use solution::*;

#[test]
fn three_chunks() {
    check!(r#"[[1, 2], [3], [4, 5, 6]]"#, parallel_sum(vec![vec![1, 2], vec![3], vec![4, 5, 6]]), 21);
}

#[test]
fn empty() {
    check!(r#"[]"#, parallel_sum(vec![]), 0);
}

#[test]
fn single_chunk() {
    check!(r#"[[10, 20]]"#, parallel_sum(vec![vec![10, 20]]), 30);
}

#[test]
fn one_empty_chunk() {
    check!(r#"[[]]"#, parallel_sum(vec![vec![]]), 0);
}

#[test]
fn zeros() {
    check!(r#"[[0, 0], [0]]"#, parallel_sum(vec![vec![0, 0], vec![0]]), 0);
}
