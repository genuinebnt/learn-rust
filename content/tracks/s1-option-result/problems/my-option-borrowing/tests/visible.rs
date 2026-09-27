use solution::*;

#[test]
fn as_ref_borrows() {
    check!(r#"Some(String::from("hi"))"#, { let o = MyOption::Some(String::from("hi")); let r = o.as_ref() == MyOption::Some(&"hi".to_string()); (r, o) }, (true, MyOption::Some("hi".to_string())));
}

#[test]
fn as_mut_edits_in_place() {
    check!(r#"Some(String::from("hi")), push '!'"#, { let mut o = MyOption::Some(String::from("hi")); if let MyOption::Some(s) = o.as_mut() { s.push('!'); } o }, MyOption::Some("hi!".to_string()));
}

#[test]
fn replace_returns_the_old_value() {
    check!(r#"Some(1), replace(2)"#, { let mut o = MyOption::Some(1); let old = o.replace(2); (old, o) }, (MyOption::Some(1), MyOption::Some(2)));
}

#[test]
fn get_or_insert_with_fills_none() {
    check!(r#"None, get_or_insert_with(|| 5), then += 1"#, { let mut o = MyOption::None; *o.get_or_insert_with(|| 5) += 1; o }, MyOption::Some(6));
}

#[test]
fn zip_inspect_map_or_else() {
    check!(r#"Some(1).zip(Some("a")), Some(5).inspect(log), None.map_or_else(|| -1, ..)"#, { let mut seen = Vec::new(); let r = (MyOption::Some(1).zip(MyOption::Some("a")), MyOption::Some(5).inspect(|x| seen.push(*x)), MyOption::<i32>::None.map_or_else(|| -1, |x| x * 2)); (r, seen) }, ((MyOption::Some((1, "a")), MyOption::Some(5), -1), vec![5]));
}
