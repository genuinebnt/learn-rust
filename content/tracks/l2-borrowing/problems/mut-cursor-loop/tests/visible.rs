use solution::*;

#[test]
fn push_back() {
    check!(r#"[1, 2]; push_back 3"#, { let mut l = List::from_slice(&[1, 2]); l.push_back(3); l.to_vec() }, vec![1, 2, 3]);
}

#[test]
fn insert_sorted_middle() {
    check!(r#"[1, 3, 5]; insert_sorted 4"#, { let mut l = List::from_slice(&[1, 3, 5]); l.insert_sorted(4); l.to_vec() }, vec![1, 3, 4, 5]);
}

#[test]
fn insert_after_equal() {
    check!(r#"[5, 3]; insert_sorted 5"#, { let mut l = List::from_slice(&[5, 3]); l.insert_sorted(5); l.to_vec() }, vec![5, 3, 5]);
}

#[test]
fn remove_if_example() {
    check!(r#"[1, 2, 3, 4, 6]; remove even"#, { let mut l = List::from_slice(&[1, 2, 3, 4, 6]); let n = l.remove_if(|x| x % 2 == 0); (n, l.to_vec()) }, (3, vec![1, 3]));
}

#[test]
fn last_mut_example() {
    check!(r#"[7, 8, 9]; last += 100"#, { let mut l = List::from_slice(&[7, 8, 9]); *l.last_mut().unwrap() += 100; l.to_vec() }, vec![7, 8, 109]);
}

#[test]
fn empty_list() {
    check!(r#"[]"#, { let mut l = List::from_slice(&[]); (l.last_mut().is_none(), l.remove_if(|_| true), { l.insert_sorted(1); l.to_vec() }) }, (true, 0, vec![1]));
}
