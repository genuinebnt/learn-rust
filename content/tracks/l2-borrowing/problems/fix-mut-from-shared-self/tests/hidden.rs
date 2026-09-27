use solution::*;

#[test]
fn only_top_changes() {
    check!(r#"push 5, 6; set top to 0"#, { let mut s = Stack::new(); s.push(5); s.push(6); if let Some(t) = s.top_mut() { *t = 0; } s.items_for_test() }, vec![5, 0]);
}
