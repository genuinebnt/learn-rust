use solution::*;

#[test]
fn duplicates_needed() {
    check!(r#"s = "aaflslflsldkalskaaa", t = "aaa""#, min_window("aaflslflsldkalskaaa", "aaa"), "aaa");
}

#[test]
fn leftmost_tie() {
    check!(r#"s = "abcab", t = "ab""#, min_window("abcab", "ab"), "ab");
}

#[test]
fn empty_s() {
    check!(r#"s = "", t = "a""#, min_window("", "a"), "");
}

#[test]
fn t_longer() {
    check!(r#"s = "ab", t = "abc""#, min_window("ab", "abc"), "");
}

#[test]
fn case_sensitive() {
    check!(r#"s = "aA", t = "A""#, min_window("aA", "A"), "A");
}

#[test]
fn whole_string() {
    check!(r#"s = "cab", t = "bac""#, min_window("cab", "bac"), "cab");
}

#[test]
fn window_at_end() {
    check!(r#"s = "xxxxab", t = "ba""#, min_window("xxxxab", "ba"), "ab");
}

#[test]
fn shrinks_past_surplus() {
    check!(r#"s = "aab", t = "ab""#, min_window("aab", "ab"), "ab");
}

#[test]
fn symbols_and_spaces() {
    check!(r#"s = "x !y! z", t = "! ""#, min_window("x !y! z", "! "), " !");
}

#[test]
fn returns_a_slice_of_s() {
    let s = String::from("ADOBECODEBANC");
    let got = min_window(&s, "ABC");
    check!("s = \"ADOBECODEBANC\", t = \"ABC\" (the result points into s)", (got, got.as_ptr() as usize - s.as_ptr() as usize), ("BANC", 9));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(216);
    for _ in 0..300 {
        let n = rng.below(12);
        let tn = 1 + rng.below(4);
        let s = rng.string(n, "abc");
        let t = rng.string(tn, "abc");
        let count = |w: &str, c: char| w.chars().filter(|&x| x == c).count();
        let covers = |w: &str| t.chars().all(|c| count(w, c) >= count(&t, c));
        let mut want = "";
        'outer: for len in 1..=n {
            for i in 0..=n - len {
                if covers(&s[i..i + len]) {
                    want = &s[i..i + len];
                    break 'outer;
                }
            }
        }
        check!(format!("s = {s:?}, t = {t:?}"), min_window(&s, &t).to_string(), want.to_string());
    }
}

#[test]
fn scale_200k() {
    let s = "a".to_string() + &"x".repeat(199_998) + "b";
    let got = min_window(&s, "ab");
    check!("s = \"a\" + \"x\" × 199998 + \"b\", t = \"ab\"", got.len(), 200_000);
}
