use solution::*;

#[test]
fn single_word() {
    check!(r#"words = ["abc"]"#, palindrome_pairs(&["abc"]), Vec::<(usize, usize)>::new());
}

#[test]
fn palindrome_and_empty() {
    check!(r#"words = ["aba", ""]"#, palindrome_pairs(&["aba", ""]), vec![(0, 1), (1, 0)]);
}

#[test]
fn empty_with_non_palindrome() {
    check!(r#"words = ["ab", ""]"#, palindrome_pairs(&["ab", ""]), Vec::<(usize, usize)>::new());
}

#[test]
fn same_letter_words() {
    check!(r#"words = ["a", "aa", "aaa"]"#, palindrome_pairs(&["a", "aa", "aaa"]), vec![(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]);
}

#[test]
fn mixed_with_empty() {
    check!(r#"words = ["x", "xx", ""]"#, palindrome_pairs(&["x", "xx", ""]), vec![(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]);
}

#[test]
fn reverse_pair_once() {
    check!(r#"words = ["ab", "ba", "abab"]"#, palindrome_pairs(&["ab", "ba", "abab"]), vec![(0, 1), (1, 0)]);
}

#[test]
fn only_one_order() {
    check!(r#"words = ["abc", "ba"] ("abcba" works, "baabc" doesn't)"#, palindrome_pairs(&["abc", "ba"]), vec![(0, 1)]);
}

#[test]
fn palindrome_suffix() {
    check!(r#"words = ["cbaa", "abc"] ("cbaa" + "abc" is "cbaaabc")"#, palindrome_pairs(&["cbaa", "abc"]), vec![(0, 1)]);
}

        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1023);
            for _ in 0..300 {
                let mut words: Vec<String> = Vec::new();
                for _ in 0..rng.below(7) {
                    let len = rng.below(4);
                    let w = rng.string(len, "ab");
                    if !words.contains(&w) {
                        words.push(w);
                    }
                }
                let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
                let mut want = Vec::new();
                for i in 0..refs.len() {
                    for j in 0..refs.len() {
                        let s = format!("{}{}", refs[i], refs[j]);
                        if i != j && s.bytes().eq(s.bytes().rev()) {
                            want.push((i, j));
                        }
                    }
                }
                check!(format!("words = {refs:?}"), palindrome_pairs(&refs), want);
            }
        }

        #[test]
        fn scale_20k_words() {
            use std::collections::HashMap;
            let mut words: Vec<String> = (0..20_000).map(|i| base10(i * 499_979, 10)).collect();
            let fifth_reversed: String = words[5].chars().rev().collect();
            words.push(fifth_reversed);
            words.extend(["qrstuvwxyz", "zyxwvutsrq", "klmnoonmlk", ""].map(String::from));
            let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            // Every word has 10 letters except "": pairs are a word with its reverse, or "" with a palindrome.
            let index: HashMap<&str, usize> = refs.iter().enumerate().map(|(i, &w)| (w, i)).collect();
            let empty = index[""];
            let mut want = Vec::new();
            for (i, w) in refs.iter().enumerate() {
                let r: String = w.chars().rev().collect();
                if let Some(&j) = index.get(r.as_str()) {
                    if j != i {
                        want.push((i, j));
                    } else if i != empty {
                        want.push((i, empty));
                        want.push((empty, i));
                    }
                }
            }
            want.sort_unstable();
            check!("20000 ten-letter words over a..j, one's reverse, qrstuvwxyz and its reverse, klmnoonmlk, \"\"", palindrome_pairs(&refs), want);
        }

fn base10(mut i: usize, len: usize) -> String {
    let mut w = vec![b'a'; len];
    for k in (0..len).rev() {
        w[k] = b'a' + (i % 10) as u8;
        i /= 10;
    }
    String::from_utf8(w).unwrap()
}
