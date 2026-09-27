use solution::*;

#[test]
fn naive() {
    check!(r#""naïve""#, sizes("naïve"), (6, 5));
}

#[test]
fn byte_offsets() {
    check!(r#""añoño", 'ñ'"#, positions("añoño", 'ñ'), vec![1, 4]);
}

#[test]
fn ascii_sizes() {
    check!(r#""abc""#, sizes("abc"), (3, 3));
}

#[test]
fn nth_is_by_char() {
    check!(r#""héllo", 2"#, nth_char("héllo", 2), Some('l'));
}

#[test]
fn no_occurrence() {
    check!(r#""abc", 'z'"#, positions("abc", 'z'), Vec::<usize>::new());
}
