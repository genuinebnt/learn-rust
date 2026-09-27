use solution::*;

#[test]
fn three_chunks() {
    check!(r#"[[1, 2], [3], [4, 5, 6]]"#, parallel_sum(vec![vec![1, 2], vec![3], vec![4, 5, 6]]), 21);
}

#[test]
fn empty() {
    check!(r#"[]"#, parallel_sum(vec![]), 0);
}
