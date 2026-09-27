use solution::*;

#[test]
fn empty() {
    check!(r#"[], 0"#, search_range(&[], 0), None);
}

#[test]
fn all_same() {
    check!(r#"[2,2,2], 2"#, search_range(&[2, 2, 2], 2), Some((0, 2)));
}

#[test]
fn big_run() {
    let mut v = vec![0; 10];
    v.extend(std::iter::repeat(1).take(1_000_000));
    v.extend([2, 2]);
    check!(r#"10⁶ copies of 1 between 0s and 2s"#, search_range(&v, 1), Some((10, 1_000_009)));
}
