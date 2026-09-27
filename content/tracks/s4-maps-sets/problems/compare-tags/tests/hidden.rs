use solution::*;

#[test]
fn b_only_duplicates() {
    check!(r#"a = [], b = [y, y]"#, compare_tags(&[], &["y", "y"]), (vec![], vec![], vec!["y".to_string()]));
}

#[test]
fn identical() {
    check!(r#"a = [a, b], b = [b, a]"#, compare_tags(&["a", "b"], &["b", "a"]), (vec!["a".to_string(), "b".to_string()], vec![], vec![]));
}

#[test]
fn case_sensitive() {
    check!(r#"a = [Rust], b = [rust]"#, compare_tags(&["Rust"], &["rust"]), (vec![], vec!["Rust".to_string()], vec!["rust".to_string()]));
}

#[test]
fn unicode() {
    check!(r#"a = [é, e], b = [e]"#, compare_tags(&["é", "e"], &["e"]), (vec!["e".to_string()], vec!["é".to_string()], vec![]));
}

#[test]
fn byte_order() {
    check!(r#"a = [b, B, a], b = []"#, compare_tags(&["b", "B", "a"], &[]), (vec![], vec!["B".to_string(), "a".to_string(), "b".to_string()], vec![]));
}

#[test]
fn empty_tag() {
    check!(r#"a = [""], b = [""]"#, compare_tags(&[""], &[""]), (vec![String::new()], vec![], vec![]));
}

#[test]
fn one_side_empty() {
    check!(r#"a = [x], b = []"#, compare_tags(&["x"], &[]), (vec![], vec!["x".to_string()], vec![]));
}

#[test]
fn sorted_intersection() {
    check!(r#"a = [z, m, a], b = [a, z, m]"#, compare_tags(&["z", "m", "a"], &["a", "z", "m"]).0, vec!["a".to_string(), "m".to_string(), "z".to_string()]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4003);
    let pool = ["a", "b", "c", "d", "e", "B"];
    for _ in 0..300 {
        let (na, nb) = (rng.below(6), rng.below(6));
        let a: Vec<&str> = (0..na).map(|_| *rng.pick(&pool)).collect();
        let b: Vec<&str> = (0..nb).map(|_| *rng.pick(&pool)).collect();
        let sa: std::collections::BTreeSet<String> = a.iter().map(|s| s.to_string()).collect();
        let sb: std::collections::BTreeSet<String> = b.iter().map(|s| s.to_string()).collect();
        let want = (
            sa.intersection(&sb).cloned().collect::<Vec<_>>(),
            sa.difference(&sb).cloned().collect::<Vec<_>>(),
            sb.difference(&sa).cloned().collect::<Vec<_>>(),
        );
        check!(format!("a = {a:?}, b = {b:?}"), compare_tags(&a, &b), want);
    }
}

#[test]
fn scale_100k_each() {
    let a_tags: Vec<String> = (0..100_000).map(|i| format!("t{i}")).collect();
    let b_tags: Vec<String> = (50_000..150_000).map(|i| format!("t{i}")).collect();
    let a: Vec<&str> = a_tags.iter().map(|s| s.as_str()).collect();
    let b: Vec<&str> = b_tags.iter().map(|s| s.as_str()).collect();
    let (both, only_a, only_b) = compare_tags(&a, &b);
    check!("a = t0..t99999, b = t50000..t149999", (both.len(), only_a.len(), only_b.len(), only_a[0].clone()), (50_000, 50_000, 50_000, "t0".to_string()));
}
