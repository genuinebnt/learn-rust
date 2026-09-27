use solution::*;

#[test]
fn empty() {
    check!(r#"[]"#, { let mut v: [u32; 0] = []; bump_below_average(&mut v); v }, []);
}

#[test]
fn all_equal() {
    check!(r#"[5, 5]"#, { let mut v = [5, 5]; bump_below_average(&mut v); v }, [5, 5]);
}
