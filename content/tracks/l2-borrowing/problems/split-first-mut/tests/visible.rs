use solution::*;

#[test]
fn adds() {
    check!(r#"v = [10, 1, 2]"#, { let mut v = [10, 1, 2]; add_head_to_rest(&mut v); v }, [10, 11, 12]);
}

#[test]
fn single() {
    check!(r#"v = [5]"#, { let mut v = [5]; add_head_to_rest(&mut v); v }, [5]);
}
