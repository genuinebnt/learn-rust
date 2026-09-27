use solution::*;

fn rules(xs: &[(&str, &[&str])]) -> std::collections::HashMap<String, Vec<String>> {
    xs.iter().map(|(k, v)| (k.to_string(), v.iter().map(|s| s.to_string()).collect())).collect()
}

fn run(tasks: &[&str], r: &[(&str, &[&str])]) -> (usize, Vec<String>) {
    let mut t: Vec<String> = tasks.iter().map(|s| s.to_string()).collect();
    let n = expand(&mut t, &rules(r));
    (n, t)
}

#[test]
fn self_rule() {
    check!(r#"tasks ["a"], rules {"a": ["a"]}"#, run(&["a"], &[("a", &["a"][..])]), (0, ["a"].map(String::from).to_vec()));
}

#[test]
fn deep_chain() {
    check!(r#"tasks ["a"], rules {"a": ["b"], "b": ["c"], "c": ["d"], "d": ["e"]}"#, run(&["a"], &[("a", &["b"][..]), ("b", &["c"][..]), ("c", &["d"][..]), ("d", &["e"][..])]), (4, ["a", "b", "c", "d", "e"].map(String::from).to_vec()));
}

#[test]
fn order_is_breadth_first() {
    check!(r#"tasks ["r"], rules {"r": ["a", "b"], "a": ["c"], "b": ["d"]}"#, run(&["r"], &[("r", &["a", "b"][..]), ("a", &["c"][..]), ("b", &["d"][..])]), (4, ["r", "a", "b", "c", "d"].map(String::from).to_vec()));
}

#[test]
fn duplicate_subtasks() {
    check!(r#"tasks ["a"], rules {"a": ["x", "x", "y"]}"#, run(&["a"], &[("a", &["x", "x", "y"][..])]), (2, ["a", "x", "y"].map(String::from).to_vec()));
}

#[test]
fn shared_child() {
    check!(r#"tasks ["a", "b"], rules {"a": ["c"], "b": ["c"], "c": ["d"]}"#, run(&["a", "b"], &[("a", &["c"][..]), ("b", &["c"][..]), ("c", &["d"][..])]), (2, ["a", "b", "c", "d"].map(String::from).to_vec()));
}

#[test]
fn empty_rule() {
    check!(r#"tasks ["a"], rules {"a": []}"#, run(&["a"], &[("a", &[][..])]), (0, ["a"].map(String::from).to_vec()));
}

#[test]
fn no_rules() {
    check!(r#"tasks ["a"], rules {}"#, run(&["a"], &[]), (0, ["a"].map(String::from).to_vec()));
}

#[test]
fn unicode() {
    check!(r#"tasks ["日本"], rules {"日本": ["東京"], "東京": ["新宿"]}"#, run(&["日本"], &[("日本", &["東京"][..]), ("東京", &["新宿"][..])]), (2, ["日本", "東京", "新宿"].map(String::from).to_vec()));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6220);
    let names = ["a", "b", "c", "d", "e", "f"];
    for _ in 0..300 {
        let mut r: std::collections::HashMap<String, Vec<String>> = std::collections::HashMap::new();
        for n in names {
            if rng.bool() {
                let k = rng.below(3);
                let subs: Vec<String> = (0..k).map(|_| rng.pick(&names).to_string()).collect();
                r.insert(n.to_string(), subs);
            }
        }
        let k = rng.below(3);
        let start: Vec<String> = (0..k).map(|_| rng.pick(&names).to_string()).collect();
        let mut want = start.clone();
        let mut i = 0;
        while i < want.len() {
            for s in r.get(&want[i]).cloned().unwrap_or_default() {
                if !want.contains(&s) {
                    want.push(s);
                }
            }
            i += 1;
        }
        let mut got = start.clone();
        let n = expand(&mut got, &r);
        let mut shown: Vec<_> = r.iter().collect();
        shown.sort();
        check!(format!("tasks {start:?}, rules {shown:?}"), (n, got), (want.len() - start.len(), want));
    }
}

#[test]
fn long_chain() {
    let r: std::collections::HashMap<String, Vec<String>> = (0..2000).map(|i| (format!("t{i}"), vec![format!("t{}", i + 1)])).collect();
    let mut tasks = vec!["t0".to_string()];
    let n = expand(&mut tasks, &r);
    check!("a chain t0 -> t1 -> ... -> t2000", (n, tasks.last().cloned()), (2000, Some("t2000".to_string())));
}
