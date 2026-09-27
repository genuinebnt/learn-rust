use solution::*;

#[test]
fn mixed() {
    check!(r#"v = [1, 1, -2, 1, 3, 3, -3, 3]"#, { let mut v = vec![1, 1, -2, 1, 3, 3, -3, 3]; clean(&mut v); v }, vec![1, 3]);
}

#[test]
fn no_change() {
    check!(r#"v = [1, 2]"#, { let mut v = vec![1, 2]; clean(&mut v); v }, vec![1, 2]);
}

#[test]
fn empty() {
    check!(r#"v = []"#, { let mut v: Vec<i32> = vec![]; clean(&mut v); v }, Vec::<i32>::new());
}

#[test]
fn all_same() {
    check!(r#"v = [2, 2, 2]"#, { let mut v = vec![2, 2, 2]; clean(&mut v); v }, vec![2]);
}

#[test]
fn zero_is_kept() {
    check!(r#"v = [0, -1, 0]"#, { let mut v = vec![0, -1, 0]; clean(&mut v); v }, vec![0]);
}
