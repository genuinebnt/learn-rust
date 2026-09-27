use solution::*;

#[test]
fn two_most() {
    check!(r#"nums = [1, 1, 1, 2, 2, 3], k = 2"#, top_k_frequent(&[1, 1, 1, 2, 2, 3], 2), vec![1, 2]);
}

#[test]
fn single() {
    check!(r#"nums = [1], k = 1"#, top_k_frequent(&[1], 1), vec![1]);
}

#[test]
fn ties_by_value() {
    check!(r#"nums = [4, 4, 1, 1, 7], k = 2"#, top_k_frequent(&[4, 4, 1, 1, 7], 2), vec![1, 4]);
}
