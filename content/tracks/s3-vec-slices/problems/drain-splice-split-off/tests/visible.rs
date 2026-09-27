use solution::*;

#[test]
fn tail() {
    check!(r#"v = [1, 2, 3, 4], at = 2"#, { let mut v = vec![1, 2, 3, 4]; let t = take_tail(&mut v, 2); (v, t) }, (vec![1, 2], vec![3, 4]));
}

#[test]
fn splice() {
    check!(r#"v = [1, 2, 3, 4], replace 1..3 with [9]"#, { let mut v = vec![1, 2, 3, 4]; let r = replace_range(&mut v, 1, 3, &[9]); (v, r) }, (vec![1, 9, 4], vec![2, 3]));
}

#[test]
fn tail_at_zero() {
    check!(r#"v = [1, 2], at = 0"#, { let mut v = vec![1, 2]; let t = take_tail(&mut v, 0); (v, t) }, (vec![], vec![1, 2]));
}

#[test]
fn tail_at_len() {
    check!(r#"v = [1, 2], at = 2"#, { let mut v = vec![1, 2]; let t = take_tail(&mut v, 2); (v, t) }, (vec![1, 2], vec![]));
}

#[test]
fn splice_delete() {
    check!(r#"v = [1, 2, 3, 4], replace 1..3 with []"#, { let mut v = vec![1, 2, 3, 4]; let r = replace_range(&mut v, 1, 3, &[]); (v, r) }, (vec![1, 4], vec![2, 3]));
}
