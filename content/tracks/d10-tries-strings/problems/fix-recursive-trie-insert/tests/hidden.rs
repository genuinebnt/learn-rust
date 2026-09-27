use solution::*;

#[test]
fn empty_word() {
    let mut t = Trie::new();
    t.insert("");
    check!(r#"insert ""; contains """#, t.contains(""), true);
}

#[test]
fn siblings() {
    let mut t = Trie::new();
    for w in ["cat", "car", "cab"] {
        t.insert(w);
    }
    check!(r#"insert "cat", "car", "cab"; contains each"#, (t.contains("cat"), t.contains("car"), t.contains("cab")), (true, true, true));
}

#[test]
fn insert_twice() {
    let mut t = Trie::new();
    t.insert("z");
    t.insert("z");
    check!(r#"insert "z" twice; contains "z""#, t.contains("z"), true);
}

#[test]
fn longer_not_found() {
    let mut t = Trie::new();
    t.insert("ab");
    check!(r#"insert "ab"; contains "abc""#, t.contains("abc"), false);
}

#[test]
fn other_branch() {
    let mut t = Trie::new();
    t.insert("ab");
    check!(r#"insert "ab"; contains "b""#, t.contains("b"), false);
}

#[test]
fn deep_word() {
    let mut t = Trie::new();
    let long = "q".repeat(1000);
    t.insert(&long);
    check!(r#"insert 'q' × 1000; contains it and 'q' × 999"#, (t.contains(&long), t.contains(&long[..999])), (true, false));
}

#[test]
fn chain_of_prefixes() {
    let mut t = Trie::new();
    let ws = ["a", "ab", "abc", "abcd"];
    for w in ws {
        t.insert(w);
    }
    let all = ws.iter().all(|w| t.contains(w));
    check!(r#"insert a, ab, abc, abcd; contains each"#, all, true);
}

#[test]
fn first_word_survives_many() {
    let mut t = Trie::new();
    t.insert("apple");
    for b in b'b'..=b'z' {
        t.insert(&format!("a{}", b as char));
    }
    check!(r#"insert "apple" then 25 other words starting with 'a'; contains "apple""#, t.contains("apple"), true);
}

        #[test]
        fn random_vs_model() {
            use std::collections::HashSet;
            let mut rng = anneal_prelude::Rng::new(1007);
            for _ in 0..300 {
                let mut t = Trie::new();
                let mut model: HashSet<String> = HashSet::new();
                let mut log = Vec::new();
                for _ in 0..rng.below(12) {
                    let len = rng.below(4);
                    let w = rng.string(len, "abc");
                    if rng.bool() {
                        t.insert(&w);
                        log.push(format!("insert {w:?}"));
                        model.insert(w);
                    } else {
                        log.push(format!("contains {w:?}"));
                        check!(log.join(", "), t.contains(&w), model.contains(&w));
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
            let found = (0..100_000).filter(|&i| t.contains(&base10(i, 5))).count();
            check!("insert 100000 five-letter words over a..j, then look each one up", found, 100_000);
        }

fn base10(mut i: usize, len: usize) -> String {
    let mut w = vec![b'a'; len];
    for k in (0..len).rev() {
        w[k] = b'a' + (i % 10) as u8;
        i /= 10;
    }
    String::from_utf8(w).unwrap()
}
