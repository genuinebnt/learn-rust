use solution::*;

#[allow(dead_code)]
struct Person {
    name: String,
    age: u32,
    tags: Vec<i32>,
}

fn people() -> Vec<Person> {
    vec![
        Person { name: "ada".into(), age: 36, tags: vec![1, 5] },
        Person { name: "zed".into(), age: 31, tags: vec![1, 5, 0] },
        Person { name: "bob".into(), age: 36, tags: vec![2] },
    ]
}

#[test]
fn by_name() {
    let v = people();
    check!(r#"people by name"#, max_by_key(&v, |p| p.name.as_str()).map(|p| p.age), Some(31));
}

#[test]
fn by_age_first_on_tie() {
    let v = people();
    check!(r#"people by &age: ada and bob are both 36"#, max_by_key(&v, |p| &p.age).map(|p| p.name.as_str()), Some("ada"));
}

#[test]
fn by_slice() {
    let v = people();
    check!(r#"people by tags as &[i32] (lexicographic)"#, max_by_key(&v, |p| p.tags.as_slice()).map(|p| p.name.as_str()), Some("bob"));
}

#[test]
fn empty() {
    let v: Vec<Person> = Vec::new();
    check!(r#"no people"#, max_by_key(&v, |p| p.name.as_str()).is_none(), true);
}

#[test]
fn key_called_once_per_item() {
    let v = people();
    let mut calls = 0;
    let best = max_by_key(&v, |p| {
        calls += 1;
        p.name.as_str()
    }).map(|p| p.name.as_str());
    check!(r#"count the calls over three people"#, (best, calls), (Some("zed"), 3));
}
