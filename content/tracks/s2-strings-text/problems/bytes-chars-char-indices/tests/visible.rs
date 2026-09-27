use solution::*;

#[test]
fn naive() {
    check!(r#""naïve""#, sizes("naïve"), (6, 5));
}

#[test]
fn byte_offsets() {
    check!(r#""añoño", 'ñ'"#, positions("añoño", 'ñ'), vec![1, 4]);
}
