use solution::*;

use std::time::Duration;

#[test]
fn find_found_and_missing() {
    check!(r#"find([4, 8, 15], 8), find([4, 8, 15], 16)"#, (find(&[4, 8, 15], 8), find(&[4, 8, 15], 16)), (Some(1), None));
}

#[test]
fn index_zero_is_found() {
    check!(r#"find([7, 3], 7), rfind("/x", '/')"#, (find(&[7, 3], 7), rfind("/x", '/')), (Some(0), Some(0)));
}

#[test]
fn rfind_last_match() {
    check!(r#"rfind("a/b/c", '/'), rfind("abc", '/')"#, (rfind("a/b/c", '/'), rfind("abc", '/')), (Some(3), None));
}

#[test]
fn timeouts() {
    check!(r#"None, Some(0), Some(250 ms)"#, (timeout_ms(None), timeout_ms(Some(Duration::ZERO)), timeout_ms(Some(Duration::from_millis(250)))), (-1, 0, 250));
}

#[test]
fn sub_millisecond_rounds_up() {
    check!(r#"Some(500 µs)"#, timeout_ms(Some(Duration::from_micros(500))), 1);
}
