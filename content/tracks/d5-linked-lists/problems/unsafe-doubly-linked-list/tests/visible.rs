use solution::*;

#[test]
fn both_ends() {
    let mut l = LinkedList::new();
    l.push_back(1);
    l.push_back(2);
    l.push_front(0);
    check!(r#"push_back 1,2; push_front 0; pop_back, pop_front"#, (l.pop_back(), l.pop_front(), l.len()), (Some(2), Some(0), 1));
}

#[test]
fn iter() {
    let mut l = LinkedList::new();
    for i in 1..=4 {
        l.push_back(i);
    }
    check!(r#"push_back 1..=4"#, l.iter().copied().collect::<Vec<_>>(), vec![1, 2, 3, 4]);
}

#[test]
fn empty() {
    let mut l = LinkedList::new();
    check!(r#"new list"#, (l.pop_front(), l.pop_back(), l.iter().next(), l.is_empty()), (None, None, None, true));
}

#[test]
fn single_both_ways() {
    let mut l = LinkedList::new();
    check!(r#"push 5; pop_back; push 6; pop_front"#, { l.push_front(5); let a = l.pop_back(); l.push_back(6); (a, l.pop_front(), l.is_empty(), l.iter().count()) }, (Some(5), Some(6), true, 0));
}

#[test]
fn pushed_front_popped_back() {
    let mut l = LinkedList::new();
    l.push_front(1);
    l.push_front(2);
    l.push_front(3);
    check!(r#"push_front 1, 2, 3; pop_back three times"#, (l.pop_back(), l.pop_back(), l.pop_back(), l.len()), (Some(1), Some(2), Some(3), 0));
}
