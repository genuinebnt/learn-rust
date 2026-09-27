use solution::*;

fn profile(name: &str, nickname: Option<&str>, labels: &[(u32, &str)]) -> Profile {
    let mut p = Profile::new(name, nickname);
    for &(id, l) in labels {
        p.labels.insert(id, l.to_string());
    }
    p
}

#[test]
fn empty_nickname_is_still_a_nickname() {
    let p = profile("Ada", Some(""), &[]);
    check!(r#"profile Ada / """#, greeting(&p.name, p.nickname()), "Hello, !".to_string());
}

#[test]
fn empty_label_is_still_a_label() {
    let p = profile("Ada", None, &[(3, "")]);
    check!(r#"labels {3: ""}"#, (p.label(3), label_or(&p, 3, "?")), (Some(""), ""));
}

#[test]
fn id_extremes() {
    let p = profile("Ada", None, &[(0, "zero"), (u32::MAX, "max")]);
    check!(r#"labels {0: "zero", u32::MAX: "max"}"#, (label_or(&p, 0, "?"), label_or(&p, u32::MAX, "?"), p.label(1)), ("zero", "max", None));
}

#[test]
fn unicode() {
    let p = profile("Zoë", Some("🦀"), &[(5, "café ☕")]);
    check!(r#"profile "Zoë" / "🦀", label {5: "café ☕"}"#, (greeting(&p.name, p.nickname()), p.label(5)), ("Hello, 🦀!".to_string(), Some("café ☕")));
}

#[test]
fn greeting_with_an_owned_option() {
    let nick: Option<String> = Some("bo".into());
    check!(r#"nickname: Option<String> held by the caller"#, greeting("Ada", nick.as_deref()), "Hello, bo!".to_string());
}

#[test]
fn no_nickname_uses_the_name() {
    let p = profile("Zed", None, &[]);
    check!(r#"profile Zed / none"#, greeting(&p.name, p.nickname()), "Hello, Zed!".to_string());
}

#[test]
fn label_or_borrows_from_the_map() {
    let p = profile("Ada", None, &[(1, "one")]);
    check!(r#"labels {1: "one"}"#, std::ptr::eq(label_or(&p, 1, "?").as_ptr(), p.labels[&1].as_ptr()), true);
}

#[test]
fn label_or_returns_the_default_itself() {
    let p = profile("Ada", None, &[]);
    let d = "fallback";
    check!(r#"labels {}, default d"#, std::ptr::eq(label_or(&p, 1, d).as_ptr(), d.as_ptr()), true);
}

#[test]
fn default_from_a_short_lived_string() {
    let p = profile("Ada", None, &[]);
    let local = String::from("local");
    check!(r#"default is a local String"#, label_or(&p, 9, &local).len(), 5);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7105);
    for _ in 0..300 {
        let n = rng.below(5);
        let mut pairs: Vec<(u32, String)> = Vec::new();
        for _ in 0..n {
            let k = rng.below(6) as u32;
            let len = rng.below(3);
            let v = rng.string(len, "ab");
            pairs.retain(|(pk, _)| *pk != k);
            pairs.push((k, v));
        }
        let refs: Vec<(u32, &str)> = pairs.iter().map(|(k, v)| (*k, v.as_str())).collect();
        let nick = if rng.bool() { Some(*rng.pick(&["", "x", "ß"])) } else { None };
        let p = profile("N", nick, &refs);
        let id = rng.below(6) as u32;
        let want = refs.iter().find(|(k, _)| *k == id).map(|(_, v)| *v);
        let desc = format!("nickname = {nick:?}, labels = {refs:?}, id = {id}");
        check!(format!("label, {desc}"), p.label(id), want);
        check!(format!("label_or, {desc}"), label_or(&p, id, "-"), want.unwrap_or("-"));
        check!(format!("greeting, {desc}"), greeting(&p.name, p.nickname()), format!("Hello, {}!", nick.unwrap_or("N")));
    }
}

#[test]
fn scale_many_lookups() {
    let mut p = profile("Ada", None, &[]);
    for i in 0..200_000u32 {
        p.labels.insert(i * 2, "x".into());
    }
    let found = (0..400_000u32).filter(|&id| label_or(&p, id, "").len() == 1).count();
    check!("200000 labels (even ids), look up every id below 400000", found, 200_000);
}
