use solution::*;

#[test]
fn two_lines() {
    check!(r#"lines = [("250", "4"), ("100", "1")]"#, order_total(&[("250", "4"), ("100", "1")]), Some(1100));
}

#[test]
fn empty_order() {
    check!(r#"lines = []"#, order_total(&[]), Some(0));
}

#[test]
fn bad_qty() {
    check!(r#"lines = [("250", "x")]"#, order_total(&[("250", "x")]), None);
}

#[test]
fn one_bad_line_spoils_the_total() {
    check!(r#"lines = [("5", "2"), ("oops", "1")]"#, order_total(&[("5", "2"), ("oops", "1")]), None);
}

#[test]
fn product_overflow_is_none() {
    check!(r#"lines = [("4294967296", "4294967296")]"#, order_total(&[("4294967296", "4294967296")]), None);
}
