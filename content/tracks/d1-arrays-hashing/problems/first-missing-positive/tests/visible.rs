use solution::*;

#[test]
fn gap_at_two() {
    check!(r#"nums = [3, 4, -1, 1]"#, first_missing_positive(&mut [3, 4, -1, 1]), 2);
}

#[test]
fn next_after_run() {
    check!(r#"nums = [1, 2, 0]"#, first_missing_positive(&mut [1, 2, 0]), 3);
}

#[test]
fn all_large() {
    check!(r#"nums = [7, 8, 9, 11, 12]"#, first_missing_positive(&mut [7, 8, 9, 11, 12]), 1);
}
