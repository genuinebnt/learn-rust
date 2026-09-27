use solution::*;

#[test]
fn empty() {
    check!(r#"v = [], k = 3"#, { let mut v: [i32; 0] = []; rotate_right(&mut v, 3); v }, []);
}

#[test]
fn large_k() {
    check!(r#"v = [1, 2, 3], k = 7"#, { let mut v = [1, 2, 3]; rotate_right(&mut v, 7); v }, [3, 1, 2]);
}
