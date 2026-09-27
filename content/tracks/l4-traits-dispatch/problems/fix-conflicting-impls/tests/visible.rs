use solution::*;

#[test]
fn numbers_and_text() {
    check!(r#"5, 2.5, "hi", String "s", 'c', true"#, (5i32.label(), 2.5f64.label(), "hi".label(), String::from("s").label(), 'c'.label(), true.label()), ("5".to_string(), "2.5".to_string(), "hi".to_string(), "s".to_string(), "c".to_string(), "true".to_string()));
}

#[test]
fn vec_of_str() {
    check!(r#"vec!["a", "b"]"#, vec!["a", "b"].label(), "[a, b]");
}

#[test]
fn nested() {
    check!(r#"vec![vec![1], vec![]]"#, vec![vec![1i32], vec![]].label(), "[[1], []]");
}

#[test]
fn options() {
    check!(r#"vec![Some(1), None]"#, vec![Some(1i64), None].label(), "[1, -]");
}

#[test]
fn outside_type() {
    struct Money(i64);
    impl Label for Money {
        fn label(&self) -> String {
            format!("${}", self.0)
        }
    }
    check!("vec![Some(Money(5)), None]", vec![Some(Money(5)), None].label(), "[$5, -]");
}
