use solution::*;

#[test]
fn keeps_length() {
    check!(r#"names = ["a", "b", "c"]"#, { let mut v = vec!["a".to_string(), "b".to_string(), "c".to_string()]; take_first(&mut v); v.len() }, 3);
}

#[test]
fn rest_untouched() {
    check!(r#"names = ["a", "b", "c"]"#, { let mut v = vec!["a".to_string(), "b".to_string(), "c".to_string()]; take_first(&mut v); v }, vec!["", "b", "c"]);
}

#[test]
fn first_already_empty() {
    check!(r#"names = ["", "b"]"#, { let mut v = vec![String::new(), "b".to_string()]; (take_first(&mut v), v) }, (String::new(), vec![String::new(), "b".to_string()]));
}

#[test]
fn twice() {
    check!(r#"take_first twice on ["ann", "bo"]"#, { let mut v = vec!["ann".to_string(), "bo".to_string()]; let a = take_first(&mut v); let b = take_first(&mut v); (a, b) }, ("ann".to_string(), String::new()));
}

#[test]
fn same_buffer() {
    check!(r#"the returned String is the one from the Vec"#, { let mut v = vec![String::from("moved")]; let p = v[0].as_ptr(); take_first(&mut v).as_ptr() == p }, true);
}

#[test]
fn slot_not_allocated() {
    check!(r#"capacity left in names[0]"#, { let mut v = vec![String::from("gone")]; take_first(&mut v); v[0].capacity() }, 0);
}

#[test]
fn unicode() {
    check!(r#"names = ["日本", "é"]"#, { let mut v = vec!["日本".to_string(), "é".to_string()]; (take_first(&mut v), v) }, ("日本".to_string(), vec![String::new(), "é".to_string()]));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1114);
    for _ in 0..300 {
        let n = rng.below(6) + 1;
        let mut names = Vec::new();
        for _ in 0..n {
            let len = rng.below(4);
            names.push(rng.string(len, "abé"));
        }
        let mut want_rest = names.clone();
        let want_first = std::mem::replace(&mut want_rest[0], String::new());
        let input = format!("names = {names:?}");
        let first = take_first(&mut names);
        check!(input, (first, names), (want_first, want_rest));
    }
}
