use solution::*;

#[test]
fn twice() {
    check!(r#"xs = [7, 8]"#, { let mut v = vec![]; emit_twice(&mut v, &[7, 8]); v }, vec![7, 8, 7, 8]);
}

#[test]
fn appends() {
    check!(r#"sink = [0], xs = [1]"#, { let mut v = vec![0]; emit_twice(&mut v, &[1]); v }, vec![0, 1, 1]);
}

#[test]
fn order_kept() {
    check!(r#"xs = [3, 1, 2]"#, { let mut v = vec![]; emit_twice(&mut v, &[3, 1, 2]); v }, vec![3, 1, 2, 3, 1, 2]);
}

#[test]
fn single() {
    check!(r#"xs = [5]"#, { let mut v = vec![]; emit_twice(&mut v, &[5]); v }, vec![5, 5]);
}

#[test]
fn empty() {
    check!(r#"xs = []"#, { let mut v = vec![1]; emit_twice(&mut v, &[]); v }, vec![1]);
}
