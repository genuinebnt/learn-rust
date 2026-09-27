use solution::*;

#[test]
fn ten() {
    check!(r#"n = 10"#, (fib_memo(10), fib_table(10)), (55, 55));
}

#[test]
fn zero() {
    check!(r#"n = 0"#, (fib_memo(0), fib_table(0)), (0, 0));
}

#[test]
fn one() {
    check!(r#"n = 1"#, (fib_memo(1), fib_table(1)), (1, 1));
}

#[test]
fn leetcode_two() {
    check!(r#"n = 2"#, (fib_memo(2), fib_table(2)), (1, 1));
}

#[test]
fn leetcode_three() {
    check!(r#"n = 3"#, (fib_memo(3), fib_table(3)), (2, 2));
}

#[test]
fn leetcode_four() {
    check!(r#"n = 4"#, (fib_memo(4), fib_table(4)), (3, 3));
}

#[test]
fn fifty() {
    check!(r#"n = 50"#, (fib_memo(50), fib_table(50)), (12_586_269_025, 12_586_269_025));
}
