use solution::*;

#[test]
fn sums() {
    check!(r#""a=1\n\nb = 2\n""#, sum_config("a=1\n\nb = 2\n").ok(), Some(3));
}

#[test]
fn missing_equals() {
    check!(r#""a=1\nnope" → line 2"#, sum_config("a=1\nnope").map_err(|e| (bad_line(&*e), e.to_string(), e.source().is_none())), Err((Some(2), "line 2: expected key=value".to_string(), true)));
}

#[test]
fn chain_of_a_bad_number() {
    check!(r#""x=oops": the error chain"#, chain(&*sum_config("x=oops").unwrap_err()), vec!["line 1: bad number".to_string(), "invalid digit found in string".to_string()]);
}

#[test]
fn root_cause_is_the_parse_error() {
    check!(r#""x=": root cause"#, root_cause(&*sum_config("x=").unwrap_err()).downcast_ref::<std::num::ParseIntError>().is_some(), true);
}

#[test]
fn bad_line_on_other_errors() {
    check!(r#"bad_line of a plain ParseIntError"#, bad_line(&"z".parse::<i32>().unwrap_err()), None);
}
