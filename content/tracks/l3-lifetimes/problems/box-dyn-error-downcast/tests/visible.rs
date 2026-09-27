use solution::*;

#[test]
fn sums() {
    check!(r#""a=1\nb = 2""#, sum_config("a=1\nb = 2").ok(), Some(3));
}

#[test]
fn config_error_line() {
    check!(r#""a=1\nb""#, bad_line(&*sum_config("a=1\nb").unwrap_err()), Some(2));
}
