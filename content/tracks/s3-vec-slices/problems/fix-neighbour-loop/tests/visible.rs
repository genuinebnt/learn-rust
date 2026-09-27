use solution::*;

#[test]
fn three() {
    check!(r#"v = [1, 2, 3]"#, pair_sums(&[1, 2, 3]), vec![3, 5]);
}

#[test]
fn one() {
    check!(r#"v = [9]"#, pair_sums(&[9]), Vec::<i32>::new());
}

#[test]
fn four() {
    check!(r#"v = [1, 2, 3, 4]"#, pair_sums(&[1, 2, 3, 4]), vec![3, 5, 7]);
}

#[test]
fn two() {
    check!(r#"v = [5, 6]"#, pair_sums(&[5, 6]), vec![11]);
}

#[test]
fn empty_visible() {
    check!(r#"v = []"#, pair_sums(&[]), Vec::<i32>::new());
}
