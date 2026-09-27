use solution::*;

#[test]
fn two_cycles() {
    check!(r#"adj = [[1], [2], [0, 3], [4], [5], [3]]"#, strongly_connected(&[vec![1], vec![2], vec![0, 3], vec![4], vec![5], vec![3]]), vec![vec![0, 1, 2], vec![3, 4, 5]]);
}

#[test]
fn dag() {
    check!(r#"adj = [[1], [2], []]"#, strongly_connected(&[vec![1], vec![2], vec![]]), vec![vec![0], vec![1], vec![2]]);
}
