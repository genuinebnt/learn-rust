use solution::*;

#[test]
fn duplicates() {
    check!(r#"nums = [1, 1]"#, first_missing_positive(&mut [1, 1]), 2);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, first_missing_positive(&mut []), 1);
}

#[test]
fn permutation() {
    check!(r#"nums = (1..=1000).rev()"#, first_missing_positive(&mut (1..=1000).rev().collect::<Vec<_>>()), 1001);
}
