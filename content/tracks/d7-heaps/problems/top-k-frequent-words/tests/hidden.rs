use solution::*;

#[test]
fn uppercase_sorts_first() {
    check!(r#"words = ["b", "B", "a"], k = 3"#, top_k_frequent(&["b", "B", "a"], 3), vec!["B", "a", "b"]);
}

#[test]
fn accent_after_z() {
    check!(r#"words = ["é", "z"], k = 2"#, top_k_frequent(&["é", "z"], 2), vec!["z", "é"]);
}

#[test]
fn prefixes_first() {
    check!(r#"words = ["abc", "a", "ab"], k = 3"#, top_k_frequent(&["abc", "a", "ab"], 3), vec!["a", "ab", "abc"]);
}

#[test]
fn count_beats_alphabet() {
    check!(r#"words = ["z", "a", "z"], k = 1"#, top_k_frequent(&["z", "a", "z"], 1), vec!["z"]);
}

#[test]
fn tie_at_the_cut() {
    check!(r#"words = ["d", "c", "b", "a", "e", "e"], k = 3"#, top_k_frequent(&["d", "c", "b", "a", "e", "e"], 3), vec!["e", "a", "b"]);
}

#[test]
fn empty_word() {
    check!(r#"words = ["", "a", ""], k = 2"#, top_k_frequent(&["", "a", ""], 2), vec!["", "a"]);
}

#[test]
fn one_word_many_times() {
    check!(r#"words = ["same"; 1000], k = 1"#, top_k_frequent(&vec!["same"; 1000], 1), vec!["same"]);
}

#[test]
fn returns_slices_of_the_input() {
    let s = String::from("borrowed");
    check!(r#"words = [s, s] where s is a String, k = 1"#, top_k_frequent(&[s.as_str(), s.as_str()], 1)[0].as_ptr() == s.as_ptr(), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(713);
    let pool = ["a", "b", "ab", "B", "é", "ba", ""];
    for _ in 0..300 {
        let n = rng.below(12);
        let words: Vec<&str> = (0..n).map(|_| *rng.pick(&pool)).collect();
        let k = rng.below(8);
        let mut distinct = words.clone();
        distinct.sort_unstable();
        distinct.dedup();
        let count = |w: &str| words.iter().filter(|&&x| x == w).count();
        distinct.sort_by(|a, b| count(b).cmp(&count(a)).then(a.cmp(b)));
        distinct.truncate(k);
        check!(format!("words = {words:?}, k = {k}"), top_k_frequent(&words, k), distinct);
    }
}

#[test]
fn scale_100k_distinct_words() {
    let names: Vec<String> = (0..100_000).map(|i| format!("w{:05}", (i * 7919) % 100_000)).collect();
    let mut words: Vec<&str> = Vec::new();
    for (i, w) in names.iter().enumerate() {
        for _ in 0..(i % 4) + 1 {
            words.push(w);
        }
    }
    let mut want: Vec<(usize, &str)> = names.iter().enumerate().map(|(i, w)| ((i % 4) + 1, w.as_str())).collect();
    want.sort_unstable_by(|a, b| b.0.cmp(&a.0).then(a.1.cmp(b.1)));
    let want: Vec<&str> = want.into_iter().take(50_000).map(|(_, w)| w).collect();
    check!("100000 different words appearing 1–4 times (250000 words), k = 50000", top_k_frequent(&words, 50_000) == want, true);
}
