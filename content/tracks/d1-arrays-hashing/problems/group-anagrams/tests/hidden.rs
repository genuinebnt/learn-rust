use solution::*;

#[test]
fn no_words() {
    check!(r#"[]"#, group_anagrams(&[]), Vec::<Vec<String>>::new());
}

#[test]
fn duplicates() {
    check!(r#"["ab", "ba", "ab"]"#, group_anagrams(&["ab", "ba", "ab"]), vec![vec!["ab", "ab", "ba"]]);
}

#[test]
fn single_word() {
    check!(r#"["abc"]"#, group_anagrams(&["abc"]), vec![vec!["abc"]]);
}

#[test]
fn no_anagrams() {
    check!(r#"["b", "a", "c"]"#, group_anagrams(&["b", "a", "c"]), vec![vec!["a"], vec!["b"], vec!["c"]]);
}

#[test]
fn repeat_counts_matter() {
    check!(r#"["a", "aa", "aab", "abb"]"#, group_anagrams(&["a", "aa", "aab", "abb"]), vec![vec!["a"], vec!["aa"], vec!["aab"], vec!["abb"]]);
}

#[test]
fn all_one_group() {
    check!(r#"["cab", "bca", "abc"]"#, group_anagrams(&["cab", "bca", "abc"]), vec![vec!["abc", "bca", "cab"]]);
}

#[test]
fn empty_strings_together() {
    check!(r#"["", "a", ""]"#, group_anagrams(&["", "a", ""]), vec![vec!["", ""], vec!["a"]]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(11);
    for _ in 0..200 {
        let n = rng.below(8);
        let owned: Vec<String> = (0..n).map(|_| { let len = rng.below(4); rng.string(len, "abc") }).collect();
        let words: Vec<&str> = owned.iter().map(String::as_str).collect();
        let key = |w: &str| { let mut c: Vec<char> = w.chars().collect(); c.sort(); c };
        let mut want: Vec<Vec<String>> = Vec::new();
        for w in &words {
            match want.iter_mut().find(|g| key(&g[0]) == key(w)) {
                Some(g) => g.push(w.to_string()),
                None => want.push(vec![w.to_string()]),
            }
        }
        for g in &mut want {
            g.sort();
        }
        want.sort();
        check!(format!("{words:?}"), group_anagrams(&words), want);
    }
}

#[test]
fn scale_54264_classes() {
    // Every non-decreasing 6-letter word over a..p, plus its reverse: 54264 classes, 108528 words.
    let mut owned = Vec::new();
    for a in 0..16u8 { for b in a..16 { for c in b..16 { for d in c..16 { for e in d..16 { for f in e..16 {
        let w: String = [a, b, c, d, e, f].iter().map(|&x| (b'a' + x) as char).collect();
        owned.push(w.chars().rev().collect::<String>());
        owned.push(w);
    } } } } } }
    let words: Vec<&str> = owned.iter().map(String::as_str).collect();
    let groups = group_anagrams(&words);
    check!("108528 words in 54264 anagram classes", (groups.len(), groups[0].clone()), (54_264, vec!["aaaaaa".to_string(), "aaaaaa".to_string()]));
}
