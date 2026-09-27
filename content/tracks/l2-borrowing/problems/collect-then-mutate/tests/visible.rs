use solution::*;

#[test]
fn bumps() {
    check!(r#"[10, 20, 30]"#, { let mut v = [10, 20, 30]; bump_below_average(&mut v); v }, [20, 20, 30]);
}

#[test]
fn rounds_down() {
    check!(r#"[1, 2]"#, { let mut v = [1, 2]; bump_below_average(&mut v); v }, [1, 2]);
}
