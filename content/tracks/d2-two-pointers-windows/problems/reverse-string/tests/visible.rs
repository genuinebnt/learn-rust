use solution::*;

#[test]
fn hello() {
    check!(r#"s = b"hello""#, { let mut s = b"hello".to_vec(); reverse_in_place(&mut s); s }, b"olleh".to_vec());
}

#[test]
fn even() {
    check!(r#"s = b"ab""#, { let mut s = b"ab".to_vec(); reverse_in_place(&mut s); s }, b"ba".to_vec());
}
