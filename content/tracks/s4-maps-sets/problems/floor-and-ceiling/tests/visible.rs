use solution::*;

#[test]
fn between() {
    check!(r#"prices = {10, 20, 30}, x = 25"#, nearest(&std::collections::BTreeSet::from([10, 20, 30]), 25), (Some(20), Some(30)));
}

#[test]
fn exact() {
    check!(r#"prices = {10, 20}, x = 20"#, nearest(&std::collections::BTreeSet::from([10, 20]), 20), (Some(20), Some(20)));
}

#[test]
fn below_all() {
    check!(r#"prices = {10}, x = 3"#, nearest(&std::collections::BTreeSet::from([10]), 3), (None, Some(10)));
}

#[test]
fn above_all() {
    check!(r#"prices = {10, 20}, x = 25"#, nearest(&std::collections::BTreeSet::from([10, 20]), 25), (Some(20), None));
}

#[test]
fn empty() {
    check!(r#"prices = {}, x = 3"#, nearest(&std::collections::BTreeSet::new(), 3), (None, None));
}
