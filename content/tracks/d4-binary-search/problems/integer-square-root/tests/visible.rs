use solution::*;

#[test]
fn eight() {
    check!(r#"8"#, isqrt(8), 2);
}

#[test]
fn perfect() {
    check!(r#"16"#, isqrt(16), 4);
}
