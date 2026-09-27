use solution::*;

#[test]
fn two() {
    check!(r#"v = [1, 2, 3, 4, 5], k = 2"#, { let mut v = [1, 2, 3, 4, 5]; rotate_right(&mut v, 2); v }, [4, 5, 1, 2, 3]);
}

#[test]
fn full_turn() {
    check!(r#"v = [1, 2], k = 2"#, { let mut v = [1, 2]; rotate_right(&mut v, 2); v }, [1, 2]);
}
