use solution::*;

#[test]
fn is_some_none() {
    check!(r#"Some(1), None"#, (MyOption::Some(1).is_some(), MyOption::<i32>::None.is_none()), (true, true));
}

#[test]
fn map_and_then() {
    check!(r#"Some(2)"#, MyOption::Some(2).map(|x| x * 10).and_then(|x| if x > 5 { MyOption::Some(x + 1) } else { MyOption::None }), MyOption::Some(21));
}

#[test]
fn unwrap_or() {
    check!(r#"None"#, MyOption::None.unwrap_or(7), 7);
}

#[test]
fn take() {
    check!(r#"Some("a")"#, { let mut o = MyOption::Some("a"); let t = o.take(); (t, o) }, (MyOption::Some("a"), MyOption::None));
}

#[test]
fn or_keeps_the_first() {
    check!(r#"Some(1) or Some(2)"#, MyOption::Some(1).or(MyOption::Some(2)), MyOption::Some(1));
}
