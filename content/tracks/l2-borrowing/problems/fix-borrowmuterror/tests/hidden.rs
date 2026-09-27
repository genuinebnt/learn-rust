use solution::*;

#[test]
fn empty_name() {
    check!(r#"add "" twice"#, { let r = Registry::new(); r.add(""); r.add(""); r.len() }, 1);
}

#[test]
fn unicode() {
    check!(r#"add "é" twice"#, { let r = Registry::new(); r.add("é"); r.add("é"); r.len() }, 1);
}

#[test]
fn many_distinct() {
    check!(r#"1000 names"#, { let r = Registry::new(); for i in 0..1000 { r.add(&i.to_string()); } r.len() }, 1000);
}

#[test]
fn many_duplicates() {
    check!(r#"1000 adds of 10 names"#, { let r = Registry::new(); for i in 0..1000 { r.add(&(i % 10).to_string()); } r.len() }, 10);
}

#[test]
fn shared_refs() {
    check!(r#"add through two &Registry"#, { let r = Registry::new(); let (a, b) = (&r, &r); a.add("x"); b.add("y"); b.add("x"); r.len() }, 2);
}

#[test]
fn prefix_is_different() {
    check!(r#"add "ab", "a""#, { let r = Registry::new(); r.add("ab"); r.add("a"); r.len() }, 2);
}

#[test]
fn spaces_matter() {
    check!(r#"add "a", "a ""#, { let r = Registry::new(); r.add("a"); r.add("a "); r.len() }, 2);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2031);
    for _ in 0..300 {
        let r = Registry::new();
        let mut model: Vec<String> = Vec::new();
        let n = rng.below(10);
        let mut log = Vec::new();
        for _ in 0..n {
            let l = 1 + rng.below(2);
            let name = rng.string(l, "aAb");
            r.add(&name);
            if !model.contains(&name) {
                model.push(name.clone());
            }
            log.push(name);
        }
        check!(format!("adds {log:?}"), r.len(), model.len());
    }
}
