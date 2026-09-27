use solution::*;

#[test]
fn run() {
    check!(r#"[5,7,7,8,8,10], 8"#, search_range(&[5, 7, 7, 8, 8, 10], 8), Some((3, 4)));
}

#[test]
fn missing() {
    check!(r#"[5,7,7,8,8,10], 6"#, search_range(&[5, 7, 7, 8, 8, 10], 6), None);
}
