use solution::*;

#[test]
fn unwrap_or_default() {
    check!(r#"None::<String>, Some("x"), None::<Vec<u8>>"#, (MyOption::<String>::None.unwrap_or_default(), MyOption::Some("x".to_string()).unwrap_or_default(), MyOption::<Vec<u8>>::None.unwrap_or_default()), (String::new(), "x".to_string(), Vec::new()));
}

#[test]
fn unwrap_or_else_lazy() {
    check!(r#"Some(1)"#, MyOption::Some(1).unwrap_or_else(|| panic!("should not run")), 1);
}

#[test]
fn unwrap_or_else_none() {
    check!(r#"None"#, MyOption::None.unwrap_or_else(|| 9), 9);
}

#[test]
fn or_else_keeps_some_and_skips_f() {
    check!(r#"Some(1).or_else(panics)"#, MyOption::Some(1).or_else(|| panic!("should not run")), MyOption::Some(1));
}

#[test]
fn or_else_both_none() {
    check!(r#"None.or_else(|| None)"#, MyOption::<i32>::None.or_else(|| MyOption::None), MyOption::None);
}

#[test]
fn and_with_none() {
    check!(r#"Some(1).and(None), None.and(Some(2))"#, (MyOption::Some(1).and(MyOption::<u8>::None), MyOption::<i32>::None.and(MyOption::Some(2u8))), (MyOption::None, MyOption::None));
}

#[test]
fn and_changes_type() {
    check!(r#"Some("s").and(Some(5u64))"#, MyOption::Some("s").and(MyOption::Some(5u64)), MyOption::Some(5u64));
}

#[test]
fn is_some_and_skips_f_on_none() {
    check!(r#"None.is_some_and(panics)"#, MyOption::<i32>::None.is_some_and(|x| panic!("should not run: {x}")), false);
}

#[test]
fn is_some_and_takes_ownership() {
    check!(r#"Some(String::from("hi")).is_some_and(|s| s.len() == 2)"#, MyOption::Some(String::from("hi")).is_some_and(|s: String| s.len() == 2), true);
}

#[test]
fn filter() {
    check!(r#"Some(4), Some(5), None"#, (MyOption::Some(4).filter(|x| x % 2 == 0), MyOption::Some(5).filter(|x| x % 2 == 0), MyOption::<i32>::None.filter(|x| panic!("should not run: {x}"))), (MyOption::Some(4), MyOption::None, MyOption::None));
}

#[test]
fn map_changes_type_and_skips_none() {
    check!(r#"Some("abc").map(len), None.map(panics)"#, (MyOption::Some("abc").map(str::len), MyOption::<i32>::None.map(|x| -> i32 { panic!("should not run: {x}") })), (MyOption::Some(3), MyOption::None));
}

#[test]
fn and_then_none_skips_f() {
    check!(r#"None"#, MyOption::<i32>::None.and_then(|x| -> MyOption<i32> { panic!("should not run: {x}") }), MyOption::None);
}

#[test]
fn take_none() {
    check!(r#"None"#, { let mut o = MyOption::<i32>::None; let t = o.take(); (t, o) }, (MyOption::None, MyOption::None));
}

#[test]
fn take_moves_a_string() {
    check!(r#"Some(String::from("hi"))"#, { let mut o = MyOption::Some(String::from("hi")); let t = o.take(); (t, o) }, (MyOption::Some("hi".to_string()), MyOption::None));
}

#[test]
fn iter_stops_after_one() {
    check!(r#"Some(1).iter(), next() three times"#, { let o = MyOption::Some(1); let mut it = o.iter(); (it.next().copied(), it.next().copied(), it.next().copied()) }, (Some(1), None, None));
}

#[test]
fn iter_borrows_in_place() {
    check!(r#"Some(String::from("x")).iter()"#, { let o = MyOption::Some(String::from("x")); let p = o.iter().next().map(|s| s.as_ptr()); let q = match &o { MyOption::Some(s) => Some(s.as_ptr()), MyOption::None => None }; p == q && p.is_some() }, true);
}

#[test]
fn iter_chains_like_std() {
    check!(r#"[Some(1), None, Some(3)] flattened through iter()"#, [MyOption::Some(1), MyOption::None, MyOption::Some(3)].iter().flat_map(|o| o.iter()).copied().take(5).collect::<Vec<_>>(), vec![1, 3]);
}

fn mine<T>(o: Option<T>) -> MyOption<T> {
    match o {
        Some(v) => MyOption::Some(v),
        None => MyOption::None,
    }
}

#[test]
fn random_vs_std_option() {
    let mut rng = anneal_prelude::Rng::new(7110);
    for _ in 0..300 {
        let a = if rng.bool() { Some(rng.int(-5, 5) as i32) } else { None };
        let b = if rng.bool() { Some(rng.int(-5, 5) as i32) } else { None };
        let d = rng.int(-5, 5) as i32;
        let desc = format!("a = {a:?}, b = {b:?}, d = {d}");
        let mut calls = (0, 0);
        check!(format!("is_some_and(x > d), {desc}"), mine(a).is_some_and(|x| { calls.0 += 1; x > d }), a.is_some_and(|x| { calls.1 += 1; x > d }));
        let mut calls2 = (0, 0);
        check!(format!("unwrap_or_else(|| d), {desc}"), mine(a).unwrap_or_else(|| { calls2.0 += 1; d }), a.unwrap_or_else(|| { calls2.1 += 1; d }));
        check!(format!("unwrap_or_default, {desc}"), mine(a).unwrap_or_default(), a.unwrap_or_default());
        check!(format!("map(x + d), {desc}"), mine(a).map(|x| x + d), mine(a.map(|x| x + d)));
        check!(format!("and_then(positive), {desc}"), mine(a).and_then(|x| if x > 0 { MyOption::Some(x * 3) } else { MyOption::None }), mine(a.and_then(|x| if x > 0 { Some(x * 3) } else { None })));
        check!(format!("a.and(b), {desc}"), mine(a).and(mine(b)), mine(a.and(b)));
        let mut calls3 = (0, 0);
        check!(format!("a.or_else(|| b), {desc}"), mine(a).or_else(|| { calls3.0 += 1; mine(b) }), mine(a.or_else(|| { calls3.1 += 1; b })));
        check!(format!("filter(even), {desc}"), mine(a).filter(|x| x % 2 == 0), mine(a.filter(|x| x % 2 == 0)));
        let mut m = mine(a);
        let mut s = a;
        check!(format!("take, {desc}"), (m.take(), m), (mine(s.take()), mine(s)));
        check!(format!("iter, {desc}"), mine(a).iter().copied().take(5).collect::<Vec<_>>(), a.iter().copied().collect::<Vec<_>>());
        check!(format!("closure calls, {desc}"), (calls.0, calls2.0, calls3.0), (calls.1, calls2.1, calls3.1));
    }
}
