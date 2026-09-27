use solution::*;

#[test]
fn ascii_only() {
    check!(r#"names = ["straße", "b"]"#, { let mut v = vec!["straße".to_string(), "b".to_string()]; shout_first(&mut v); v }, vec!["STRAßE!".to_string(), "b!".to_string()]);
}

#[test]
fn accents_untouched() {
    check!(r#"names = ["é"]"#, { let mut v = vec!["é".to_string()]; shout_first(&mut v); v }, vec!["é!".to_string()]);
}

#[test]
fn letters_and_digits() {
    check!(r#"names = ["a1b2"]"#, { let mut v = vec!["a1b2".to_string()]; shout_first(&mut v); v }, vec!["A1B2!".to_string()]);
}

#[test]
fn empty_first() {
    check!(r#"names = ["", "x"]"#, { let mut v = vec![String::new(), "x".to_string()]; shout_first(&mut v); v }, vec!["!".to_string(), "x!".to_string()]);
}

#[test]
fn duplicates() {
    check!(r#"names = ["x", "x"]"#, { let mut v = vec!["x".to_string(), "x".to_string()]; shout_first(&mut v); v }, vec!["X!".to_string(), "x!".to_string()]);
}

#[test]
fn spaces() {
    check!(r#"names = ["hi there"]"#, { let mut v = vec!["hi there".to_string()]; shout_first(&mut v); v }, vec!["HI THERE!".to_string()]);
}

#[test]
fn many() {
    check!(r#"1000 names "n""#, { let mut v = vec!["n".to_string(); 1000]; shout_first(&mut v); (v.len(), v[0].clone(), v[999].clone()) }, (1000, "N!".to_string(), "n!".to_string()));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2007);
    for _ in 0..300 {
        let n = 1 + rng.below(5);
        let names: Vec<String> = (0..n).map(|_| { let l = rng.below(4); rng.string(l, "abXY1é") }).collect();
        let want: Vec<String> = names.iter().enumerate().map(|(i, s)| if i == 0 { format!("{}!", s.to_ascii_uppercase()) } else { format!("{s}!") }).collect();
        let mut got = names.clone();
        shout_first(&mut got);
        check!(format!("names = {names:?}"), got, want);
    }
}
