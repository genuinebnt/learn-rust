use solution::*;

#[test]
fn none() {
    check!(r#"deadline 50; now 10"#, { let mut v = vec![Job { name: "a", deadline: 50 }]; take_expired(&mut v, 10).len() }, 0);
}
