use solution::*;

#[test]
fn two_values() {
    check!(r#"0..=1, always true"#, last_true(0, 1, |_| true), Some(1));
}

#[test]
fn none() {
    check!(r#"5..=9, never true"#, last_true(5, 9, |_| false), None);
}

#[test]
fn top_of_range() {
    check!(r#"u32::MAX - 1..=u32::MAX, always true"#, last_true(u32::MAX - 1, u32::MAX, |_| true), Some(u32::MAX));
}
