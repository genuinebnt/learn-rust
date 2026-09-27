use solution::*;

#[test]
fn div_zero() {
    check!(r#"["1","0","/"]"#, eval(&["1", "0", "/"]), Err(RpnError::DivideByZero));
}

#[test]
fn leftover() {
    check!(r#"["1","2"]"#, eval(&["1", "2"]), Err(RpnError::LeftoverOperands));
}

#[test]
fn empty() {
    check!(r#"[]"#, eval(&[]), Err(RpnError::NotEnoughOperands));
}

#[test]
fn min_div_minus_one() {
    check!(r#"["-9223372036854775808","-1","/"]"#, eval(&["-9223372036854775808", "-1", "/"]), Err(RpnError::DivideByZero));
}
