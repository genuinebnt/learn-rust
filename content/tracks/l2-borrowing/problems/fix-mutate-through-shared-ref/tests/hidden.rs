use solution::*;

#[test]
fn empty() {
    check!(r#"no accounts"#, { let mut a: [Account; 0] = []; deposit_all(&mut a, 5); a.len() }, 0);
}
