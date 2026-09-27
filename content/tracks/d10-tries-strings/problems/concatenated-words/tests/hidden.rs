use solution::*;

#[test]
fn only_empty() {
    check!(r#"words = [""]"#, find_all_concatenated_words(&[""]), Vec::<&str>::new());
}

#[test]
fn input_order() {
    check!(r#"words = ["abab", "ab", "ababab", "b", "ba"]"#, find_all_concatenated_words(&["abab", "ab", "ababab", "b", "ba"]), vec!["abab", "ababab"]);
}

#[test]
fn three_pieces_needed() {
    check!(r#"words = ["x", "y", "xyx", "yxy", "xyz"]"#, find_all_concatenated_words(&["x", "y", "xyx", "yxy", "xyz"]), vec!["xyx", "yxy"]);
}

#[test]
fn greedy_longest_piece_fails() {
    check!(r#"words = ["ab", "abc", "cd", "abcd"] ("abc" leaves "d"; "ab" + "cd" works)"#, find_all_concatenated_words(&["ab", "abc", "cd", "abcd"]), vec!["abcd"]);
}

#[test]
fn pieces_are_whole_words() {
    check!(r#"words = ["ab", "cd", "abc"]"#, find_all_concatenated_words(&["ab", "cd", "abc"]), Vec::<&str>::new());
}

#[test]
fn longer_word_as_a_piece() {
    check!(r#"words = ["abc", "d", "abcd", "abcdabc"]"#, find_all_concatenated_words(&["abc", "d", "abcd", "abcdabc"]), vec!["abcd", "abcdabc"]);
}

#[test]
fn thirty_letters() {
    let long = "a".repeat(30);
    check!(r#"words = ["a", 'a' × 30]"#, find_all_concatenated_words(&["a", &long]), vec!["a".repeat(30)]);
}

#[test]
fn answers_are_the_input_slices() {
    let w = String::from("xx");
    let got = find_all_concatenated_words(&["x", &w]);
    check!(r#"the answer points into words"#, std::ptr::eq(got[0].as_ptr(), w.as_ptr()), true);
}

        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1022);
            for _ in 0..300 {
                let mut words: Vec<String> = Vec::new();
                for _ in 0..rng.below(7) {
                    let len = rng.below(5);
                    let w = rng.string(len, "ab");
                    if !words.contains(&w) {
                        words.push(w);
                    }
                }
                let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
                // Brute force: ways[i] has bit 1 if w[..i] is one listed word, bit 2 if it splits into two or more.
                let want: Vec<&str> = refs
                    .iter()
                    .copied()
                    .filter(|w| {
                        let n = w.len();
                        let mut ways = vec![0u8; n + 1];
                        for i in 1..=n {
                            for j in 0..i {
                                if refs.contains(&&w[j..i]) {
                                    ways[i] |= if j == 0 { 1 } else if ways[j] != 0 { 2 } else { 0 };
                                }
                            }
                        }
                        n > 0 && ways[n] & 2 != 0
                    })
                    .collect();
                check!(format!("words = {refs:?}"), find_all_concatenated_words(&refs), want);
            }
        }

        #[test]
        fn scale_many_ways_to_fail() {
            // Runs of a's end in a letter no other word ends with, so no split works,
            // but a run of 29 a's splits into pieces of 1–10 a's in ~2²⁸ ways.
            let mut words: Vec<String> = (1..=10).map(|n| "a".repeat(n)).collect();
            for n in 20..=29 {
                words.push(format!("{}{}", "a".repeat(n), (b'b' + (29 - n) as u8) as char));
            }
            words.push("a".repeat(30));
            let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            let mut want: Vec<String> = (2..=10).map(|n| "a".repeat(n)).collect();
            want.push("a".repeat(30));
            check!("words = 'a' × 1..=10, then 'a' × 29 + \"b\", 'a' × 28 + \"c\", …, 'a' × 20 + \"k\", then 'a' × 30", find_all_concatenated_words(&refs), want);
        }

        #[test]
        fn scale_10k_words() {
            // 8000 five-letter words and 2000 ten-letter words, each two of them joined.
            let mut words: Vec<String> = (0..8_000).map(|i| base10(i, 5)).collect();
            for i in 0..2_000 {
                words.push(format!("{}{}", base10(i * 3, 5), base10(i * 7 % 8_000, 5)));
            }
            let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            let got = find_all_concatenated_words(&refs);
            check!("8000 five-letter words and 2000 pairs of them joined", (got.len(), got == refs[8_000..]), (2_000, true));
        }

fn base10(mut i: usize, len: usize) -> String {
    let mut w = vec![b'a'; len];
    for k in (0..len).rev() {
        w[k] = b'a' + (i % 10) as u8;
        i /= 10;
    }
    String::from_utf8(w).unwrap()
}
