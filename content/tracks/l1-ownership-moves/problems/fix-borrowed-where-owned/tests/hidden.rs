use solution::*;

#[test]
fn outlives_input() {
    check!(r#"tag kept after its input is dropped"#, { let t = { let s = String::from("tmp"); Tag::new(&s) }; t.name }, "tmp".to_string());
}

#[test]
fn spaces_kept() {
    check!(r#"name = " a b ""#, Tag::new(" a b ").name, " a b ".to_string());
}

#[test]
fn case_kept() {
    check!(r#"name = "RuSt""#, Tag::new("RuSt").name, "RuSt".to_string());
}

#[test]
fn unicode() {
    check!(r#"name = "日本語""#, Tag::new("日本語").name, "日本語".to_string());
}

#[test]
fn emoji() {
    check!(r#"name = "🦀 crab""#, Tag::new("🦀 crab").name, "🦀 crab".to_string());
}

#[test]
fn source_changed_later() {
    check!(r#"input String changed after new"#, { let mut s = String::from("old"); let t = Tag::new(&s); s.push_str("er"); (t.name, s) }, ("old".to_string(), "older".to_string()));
}

#[test]
fn two_tags_one_str() {
    check!(r#"two tags from the same &str"#, { let s = "same"; let (a, b) = (Tag::new(s), Tag::new(s)); a == b && a.name.as_ptr() != b.name.as_ptr() }, true);
}

#[test]
fn long_name() {
    check!(r#"name = 100000 × 'x'"#, Tag::new(&"x".repeat(100_000)).name.len(), 100_000);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1106);
    for _ in 0..300 {
        let len = rng.below(12);
        let s = rng.string(len, "aZ é日🦀\t");
        check!(format!("name = {s:?}"), Tag::new(&s).name, s.clone());
    }
}
