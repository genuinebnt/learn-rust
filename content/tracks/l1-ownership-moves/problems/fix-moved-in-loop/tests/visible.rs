use solution::*;

#[test]
fn three() {
    check!(r#"name = "ann""#, { let mut out = vec![]; greet_thrice("ann".into(), &mut out); out }, vec!["hello, ann"; 3]);
}

#[test]
fn appends() {
    check!(r#"out already holds one line"#, { let mut out = vec!["hi".to_string()]; greet_thrice("bo".into(), &mut out); out.len() }, 4);
}
