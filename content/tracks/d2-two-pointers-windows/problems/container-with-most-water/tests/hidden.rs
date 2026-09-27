use solution::*;

#[test]
fn one_line() {
    check!(r#"heights = [5]"#, max_area(&[5]), 0);
}

#[test]
fn large() {
    check!(r#"heights = [u32::MAX, u32::MAX]"#, max_area(&[u32::MAX, u32::MAX]), u32::MAX as u64);
}
