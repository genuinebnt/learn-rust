use solution::*;

#[test]
fn hello() {
    check!(r#"s = b"hello""#, { let mut s = b"hello".to_vec(); reverse_in_place(&mut s); s }, b"olleh".to_vec());
}

#[test]
fn even() {
    check!(r#"s = b"ab""#, { let mut s = b"ab".to_vec(); reverse_in_place(&mut s); s }, b"ba".to_vec());
}

#[test]
fn even_four() {
    check!(r#"s = b"abcd""#, { let mut s = b"abcd".to_vec(); reverse_in_place(&mut s); s }, b"dcba".to_vec());
}

#[test]
fn hannah() {
    check!(r#"s = b"Hannah""#, { let mut s = b"Hannah".to_vec(); reverse_in_place(&mut s); s }, b"hannaH".to_vec());
}

#[test]
fn empty() {
    check!(r#"s = b"""#, { let mut s: Vec<u8> = vec![]; reverse_in_place(&mut s); s }, Vec::<u8>::new());
}

#[test]
fn single() {
    check!(r#"s = b"x""#, { let mut s = b"x".to_vec(); reverse_in_place(&mut s); s }, b"x".to_vec());
}
