use solution::*;

#[test]
fn push_pop() {
    check!(r#"Push 1, Push 2, Pop, Push 3"#, apply(&[Op::Push(1), Op::Push(2), Op::Pop, Op::Push(3)]), vec![1, 3]);
}

#[test]
fn insert_front() {
    check!(r#"Push 2, Insert(0, 1)"#, apply(&[Op::Push(2), Op::Insert(0, 1)]), vec![1, 2]);
}

#[test]
fn pop_empty() {
    check!(r#"Pop"#, apply(&[Op::Pop]), Vec::<i32>::new());
}

#[test]
fn remove_middle() {
    check!(r#"Push 1, Push 2, Push 3, Remove(1)"#, apply(&[Op::Push(1), Op::Push(2), Op::Push(3), Op::Remove(1)]), vec![1, 3]);
}

#[test]
fn insert_past_end_ignored() {
    check!(r#"Insert(1, 5) on an empty vec"#, apply(&[Op::Insert(1, 5)]), Vec::<i32>::new());
}

#[test]
fn insert_at_len_appends() {
    check!(r#"Push 1, Insert(1, 2)"#, apply(&[Op::Push(1), Op::Insert(1, 2)]), vec![1, 2]);
}
