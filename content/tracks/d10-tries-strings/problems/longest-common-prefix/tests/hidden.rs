use solution::*;

#[test]
fn single_empty() {
    check!(r#"strs = [""]"#, longest_common_prefix(&[""]), "");
}

#[test]
fn identical() {
    check!(r#"strs = ["same", "same", "same"]"#, longest_common_prefix(&["same", "same", "same"]), "same");
}

#[test]
fn accents_share_a_byte() {
    check!(r#"strs = ["café", "cafè"] (é and è share their first byte)"#, longest_common_prefix(&["café", "cafè"]), "caf");
}

#[test]
fn emoji() {
    check!(r#"strs = ["🦀rust", "🦀rest"]"#, longest_common_prefix(&["🦀rust", "🦀rest"]), "🦀r");
}

#[test]
fn shortest_in_the_middle() {
    check!(r#"strs = ["ab", "a", "ab"]"#, longest_common_prefix(&["ab", "a", "ab"]), "a");
}

#[test]
fn case_matters() {
    check!(r#"strs = ["Ab", "ab"]"#, longest_common_prefix(&["Ab", "ab"]), "");
}

#[test]
fn differs_only_in_last_string() {
    check!(r#"strs = ["prefix", "prefix", "prelude"]"#, longest_common_prefix(&["prefix", "prefix", "prelude"]), "pre");
}

#[test]
fn first_is_longest() {
    check!(r#"strs = ["interview", "inter", "internet"]"#, longest_common_prefix(&["interview", "inter", "internet"]), "inter");
}

#[test]
fn spaces_count() {
    check!(r#"strs = ["a b", "a c"]"#, longest_common_prefix(&["a b", "a c"]), "a ");
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1001);
    for _ in 0..300 {
        let n = rng.below(5);
        let mut strs: Vec<String> = Vec::new();
        for _ in 0..n {
            let len = rng.below(6);
            strs.push(rng.string(len, "abé"));
        }
        let refs: Vec<&str> = strs.iter().map(|s| s.as_str()).collect();
        let chars: Vec<Vec<char>> = strs.iter().map(|s| s.chars().collect()).collect();
        let mut k = 0;
        while n > 0 && chars.iter().all(|c| k < c.len() && c[k] == chars[0][k]) {
            k += 1;
        }
        let want: String = if n == 0 { String::new() } else { chars[0][..k].iter().collect() };
        check!(format!("strs = {refs:?}"), longest_common_prefix(&refs).to_string(), want);
    }
}

#[test]
fn scale_100k_strings() {
    let strs: Vec<String> = (0..100_000).map(|i| format!("common-prefix-{i:06}")).collect();
    let refs: Vec<&str> = strs.iter().map(|s| s.as_str()).collect();
    check!("strs = [\"common-prefix-000000\", …, \"common-prefix-099999\"]", longest_common_prefix(&refs), "common-prefix-0");
}
