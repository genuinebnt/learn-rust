use solution::*;

#[test]
fn plus() {
    check!(r#""1 + 1""#, calculate("1 + 1"), 2);
}

#[test]
fn spaces() {
    check!(r#"" 2-1 + 2 ""#, calculate(" 2-1 + 2 "), 3);
}

#[test]
fn parens() {
    check!(r#""(1+(4+5+2)-3)+(6+8)""#, calculate("(1+(4+5+2)-3)+(6+8)"), 23);
}

#[test]
fn unary() {
    check!(r#""-(2+3)""#, calculate("-(2+3)"), -5);
}

#[test]
fn double_negative() {
    check!(r#""1-(     -2)""#, calculate("1-(     -2)"), 3);
}
