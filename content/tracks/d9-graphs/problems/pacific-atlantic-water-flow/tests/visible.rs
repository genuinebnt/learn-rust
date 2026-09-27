use solution::*;

#[test]
fn example() {
    check!(r#"heights = [[1,2,2,3,5],[3,2,3,4,4],[2,4,5,3,1],[6,7,1,4,5],[5,1,1,2,4]]"#, pacific_atlantic(&[vec![1, 2, 2, 3, 5], vec![3, 2, 3, 4, 4], vec![2, 4, 5, 3, 1], vec![6, 7, 1, 4, 5], vec![5, 1, 1, 2, 4]]), vec![(0, 4), (1, 3), (1, 4), (2, 2), (3, 0), (3, 1), (4, 0)]);
}

#[test]
fn single() {
    check!(r#"heights = [[1]]"#, pacific_atlantic(&[vec![1]]), vec![(0, 0)]);
}

#[test]
fn single_row_touches_both() {
    check!(r#"heights = [[1,2,3]]"#, pacific_atlantic(&[vec![1, 2, 3]]), vec![(0, 0), (0, 1), (0, 2)]);
}

#[test]
fn pit_drains_nowhere() {
    check!(r#"heights = [[3,3,3],[3,1,3],[3,3,3]]"#, pacific_atlantic(&[vec![3, 3, 3], vec![3, 1, 3], vec![3, 3, 3]]), vec![(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]);
}

#[test]
fn spiral() {
    check!(r#"heights = [[1,2,3],[8,9,4],[7,6,5]]"#, pacific_atlantic(&[vec![1, 2, 3], vec![8, 9, 4], vec![7, 6, 5]]), vec![(0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]);
}
