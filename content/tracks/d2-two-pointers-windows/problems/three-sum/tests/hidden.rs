use solution::*;

#[test]
fn many_dups() {
    check!(r#"nums = [-2, 0, 0, 2, 2, -2]"#, three_sum(&[-2, 0, 0, 2, 2, -2]), vec![[-2, 0, 2]]);
}

#[test]
fn wide() {
    check!(r#"nums = [-4, -1, -1, 0, 1, 2, 3]"#, three_sum(&[-4, -1, -1, 0, 1, 2, 3]), vec![[-4, 1, 3], [-1, -1, 2], [-1, 0, 1]]);
}
