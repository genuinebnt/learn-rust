use solution::*;

#[test]
fn leetcode_example() {
    check!(r#"arrays = [[1, 4, 5], [1, 3, 4], [2, 6]]"#, merge_k_sorted(&[vec![1, 4, 5], vec![1, 3, 4], vec![2, 6]]), vec![1, 1, 2, 3, 4, 4, 5, 6]);
}

#[test]
fn no_arrays() {
    check!(r#"arrays = []"#, merge_k_sorted(&[]), Vec::<i32>::new());
}

#[test]
fn one_empty_array() {
    check!(r#"arrays = [[]]"#, merge_k_sorted(&[vec![]]), Vec::<i32>::new());
}

#[test]
fn empty_arrays_skipped() {
    check!(r#"arrays = [[], [3], [], [1, 2]]"#, merge_k_sorted(&[vec![], vec![3], vec![], vec![1, 2]]), vec![1, 2, 3]);
}

#[test]
fn duplicates_kept() {
    check!(r#"arrays = [[2, 2], [2]]"#, merge_k_sorted(&[vec![2, 2], vec![2]]), vec![2, 2, 2]);
}

#[test]
fn negatives() {
    check!(r#"arrays = [[-5, 0], [-7, -1, 8]]"#, merge_k_sorted(&[vec![-5, 0], vec![-7, -1, 8]]), vec![-7, -5, -1, 0, 8]);
}
