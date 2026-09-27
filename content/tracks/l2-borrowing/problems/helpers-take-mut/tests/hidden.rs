use solution::*;

#[test]
fn different() {
    check!(r#""a", "b""#, { let (mut a, mut b) = ("a".to_string(), "b".to_string()); same_after_normalizing(&mut a, &mut b) }, false);
}
