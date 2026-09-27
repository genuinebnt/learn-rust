use solution::*;

#[test]
fn single() {
    check!(r#"words = ["z"]"#, longest_word(&["z"]), "z");
}

#[test]
fn duplicates() {
    check!(r#"words = ["a", "a", "ab", "ab"]"#, longest_word(&["a", "a", "ab", "ab"]), "ab");
}

#[test]
fn gap_in_the_chain() {
    check!(r#"words = ["a", "ab", "abcd"]"#, longest_word(&["a", "ab", "abcd"]), "ab");
}

#[test]
fn longer_beats_smaller() {
    check!(r#"words = ["a", "b", "ba", "bac"]"#, longest_word(&["a", "b", "ba", "bac"]), "bac");
}

#[test]
fn tie_on_long_words() {
    check!(r#"words = ["y", "yz", "x", "xy"]"#, longest_word(&["y", "yz", "x", "xy"]), "xy");
}

#[test]
fn input_order_irrelevant() {
    check!(r#"words = ["world", "worl", "wor", "wo", "w"]"#, longest_word(&["world", "worl", "wor", "wo", "w"]), "world");
}

#[test]
fn unbuildable_longer() {
    check!(r#"words = ["k", "ki", "kiwi", "kiw", "kiwis", "bananas"]"#, longest_word(&["k", "ki", "kiwi", "kiw", "kiwis", "bananas"]), "kiwis");
}

#[test]
fn thirty_letters() {
    let words: Vec<String> = (1..=30).map(|n| "z".repeat(n)).collect();
    let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
    check!(r#"words = every prefix of 'z' × 30"#, longest_word(&refs), "z".repeat(30));
}

        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1004);
            for _ in 0..300 {
                let n = rng.below(10);
                let mut words: Vec<String> = Vec::new();
                for _ in 0..n {
                    let len = 1 + rng.below(4);
                    words.push(rng.string(len, "abc"));
                }
                let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
                let mut want = "";
                for &w in &refs {
                    let buildable = (1..=w.len()).all(|k| refs.contains(&&w[..k]));
                    if buildable && (w.len() > want.len() || (w.len() == want.len() && w < want)) {
                        want = w;
                    }
                }
                check!(format!("words = {refs:?}"), longest_word(&refs), want);
            }
        }

        #[test]
        fn scale_111k_words() {
            // Every word of 1 to 5 letters over a..j except "aaaa", so nothing under "aaaa" can be built.
            let mut words: Vec<String> = Vec::new();
            for len in 1..=5 {
                let count = 10usize.pow(len as u32);
                for i in 0..count {
                    let w = base10(i, len);
                    if w != "aaaa" {
                        words.push(w);
                    }
                }
            }
            let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            check!("words = every 1–5 letter word over a..j except \"aaaa\" (111109 words)", longest_word(&refs), "aaaba");
        }

fn base10(mut i: usize, len: usize) -> String {
    let mut w = vec![b'a'; len];
    for k in (0..len).rev() {
        w[k] = b'a' + (i % 10) as u8;
        i /= 10;
    }
    String::from_utf8(w).unwrap()
}
