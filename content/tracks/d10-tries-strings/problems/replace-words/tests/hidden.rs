use solution::*;

#[test]
fn word_equals_root() {
    check!(r#"roots = ["the"], sentence = "the theme""#, replace_words(&["the"], "the theme"), "the the");
}

#[test]
fn duplicate_roots() {
    check!(r#"roots = ["ab", "ab"], sentence = "abc""#, replace_words(&["ab", "ab"], "abc"), "ab");
}

#[test]
fn root_must_be_prefix() {
    check!(r#"roots = ["tle"], sentence = "cattle""#, replace_words(&["tle"], "cattle"), "cattle");
}

#[test]
fn longer_root_listed_first() {
    check!(r#"roots = ["abcd", "abc", "ab"], sentence = "abcde abx a""#, replace_words(&["abcd", "abc", "ab"], "abcde abx a"), "ab ab a");
}

#[test]
fn single_word() {
    check!(r#"roots = ["x"], sentence = "xylophone""#, replace_words(&["x"], "xylophone"), "x");
}

#[test]
fn all_unchanged() {
    check!(r#"roots = ["q"], sentence = "a b c""#, replace_words(&["q"], "a b c"), "a b c");
}

#[test]
fn repeated_words() {
    check!(r#"roots = ["re"], sentence = "redo redo undo""#, replace_words(&["re"], "redo redo undo"), "re re undo");
}

#[test]
fn long_root_chain() {
    let roots: Vec<String> = (1..=100).map(|n| "z".repeat(n)).collect();
    let refs: Vec<&str> = roots.iter().rev().map(|s| s.as_str()).collect();
    check!(r#"roots = ['z' × 1..=100], sentence = 'z' × 200"#, replace_words(&refs, &"z".repeat(200)), "z");
}

        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1006);
            for _ in 0..300 {
                let mut roots: Vec<String> = Vec::new();
                for _ in 0..rng.below(5) {
                    let len = 1 + rng.below(3);
                    roots.push(rng.string(len, "ab"));
                }
                let mut words: Vec<String> = Vec::new();
                for _ in 0..1 + rng.below(5) {
                    let len = 1 + rng.below(4);
                    words.push(rng.string(len, "abc"));
                }
                let sentence = words.join(" ");
                let refs: Vec<&str> = roots.iter().map(|s| s.as_str()).collect();
                let want: Vec<&str> = words
                    .iter()
                    .map(|w| refs.iter().filter(|r| w.starts_with(**r)).min_by_key(|r| r.len()).copied().unwrap_or(w.as_str()))
                    .collect();
                check!(format!("roots = {refs:?}, sentence = {sentence:?}"), replace_words(&refs, &sentence), want.join(" "));
            }
        }

        #[test]
        fn scale_100k_roots_and_words() {
            // Roots: 5-letter words for even i, 3-letter words for i divisible by 7.
            let mut roots: Vec<String> = (0..100_000).step_by(2).map(|i| base10(i, 5)).collect();
            roots.extend((0..1_000).step_by(7).map(|i| base10(i, 3)));
            let refs: Vec<&str> = roots.iter().map(|s| s.as_str()).collect();
            let js: Vec<usize> = (0..100_000).map(|i| i * 997 % 100_000_000).collect();
            let words: Vec<String> = js.iter().map(|&j| base10(j, 8)).collect();
            let sentence = words.join(" ");
            let want: Vec<&str> = js
                .iter()
                .zip(&words)
                .map(|(&j, w)| if (j / 100_000) % 7 == 0 { &w[..3] } else if (j / 1_000) % 2 == 0 { &w[..5] } else { w.as_str() })
                .collect();
            check!("50000 five-letter roots + 143 three-letter roots, a sentence of 100000 eight-letter words", replace_words(&refs, &sentence), want.join(" "));
        }

fn base10(mut i: usize, len: usize) -> String {
    let mut w = vec![b'a'; len];
    for k in (0..len).rev() {
        w[k] = b'a' + (i % 10) as u8;
        i /= 10;
    }
    String::from_utf8(w).unwrap()
}
