use solution::*;

#[test]
fn parse_error_kept() {
    check!(r#""a=x""#, sum_config("a=x").unwrap_err().is::<std::num::ParseIntError>(), true);
}

#[test]
fn parse_error_has_no_line() {
    check!(r#""a=x""#, bad_line(&*sum_config("a=x").unwrap_err()), None);
}

#[test]
fn blank_lines() {
    check!(r#""a=1\n\n b=2 ""#, sum_config("a=1\n\n b=2 ").ok(), Some(3));
}

#[test]
fn line_numbers_count_blanks() {
    check!(r#""\n\nx""#, bad_line(&*sum_config("\n\nx").unwrap_err()), Some(3));
}

#[test]
fn message() {
    check!(r#""x""#, sum_config("x").unwrap_err().to_string(), "line 1: expected key=value".to_string());
}
