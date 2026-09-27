use solution::*;

#[test]
fn leetcode_two() {
    check!(r#"n = 2"#, count_bits(2), vec![0, 1, 1]);
}

#[test]
fn leetcode_five() {
    check!(r#"n = 5"#, count_bits(5), vec![0, 1, 1, 2, 1, 2]);
}

#[test]
fn zero() {
    check!(r#"n = 0"#, count_bits(0), vec![0]);
}

#[test]
fn one() {
    check!(r#"n = 1"#, count_bits(1), vec![0, 1]);
}

#[test]
fn up_to_eight() {
    check!(r#"n = 8"#, count_bits(8), vec![0, 1, 1, 2, 1, 2, 2, 3, 1]);
}
