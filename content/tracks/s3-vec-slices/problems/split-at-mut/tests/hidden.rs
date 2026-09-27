use solution::*;

#[test]
fn empty() {
    check!(r#"v = []"#, { let mut v: [i32; 0] = []; add_halves(&mut v); v }, []);
}

#[test]
fn one() {
    check!(r#"v = [4]"#, { let mut v = [4]; add_halves(&mut v); v }, [4]);
}
