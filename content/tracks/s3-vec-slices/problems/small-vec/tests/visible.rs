use solution::*;

#[test]
fn stays_inline() {
    check!(r#"push 4 items"#, { let mut v = SmallVec4::new(); for i in 0..4 { v.push(i); } (v.len(), v.is_inline(), v.get(3).copied()) }, (4, true, Some(3)));
}

#[test]
fn spills() {
    check!(r#"push 5 items"#, { let mut v = SmallVec4::new(); for i in 0..5 { v.push(i * 10); } (v.len(), v.is_inline(), v.get(0).copied(), v.get(4).copied()) }, (5, false, Some(0), Some(40)));
}

#[test]
fn new_is_empty() {
    check!(r#"new SmallVec4"#, { let v = SmallVec4::<i32>::new(); (v.len(), v.is_inline(), v.get(0).copied()) }, (0, true, None));
}

#[test]
fn order_after_spill() {
    check!(r#"push 0..6"#, { let mut v = SmallVec4::new(); for i in 0..6 { v.push(i); } (0..6).map(|i| v.get(i).copied()).collect::<Vec<_>>() }, (0..6).map(Some).collect::<Vec<_>>());
}

#[test]
fn get_past_len_after_spill() {
    check!(r#"push 5 items, get(5)"#, { let mut v = SmallVec4::new(); for i in 0..5 { v.push(i); } v.get(5).copied() }, None);
}
