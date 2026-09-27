use solution::*;

#[test]
fn adds() {
    check!(r#"v = [10, 1, 2]"#, { let mut v = [10, 1, 2]; add_head_to_rest(&mut v); v }, [10, 11, 12]);
}

#[test]
fn single() {
    check!(r#"v = [5]"#, { let mut v = [5]; add_head_to_rest(&mut v); v }, [5]);
}

#[test]
fn negative_head() {
    check!(r#"v = [-1, 0, 1]"#, { let mut v = [-1, 0, 1]; add_head_to_rest(&mut v); v }, [-1, -1, 0]);
}

#[test]
fn head_not_doubled() {
    check!(r#"v = [2, 2, 2]"#, { let mut v = [2, 2, 2]; add_head_to_rest(&mut v); v }, [2, 4, 4]);
}

#[test]
fn empty() {
    check!(r#"v = []"#, { let mut v: [i32; 0] = []; add_head_to_rest(&mut v); v }, []);
}
