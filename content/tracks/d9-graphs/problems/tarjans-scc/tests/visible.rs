use solution::*;

#[test]
fn two_cycles() {
    check!(r#"adj = [[1], [2], [0, 3], [4], [5], [3]]"#, strongly_connected(&[vec![1], vec![2], vec![0, 3], vec![4], vec![5], vec![3]]), vec![vec![0, 1, 2], vec![3, 4, 5]]);
}

#[test]
fn dag() {
    check!(r#"adj = [[1], [2], []]"#, strongly_connected(&[vec![1], vec![2], vec![]]), vec![vec![0], vec![1], vec![2]]);
}

#[test]
fn single_node() {
    check!(r#"adj = [[]]"#, strongly_connected(&[vec![]]), vec![vec![0]]);
}

#[test]
fn mutual_pair() {
    check!(r#"adj = [[1], [0]]"#, strongly_connected(&[vec![1], vec![0]]), vec![vec![0, 1]]);
}

#[test]
fn components_sorted_by_smallest_node() {
    check!(r#"adj = [[3], [2], [1], [0]]"#, strongly_connected(&[vec![3], vec![2], vec![1], vec![0]]), vec![vec![0, 3], vec![1, 2]]);
}
