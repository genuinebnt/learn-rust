use solution::*;

#[test]
fn after_no_match() {
    check!(r#"after("abc", "x")"#, after("abc", "x"), None);
}

#[test]
fn after_empty_prefix() {
    check!(r#"after("abc", "")"#, after("abc", ""), Some("abc"));
}

#[test]
fn after_whole_line() {
    check!(r#"after("abc", "abc")"#, after("abc", "abc"), Some(""));
}

#[test]
fn lookup_missing() {
    let m = std::collections::HashMap::new();
    check!(r#"map {}; lookup x"#, lookup(&m, "x"), None);
}

#[test]
fn layered_empty_local() {
    const GLOBAL: &[(&str, &str)] = &[("color", "auto"), ("pager", "less")];
    let layered = Layered { global: GLOBAL, local: &[] };
    check!(r#"local {}"#, layered.get("pager"), Some("less"));
}

#[test]
fn layered_first_local_duplicate() {
    const GLOBAL: &[(&str, &str)] = &[("color", "auto"), ("pager", "less")];
    let local = [("a", "1"), ("a", "2")];
    let layered = Layered { global: GLOBAL, local: &local };
    check!(r#"local {a: 1, a: 2}"#, layered.get("a"), Some("1"));
}

#[test]
fn after_result_points_into_line() {
    let line = String::from("abcd");
    check!(r#"after's result borrows the line"#, after(&line, "ab").unwrap().as_ptr() == line[2..].as_ptr(), true);
}

#[test]
fn lookup_result_outlives_key_scope() {
    let map = std::collections::HashMap::from([("k".to_string(), "val".to_string())]);
    let v = {
        let key = String::from("k");
        lookup(&map, &key).unwrap()
    };
    check!(r#"lookup result used after the key's block"#, v.len(), 3);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6304);
    for _ in 0..300 {
        let len = rng.below(5);
        let line = rng.string(len, "ab");
        let plen = rng.below(3);
        let prefix = rng.string(plen, "ab");
        check!(format!("after({line:?}, {prefix:?})"), after(&line, &prefix), line.strip_prefix(prefix.as_str()));
        let keys = ["a", "b", "c"];
        let global: Vec<(&str, &str)> = keys.iter().filter(|_| rng.bool()).map(|&k| (k, "g")).collect();
        let local: Vec<(&str, &str)> = keys.iter().filter(|_| rng.bool()).map(|&k| (k, "l")).collect();
        let layered = Layered { global: &global, local: &local };
        for k in keys {
            let want = local.iter().chain(global.iter()).find(|e| e.0 == k).map(|e| e.1);
            check!(format!("global {global:?}, local {local:?}; get({k})"), layered.get(k), want);
        }
    }
}
