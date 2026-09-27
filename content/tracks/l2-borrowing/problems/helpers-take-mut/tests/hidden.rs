use solution::*;

#[test]
fn different() {
    check!(r#""a", "b""#, { let (mut a, mut b) = ("a".to_string(), "b".to_string()); same_after_normalizing(&mut a, &mut b) }, false);
}

#[test]
fn only_spaces() {
    check!(r#""   ", """#, { let (mut a, mut b) = ("   ".to_string(), String::new()); (same_after_normalizing(&mut a, &mut b), a) }, (true, String::new()));
}

#[test]
fn unicode_lowercase() {
    check!(r#""ÉCOLE", "école""#, { let (mut a, mut b) = ("ÉCOLE".to_string(), "école".to_string()); (same_after_normalizing(&mut a, &mut b), a) }, (true, "école".to_string()));
}

#[test]
fn tabs_newlines() {
    check!(r#""\tHi\n", "hi""#, { let (mut a, mut b) = ("\tHi\n".to_string(), "hi".to_string()); (same_after_normalizing(&mut a, &mut b), a) }, (true, "hi".to_string()));
}

#[test]
fn both_changed() {
    check!(r#""X ", " x""#, { let (mut a, mut b) = ("X ".to_string(), " x".to_string()); same_after_normalizing(&mut a, &mut b); (a, b) }, ("x".to_string(), "x".to_string()));
}

#[test]
fn different_after_trim() {
    check!(r#""ab", "a b""#, { let (mut a, mut b) = ("ab".to_string(), "a b".to_string()); same_after_normalizing(&mut a, &mut b) }, false);
}

#[test]
fn trailing_only() {
    check!(r#""go  ", "go""#, { let (mut a, mut b) = ("go  ".to_string(), "go".to_string()); same_after_normalizing(&mut a, &mut b) }, true);
}

#[test]
fn normalize_idempotent() {
    check!(r#"normalize " A " twice"#, { let mut s = " A ".to_string(); normalize(&mut s); normalize(&mut s); s }, "a".to_string());
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2012);
    for _ in 0..300 {
        let la = rng.below(6);
        let a0 = rng.string(la, " aAéÉ\t");
        let lb = rng.below(6);
        let b0 = rng.string(lb, " aAéÉ\t");
        let (mut a, mut b) = (a0.clone(), b0.clone());
        let got = same_after_normalizing(&mut a, &mut b);
        let (na, nb) = (a0.trim().to_lowercase(), b0.trim().to_lowercase());
        check!(format!("a = {a0:?}, b = {b0:?}"), (got, a, b), (na == nb, na, nb));
    }
}
