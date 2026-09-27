use solution::*;

#[test]
fn empty() {
    check!(r#"heights = []"#, trap(&[]), 0);
}

#[test]
fn monotonic() {
    check!(r#"heights = [1, 2, 3, 4]"#, trap(&[1, 2, 3, 4]), 0);
}

#[test]
fn tall_walls() {
    check!(r#"heights = [u32::MAX, 0, u32::MAX]"#, trap(&[u32::MAX, 0, u32::MAX]), u32::MAX as u64);
}
