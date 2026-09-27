use solution::*;

#[test]
fn spaces() {
    check!(r#""1, 2 ,3""#, sum_csv("1, 2 ,3"), Ok(6));
}

#[test]
fn bad_field() {
    check!(r#""1,x""#, sum_csv("1,x").is_err(), true);
}
