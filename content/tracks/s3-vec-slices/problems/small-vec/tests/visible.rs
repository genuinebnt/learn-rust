use solution::*;

#[test]
fn stays_inline() {
    check!(r#"push 4 items"#, { let mut v = SmallVec4::new(); for i in 0..4 { v.push(i); } (v.len(), v.is_inline(), v.get(3).copied()) }, (4, true, Some(3)));
}

#[test]
fn spills() {
    check!(r#"push 5 items"#, { let mut v = SmallVec4::new(); for i in 0..5 { v.push(i * 10); } (v.len(), v.is_inline(), v.get(0).copied(), v.get(4).copied()) }, (5, false, Some(0), Some(40)));
}
