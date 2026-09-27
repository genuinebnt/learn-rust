use solution::*;

#[test]
fn even() {
    check!(r#"v = [1, 2, 10, 20]"#, { let mut v = [1, 2, 10, 20]; add_halves(&mut v); v }, [1, 2, 11, 22]);
}

#[test]
fn odd() {
    check!(r#"v = [1, 5, 5]"#, { let mut v = [1, 5, 5]; add_halves(&mut v); v }, [1, 6, 5]);
}

#[test]
fn two() {
    check!(r#"v = [1, 2]"#, { let mut v = [1, 2]; add_halves(&mut v); v }, [1, 3]);
}

#[test]
fn five() {
    check!(r#"v = [1, 2, 3, 4, 5] (mid = 2, the last value is untouched)"#, { let mut v = [1, 2, 3, 4, 5]; add_halves(&mut v); v }, [1, 2, 4, 6, 5]);
}

#[test]
fn negatives() {
    check!(r#"v = [-1, -2, 1, 2]"#, { let mut v = [-1, -2, 1, 2]; add_halves(&mut v); v }, [-1, -2, 0, 0]);
}
