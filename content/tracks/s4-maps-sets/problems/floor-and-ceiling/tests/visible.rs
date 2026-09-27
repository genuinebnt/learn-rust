use solution::*;

#[test]
fn between() {
    check!(r#"prices = {10, 20, 30}, x = 25"#, nearest(&std::collections::BTreeSet::from([10, 20, 30]), 25), (Some(20), Some(30)));
}

#[test]
fn exact() {
    check!(r#"prices = {10, 20}, x = 20"#, nearest(&std::collections::BTreeSet::from([10, 20]), 20), (Some(20), Some(20)));
}
