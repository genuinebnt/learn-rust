use solution::*;

#[test]
fn first_row() {
    check!(r#"n = 1, k = 1"#, kth_grammar(1, 1), 0);
}

#[test]
fn leetcode_row_two_first() {
    check!(r#"n = 2, k = 1"#, kth_grammar(2, 1), 0);
}

#[test]
fn leetcode_row_two_second() {
    check!(r#"n = 2, k = 2"#, kth_grammar(2, 2), 1);
}

#[test]
fn k_counts_from_one() {
    check!(r#"n = 3, k = 4 (row 0110)"#, kth_grammar(3, 4), 0);
}

#[test]
fn row_four() {
    check!(r#"n = 4, k = 1..=8 (row 01101001)"#, (1..=8).map(|k| kth_grammar(4, k)).collect::<Vec<u8>>(), vec![0, 1, 1, 0, 1, 0, 0, 1]);
}
