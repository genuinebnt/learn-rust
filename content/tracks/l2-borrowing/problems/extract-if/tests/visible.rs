use solution::*;

#[test]
fn splits() {
    check!(r#"deadlines 5, 20, 7; now 10"#, { let mut v = vec![Job { name: "a", deadline: 5 }, Job { name: "b", deadline: 20 }, Job { name: "c", deadline: 7 }]; let gone = take_expired(&mut v, 10); (gone.iter().map(|j| j.name).collect::<Vec<_>>(), v.iter().map(|j| j.name).collect::<Vec<_>>()) }, (vec!["a", "c"], vec!["b"]));
}

#[test]
fn all_expired() {
    check!(r#"deadlines 1, 2; now 10"#, { let mut v = vec![Job { name: "a", deadline: 1 }, Job { name: "b", deadline: 2 }]; let gone = take_expired(&mut v, 10); (gone.len(), v.len()) }, (2, 0));
}
