use solution::*;

fn err<T>(s: &str) -> Result<T, std::num::ParseIntError> {
    Err(s.parse::<i64>().unwrap_err())
}

#[test]
fn optional() {
    check!(r#"parse_optional(None), (Some("42")), (Some("x"))"#, parse_optional(None).unwrap() == None && parse_optional(Some("42")) == Ok(Some(42)) && parse_optional(Some("x")).is_err(), true);
}

#[test]
fn lines() {
    check!(r##"parse_line(" 7 "), (""), ("# note"), ("7x")"##, (parse_line(" 7 "), parse_line(""), parse_line("# note"), parse_line("7x")), (Ok(Some(7)), Ok(None), Ok(None), err("7x")));
}

#[test]
fn file_skips_blanks_and_comments() {
    check!(r#""1\n# two\n\n3""#, parse_file("1\n# two\n\n3"), Ok(vec![1, 3]));
}

#[test]
fn file_reports_the_first_bad_line() {
    check!(r#""1\nx\ny""#, parse_file("1\nx\ny"), err("x").map_err(|e| (2, e)));
}

#[test]
fn empty_file() {
    check!(r#""""#, parse_file(""), Ok(vec![]));
}
