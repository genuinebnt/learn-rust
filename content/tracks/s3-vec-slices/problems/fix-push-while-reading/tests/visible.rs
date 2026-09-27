use solution::*;

#[test]
fn two() {
    check!(r#"v = [1, 2]"#, { let mut v = vec![1, 2]; double_up(&mut v); v }, vec![1, 2, 1, 2]);
}

#[test]
fn empty() {
    check!(r#"v = []"#, { let mut v: Vec<i32> = vec![]; double_up(&mut v); v }, Vec::<i32>::new());
}

#[test]
fn single() {
    check!(r#"v = [7]"#, { let mut v = vec![7]; double_up(&mut v); v }, vec![7, 7]);
}

#[test]
fn three() {
    check!(r#"v = [1, 2, 3]"#, { let mut v = vec![1, 2, 3]; double_up(&mut v); v }, vec![1, 2, 3, 1, 2, 3]);
}

#[test]
fn duplicates() {
    check!(r#"v = [5, 5]"#, { let mut v = vec![5, 5]; double_up(&mut v); v }, vec![5, 5, 5, 5]);
}
