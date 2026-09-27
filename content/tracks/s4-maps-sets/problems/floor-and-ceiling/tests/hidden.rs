use solution::*;

#[test]
fn below_all() {
    check!(r#"prices = {10}, x = 3"#, nearest(&std::collections::BTreeSet::from([10]), 3), (None, Some(10)));
}

#[test]
fn empty() {
    check!(r#"prices = {}, x = 3"#, nearest(&std::collections::BTreeSet::new(), 3), (None, None));
}
