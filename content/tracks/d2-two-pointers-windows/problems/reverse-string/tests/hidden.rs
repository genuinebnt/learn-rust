use solution::*;

#[test]
fn empty() {
    check!(r#"s = b"""#, { let mut s: Vec<u8> = vec![]; reverse_in_place(&mut s); s }, Vec::<u8>::new());
}

#[test]
fn single() {
    check!(r#"s = b"x""#, { let mut s = b"x".to_vec(); reverse_in_place(&mut s); s }, b"x".to_vec());
}
