use solution::*;

#[test]
fn tie() {
    check!(r#""x y y x""#, most_repeated("x y y x"), Some("x"));
}
