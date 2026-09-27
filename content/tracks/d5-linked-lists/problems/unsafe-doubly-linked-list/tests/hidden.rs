use solution::*;

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
fn alternating() {
    let mut l = LinkedList::new();
    for i in 0..6 {
        if i % 2 == 0 { l.push_front(i) } else { l.push_back(i) }
    }
    check!(r#"push front/back alternately, 0..6"#, l.iter().copied().collect::<Vec<_>>(), vec![4, 2, 0, 1, 3, 5]);
}

#[test]
fn big_drop() {
    let mut l = LinkedList::new();
    for i in 0..1_000_000 {
        l.push_back(i);
    }
    check!(r#"push 10⁶ then drop"#, l.len(), 1_000_000);
}
