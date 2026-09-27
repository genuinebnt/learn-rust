use solution::*;

#[test]
fn both_ends() {
    let mut d = Deque::new();
    d.push_back(1);
    d.push_back(2);
    d.push_front(0);
    check!(r#"push_back 1,2; push_front 0; pop_back, pop_front"#, (d.pop_back(), d.pop_front(), d.front(), d.back(), d.len()), (Some(2), Some(0), Some(1), Some(1), 1));
}

#[test]
fn empty() {
    let mut d = Deque::new();
    check!(r#"new deque"#, (d.pop_front(), d.pop_back(), d.front(), d.is_empty()), (None, None, None, true));
}

#[test]
fn single_both_ways() {
    let mut d = Deque::new();
    check!(r#"push 7; pop_back; then push 8; pop_front"#, { d.push_back(7); let a = d.pop_back(); d.push_front(8); (a, d.pop_front(), d.is_empty()) }, (Some(7), Some(8), true));
}

#[test]
fn fifo() {
    let mut d = Deque::new();
    d.push_back(1);
    d.push_back(2);
    d.push_back(3);
    check!(r#"push_back 1,2,3; pop_front three times"#, (d.pop_front(), d.pop_front(), d.pop_front(), d.len()), (Some(1), Some(2), Some(3), 0));
}

#[test]
fn front_and_back_peek() {
    let mut d = Deque::new();
    d.push_front(2);
    d.push_front(1);
    d.push_back(3);
    check!(r#"push_front 2, push_front 1, push_back 3"#, (d.front(), d.back(), d.len()), (Some(1), Some(3), 3));
}
