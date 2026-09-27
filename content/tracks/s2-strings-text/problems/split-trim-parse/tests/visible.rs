use solution::*;

#[test]
fn sums_trimmed_fields() {
    check!(r#""1, 2 ,3""#, sum_csv("1, 2 ,3"), Ok(6));
}

#[test]
fn trailing_comma_allowed() {
    check!(r#""1,2,""#, sum_csv("1,2,"), Ok(3));
}

#[test]
fn inner_empty_field() {
    check!(r#""1,,3""#, sum_csv("1,,3"), Err(CsvError::Empty(2)));
}

#[test]
fn bad_field_says_where() {
    check!(r#""4, x1 ,5""#, sum_csv("4, x1 ,5"), Err(CsvError::Bad(2, "x1".to_string())));
}

#[test]
fn log_message_keeps_spaces() {
    check!(r#""2024-05-01 12:00:03 WARN slow query took 250ms""#, parse_log("2024-05-01 12:00:03 WARN slow query took 250ms"), Some(LogLine { date: "2024-05-01", time: "12:00:03", level: "WARN", message: "slow query took 250ms", millis: Some(250) }));
}
