use solution::*;

#[test]
fn big() {
    check!(r#"v = 0..1000"#, { let mut v: Vec<i32> = (0..1000).collect(); double_up(&mut v); (v.len(), v[1000], v[1999]) }, (2000, 0, 999));
}
