use solution::*;

#[test]
fn three() {
    check!(r#"v = [], n = 3"#, { let mut v = vec![]; push_lengths(&mut v, 3); v }, vec![0, 1, 2]);
}

#[test]
fn zero_times() {
    check!(r#"v = [4], n = 0"#, { let mut v = vec![4]; push_lengths(&mut v, 0); v }, vec![4]);
}

#[test]
fn one() {
    check!(r#"v = [], n = 1"#, { let mut v = vec![]; push_lengths(&mut v, 1); v }, vec![0]);
}

#[test]
fn existing() {
    check!(r#"v = [9], n = 2"#, { let mut v = vec![9]; push_lengths(&mut v, 2); v }, vec![9, 1, 2]);
}

#[test]
fn zero_on_empty() {
    check!(r#"v = [], n = 0"#, { let mut v = vec![]; push_lengths(&mut v, 0); v }, Vec::<usize>::new());
}
