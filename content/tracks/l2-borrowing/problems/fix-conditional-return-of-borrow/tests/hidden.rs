use solution::*;

#[test]
fn no_push_when_found() {
    check!(r#"["a", "b", "long"], n = 3"#, { let mut v = vec!["a".to_string(), "b".to_string(), "long".to_string()]; let r = first_long_or_push(&mut v, 3).clone(); (r, v.len()) }, ("long".to_string(), 3));
}

#[test]
fn n_zero() {
    check!(r#"["x"], n = 0"#, { let mut v = vec!["x".to_string()]; first_long_or_push(&mut v, 0).clone() }, "x".to_string());
}

#[test]
fn existing_fallback_word() {
    check!(r#"["fallback"], n = 8"#, { let mut v = vec!["fallback".to_string()]; first_long_or_push(&mut v, 8); v.len() }, 2);
}

#[test]
fn unicode_bytes() {
    check!(r#"["日本"], n = 5"#, { let mut v = vec!["日本".to_string()]; first_long_or_push(&mut v, 5).clone() }, "日本".to_string());
}

#[test]
fn n_max() {
    check!(r#"["abc"], n = usize::MAX"#, { let mut v = vec!["abc".to_string()]; first_long_or_push(&mut v, usize::MAX).clone() }, "fallback".to_string());
}

#[test]
fn twice_pushes_twice() {
    check!(r#"[], n = 10, twice"#, { let mut v = vec![]; first_long_or_push(&mut v, 10); first_long_or_push(&mut v, 10); v.len() }, 2);
}

#[test]
fn fallback_found_second_time() {
    check!(r#"[], n = 3, twice"#, { let mut v = vec![]; first_long_or_push(&mut v, 3); first_long_or_push(&mut v, 3); v.len() }, 1);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2028);
    for _ in 0..300 {
        let k = rng.below(5);
        let words: Vec<String> = (0..k).map(|_| { let l = rng.below(5); rng.string(l, "ab") }).collect();
        let n = rng.below(5);
        let mut want_v = words.clone();
        let want = match words.iter().position(|w| w.len() > n) {
            Some(i) => words[i].clone(),
            None => {
                want_v.push("fallback".to_string());
                "fallback".to_string()
            }
        };
        let mut v = words.clone();
        let got = first_long_or_push(&mut v, n).clone();
        check!(format!("words = {words:?}, n = {n}"), (got, v), (want, want_v));
    }
}
