use solution::*;

#[test]
fn push_back_empty() {
    check!(r#"[]; push_back 1, 2"#, { let mut l = List::from_slice(&[]); l.push_back(1); l.push_back(2); l.to_vec() }, vec![1, 2]);
}

#[test]
fn insert_at_front() {
    check!(r#"[2, 3]; insert_sorted 1"#, { let mut l = List::from_slice(&[2, 3]); l.insert_sorted(1); l.to_vec() }, vec![1, 2, 3]);
}

#[test]
fn insert_at_end() {
    check!(r#"[1, 2]; insert_sorted 9"#, { let mut l = List::from_slice(&[1, 2]); l.insert_sorted(9); l.to_vec() }, vec![1, 2, 9]);
}

#[test]
fn insert_unsorted() {
    check!(r#"[1, 9, 2]; insert_sorted 5"#, { let mut l = List::from_slice(&[1, 9, 2]); l.insert_sorted(5); l.to_vec() }, vec![1, 5, 9, 2]);
}

#[test]
fn remove_all() {
    check!(r#"[4, 4, 4]; remove 4"#, { let mut l = List::from_slice(&[4, 4, 4]); (l.remove_if(|x| x == 4), l.to_vec(), l.last_mut().is_none()) }, (3, vec![], true));
}

#[test]
fn remove_adjacent() {
    check!(r#"[1, 2, 2, 3, 2]; remove 2"#, { let mut l = List::from_slice(&[1, 2, 2, 3, 2]); let n = l.remove_if(|x| x == 2); (n, l.to_vec()) }, (3, vec![1, 3]));
}

#[test]
fn remove_sees_each_once_in_order() {
    check!(r#"[5, 6, 7, 8]; remove every other visited"#, { let mut l = List::from_slice(&[5, 6, 7, 8]); let mut seen = vec![]; let mut k = 0; let n = l.remove_if(|x| { seen.push(x); k += 1; k % 2 == 1 }); (n, l.to_vec(), seen) }, (2, vec![6, 8], vec![5, 6, 7, 8]));
}

#[test]
fn last_after_remove() {
    check!(r#"[1, 2, 3]; remove 3; last"#, { let mut l = List::from_slice(&[1, 2, 3]); l.remove_if(|x| x == 3); l.last_mut().copied() }, Some(2));
}

#[test]
fn push_after_last_edit() {
    check!(r#"[1]; last = 5; push_back 6"#, { let mut l = List::from_slice(&[1]); *l.last_mut().unwrap() = 5; l.push_back(6); l.to_vec() }, vec![5, 6]);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6213);
    for _ in 0..300 {
        let n = rng.below(6);
        let start: Vec<i32> = rng.vec(n, 0, 5);
        let mut l = List::from_slice(&start);
        let mut model = start.clone();
        let mut ops = Vec::new();
        for _ in 0..6 {
            let v = rng.int(0, 5) as i32;
            match rng.below(4) {
                0 => {
                    l.push_back(v);
                    model.push(v);
                    ops.push(format!("push_back {v}"));
                }
                1 => {
                    l.insert_sorted(v);
                    let at = model.iter().position(|&x| x > v).unwrap_or(model.len());
                    model.insert(at, v);
                    ops.push(format!("insert_sorted {v}"));
                }
                2 => {
                    let before = model.len();
                    model.retain(|&x| x != v);
                    ops.push(format!("remove_if(== {v})"));
                    check!(format!("{start:?}; {}", ops.join(", ")), l.remove_if(|x| x == v), before - model.len());
                }
                _ => {
                    if let Some(x) = l.last_mut() {
                        *x += 10;
                    }
                    if let Some(x) = model.last_mut() {
                        *x += 10;
                    }
                    ops.push("last += 10".to_string());
                }
            }
        }
        check!(format!("{start:?}; {}", ops.join(", ")), l.to_vec(), model);
    }
}

#[test]
fn long_list() {
    let xs: Vec<i32> = (0..200_000).collect();
    let mut l = List::from_slice(&xs);
    l.insert_sorted(199_998);
    l.push_back(7);
    let removed = l.remove_if(|x| x % 2 == 1);
    *l.last_mut().unwrap() = -1;
    let v = l.to_vec();
    check!("0..200000; insert_sorted 199998; push_back 7; remove odd; last = -1", (removed, v.len(), v[99_999], v[100_000]), (100_001, 100_001, 199_998, -1));
}
