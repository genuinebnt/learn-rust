use solution::*;

#[test]
fn ok() {
    check!(r#"["2","1","+","3","*"]"#, eval(&["2", "1", "+", "3", "*"]), Ok(9));
}

#[test]
fn underflow() {
    check!(r#"["+"]"#, eval(&["+"]), Err(RpnError::NotEnoughOperands));
}

#[test]
fn bad_token() {
    check!(r#"["1","x","+"]"#, eval(&["1", "x", "+"]), Err(RpnError::BadToken("x".to_string())));
}

#[test]
fn div_zero() {
    check!(r#"["1","0","/"]"#, eval(&["1", "0", "/"]), Err(RpnError::DivideByZero));
}

#[test]
fn leftover() {
    check!(r#"["1","2"]"#, eval(&["1", "2"]), Err(RpnError::LeftoverOperands));
}
