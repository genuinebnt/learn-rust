use solution::*;

#[test]
fn halves_to_zero() {
    check!(r#"[1, 2]"#, { let mut v = vec![1, 2]; drop_zeros_and_halve(&mut v); v }, vec![0, 1]);
}
