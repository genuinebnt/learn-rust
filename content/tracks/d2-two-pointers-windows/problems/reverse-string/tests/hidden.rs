use solution::*;

#[test]
fn empty() {
    check!(r#"s = b"""#, { let mut s: Vec<u8> = vec![]; reverse_in_place(&mut s); s }, Vec::<u8>::new());
}

#[test]
fn single() {
    check!(r#"s = b"x""#, { let mut s = b"x".to_vec(); reverse_in_place(&mut s); s }, b"x".to_vec());
}

#[test]
fn odd_three() {
    check!(r#"s = b"abc""#, { let mut s = b"abc".to_vec(); reverse_in_place(&mut s); s }, b"cba".to_vec());
}

#[test]
fn palindrome() {
    check!(r#"s = b"racecar""#, { let mut s = b"racecar".to_vec(); reverse_in_place(&mut s); s }, b"racecar".to_vec());
}

#[test]
fn all_same() {
    check!(r#"s = b"zzzz""#, { let mut s = b"zzzz".to_vec(); reverse_in_place(&mut s); s }, b"zzzz".to_vec());
}

#[test]
fn utf8_bytes() {
    check!(r#"s = "é!".as_bytes() = [0xC3, 0xA9, 0x21]"#, { let mut s = "é!".as_bytes().to_vec(); reverse_in_place(&mut s); s }, vec![0x21, 0xA9, 0xC3]);
}

#[test]
fn extreme_bytes() {
    check!(r#"s = [0, 255, 128]"#, { let mut s = vec![0u8, 255, 128]; reverse_in_place(&mut s); s }, vec![128u8, 255, 0]);
}

#[test]
fn five() {
    check!(r#"s = b"hello""#, { let mut s = b"hello".to_vec(); reverse_in_place(&mut s); s }, b"olleh".to_vec());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(202);
    for _ in 0..300 {
        let n = rng.below(16);
        let s: Vec<u8> = rng.vec(n, 0, 255);
        let want: Vec<u8> = s.iter().rev().copied().collect();
        let mut got = s.clone();
        reverse_in_place(&mut got);
        check!(format!("s = {s:?}"), got, want);
    }
}

#[test]
fn scale_200k() {
    let s: Vec<u8> = (0..200_000u32).map(|i| (i % 251) as u8).collect();
    let want: Vec<u8> = s.iter().rev().copied().collect();
    let mut got = s.clone();
    reverse_in_place(&mut got);
    check!("s = [i % 251 for i in 0..200000]", got == want, true);
}
