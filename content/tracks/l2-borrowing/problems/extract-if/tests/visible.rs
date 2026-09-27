use solution::*;

#[test]
fn splits() {
    check!(r#"deadlines 5, 20, 7; now 10"#, { let mut v = vec![Job { name: "a", deadline: 5 }, Job { name: "b", deadline: 20 }, Job { name: "c", deadline: 7 }]; let gone = take_expired(&mut v, 10); (gone.iter().map(|j| j.name).collect::<Vec<_>>(), v.iter().map(|j| j.name).collect::<Vec<_>>()) }, (vec!["a", "c"], vec!["b"]));
}

#[test]
fn all_expired() {
    check!(r#"deadlines 1, 2; now 10"#, { let mut v = vec![Job { name: "a", deadline: 1 }, Job { name: "b", deadline: 2 }]; let gone = take_expired(&mut v, 10); (gone.len(), v.len()) }, (2, 0));
}

#[test]
fn at_deadline_kept() {
    check!(r#"deadline 10; now 10"#, { let mut v = vec![Job { name: "a", deadline: 10 }]; let gone = take_expired(&mut v, 10); (gone.len(), v.len()) }, (0, 1));
}

#[test]
fn order_both() {
    check!(r#"deadlines 1, 9, 2, 8, 3; now 5"#, { let mut v = vec![Job { name: "a", deadline: 1 }, Job { name: "b", deadline: 9 }, Job { name: "c", deadline: 2 }, Job { name: "d", deadline: 8 }, Job { name: "e", deadline: 3 }]; let gone = take_expired(&mut v, 5); (gone.iter().map(|j| j.name).collect::<Vec<_>>(), v.iter().map(|j| j.name).collect::<Vec<_>>()) }, (vec!["a", "c", "e"], vec!["b", "d"]));
}

#[test]
fn empty() {
    check!(r#"no jobs"#, { let mut v: Vec<Job> = vec![]; let gone = take_expired(&mut v, 5); (gone.len(), v.len()) }, (0, 0));
}
