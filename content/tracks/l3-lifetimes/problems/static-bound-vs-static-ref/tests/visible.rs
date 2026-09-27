use solution::*;

#[test]
fn insert_and_get() {
    let mut ext = Extensions::new();
    ext.insert(5u32);
    ext.insert(format!("run{}", "time"));
    check!(r#"insert 5u32 and a String"#, (ext.get::<u32>(), ext.get::<String>().map(|s| s.as_str()), ext.get::<i64>(), ext.len()), (Some(&5), Some("runtime"), None, 2));
}

#[test]
fn insert_returns_previous() {
    let mut ext = Extensions::new();
    check!(r#"insert 1u8, then 2u8"#, (ext.insert(1u8), ext.insert(2u8), ext.get::<u8>()), (None, Some(1), Some(&2)));
}

#[test]
fn get_mut_edits() {
    let mut ext = Extensions::new();
    ext.insert(vec![1]);
    check!(r#"insert vec![1]; get_mut push 2"#, { ext.get_mut::<Vec<i32>>().unwrap().push(2); ext.get::<Vec<i32>>().cloned() }, Some(vec![1, 2]));
}

#[test]
fn remove_by_value() {
    let mut ext = Extensions::new();
    ext.insert("x".to_string());
    check!(r#"insert a String; remove it"#, (ext.remove::<String>(), ext.remove::<String>(), ext.len()), (Some("x".to_string()), None, 0));
}

#[test]
fn remember_owned_and_static() {
    let mut log: Vec<Box<dyn std::fmt::Debug>> = Vec::new();
    remember(&mut log, String::from("made"));
    remember(&mut log, "literal");
    check!(r#"remember a runtime String and a &'static str"#, format!("{log:?}"), "[\"made\", \"literal\"]");
}

#[test]
fn intern_forever_is_static() {
    let mut ext = Extensions::new();
    ext.insert(intern_forever(String::from("dyn")));
    check!(r#"intern_forever of a runtime String, stored in an Extensions"#, ext.get::<&'static str>().copied(), Some("dyn"));
}
