use solution::*;

#[test]
fn out_of_range() {
    check!(r#"Push 5, Insert(3, 9), Remove(1)"#, apply(&[Op::Push(5), Op::Insert(3, 9), Op::Remove(1)]), vec![5]);
}

#[test]
fn insert_at_end() {
    check!(r#"Push 1, Insert(1, 2), Remove(0)"#, apply(&[Op::Push(1), Op::Insert(1, 2), Op::Remove(0)]), vec![2]);
}
