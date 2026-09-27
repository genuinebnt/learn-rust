use solution::*;

#[test]
fn flat() {
    check!(r#"heights = [[3,3],[3,3]]"#, pacific_atlantic(&[vec![3, 3], vec![3, 3]]), vec![(0, 0), (0, 1), (1, 0), (1, 1)]);
}

#[test]
fn valley() {
    check!(r#"heights = [[5,1,5]]"#, pacific_atlantic(&[vec![5, 1, 5]]), vec![(0, 0), (0, 1), (0, 2)]);
}

#[test]
fn pit() {
    check!(r#"heights = [[3,3,3],[3,1,3],[3,3,3]]"#, pacific_atlantic(&[vec![3, 3, 3], vec![3, 1, 3], vec![3, 3, 3]]).len(), 8);
}
