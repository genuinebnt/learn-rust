use solution::*;

#[test]
fn interleave() {
    check!(r#"[1,2,4] + [1,3,4]"#, values(&merge(list(&[1, 2, 4]), list(&[1, 3, 4]))), vec![1, 1, 2, 3, 4, 4]);
}

#[test]
fn one_empty() {
    check!(r#"[] + [0]"#, values(&merge(None, list(&[0]))), vec![0]);
}

#[test]
fn both_empty() {
    check!(r#"[] + []"#, merge(None, None), None);
}

#[test]
fn disjoint() {
    check!(r#"[5,6] + [1,2]"#, values(&merge(list(&[5, 6]), list(&[1, 2]))), vec![1, 2, 5, 6]);
}

#[test]
fn uneven_lengths() {
    check!(r#"[1] + [2,3,4]"#, values(&merge(list(&[1]), list(&[2, 3, 4]))), vec![1, 2, 3, 4]);
}
