use solution::*;

#[test]
fn three() {
    check!(r#"[[1,4,5],[1,3,4],[2,6]]"#, values(&merge_k(vec![list(&[1, 4, 5]), list(&[1, 3, 4]), list(&[2, 6])])), vec![1, 1, 2, 3, 4, 4, 5, 6]);
}

#[test]
fn none() {
    check!(r#"[]"#, merge_k(vec![]), None);
}
