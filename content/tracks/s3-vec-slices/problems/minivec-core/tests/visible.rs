use solution::*;

#[test]
fn push_pop() {
    check!(r#"push 1, 2, 3 then pop twice"#, { let mut v = MiniVec::new(); v.push(1); v.push(2); v.push(3); (v.pop(), v.pop(), v.len()) }, (Some(3), Some(2), 1));
}

#[test]
fn growth() {
    check!(r#"capacity after 0, 1 and 5 pushes"#, { let mut v = MiniVec::new(); let a = v.capacity(); v.push(1u64); let b = v.capacity(); for i in 0..4 { v.push(i); } (a, b, v.capacity()) }, (0, 4, 8));
}

#[test]
fn get() {
    check!(r#"push "a", "b""#, { let mut v = MiniVec::new(); v.push(String::from("a")); v.push(String::from("b")); (v.get(1).cloned(), v.get(2).cloned()) }, (Some("b".to_string()), None));
}
