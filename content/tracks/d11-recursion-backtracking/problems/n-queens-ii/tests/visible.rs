use solution::*;

#[test]
fn leetcode_four() {
    check!(r#"n = 4"#, total_n_queens(4), 2);
}

#[test]
fn leetcode_one() {
    check!(r#"n = 1"#, total_n_queens(1), 1);
}

#[test]
fn two_has_none() {
    check!(r#"n = 2"#, total_n_queens(2), 0);
}

#[test]
fn three_has_none() {
    check!(r#"n = 3"#, total_n_queens(3), 0);
}

#[test]
fn five_is_odd() {
    check!(r#"n = 5 (odd: the middle column counts once)"#, total_n_queens(5), 10);
}

#[test]
fn eight_queens() {
    check!(r#"n = 8"#, total_n_queens(8), 92);
}
