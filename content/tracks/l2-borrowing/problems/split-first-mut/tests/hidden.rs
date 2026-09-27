use solution::*;

#[test]
fn empty() {
    check!(r#"v = []"#, { let mut v: [i32; 0] = []; add_head_to_rest(&mut v); v }, []);
}
