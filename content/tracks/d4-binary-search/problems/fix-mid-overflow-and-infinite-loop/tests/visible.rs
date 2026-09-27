use solution::*;

#[test]
fn big_range() {
    check!(r#"0..=u32::MAX, x ≤ 3·10⁹"#, last_true(0, u32::MAX, |x| x <= 3_000_000_000), Some(3_000_000_000));
}

#[test]
fn squares() {
    check!(r#"0..=100, x² ≤ 50"#, last_true(0, 100, |x| x * x <= 50), Some(7));
}

#[test]
fn single_value() {
    check!(r#"7..=7, always true"#, last_true(7, 7, |_| true), Some(7));
}

#[test]
fn pair_both_true() {
    check!(r#"3..=4, x ≤ 4"#, last_true(3, 4, |x| x <= 4), Some(4));
}

#[test]
fn false_from_the_start() {
    check!(r#"10..=20, never true"#, last_true(10, 20, |_| false), None);
}
