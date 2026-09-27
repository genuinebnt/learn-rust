use solution::*;

#[test]
fn empty_name() {
    check!(r#"name = """#, { let mut out = vec![]; greet_thrice(String::new(), &mut out); out[2].clone() }, "hello, ".to_string());
}

#[test]
fn empty_name_all_three() {
    check!(r#"name = """#, { let mut out = vec![]; greet_thrice(String::new(), &mut out); out }, vec!["hello, "; 3]);
}

#[test]
fn keeps_existing_first() {
    check!(r#"out = ["hi"], name = "bo""#, { let mut out = vec!["hi".to_string()]; greet_thrice("bo".into(), &mut out); out }, vec!["hi", "hello, bo", "hello, bo", "hello, bo"]);
}

#[test]
fn third_is_full() {
    check!(r#"name = "ann", the last push"#, { let mut out = vec![]; greet_thrice("ann".into(), &mut out); out[2].clone() }, "hello, ann".to_string());
}

#[test]
fn name_with_spaces() {
    check!(r#"name = "ann lee""#, { let mut out = vec![]; greet_thrice("ann lee".into(), &mut out); out }, vec!["hello, ann lee"; 3]);
}

#[test]
fn called_twice() {
    check!(r#"greet_thrice("a"), then greet_thrice("b")"#, { let mut out = vec![]; greet_thrice("a".into(), &mut out); greet_thrice("b".into(), &mut out); out }, vec!["hello, a", "hello, a", "hello, a", "hello, b", "hello, b", "hello, b"]);
}

#[test]
fn independent_strings() {
    check!(r#"change out[0] afterwards"#, { let mut out = vec![]; greet_thrice("x".into(), &mut out); out[0].push('!'); out }, vec!["hello, x!", "hello, x", "hello, x"]);
}

#[test]
fn long_name() {
    check!(r#"name = 10000 × 'n'"#, { let mut out = vec![]; greet_thrice("n".repeat(10_000), &mut out); out.iter().map(|s| s.len()).collect::<Vec<_>>() }, vec![10_007; 3]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1103);
    for _ in 0..300 {
        let before = rng.below(4);
        let len = rng.below(8);
        let name = rng.string(len, "abé ");
        let mut out: Vec<String> = (0..before).map(|i| format!("old {i}")).collect();
        let mut want = out.clone();
        for _ in 0..3 {
            want.push(format!("hello, {name}"));
        }
        greet_thrice(name.clone(), &mut out);
        check!(format!("name = {name:?}, out had {before} lines"), out, want);
    }
}
