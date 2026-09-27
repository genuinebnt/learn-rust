use solution::*;

#[test]
fn empty_list() {
    check!(r#"[], prefix "a""#, { let mut v: Vec<String> = vec![]; remove_prefixed(&mut v, "a"); v.len() }, 0);
}

#[test]
fn all_match() {
    check!(r#"["x", "xx", "xxx"], prefix "x""#, { let mut v: Vec<String> = ["x", "xx", "xxx"].map(String::from).to_vec(); remove_prefixed(&mut v, "x"); v.len() }, 0);
}

#[test]
fn exact_match() {
    check!(r#"["tmp"], prefix "tmp""#, { let mut v = vec!["tmp".to_string()]; remove_prefixed(&mut v, "tmp"); v.len() }, 0);
}

#[test]
fn case_sensitive() {
    check!(r#"["Tmp", "tmp"], prefix "tmp""#, { let mut v: Vec<String> = ["Tmp", "tmp"].map(String::from).to_vec(); remove_prefixed(&mut v, "tmp"); v }, vec!["Tmp".to_string()]);
}

#[test]
fn prefix_longer() {
    check!(r#"["tm"], prefix "tmp""#, { let mut v = vec!["tm".to_string()]; remove_prefixed(&mut v, "tmp"); v }, vec!["tm".to_string()]);
}

#[test]
fn unicode_prefix() {
    check!(r#"["élan", "elan"], prefix "é""#, { let mut v: Vec<String> = ["élan", "elan"].map(String::from).to_vec(); remove_prefixed(&mut v, "é"); v }, vec!["elan".to_string()]);
}

#[test]
fn order_kept() {
    check!(r#"["b1", "a", "b2", "c", "b3"], prefix "b""#, { let mut v: Vec<String> = ["b1", "a", "b2", "c", "b3"].map(String::from).to_vec(); remove_prefixed(&mut v, "b"); v }, vec!["a".to_string(), "c".to_string()]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2016);
    for _ in 0..300 {
        let n = rng.below(8);
        let names: Vec<String> = (0..n).map(|_| { let l = rng.below(4); rng.string(l, "ab") }).collect();
        let pl = rng.below(3);
        let prefix = rng.string(pl, "ab");
        let want: Vec<String> = names.iter().filter(|s| !s.starts_with(prefix.as_str())).cloned().collect();
        let mut got = names.clone();
        remove_prefixed(&mut got, &prefix);
        check!(format!("names = {names:?}, prefix = {prefix:?}"), got, want);
    }
}

#[test]
fn scale_300k_matches_first() {
    let mut v: Vec<String> = (0..300_000).map(|i| if i < 150_000 { format!("tmp{i}") } else { format!("keep{i}") }).collect();
    remove_prefixed(&mut v, "tmp");
    check!("150000 names \"tmp…\" then 150000 others, prefix \"tmp\"", (v.len(), v[0].as_str() == "keep150000"), (150_000, true));
}
