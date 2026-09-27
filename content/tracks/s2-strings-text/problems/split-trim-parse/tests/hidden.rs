use solution::*;

#[test]
fn empty() {
    check!(r#""""#, sum_csv(""), Ok(0));
}

#[test]
fn empty_fields_and_negatives() {
    check!(r#"" -4 ,, 10""#, sum_csv(" -4 ,, 10"), Ok(6));
}

#[test]
fn float_is_not_int() {
    check!(r#""1.5""#, sum_csv("1.5").is_err(), true);
}
