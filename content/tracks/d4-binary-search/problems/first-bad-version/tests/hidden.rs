use solution::*;

#[test]
fn none_bad() {
    check!(r#"n = 10, none bad"#, first_bad(10, |_| false), None);
}

#[test]
fn max_n() {
    check!(r#"n = u32::MAX, first bad u32::MAX - 1"#, first_bad(u32::MAX, |v| v >= u32::MAX - 1), Some(u32::MAX - 1));
}

#[test]
fn few_calls() {
    let calls = std::cell::Cell::new(0);
    let found = first_bad(u32::MAX, |v| {
        calls.set(calls.get() + 1);
        v >= 123_456_789
    });
    check!(r#"n = u32::MAX, count calls"#, (found, calls.get() <= 33), (Some(123_456_789), true));
}
