use solution::*;

#[test]
fn empty() {
    check!(r#"v = []"#, pair_sums(&[]), Vec::<i32>::new());
}

#[test]
fn negatives() {
    check!(r#"v = [-1, 1, -1]"#, pair_sums(&[-1, 1, -1]), vec![0, 0]);
}
