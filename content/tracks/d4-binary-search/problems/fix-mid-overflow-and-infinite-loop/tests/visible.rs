use solution::*;

#[test]
fn big_range() {
    check!(r#"0..=u32::MAX, x ≤ 3·10⁹"#, last_true(0, u32::MAX, |x| x <= 3_000_000_000), Some(3_000_000_000));
}

#[test]
fn squares() {
    check!(r#"0..=100, x² ≤ 50"#, last_true(0, 100, |x| x * x <= 50), Some(7));
}
