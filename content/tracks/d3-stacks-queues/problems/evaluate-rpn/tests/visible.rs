use solution::*;

#[test]
fn simple() {
    check!(r#"["2","1","+","3","*"]"#, eval_rpn(&["2", "1", "+", "3", "*"]), 9);
}

#[test]
fn division() {
    check!(r#"["4","13","5","/","+"]"#, eval_rpn(&["4", "13", "5", "/", "+"]), 6);
}

#[test]
fn long() {
    check!(r#"["10","6","9","3","+","-11","*","/","*","17","+","5","+"]"#, eval_rpn(&["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]), 22);
}

#[test]
fn order_matters() {
    check!(r#"["3","5","-"]"#, eval_rpn(&["3", "5", "-"]), -2);
}

#[test]
fn negative_division_truncates() {
    check!(r#"["-7","2","/"]"#, eval_rpn(&["-7", "2", "/"]), -3);
}
