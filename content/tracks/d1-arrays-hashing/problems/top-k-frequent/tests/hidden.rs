use solution::*;

#[test]
fn all_distinct() {
    check!(r#"nums = [5, 3, 9], k = 3"#, top_k_frequent(&[5, 3, 9], 3), vec![3, 5, 9]);
}

#[test]
fn negatives() {
    check!(r#"nums = [-1, -1, 2, -1, 2, 3], k = 1"#, top_k_frequent(&[-1, -1, 2, -1, 2, 3], 1), vec![-1]);
}
