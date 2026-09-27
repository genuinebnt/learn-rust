use solution::*;

#[test]
fn sums() {
    check!(r#""a=1\nb = 2""#, sum_config("a=1\nb = 2").ok(), Some(3));
}

#[test]
fn config_error_line() {
    check!(r#""a=1\nb""#, bad_line(&*sum_config("a=1\nb").unwrap_err()), Some(2));
}

#[test]
fn empty_text() {
    check!(r#""""#, sum_config("").ok(), Some(0));
}

#[test]
fn parse_error_kept() {
    check!(r#""a=x""#, sum_config("a=x").unwrap_err().is::<std::num::ParseIntError>(), true);
}

#[test]
fn blank_lines() {
    check!(r#""a=1\n\n b=2 ""#, sum_config("a=1\n\n b=2 ").ok(), Some(3));
}
