use solution::*;

#[test]
fn empty() {
    check!(r#"[]"#, { let mut v: Vec<String> = vec![]; expand(&mut v); v.len() }, 0);
}

#[test]
fn only_star() {
    check!(r#"["*"]"#, { let mut v = vec!["*".to_string()]; expand(&mut v); v }, vec!["*", "*.1", "*.2"]);
}

#[test]
fn double_star() {
    check!(r#"["a**"]"#, { let mut v = vec!["a**".to_string()]; expand(&mut v); v }, vec!["a**", "a**.1", "a**.2"]);
}

#[test]
fn unicode() {
    check!(r#"["é*"]"#, { let mut v = vec!["é*".to_string()]; expand(&mut v); v }, vec!["é*", "é*.1", "é*.2"]);
}

#[test]
fn duplicates() {
    check!(r#"["a*", "a*"]"#, { let mut v: Vec<String> = ["a*", "a*"].map(String::from).to_vec(); expand(&mut v); v }, vec!["a*", "a*", "a*.1", "a*.2", "a*.1", "a*.2"]);
}

#[test]
fn star_first() {
    check!(r#"["*a"]"#, { let mut v = vec!["*a".to_string()]; expand(&mut v); v }, vec!["*a"]);
}

#[test]
fn many() {
    check!(r#"1000 starred tasks"#, { let mut v: Vec<String> = (0..1000).map(|i| format!("t{i}*")).collect(); expand(&mut v); (v.len(), v[1000].clone(), v[2999].clone()) }, (3000, "t0*.1".to_string(), "t999*.2".to_string()));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2018);
    for _ in 0..300 {
        let n = rng.below(6);
        let tasks: Vec<String> = (0..n).map(|_| { let l = rng.below(4); rng.string(l, "a*") }).collect();
        let mut want = tasks.clone();
        for t in &tasks {
            if t.ends_with('*') {
                want.push(format!("{t}.1"));
                want.push(format!("{t}.2"));
            }
        }
        let mut got = tasks.clone();
        expand(&mut got);
        check!(format!("tasks = {tasks:?}"), got, want);
    }
}
