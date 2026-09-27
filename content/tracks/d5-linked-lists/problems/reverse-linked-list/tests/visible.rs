use solution::*;

#[test]
fn five() {
    check!(r#"[1,2,3,4,5]"#, values(&reverse(list(&[1, 2, 3, 4, 5]))), vec![5, 4, 3, 2, 1]);
}

#[test]
fn two() {
    check!(r#"[1,2]"#, values(&reverse(list(&[1, 2]))), vec![2, 1]);
}
