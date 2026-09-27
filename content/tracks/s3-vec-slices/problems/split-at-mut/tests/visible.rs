use solution::*;

#[test]
fn even() {
    check!(r#"v = [1, 2, 10, 20]"#, { let mut v = [1, 2, 10, 20]; add_halves(&mut v); v }, [1, 2, 11, 22]);
}

#[test]
fn odd() {
    check!(r#"v = [1, 5, 5]"#, { let mut v = [1, 5, 5]; add_halves(&mut v); v }, [1, 6, 5]);
}
