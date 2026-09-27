use solution::*;

#[test]
fn map_and_then() {
    check!(r#"Some(2)"#, MyOption::Some(2).map(|x| x * 10).and_then(|x| if x > 5 { MyOption::Some(x + 1) } else { MyOption::None }), MyOption::Some(21));
}

#[test]
fn is_some_and() {
    check!(r#"Some(4), Some(5), None"#, (MyOption::Some(4).is_some_and(|x| x % 2 == 0), MyOption::Some(5).is_some_and(|x| x % 2 == 0), MyOption::<i32>::None.is_some_and(|_| true)), (true, false, false));
}

#[test]
fn take() {
    check!(r#"Some("a")"#, { let mut o = MyOption::Some("a"); let t = o.take(); (t, o) }, (MyOption::Some("a"), MyOption::None));
}

#[test]
fn and_or_else() {
    check!(r#"Some(1).and(Some("x")), None.or_else(|| Some(3))"#, (MyOption::Some(1).and(MyOption::Some("x")), MyOption::None.or_else(|| MyOption::Some(3))), (MyOption::Some("x"), MyOption::Some(3)));
}

#[test]
fn iter_yields_once() {
    check!(r#"Some(7).iter(), None.iter()"#, (MyOption::Some(7).iter().copied().take(5).collect::<Vec<_>>(), MyOption::<i32>::None.iter().take(5).count()), (vec![7], 0));
}
