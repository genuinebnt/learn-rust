use solution::*;

#[test]
fn iter_sum() {
    check!(r#"push 1..=4"#, { let mut v = MiniVec::new(); for i in 1..=4 { v.push(i); } v.iter().sum::<i32>() }, 10);
}

#[test]
fn sort() {
    check!(r#"push 3, 1, 2"#, { let mut v = MiniVec::new(); v.push(3); v.push(1); v.push(2); v.sort(); v.as_slice().to_vec() }, vec![1, 2, 3]);
}

#[test]
fn index() {
    check!(r#"push 10, 20"#, { let mut v = MiniVec::new(); v.push(10); v.push(20); (v[0], v[1]) }, (10, 20));
}

#[test]
fn slice_length() {
    check!(r#"push 3 values"#, { let mut v = MiniVec::new(); for i in 0..3 { v.push(i); } (v.as_slice().len(), v.len()) }, (3, 3));
}

#[test]
fn write_through_as_mut_slice() {
    check!(r#"push 1, 2, then as_mut_slice()[0] = 9"#, { let mut v = MiniVec::new(); v.push(1); v.push(2); v.as_mut_slice()[0] = 9; v.as_slice().to_vec() }, vec![9, 2]);
}
