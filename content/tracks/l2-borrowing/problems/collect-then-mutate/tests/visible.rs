use solution::*;

#[test]
fn bumps() {
    check!(r#"[10, 20, 30]"#, { let mut v = [10, 20, 30]; bump_below_average(&mut v); v }, [20, 20, 30]);
}

#[test]
fn rounds_down() {
    check!(r#"[1, 2]"#, { let mut v = [1, 2]; bump_below_average(&mut v); v }, [1, 2]);
}

#[test]
fn single() {
    check!(r#"[7]"#, { let mut v = [7]; bump_below_average(&mut v); v }, [7]);
}

#[test]
fn uses_the_original_average() {
    check!(r#"[0, 0, 30]"#, { let mut v = [0, 0, 30]; bump_below_average(&mut v); v }, [10, 10, 30]);
}

#[test]
fn empty() {
    check!(r#"[]"#, { let mut v: [u32; 0] = []; bump_below_average(&mut v); v }, []);
}
