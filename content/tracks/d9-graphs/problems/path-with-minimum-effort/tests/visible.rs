use solution::*;

#[test]
fn two() {
    check!(r#"heights = [[1,2,2],[3,8,2],[5,3,5]]"#, minimum_effort(&[vec![1, 2, 2], vec![3, 8, 2], vec![5, 3, 5]]), 2);
}

#[test]
fn one() {
    check!(r#"heights = [[1,2,3],[3,8,4],[5,3,5]]"#, minimum_effort(&[vec![1, 2, 3], vec![3, 8, 4], vec![5, 3, 5]]), 1);
}
