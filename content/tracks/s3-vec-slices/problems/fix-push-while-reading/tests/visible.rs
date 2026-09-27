use solution::*;

#[test]
fn two() {
    check!(r#"v = [1, 2]"#, { let mut v = vec![1, 2]; double_up(&mut v); v }, vec![1, 2, 1, 2]);
}

#[test]
fn empty() {
    check!(r#"v = []"#, { let mut v: Vec<i32> = vec![]; double_up(&mut v); v }, Vec::<i32>::new());
}
