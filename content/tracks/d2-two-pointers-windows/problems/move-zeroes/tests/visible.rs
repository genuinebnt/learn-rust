use solution::*;

#[test]
fn mixed() {
    check!(r#"nums = [0, 1, 0, 3, 12]"#, { let mut v = [0, 1, 0, 3, 12]; move_zeroes(&mut v); v }, [1, 3, 12, 0, 0]);
}

#[test]
fn single_zero() {
    check!(r#"nums = [0]"#, { let mut v = [0]; move_zeroes(&mut v); v }, [0]);
}

#[test]
fn zero_first() {
    check!(r#"nums = [0, 1]"#, { let mut v = [0, 1]; move_zeroes(&mut v); v }, [1, 0]);
}

#[test]
fn no_zeroes() {
    check!(r#"nums = [1, 2, 3]"#, { let mut v = [1, 2, 3]; move_zeroes(&mut v); v }, [1, 2, 3]);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, { let mut v: [i32; 0] = []; move_zeroes(&mut v); v }, [0i32; 0]);
}
