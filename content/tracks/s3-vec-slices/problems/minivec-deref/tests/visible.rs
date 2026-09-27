use solution::*;

#[test]
fn iter_sum() {
    check!(r#"push 1..=4"#, { let mut v = MiniVec::new(); for i in 1..=4 { v.push(i); } v.iter().sum::<i32>() }, 10);
}

#[test]
fn sort() {
    check!(r#"push 3, 1, 2"#, { let mut v = MiniVec::new(); v.push(3); v.push(1); v.push(2); v.sort(); v.as_slice().to_vec() }, vec![1, 2, 3]);
}
