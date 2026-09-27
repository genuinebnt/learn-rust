use solution::*;

#[test]
fn or() {
    check!(r#"None or Some(3)"#, MyOption::None.or(MyOption::Some(3)), MyOption::Some(3));
}

#[test]
fn ok_or() {
    check!(r#"None"#, MyOption::<u8>::None.ok_or("missing"), Err("missing"));
}

#[test]
fn filter() {
    check!(r#"Some(4), Some(5)"#, (MyOption::Some(4).filter(|x| x % 2 == 0), MyOption::Some(5).filter(|x| x % 2 == 0)), (MyOption::Some(4), MyOption::None));
}

#[test]
fn unwrap_or_else_lazy() {
    check!(r#"Some(1)"#, MyOption::Some(1).unwrap_or_else(|| panic!("should not run")), 1);
}
