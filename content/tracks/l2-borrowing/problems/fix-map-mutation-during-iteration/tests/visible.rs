use solution::*;

fn sessions(xs: &[(u32, Option<u32>, u64, u64)]) -> std::collections::HashMap<u32, Session> {
    xs.iter().map(|&(id, parent, expires, bytes)| (id, Session { parent, expires, bytes })).collect()
}

fn bytes(m: &std::collections::HashMap<u32, Session>) -> Vec<(u32, u64)> {
    let mut v: Vec<(u32, u64)> = m.iter().map(|(&id, s)| (id, s.bytes)).collect();
    v.sort();
    v
}

#[test]
fn example() {
    let mut m = sessions(&[(1, None, 100, 10), (2, Some(1), 5, 3), (3, Some(1), 50, 4)]);
    let removed = expire(&mut m, 10);
    check!(r#"sessions (id, parent, expires, bytes) (1, None, 100, 10), (2, 1, 5, 3), (3, 1, 50, 4); now 10"#, (removed, bytes(&m)), (vec![2], vec![(1, 13), (3, 4)]));
}

#[test]
fn parent_also_expires() {
    let mut m = sessions(&[(1, None, 5, 10), (2, Some(1), 5, 3)]);
    let removed = expire(&mut m, 10);
    check!(r#"sessions (id, parent, expires, bytes) (1, None, 5, 10), (2, 1, 5, 3); now 10"#, (removed, bytes(&m)), (vec![1, 2], Vec::<(u32, u64)>::new()));
}

#[test]
fn credit_not_passed_up() {
    let mut m = sessions(&[(1, Some(2), 1, 7), (2, Some(3), 1, 5), (3, None, 99, 0)]);
    let removed = expire(&mut m, 10);
    check!(r#"sessions (id, parent, expires, bytes) (1, 2, 1, 7), (2, 3, 1, 5), (3, None, 99, 0); now 10"#, (removed, bytes(&m)), (vec![1, 2], vec![(3, 5)]));
}

#[test]
fn nothing_expired() {
    let mut m = sessions(&[(1, None, 50, 1)]);
    let removed = expire(&mut m, 10);
    check!(r#"sessions (id, parent, expires, bytes) (1, None, 50, 1); now 10"#, (removed, bytes(&m)), (Vec::<u32>::new(), vec![(1, 1)]));
}

#[test]
fn expires_at_now() {
    let mut m = sessions(&[(4, None, 10, 1), (5, Some(4), 11, 1)]);
    let removed = expire(&mut m, 10);
    check!(r#"sessions (id, parent, expires, bytes) (4, None, 10, 1), (5, 4, 11, 1); now 10"#, (removed, bytes(&m)), (vec![4], vec![(5, 1)]));
}
