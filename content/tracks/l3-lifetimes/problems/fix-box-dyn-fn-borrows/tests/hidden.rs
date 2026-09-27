use solution::*;

#[test]
fn filter_empty_allowed() {
    check!(r#"allowed []"#, make_filter(&[])("a"), false);
}

#[test]
fn filter_case_sensitive() {
    check!(r#"allowed ["A"]: test a"#, make_filter(&["A"])("a"), false);
}

#[test]
fn checks_all_pass() {
    check!(r#"one check that always passes"#, { let mut c = Checks::new(); c.add("any", |_| true); c.failures("q").len() }, 0);
}

#[test]
fn checks_order() {
    let mut c = Checks::new();
    c.add("c", |_| false);
    c.add("a", |_| false);
    c.add("b", |w| w.is_empty());
    check!(r#"three failing checks"#, c.failures("z"), vec!["c", "a", "b"]);
}

#[test]
fn checks_static_closure() {
    let mut c = Checks::new();
    c.add("digit", |w| w.chars().all(|ch| ch.is_ascii_digit()));
    check!(r#"a check with no borrows"#, (c.failures("12"), c.failures("1a")), (Vec::<&str>::new(), vec!["digit"]));
}

#[test]
fn count_passing_empty() {
    check!(r#"no words"#, count_passing(&[], &|_| true), 0);
}

#[test]
fn labels_empty() {
    check!(r#"labels of []"#, labels(&[]).len(), 0);
}

#[test]
fn labels_point_into_names() {
    let names = vec![String::from("a"), String::from("b")];
    check!(r#"a label displays the name it borrows"#, format!("{}{}", labels(&names)[1], labels(&names)[0]), "ba".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6317);
    let pool = ["a", "b", "c", "ab", "ba"];
    for _ in 0..300 {
        let k = rng.below(4);
        let allowed: Vec<&str> = (0..k).map(|_| *rng.pick(&pool)).collect();
        let f = make_filter(&allowed);
        let w = *rng.pick(&pool);
        check!(format!("allowed {allowed:?}; {w}"), f(w), allowed.contains(&w));
        let min = rng.below(3);
        let mut c = Checks::new();
        c.add("min", |x| x.len() >= min);
        c.add("allowed", |x| allowed.contains(&x));
        let mut want = Vec::new();
        if w.len() < min {
            want.push("min");
        }
        if !allowed.contains(&w) {
            want.push("allowed");
        }
        check!(format!("allowed {allowed:?}, min {min}; failures({w})"), c.failures(w), want);
    }
}
