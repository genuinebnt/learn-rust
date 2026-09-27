use solution::*;

#[test]
fn non_adjacent() {
    check!(r#"v = [2, 1, 2]"#, { let mut v = vec![2, 1, 2]; clean(&mut v); v }, vec![2, 1, 2]);
}

#[test]
fn all_negative() {
    check!(r#"v = [-1, -1]"#, { let mut v = vec![-1, -1]; clean(&mut v); v }, Vec::<i32>::new());
}
