use solution::*;

#[test]
fn second() {
    check!(r#"nums = [3, 2, 1, 5, 6, 4], k = 2"#, kth_largest(&mut [3, 2, 1, 5, 6, 4], 2), 5);
}

#[test]
fn with_duplicates() {
    check!(r#"nums = [3, 2, 3, 1, 2, 4, 5, 5, 6], k = 4"#, kth_largest(&mut [3, 2, 3, 1, 2, 4, 5, 5, 6], 4), 4);
}

#[test]
fn single() {
    check!(r#"nums = [1], k = 1"#, kth_largest(&mut [1], 1), 1);
}
