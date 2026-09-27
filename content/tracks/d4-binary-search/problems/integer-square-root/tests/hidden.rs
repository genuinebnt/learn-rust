use solution::*;

#[test]
fn zero_one() {
    check!(r#"0 and 1"#, (isqrt(0), isqrt(1)), (0, 1));
}

#[test]
fn max() {
    check!(r#"u64::MAX"#, isqrt(u64::MAX), 4_294_967_295);
}

#[test]
fn near_square() {
    check!(r#"(2³² − 1)² and one less"#, (isqrt(18_446_744_065_119_617_025), isqrt(18_446_744_065_119_617_024)), (4_294_967_295, 4_294_967_294));
}
