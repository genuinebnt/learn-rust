use solution::*;

#[test]
fn spaces() {
    check!(r#""1, 2 ,3""#, sum_csv("1, 2 ,3"), Ok(6));
}

#[test]
fn bad_field() {
    check!(r#""1,x""#, sum_csv("1,x").is_err(), true);
}

#[test]
fn single() {
    check!(r#""42""#, sum_csv("42"), Ok(42));
}

#[test]
fn negatives() {
    check!(r#""-1, 1, -5""#, sum_csv("-1, 1, -5"), Ok(-5));
}

#[test]
fn empty_field_skipped() {
    check!(r#""1,,2,""#, sum_csv("1,,2,"), Ok(3));
}
