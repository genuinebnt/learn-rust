use solution::*;

#[test]
fn three() {
    check!(r#"v = [1, 2, 3]"#, pair_sums(&[1, 2, 3]), vec![3, 5]);
}

#[test]
fn one() {
    check!(r#"v = [9]"#, pair_sums(&[9]), Vec::<i32>::new());
}
