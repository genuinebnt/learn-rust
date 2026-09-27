use solution::*;

#[test]
fn found() {
    check!(r#"[[1,3,5,7],[10,11,16,20],[23,30,34,60]], 3"#, search_matrix(&[vec![1, 3, 5, 7], vec![10, 11, 16, 20], vec![23, 30, 34, 60]], 3), true);
}

#[test]
fn missing() {
    check!(r#"same, 13"#, search_matrix(&[vec![1, 3, 5, 7], vec![10, 11, 16, 20], vec![23, 30, 34, 60]], 13), false);
}

#[test]
fn first_of_a_row() {
    check!(r#"same, 10"#, search_matrix(&[vec![1, 3, 5, 7], vec![10, 11, 16, 20], vec![23, 30, 34, 60]], 10), true);
}

#[test]
fn past_the_last_cell() {
    check!(r#"same, 61"#, search_matrix(&[vec![1, 3, 5, 7], vec![10, 11, 16, 20], vec![23, 30, 34, 60]], 61), false);
}

#[test]
fn one_cell() {
    check!(r#"[[5]], 5"#, search_matrix(&[vec![5]], 5), true);
}
