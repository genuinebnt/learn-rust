use solution::*;

#[test]
fn two_provinces() {
    check!(r#"connected = [[1,1,0],[1,1,0],[0,0,1]]"#, count_provinces(&[vec![1, 1, 0], vec![1, 1, 0], vec![0, 0, 1]]), 2);
}

#[test]
fn all_separate() {
    check!(r#"connected = [[1,0,0],[0,1,0],[0,0,1]]"#, count_provinces(&[vec![1, 0, 0], vec![0, 1, 0], vec![0, 0, 1]]), 3);
}

#[test]
fn one_city() {
    check!(r#"connected = [[1]]"#, count_provinces(&[vec![1]]), 1);
}

#[test]
fn linked_through_a_middle_city() {
    check!(r#"connected = [[1,0,1],[0,1,1],[1,1,1]]"#, count_provinces(&[vec![1, 0, 1], vec![0, 1, 1], vec![1, 1, 1]]), 1);
}

#[test]
fn all_linked() {
    check!(r#"connected = [[1,1],[1,1]]"#, count_provinces(&[vec![1, 1], vec![1, 1]]), 1);
}
