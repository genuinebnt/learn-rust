use solution::*;

#[test]
fn as_ref_none() {
    check!(r#"None"#, MyOption::<String>::None.as_ref(), MyOption::None);
}

#[test]
fn as_ref_points_inside() {
    check!(r#"Some(String::from("x"))"#, { let o = MyOption::Some(String::from("x")); let same = match (o.as_ref(), &o) { (MyOption::Some(r), MyOption::Some(s)) => std::ptr::eq(r, s), _ => false }; same }, true);
}

#[test]
fn as_mut_none() {
    check!(r#"None"#, { let mut o = MyOption::<i32>::None; let r = o.as_mut() == MyOption::None; (r, o) }, (true, MyOption::None));
}

#[test]
fn insert_overwrites() {
    check!(r#"Some(1), insert(2), then += 10"#, { let mut o = MyOption::Some(1); *o.insert(2) += 10; o }, MyOption::Some(12));
}

#[test]
fn insert_into_none() {
    check!(r#"None, insert(String::from("a")), push 'b'"#, { let mut o = MyOption::None; o.insert(String::from("a")).push('b'); o }, MyOption::Some("ab".to_string()));
}

#[test]
fn flatten_all_shapes() {
    check!(r#"Some(Some(1)), Some(None), None"#, (MyOption::Some(MyOption::Some(1)).flatten(), MyOption::Some(MyOption::<i32>::None).flatten(), MyOption::<MyOption<i32>>::None.flatten()), (MyOption::Some(1), MyOption::None, MyOption::None));
}

#[test]
fn flatten_one_level_only() {
    check!(r#"Some(Some(Some(1)))"#, MyOption::Some(MyOption::Some(MyOption::Some(1))).flatten(), MyOption::Some(MyOption::Some(1)));
}

#[test]
fn copied_from_as_ref() {
    check!(r#"Some(7).as_ref().copied(), None"#, { let o = MyOption::Some(7); (o.as_ref().copied(), MyOption::<&u8>::None.copied(), o) }, (MyOption::Some(7), MyOption::None, MyOption::Some(7)));
}

#[test]
fn replace_none() {
    check!(r#"None, replace("a")"#, { let mut o = MyOption::None; let old = o.replace("a"); (old, o) }, (MyOption::None, MyOption::Some("a")));
}

#[test]
fn get_or_insert_with_keeps_some() {
    check!(r#"Some(3), get_or_insert_with(panics)"#, { let mut o = MyOption::Some(3); let v = *o.get_or_insert_with(|| panic!("should not run")); (v, o) }, (3, MyOption::Some(3)));
}

#[test]
fn get_or_insert_with_calls_once() {
    check!(r#"None, get_or_insert_with twice"#, { let mut calls = 0; let mut o = MyOption::None; o.get_or_insert_with(|| { calls += 1; 7 }); o.get_or_insert_with(|| { calls += 1; 8 }); (o, calls) }, (MyOption::Some(7), 1));
}

#[test]
fn get_or_insert_with_returns_the_slot() {
    check!(r#"Some(vec![1]), push 2 through the reference"#, { let mut o = MyOption::Some(vec![1]); o.get_or_insert_with(Vec::new).push(2); o }, MyOption::Some(vec![1, 2]));
}

#[test]
fn zip_with_none() {
    check!(r#"Some(1) zip None, None zip Some(1)"#, (MyOption::Some(1).zip(MyOption::<u8>::None), MyOption::<u8>::None.zip(MyOption::Some(1))), (MyOption::None, MyOption::None));
}

#[test]
fn inspect_none_skips_f() {
    check!(r#"None.inspect(panics)"#, MyOption::<i32>::None.inspect(|x| panic!("should not run: {x}")), MyOption::None);
}

#[test]
fn inspect_does_not_move_the_value() {
    check!(r#"Some(String::from("hi")).inspect(record the pointer)"#, { let s = String::from("hi"); let p = s.as_ptr(); let mut seen = None; let o = MyOption::Some(s).inspect(|v| seen = Some(v.as_ptr())); (seen == Some(p), o) }, (true, MyOption::Some("hi".to_string())));
}

#[test]
fn map_or_else_some_skips_default() {
    check!(r#"Some(4)"#, MyOption::Some(4).map_or_else(|| panic!("should not run"), |x| x * 2), 8);
}

#[test]
fn map_or_else_none_skips_f() {
    check!(r#"None"#, MyOption::<i32>::None.map_or_else(|| 0, |x| -> i32 { panic!("should not run: {x}") }), 0);
}

#[test]
fn map_or_else_moves_the_value() {
    check!(r#"Some(String::from("abc"))"#, MyOption::Some(String::from("abc")).map_or_else(String::new, |s| s + "!"), "abc!".to_string());
}

fn mine<T>(o: Option<T>) -> MyOption<T> {
    match o {
        Some(v) => MyOption::Some(v),
        None => MyOption::None,
    }
}

#[test]
fn random_vs_std_option() {
    let mut rng = anneal_prelude::Rng::new(1316);
    for _ in 0..300 {
        let a = if rng.bool() { Some(rng.int(-5, 5) as i32) } else { None };
        let b = if rng.bool() { Some(rng.int(-5, 5) as i32) } else { None };
        let d = rng.int(-5, 5) as i32;
        let desc = format!("a = {a:?}, b = {b:?}, d = {d}");
        let m = mine(a);
        check!(format!("as_ref, {desc}"), m.as_ref(), mine(a.as_ref()));
        let (mut m, mut s) = (mine(a), a);
        if let MyOption::Some(x) = m.as_mut() {
            *x += d;
        }
        if let Some(x) = s.as_mut() {
            *x += d;
        }
        check!(format!("as_mut then += d, {desc}"), m, mine(s));
        let (mut m, mut s) = (mine(a), a);
        check!(format!("replace(d), {desc}"), (m.replace(d), m), (mine(s.replace(d)), mine(s)));
        let (mut m, mut s) = (mine(a), a);
        let (mut calls_m, mut calls_s) = (0, 0);
        let got = *m.get_or_insert_with(|| { calls_m += 1; d });
        let want = *s.get_or_insert_with(|| { calls_s += 1; d });
        check!(format!("get_or_insert_with(d), {desc}"), (got, m, calls_m), (want, mine(s), calls_s));
        check!(format!("a.zip(b), {desc}"), mine(a).zip(mine(b)), mine(a.zip(b)));
        let (mut seen_m, mut seen_s) = (Vec::new(), Vec::new());
        check!(format!("inspect(log), {desc}"), mine(a).inspect(|x| seen_m.push(*x)), mine(a.inspect(|x| seen_s.push(*x))));
        check!(format!("inspect calls, {desc}"), seen_m, seen_s);
        check!(format!("map_or_else(d, x * 3), {desc}"), mine(a).map_or_else(|| d, |x| x * 3), a.map_or_else(|| d, |x| x * 3));
        let (mut m, mut s) = (mine(a), a);
        check!(format!("insert(d), {desc}"), (*m.insert(d), m), (*s.insert(d), mine(s)));
        let nested = if rng.bool() { Some(b) } else { None };
        check!(format!("flatten, nested = {nested:?}"), mine(nested.map(mine)).flatten(), mine(nested.flatten()));
        check!(format!("as_ref().copied(), {desc}"), mine(a).as_ref().copied(), mine(a.as_ref().copied()));
    }
}
