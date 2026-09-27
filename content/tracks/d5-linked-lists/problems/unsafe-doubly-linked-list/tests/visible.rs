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
