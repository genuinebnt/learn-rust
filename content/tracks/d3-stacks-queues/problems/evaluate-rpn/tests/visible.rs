use solution::*;

#[test]
fn simple() {
    check!(r#"["2","1","+","3","*"]"#, eval_rpn(&["2", "1", "+", "3", "*"]), 9);
}

#[test]
fn division() {
    check!(r#"["4","13","5","/","+"]"#, eval_rpn(&["4", "13", "5", "/", "+"]), 6);
}
