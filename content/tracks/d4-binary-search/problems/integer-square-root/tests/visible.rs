use solution::*;

#[test]
fn eight() {
    check!(r#"8"#, isqrt(8), 2);
}

#[test]
fn perfect() {
    check!(r#"16"#, isqrt(16), 4);
}

#[test]
fn four() {
    check!(r#"4"#, isqrt(4), 2);
}

#[test]
fn zero() {
    check!(r#"0"#, isqrt(0), 0);
}

#[test]
fn just_below_a_square() {
    check!(r#"15"#, isqrt(15), 3);
}
