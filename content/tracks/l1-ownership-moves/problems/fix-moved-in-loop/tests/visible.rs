use solution::*;

#[test]
fn three() {
    check!(r#"name = "ann""#, { let mut out = vec![]; greet_thrice("ann".into(), &mut out); out }, vec!["hello, ann"; 3]);
}

#[test]
fn appends() {
    check!(r#"out already holds one line"#, { let mut out = vec!["hi".to_string()]; greet_thrice("bo".into(), &mut out); out.len() }, 4);
}

#[test]
fn unicode_name() {
    check!(r#"name = "zoë""#, { let mut out = vec![]; greet_thrice("zoë".into(), &mut out); out }, vec!["hello, zoë"; 3]);
}

#[test]
fn empty_name_visible() {
    check!(r#"name = """#, { let mut out = vec![]; greet_thrice(String::new(), &mut out); out }, vec!["hello, "; 3]);
}

#[test]
fn existing_line_kept() {
    check!(r#"out = ["x"], name = "kim""#, { let mut out = vec!["x".to_string()]; greet_thrice("kim".into(), &mut out); out }, vec!["x", "hello, kim", "hello, kim", "hello, kim"]);
}
