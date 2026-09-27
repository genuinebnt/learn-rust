use solution::*;

#[test]
fn empty_word() {
    let mut t = Trie::new();
    t.insert("");
    t.insert("");
    let (a, b) = (t.count_words_equal_to(""), t.count_words_starting_with(""));
    let c = t.erase("");
    check!(r#"insert "" twice; equal "", starting "", erase "", equal """#, (a, b, c, t.count_words_equal_to("")), (2, 2, true, 1));
}

#[test]
fn erase_longer_missing() {
    let mut t = Trie::new();
    t.insert("ab");
    let erased = t.erase("abc");
    check!(r#"insert ab; erase abc; starting ab"#, (erased, t.count_words_starting_with("ab")), (false, 1));
}

#[test]
fn erase_prefix_of_word_missing() {
    let mut t = Trie::new();
    t.insert("abc");
    let erased = t.erase("ab");
    check!(r#"insert abc; erase ab; equal abc, starting a"#, (erased, t.count_words_equal_to("abc"), t.count_words_starting_with("a")), (false, 1, 1));
}

#[test]
fn reinsert_after_erase() {
    let mut t = Trie::new();
    t.insert("q");
    t.erase("q");
    t.insert("q");
    check!(r#"insert q; erase q; insert q; equal q, starting q"#, (t.count_words_equal_to("q"), t.count_words_starting_with("q")), (1, 1));
}

#[test]
fn erase_shorter_keeps_branch() {
    let mut t = Trie::new();
    t.insert("abc");
    t.insert("abd");
    t.erase("abc");
    check!(r#"insert abc, abd; erase abc; starting ab, equal abd"#, (t.count_words_starting_with("ab"), t.count_words_equal_to("abd")), (1, 1));
}

#[test]
fn erase_on_empty() {
    let mut t = Trie::new();
    check!(r#"new trie; erase "a""#, t.erase("a"), false);
}

#[test]
fn prefix_equals_word() {
    let mut t = Trie::new();
    t.insert("apple");
    check!(r#"insert apple; starting apple, starting apples"#, (t.count_words_starting_with("apple"), t.count_words_starting_with("apples")), (1, 0));
}

#[test]
fn many_copies() {
    let mut t = Trie::new();
    for _ in 0..1000 {
        t.insert("z");
    }
    for _ in 0..999 {
        t.erase("z");
    }
    check!(r#"insert z 1000 times; erase 999; equal z"#, t.count_words_equal_to("z"), 1);
}

        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(1010);
            for _ in 0..300 {
                let mut t = Trie::new();
                let mut words: Vec<String> = Vec::new();
                let mut log = Vec::new();
                for _ in 0..rng.below(16) {
                    let len = rng.below(4);
                    let w = rng.string(len, "ab");
                    match rng.below(4) {
                        0 => {
                            t.insert(&w);
                            log.push(format!("insert {w:?}"));
                            words.push(w);
                        }
                        1 => {
                            log.push(format!("erase {w:?}"));
                            let pos = words.iter().position(|x| *x == w);
                            if let Some(p) = pos {
                                words.swap_remove(p);
                            }
                            check!(log.join(", "), t.erase(&w), pos.is_some());
                        }
                        2 => {
                            log.push(format!("count_words_equal_to {w:?}"));
                            check!(log.join(", "), t.count_words_equal_to(&w), words.iter().filter(|x| **x == w).count());
                        }
                        _ => {
                            log.push(format!("count_words_starting_with {w:?}"));
                            check!(log.join(", "), t.count_words_starting_with(&w), words.iter().filter(|x| x.starts_with(w.as_str())).count());
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
            let mut total = 0;
            for i in (0..100_000).step_by(2) {
                total += t.erase(&base10(i, 5)) as usize;
            }
            for i in 0..100_000 {
                total += t.count_words_starting_with(&base10(i % 1000, 3)) + t.count_words_equal_to(&base10(i, 5));
            }
            check!("insert 100000 five-letter words, erase the even ones, then 100000 × (count starting with a 3-letter prefix + count equal to a word)", total, 50_000 + 5_000_000 + 50_000);
        }

fn base10(mut i: usize, len: usize) -> String {
    let mut w = vec![b'a'; len];
    for k in (0..len).rev() {
        w[k] = b'a' + (i % 10) as u8;
        i /= 10;
    }
    String::from_utf8(w).unwrap()
}
