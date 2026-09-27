use solution::*;

#[test]
fn tail() {
    check!(r#"v = [1, 2, 3, 4], at = 2"#, { let mut v = vec![1, 2, 3, 4]; let t = take_tail(&mut v, 2); (v, t) }, (vec![1, 2], vec![3, 4]));
}

#[test]
fn splice() {
    check!(r#"v = [1, 2, 3, 4], replace 1..3 with [9]"#, { let mut v = vec![1, 2, 3, 4]; let r = replace_range(&mut v, 1, 3, &[9]); (v, r) }, (vec![1, 9, 4], vec![2, 3]));
}
