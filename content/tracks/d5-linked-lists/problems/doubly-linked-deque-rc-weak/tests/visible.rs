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
