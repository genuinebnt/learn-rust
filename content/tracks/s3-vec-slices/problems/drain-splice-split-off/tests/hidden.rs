use solution::*;

#[test]
fn tail_past_end() {
    check!(r#"v = [1], at = 5"#, { let mut v = vec![1]; let t = take_tail(&mut v, 5); (v, t) }, (vec![1], vec![]));
}

#[test]
fn splice_insert() {
    check!(r#"v = [1, 4], replace 1..1 with [2, 3]"#, { let mut v = vec![1, 4]; let r = replace_range(&mut v, 1, 1, &[2, 3]); (v, r) }, (vec![1, 2, 3, 4], vec![]));
}
