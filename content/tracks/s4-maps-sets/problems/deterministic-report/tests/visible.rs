use solution::*;

#[test]
fn ordered() {
    check!(r#"{ann: 5, bob: 9, cy: 5}"#, report(&std::collections::HashMap::from([("ann".to_string(), 5), ("bob".to_string(), 9), ("cy".to_string(), 5)])), vec!["bob: 9", "ann: 5", "cy: 5"]);
}

#[test]
fn empty() {
    check!(r#"{}"#, report(&std::collections::HashMap::new()), Vec::<String>::new());
}
