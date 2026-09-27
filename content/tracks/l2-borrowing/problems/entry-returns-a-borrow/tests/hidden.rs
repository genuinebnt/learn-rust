use solution::*;

#[test]
fn separate_keys() {
    check!(r#""a" and "b""#, { let mut m = std::collections::HashMap::new(); get_or_create(&mut m, "a").push(1); get_or_create(&mut m, "b"); m.len() }, 2);
}
