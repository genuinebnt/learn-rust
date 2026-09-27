use solution::*;

#[test]
fn one_empty() {
    check!(r#"[], [5]"#, median(&[], &[5]), Some(5.0));
}

#[test]
fn both_empty() {
    check!(r#"[], []"#, median(&[], &[]), None);
}

#[test]
fn extremes() {
    check!(r#"[i32::MIN], [i32::MAX]"#, median(&[i32::MIN], &[i32::MAX]), Some(-0.5));
}

#[test]
fn interleaved() {
    let odd: Vec<i32> = (0..100_000).filter(|x| x % 2 == 1).collect();
    let even: Vec<i32> = (0..100_000).filter(|x| x % 2 == 0).collect();
    check!(r#"odds and evens up to 10⁵"#, median(&odd, &even), Some(49_999.5));
}

#[test]
fn disjoint() {
    check!(r#"[1,2,3], [10,11,12,13]"#, median(&[1, 2, 3], &[10, 11, 12, 13]), Some(10.0));
}
