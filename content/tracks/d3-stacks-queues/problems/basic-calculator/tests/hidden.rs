use solution::*;

#[test]
fn unary() {
    check!(r#""-(2+3)""#, calculate("-(2+3)"), -5);
}

#[test]
fn nested_unary() {
    check!(r#""- (3 + (4 + 5))""#, calculate("- (3 + (4 + 5))"), -12);
}

#[test]
fn double_negative() {
    check!(r#""1-(     -2)""#, calculate("1-(     -2)"), 3);
}

#[test]
fn deep() {
    let s = format!("{}1{}", "(".repeat(5000), ")".repeat(5000));
    check!(r#"5000 nested parentheses around 1"#, calculate(&s), 1);
}
