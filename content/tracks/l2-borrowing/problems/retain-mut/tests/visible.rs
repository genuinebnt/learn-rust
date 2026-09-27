use solution::*;

#[test]
fn mixed() {
    check!(r#"[4, 0, 6, 0]"#, { let mut v = vec![4, 0, 6, 0]; drop_zeros_and_halve(&mut v); v }, vec![2, 3]);
}

#[test]
fn all_zero() {
    check!(r#"[0, 0]"#, { let mut v = vec![0, 0]; drop_zeros_and_halve(&mut v); v }, vec![]);
}

#[test]
fn negatives() {
    check!(r#"[-3, 0, -4]"#, { let mut v = vec![-3, 0, -4]; drop_zeros_and_halve(&mut v); v }, vec![-1, -2]);
}

#[test]
fn halves_to_zero() {
    check!(r#"[1, 2]"#, { let mut v = vec![1, 2]; drop_zeros_and_halve(&mut v); v }, vec![0, 1]);
}

#[test]
fn empty() {
    check!(r#"[]"#, { let mut v: Vec<i32> = vec![]; drop_zeros_and_halve(&mut v); v }, Vec::<i32>::new());
}
