use solution::*;

#[test]
fn insert_empty_word() {
    let mut t = Trie::new();
    t.insert("");
    check!(r#"insert ""; search """#, t.search(""), true);
}

#[test]
fn insert_twice() {
    let mut t = Trie::new();
    t.insert("a");
    t.insert("a");
    check!(r#"insert "a" twice; search "a""#, t.search("a"), true);
}

#[test]
fn single_letters() {
    let mut t = Trie::new();
    t.insert("a");
    t.insert("z");
    check!(r#"insert "a", "z"; search a, z, b"#, (t.search("a"), t.search("z"), t.search("b")), (true, true, false));
}

#[test]
fn branching() {
    let mut t = Trie::new();
    for w in ["car", "cat", "cart"] {
        t.insert(w);
    }
    check!(r#"insert "car", "cat", "cart"; search ca, car, cat, cart, carts"#, (t.search("ca"), t.search("car"), t.search("cat"), t.search("cart"), t.search("carts")), (false, true, true, true, false));
}

#[test]
fn shorter_word_after_longer() {
    let mut t = Trie::new();
    t.insert("cart");
    t.insert("car");
    check!(r#"insert "cart", then "car"; search car, starts_with cart"#, (t.search("car"), t.starts_with("cart")), (true, true));
}

#[test]
fn longer_word_keeps_shorter() {
    let mut t = Trie::new();
    t.insert("car");
    t.insert("cart");
    check!(r#"insert "car", then "cart"; search car"#, t.search("car"), true);
}

#[test]
fn different_branch() {
    let mut t = Trie::new();
    t.insert("abc");
    check!(r#"insert "abc"; starts_with "abd", "b""#, (t.starts_with("abd"), t.starts_with("b")), (false, false));
}

#[test]
fn long_word() {
    let mut t = Trie::new();
    let long = "z".repeat(100);
    t.insert(&long);
    check!(r#"insert 'z' × 100; search it and 'z' × 99"#, (t.search(&long), t.search(&long[..99]), t.starts_with(&long[..99])), (true, false, true));
}

#[test]
fn whole_alphabet() {
    let mut t = Trie::new();
    let letters: Vec<String> = (b'a'..=b'z').map(|b| (b as char).to_string()).collect();
    for w in &letters {
        t.insert(w);
    }
    let all = letters.iter().all(|w| t.search(w));
    check!(r#"insert every letter a..z; search each"#, all, true);
}

        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(1002);
            for _ in 0..300 {
                let mut t = Trie::new();
                let mut words: Vec<String> = Vec::new();
                let mut log = Vec::new();
                for _ in 0..rng.below(12) {
                    let len = rng.below(4);
                    let w = rng.string(len, "abc");
                    match rng.below(3) {
                        0 => {
                            t.insert(&w);
                            log.push(format!("insert {w:?}"));
                            words.push(w);
                        }
                        1 => {
                            log.push(format!("search {w:?}"));
                            check!(log.join(", "), t.search(&w), words.contains(&w));
                        }
                        _ => {
                            log.push(format!("starts_with {w:?}"));
                            check!(log.join(", "), t.starts_with(&w), w.is_empty() || words.iter().any(|x| x.starts_with(w.as_str())));
                        }
                    }
                }
            }
        }

        #[test]
        fn scale_100k_words() {
            let mut t = Trie::new();
            for i in 0..100_000 {
                t.insert(&base10(i, 5));
            }
            let mut found = 0;
            for i in 0..100_000 {
                found += t.search(&base10(i, 5)) as usize + t.starts_with(&base10(i, 3)) as usize + t.search(&base10(i, 4)) as usize;
            }
            check!("insert all 100000 five-letter words over a..j; search each, starts_with its first 3 letters, search a 4-letter word", found, 200_000);
        }

fn base10(mut i: usize, len: usize) -> String {
    let mut w = vec![b'a'; len];
    for k in (0..len).rev() {
        w[k] = b'a' + (i % 10) as u8;
        i /= 10;
    }
    String::from_utf8(w).unwrap()
}
