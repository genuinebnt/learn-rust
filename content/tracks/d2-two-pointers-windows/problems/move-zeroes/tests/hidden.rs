use solution::*;

#[test]
fn no_zeroes() {
    check!(r#"nums = [1, 2, 3]"#, { let mut v = [1, 2, 3]; move_zeroes(&mut v); v }, [1, 2, 3]);
}

#[test]
fn negatives() {
    check!(r#"nums = [-1, 0, 0, -2]"#, { let mut v = [-1, 0, 0, -2]; move_zeroes(&mut v); v }, [-1, -2, 0, 0]);
}
