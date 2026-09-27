use solution::*;

#[test]
fn mixed() {
    check!(r#"nums = [0, 1, 0, 3, 12]"#, { let mut v = [0, 1, 0, 3, 12]; move_zeroes(&mut v); v }, [1, 3, 12, 0, 0]);
}

#[test]
fn single_zero() {
    check!(r#"nums = [0]"#, { let mut v = [0]; move_zeroes(&mut v); v }, [0]);
}
