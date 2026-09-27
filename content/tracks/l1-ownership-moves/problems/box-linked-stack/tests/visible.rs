use solution::*;

#[test]
fn push_pop() {
    let mut s = Stack::new();
    for i in 1..=3 {
        s.push(i);
    }
    check!(r#"push 1, 2, 3, then pop twice"#, (s.pop(), s.pop(), s.len(), s.peek()), (Some(3), Some(2), 1, Some(&1)));
}

#[test]
fn reverse() {
    let mut s = Stack::new();
    for i in 1..=3 {
        s.push(i);
    }
    check!(r#"push 1, 2, 3, reverse, into_vec"#, { s.reverse(); s.into_vec() }, vec![1, 2, 3]);
}

#[test]
fn move_top() {
    let mut a = Stack::new();
    a.push(1);
    a.push(2);
    let mut b = Stack::new();
    b.push(9);
    check!(r#"a = [1, 2] (2 on top), b = [9]; move_top_to three times"#, (a.move_top_to(&mut b), a.move_top_to(&mut b), a.move_top_to(&mut b), a.len(), b.into_vec()), (true, true, false, 0, vec![1, 2, 9]));
}

#[test]
fn strings_move_through() {
    let mut s = Stack::new();
    s.push("x".to_string());
    s.push("y".to_string());
    check!(r#"push "x", "y" as Strings, into_vec"#, s.into_vec(), vec!["y".to_string(), "x".to_string()]);
}

#[test]
fn empty() {
    let mut s: Stack<u8> = Stack::new();
    check!(r#"a new stack"#, (s.pop(), s.peek().is_none(), s.len(), s.into_vec()), (None, true, 0, Vec::<u8>::new()));
}
