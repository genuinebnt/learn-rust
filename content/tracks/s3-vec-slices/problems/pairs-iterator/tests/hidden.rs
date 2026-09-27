use solution::*;

#[test]
fn len() {
    check!(r#"v = [0; 7]"#, pairs(&[0; 7]).len(), 3);
}

#[test]
fn empty() {
    check!(r#"v = []"#, pairs::<u8>(&[]).next(), None);
}
