use solution::*;

#[test]
fn longer_than_word() {
    let wf = WordFilter::new(&["ab"]);
    check!(r#"words = ["ab"], f("abc", ""), f("", "zab")"#, (wf.f("abc", ""), wf.f("", "zab")), (None, None));
}

#[test]
fn duplicate_words() {
    let wf = WordFilter::new(&["x", "y", "x"]);
    check!(r#"words = ["x", "y", "x"], f("x", "x")"#, wf.f("x", "x"), Some(2));
}

#[test]
fn single_letter() {
    let wf = WordFilter::new(&["a"]);
    check!(r#"words = ["a"], f("a", "a")"#, wf.f("a", "a"), Some(0));
}

#[test]
fn earlier_word_only_match() {
    let wf = WordFilter::new(&["pop", "pot", "top"]);
    check!(r#"words = ["pop", "pot", "top"], f("p", "p")"#, wf.f("p", "p"), Some(0));
}

#[test]
fn suffix_not_substring() {
    let wf = WordFilter::new(&["abcab"]);
    check!(r#"words = ["abcab"], f("", "bc")"#, wf.f("", "bc"), None);
}

#[test]
fn whole_word_both_sides() {
    let wf = WordFilter::new(&["level", "lever"]);
    check!(r#"words = ["level", "lever"], f("lev", "el"), f("lever", "lever")"#, (wf.f("lev", "el"), wf.f("lever", "lever")), (Some(0), Some(1)));
}

#[test]
fn seven_letters() {
    let wf = WordFilter::new(&["abcdefg"]);
    check!(r#"words = ["abcdefg"], f("abcdefg", "g"), f("a", "abcdefg")"#, (wf.f("abcdefg", "g"), wf.f("a", "abcdefg")), (Some(0), Some(0)));
}

#[test]
fn z_is_not_the_separator() {
    let wf = WordFilter::new(&["zz", "az"]);
    check!(r#"words = ["zz", "az"], f("z", "z"), f("a", "z")"#, (wf.f("z", "z"), wf.f("a", "z")), (Some(0), Some(1)));
}

        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1011);
            for _ in 0..300 {
                let mut words: Vec<String> = Vec::new();
                for _ in 0..1 + rng.below(6) {
                    let len = 1 + rng.below(4);
                    words.push(rng.string(len, "ab"));
                }
                let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
                let wf = WordFilter::new(&refs);
                for _ in 0..5 {
                    let (pl, sl) = (rng.below(3), rng.below(3));
                    let prefix = rng.string(pl, "ab");
                    let suffix = rng.string(sl, "ab");
                    let want = refs.iter().rposition(|w| w.starts_with(prefix.as_str()) && w.ends_with(suffix.as_str()));
                    check!(format!("words = {refs:?}, f({prefix:?}, {suffix:?})"), wf.f(&prefix, &suffix), want);
                }
            }
        }

        #[test]
        fn scale_10k_words_200k_queries() {
            let words: Vec<String> = (0..10_000).map(|i| base10(i, 4)).collect();
            let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            let wf = WordFilter::new(&refs);
            let mut hits = 0usize;
            let mut sum = 0usize;
            for i in 0..200_000 {
                let w = &words[i % 10_000];
                // Matches only word 0 ("aaaa"), a word with no match, then the word itself by its two halves.
                if let Some(j) = wf.f("a", "aaa") {
                    sum += j;
                    hits += 1;
                }
                hits += wf.f(&w[..1], "k").is_some() as usize;
                sum += wf.f(&w[..2], &w[2..]).unwrap_or(0);
            }
            check!("words = every 4-letter word over a..j; 200000 × (f(\"a\", \"aaa\"), f(_, \"k\"), f(first half, second half))", (hits, sum), (200_000, 20 * (0..10_000usize).sum::<usize>()));
        }

fn base10(mut i: usize, len: usize) -> String {
    let mut w = vec![b'a'; len];
    for k in (0..len).rev() {
        w[k] = b'a' + (i % 10) as u8;
        i /= 10;
    }
    String::from_utf8(w).unwrap()
}
