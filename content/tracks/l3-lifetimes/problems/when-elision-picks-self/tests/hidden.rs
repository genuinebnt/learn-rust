use solution::*;

#[test]
fn define_missing() {
    let g = Glossary::new(&[("rust", "a language"), ("borrow", "a loan"), ("ok", "fine")]);
    check!(r#"glossary {rust: "a language", borrow: "a loan", ok: "fine"}; define go"#, g.define("go"), None);
}

#[test]
fn pick_longer_second() {
    let g = Glossary::new(&[("rust", "a language"), ("borrow", "a loan"), ("ok", "fine")]);
    check!(r#"glossary {rust: "a language", borrow: "a loan", ok: "fine"}; pick(ok, rust)"#, g.pick("ok", "rust"), "rust");
}

#[test]
fn pick_equal_definitions() {
    let g = Glossary::new(&[("a", "xx"), ("b", "yy")]);
    check!(r#"glossary {a: "xx", b: "yy"}; pick(b, a)"#, g.pick("b", "a"), "b");
}

#[test]
fn define_first_unknown() {
    let g = Glossary::new(&[("rust", "a language"), ("borrow", "a loan"), ("ok", "fine")]);
    check!(r#"glossary {rust: "a language", borrow: "a loan", ok: "fine"}; define_first("go fast")"#, define_first(&g, "go fast"), None);
}

#[test]
fn define_first_leading_space() {
    let g = Glossary::new(&[("rust", "a language"), ("borrow", "a loan"), ("ok", "fine")]);
    check!(r#"glossary {rust: "a language", borrow: "a loan", ok: "fine"}; define_first(" rust")"#, define_first(&g, " rust"), None);
}

#[test]
fn empty_glossary() {
    let g = Glossary::new(&[]);
    check!(r#"empty glossary; define_or_echo """#, g.define_or_echo(""), "");
}

#[test]
fn echo_empty_definition() {
    let g = Glossary::new(&[("e", "")]);
    check!(r#"glossary {e: ""}; define_or_echo e"#, g.define_or_echo("e"), "");
}

#[test]
fn unicode() {
    let g = Glossary::new(&[("日本", "Japan")]);
    check!(r#"glossary {日本: "Japan"}; define_first("日本 語")"#, define_first(&g, "日本 語"), Some("Japan"));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6301);
    let words = ["a", "b", "c", "d"];
    for _ in 0..300 {
        let mut defs: Vec<(String, String)> = Vec::new();
        for w in words {
            if rng.bool() {
                let len = rng.below(4);
                defs.push((w.to_string(), rng.string(len, "xy")));
            }
        }
        let pairs: Vec<(&str, &str)> = defs.iter().map(|(w, d)| (w.as_str(), d.as_str())).collect();
        let g = Glossary::new(&pairs);
        let def = |w: &str| defs.iter().find(|e| e.0 == w).map(|e| e.1.clone());
        let (a, b) = (rng.pick(&words).to_string(), rng.pick(&words).to_string());
        let la = def(&a).map_or(0, |d| d.len());
        let lb = def(&b).map_or(0, |d| d.len());
        let want = if lb > la { b.clone() } else { a.clone() };
        check!(format!("defs {defs:?}; pick({a}, {b})"), g.pick(&a, &b).to_string(), want);
        check!(format!("defs {defs:?}; define_or_echo({a})"), g.define_or_echo(&a).to_string(), def(&a).unwrap_or(a.clone()));
        let text = format!("{b} {a}");
        check!(format!("defs {defs:?}; define_first({text:?})"), define_first(&g, &text).map(String::from), def(&b));
    }
}
