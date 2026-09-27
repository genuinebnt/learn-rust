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

#[test]
fn is_some_is_none_false() {
    check!(r#"None, Some(1)"#, (MyOption::<i32>::None.is_some(), MyOption::Some(1).is_none()), (false, false));
}

#[test]
fn unwrap_or_some() {
    check!(r#"Some(5)"#, MyOption::Some(5).unwrap_or(7), 5);
}

#[test]
fn unwrap_or_else_none() {
    check!(r#"None"#, MyOption::None.unwrap_or_else(|| 9), 9);
}

#[test]
fn map_changes_type() {
    check!(r#"Some("abc")"#, MyOption::Some("abc").map(str::len), MyOption::Some(3));
}

#[test]
fn map_none_skips_f() {
    check!(r#"None"#, MyOption::<i32>::None.map(|x| -> i32 { panic!("should not run: {x}") }), MyOption::None);
}

#[test]
fn and_then_none_skips_f() {
    check!(r#"None"#, MyOption::<i32>::None.and_then(|x| -> MyOption<i32> { panic!("should not run: {x}") }), MyOption::None);
}

#[test]
fn and_then_to_none() {
    check!(r#"Some(1)"#, MyOption::Some(1).and_then(|_| MyOption::<i32>::None), MyOption::None);
}

#[test]
fn or_both_none() {
    check!(r#"None or None"#, MyOption::<i32>::None.or(MyOption::None), MyOption::None);
}

#[test]
fn ok_or_some() {
    check!(r#"Some(3)"#, MyOption::Some(3).ok_or("missing"), Ok(3));
}

#[test]
fn filter_none_skips_keep() {
    check!(r#"None"#, MyOption::<i32>::None.filter(|x| panic!("should not run: {x}")), MyOption::None);
}

#[test]
fn take_none() {
    check!(r#"None"#, { let mut o = MyOption::<i32>::None; let t = o.take(); (t, o) }, (MyOption::None, MyOption::None));
}

#[test]
fn take_moves_a_string() {
    check!(r#"Some(String::from("hi"))"#, { let mut o = MyOption::Some(String::from("hi")); let t = o.take(); (t, o) }, (MyOption::Some("hi".to_string()), MyOption::None));
}

fn mine(o: Option<i32>) -> MyOption<i32> {
    match o {
        Some(v) => MyOption::Some(v),
        None => MyOption::None,
    }
}

#[test]
fn random_vs_std_option() {
    let mut rng = anneal_prelude::Rng::new(1309);
    for _ in 0..300 {
        let a = if rng.bool() { Some(rng.int(-5, 5) as i32) } else { None };
        let b = if rng.bool() { Some(rng.int(-5, 5) as i32) } else { None };
        let d = rng.int(-5, 5) as i32;
        let desc = format!("a = {a:?}, b = {b:?}, default = {d}");
        check!(format!("is_some/is_none, {desc}"), (mine(a).is_some(), mine(a).is_none()), (a.is_some(), a.is_none()));
        check!(format!("unwrap_or, {desc}"), mine(a).unwrap_or(d), a.unwrap_or(d));
        check!(format!("unwrap_or_else, {desc}"), mine(a).unwrap_or_else(|| d * 2), a.unwrap_or_else(|| d * 2));
        check!(format!("map(x + d), {desc}"), mine(a).map(|x| x + d), mine(a.map(|x| x + d)));
        check!(format!("and_then(positive), {desc}"), mine(a).and_then(|x| if x > 0 { MyOption::Some(x * 3) } else { MyOption::None }), mine(a.and_then(|x| if x > 0 { Some(x * 3) } else { None })));
        check!(format!("a.or(b), {desc}"), mine(a).or(mine(b)), mine(a.or(b)));
        check!(format!("ok_or(d), {desc}"), mine(a).ok_or(d), a.ok_or(d));
        check!(format!("filter(even), {desc}"), mine(a).filter(|x| x % 2 == 0), mine(a.filter(|x| x % 2 == 0)));
        let mut m = mine(a);
        let mut s = a;
        check!(format!("take, {desc}"), (m.take(), m), (mine(s.take()), mine(s)));
    }
}
