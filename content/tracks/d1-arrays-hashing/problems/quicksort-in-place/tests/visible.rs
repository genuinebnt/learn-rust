use solution::*;

#[test]
fn mixed() {
    check!(r#"[5, 2, 9, 1, 5, 6]"#, { let mut v = vec![5, 2, 9, 1, 5, 6]; quicksort(&mut v); v }, vec![1, 2, 5, 5, 6, 9]);
}

#[test]
fn empty() {
    check!(r#"[]"#, { let mut v: Vec<i32> = vec![]; quicksort(&mut v); v }, Vec::<i32>::new());
}

#[test]
fn two() {
    check!(r#"[2, 1]"#, { let mut v = vec![2, 1]; quicksort(&mut v); v }, vec![1, 2]);
}
