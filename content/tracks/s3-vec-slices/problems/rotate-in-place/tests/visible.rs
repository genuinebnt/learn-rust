use solution::*;

#[test]
fn two() {
    check!(r#"v = [1, 2, 3, 4, 5], k = 2"#, { let mut v = [1, 2, 3, 4, 5]; rotate_right(&mut v, 2); v }, [4, 5, 1, 2, 3]);
}

#[test]
fn full_turn() {
    check!(r#"v = [1, 2], k = 2"#, { let mut v = [1, 2]; rotate_right(&mut v, 2); v }, [1, 2]);
}

#[test]
fn leetcode_189_first() {
    check!(r#"v = [1, 2, 3, 4, 5, 6, 7], k = 3"#, { let mut v = [1, 2, 3, 4, 5, 6, 7]; rotate_right(&mut v, 3); v }, [5, 6, 7, 1, 2, 3, 4]);
}

#[test]
fn leetcode_189_second() {
    check!(r#"v = [-1, -100, 3, 99], k = 2"#, { let mut v = [-1, -100, 3, 99]; rotate_right(&mut v, 2); v }, [3, 99, -1, -100]);
}

#[test]
fn k_zero() {
    check!(r#"v = [1, 2, 3], k = 0"#, { let mut v = [1, 2, 3]; rotate_right(&mut v, 0); v }, [1, 2, 3]);
}
