use solution::*;

#[test]
fn all_dots() {
    let mut d = WordDictionary::new();
    d.add_word("hello");
    check!(r#"add "hello"; search ".....""#, d.search("....."), true);
}

#[test]
fn dot_at_end() {
    let mut d = WordDictionary::new();
    d.add_word("cat");
    d.add_word("car");
    check!(r#"add "cat", "car"; search "ca.", "c.t", "c.x""#, (d.search("ca."), d.search("c.t"), d.search("c.x")), (true, true, false));
}

#[test]
fn longer_than_word() {
    let mut d = WordDictionary::new();
    d.add_word("a");
    check!(r#"add "a"; search "a.""#, d.search("a."), false);
}

#[test]
fn shorter_word_added_later() {
    let mut d = WordDictionary::new();
    d.add_word("abc");
    d.add_word("ab");
    check!(r#"add "abc", then "ab"; search "a.""#, d.search("a."), true);
}

#[test]
fn backtrack_after_dead_end() {
    let mut d = WordDictionary::new();
    d.add_word("aab");
    d.add_word("abc");
    check!(r#"add "aab", "abc"; search "a.c""#, d.search("a.c"), true);
}

#[test]
fn last_child_matches() {
    let mut d = WordDictionary::new();
    for w in ["az", "bz", "zy"] {
        d.add_word(w);
    }
    check!(r#"add "az", "bz", "zy"; search ".y""#, d.search(".y"), true);
}

#[test]
fn no_dot_exact_miss() {
    let mut d = WordDictionary::new();
    d.add_word("abc");
    check!(r#"add "abc"; search "abd""#, d.search("abd"), false);
}

#[test]
fn twenty_five_letters() {
    let mut d = WordDictionary::new();
    d.add_word(&"y".repeat(25));
    check!(r#"add 'y' × 25; search 'y' × 24 + ".""#, d.search(&format!("{}.", "y".repeat(24))), true);
}

        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(1008);
            for _ in 0..300 {
                let mut d = WordDictionary::new();
                let mut words: Vec<String> = Vec::new();
                let mut log = Vec::new();
                for _ in 0..rng.below(12) {
                    let len = 1 + rng.below(3);
                    if rng.bool() {
                        let w = rng.string(len, "abc");
                        d.add_word(&w);
                        log.push(format!("add {w:?}"));
                        words.push(w);
                    } else {
                        let p = rng.string(len, "ab.");
                        let want = words.iter().any(|w| w.len() == p.len() && w.bytes().zip(p.bytes()).all(|(a, b)| b == b'.' || a == b));
                        log.push(format!("search {p:?}"));
                        check!(log.join(", "), d.search(&p), want);
                    }
                }
            }
        }

        #[test]
        fn scale_100k_words() {
            let mut d = WordDictionary::new();
            for i in 0..100_000 {
                d.add_word(&base10(i, 5));
            }
            let mut hits = 0;
            for i in 0..100_000 {
                let w = base10(i, 5);
                hits += d.search(&w) as usize + d.search(&format!("{}.", &w[..4])) as usize + d.search(&format!("{}k", &w[..4])) as usize;
            }
            for _ in 0..100 {
                hits += d.search("....k") as usize;
            }
            check!("add 100000 five-letter words over a..j; search each, each with a final '.', each with a final 'k'; then \"....k\" 100 times", hits, 200_000);
        }

fn base10(mut i: usize, len: usize) -> String {
    let mut w = vec![b'a'; len];
    for k in (0..len).rev() {
        w[k] = b'a' + (i % 10) as u8;
        i /= 10;
    }
    String::from_utf8(w).unwrap()
}
