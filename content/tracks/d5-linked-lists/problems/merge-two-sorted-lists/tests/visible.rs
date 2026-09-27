use solution::*;

#[test]
fn interleave() {
    check!(r#"[1,2,4] + [1,3,4]"#, values(&merge(list(&[1, 2, 4]), list(&[1, 3, 4]))), vec![1, 1, 2, 3, 4, 4]);
}

#[test]
fn one_empty() {
    check!(r#"[] + [0]"#, values(&merge(None, list(&[0]))), vec![0]);
}
