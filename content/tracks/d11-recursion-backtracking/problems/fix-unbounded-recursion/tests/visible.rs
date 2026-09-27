use solution::*;

#[test]
fn four_values() {
    check!(r#"nums = [1, 2, 3, 4]"#, split_sum(&[1, 2, 3, 4]), 10);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, split_sum(&[]), 0);
}

#[test]
fn single() {
    check!(r#"nums = [5]"#, split_sum(&[5]), 5);
}

#[test]
fn odd_length() {
    check!(r#"nums = [1, 2, 3]"#, split_sum(&[1, 2, 3]), 6);
}

#[test]
fn negatives() {
    check!(r#"nums = [-3, 3, 7]"#, split_sum(&[-3, 3, 7]), 7);
}
