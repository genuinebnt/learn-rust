use solution::*;

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
fn strings_by_str() {
    let v = vec!["pear".to_string(), "Apple".to_string(), "fig".to_string()];
    check!(r#"["pear", "Apple", "fig"] by as_str"#, max_by_key(&v, |s| s.as_str()).map(String::as_str), Some("pear"));
}

#[test]
fn tie_on_str_keys() {
    let v = vec!["b".to_string(), "a".to_string(), "b".to_string()];
    check!(r#"["b", "a", "b"] by as_str: which "b"?"#, std::ptr::eq(max_by_key(&v, |s| s.as_str()).unwrap(), &v[0]), true);
}

#[test]
fn identity_on_integers() {
    check!(r#"[3, 9, 2] with |x| x"#, max_by_key(&[3, 9, 2], |x| x), Some(&9));
}

#[test]
fn nested_field() {
    let v = [('a', 1), ('b', 7), ('c', 7)];
    check!(r#"pairs by &pair.1"#, max_by_key(&v, |p| &p.1).map(|p| p.0), Some('b'));
}

#[test]
fn vec_of_vecs_by_slice() {
    let v = vec![vec![1, 2], vec![1, 2, 0], vec![0, 9]];
    check!(r#"[[1, 2], [1, 2, 0], [0, 9]] by as_slice"#, max_by_key(&v, |x| x.as_slice()), Some(&vec![1, 2, 0]));
}

#[test]
fn single() {
    let v = people();
    check!(r#"one person"#, max_by_key(&v[..1], |p| p.name.as_str()).map(|p| p.age), Some(36));
}

#[test]
fn unicode_str_keys() {
    let v = vec!["é".to_string(), "z".to_string()];
    check!(r#"["é", "z"] by as_str"#, max_by_key(&v, |s| s.as_str()).map(String::as_str), Some("é"));
}

#[test]
fn calls_on_empty() {
    let v: Vec<String> = Vec::new();
    let mut calls = 0;
    let _ = max_by_key(&v, |s| {
        calls += 1;
        s.as_str()
    });
    check!(r#"no items: count the calls"#, calls, 0);
}

#[test]
fn calls_with_ties() {
    let v = vec!["x".to_string(); 5];
    let mut calls = 0;
    let _ = max_by_key(&v, |s| {
        calls += 1;
        s.as_str()
    });
    check!(r#"five equal names: count the calls"#, calls, 5);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4504);
    for _ in 0..300 {
        let n = rng.below(7);
        let words: Vec<String> = (0..n).map(|_| { let len = rng.below(3); rng.string(len, "ab") }).collect();
        let mut want: Option<usize> = None;
        for i in 0..n {
            if want.map_or(true, |w| words[i] > words[w]) {
                want = Some(i);
            }
        }
        let mut calls = 0;
        let got = max_by_key(&words, |w| {
            calls += 1;
            w.as_str()
        });
        check!(format!("words = {words:?}"), (got.map(|r| r as *const String), calls), (want.map(|i| &words[i] as *const String), n));
    }
}
