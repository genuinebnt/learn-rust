use solution::*;

fn feed(sc: &mut StreamChecker, letters: &str) -> Vec<bool> {
    letters.chars().map(|c| sc.query(c)).collect()
}

#[test]
fn no_words() {
    let mut sc = StreamChecker::new(&[]);
    check!(r#"words = []; letters "abc""#, feed(&mut sc, "abc"), vec![false; 3]);
}

#[test]
fn duplicate_words() {
    let mut sc = StreamChecker::new(&["z", "z"]);
    check!(r#"words = ["z", "z"]; letters "zz""#, feed(&mut sc, "zz"), vec![true, true]);
}

#[test]
fn longest_word_needs_the_whole_window() {
    let w = format!("{}b", "a".repeat(199));
    let mut sc = StreamChecker::new(&[&w, "c"]);
    let got = feed(&mut sc, &format!("{}b", "a".repeat(200)));
    check!(r#"words = ['a' × 199 + "b", "c"]; letters 'a' × 200 + "b""#, got[200], true);
}

#[test]
fn long_then_short() {
    let mut sc = StreamChecker::new(&["abcd", "d"]);
    check!(r#"words = ["abcd", "d"]; letters "xd""#, feed(&mut sc, "xd"), vec![false, true]);
}

#[test]
fn broken_by_one_letter() {
    let mut sc = StreamChecker::new(&["abc"]);
    check!(r#"words = ["abc"]; letters "abxbc""#, feed(&mut sc, "abxbc"), vec![false; 5]);
}

#[test]
fn every_letter_a_word() {
    let letters: Vec<String> = (b'a'..=b'z').map(|b| (b as char).to_string()).collect();
    let refs: Vec<&str> = letters.iter().map(|s| s.as_str()).collect();
    let mut sc = StreamChecker::new(&refs);
    check!(r#"words = a..z as one-letter words; letters "qz""#, feed(&mut sc, "qz"), vec![true, true]);
}

#[test]
fn shorter_word_matches_first() {
    let mut sc = StreamChecker::new(&["ba", "a"]);
    check!(r#"words = ["ba", "a"]; letters "ba""#, feed(&mut sc, "ba"), vec![false, true]);
}

#[test]
fn same_letter_word_long() {
    let mut sc = StreamChecker::new(&[&"q".repeat(5)]);
    check!(r#"words = ['q' × 5]; letters 'q' × 7"#, feed(&mut sc, &"q".repeat(7)), vec![false, false, false, false, true, true, true]);
}

        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1021);
            for _ in 0..300 {
                let mut words: Vec<String> = Vec::new();
                for _ in 0..1 + rng.below(4) {
                    let len = 1 + rng.below(4);
                    words.push(rng.string(len, "ab"));
                }
                let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
                let mut sc = StreamChecker::new(&refs);
                let len = rng.below(16);
                let letters = rng.string(len, "abc");
                let mut stream = String::new();
                for c in letters.chars() {
                    stream.push(c);
                    let want = refs.iter().any(|w| stream.ends_with(w));
                    check!(format!("words = {refs:?}; letters {stream:?}"), sc.query(c), want);
                }
            }
        }

        #[test]
        fn scale_20k_words_100k_letters() {
            use std::collections::HashSet;
            let words: Vec<String> = (0..20_000).map(|i| base10(i * 37, 6)).collect();
            let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            let set: HashSet<&str> = refs.iter().copied().collect();
            let mut sc = StreamChecker::new(&refs);
            let mut x: u64 = 7;
            let letters: String = (0..100_000)
                .map(|_| {
                    x = x.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
                    (b'a' + ((x >> 33) % 10) as u8) as char
                })
                .collect();
            let mut got = 0;
            let mut want = 0;
            for (i, c) in letters.char_indices() {
                got += sc.query(c) as usize;
                want += (i >= 5 && set.contains(&letters[i - 5..=i])) as usize;
            }
            check!("20000 six-letter words over a..j; 100000 pseudo-random letters (count of true answers)", got, want);
        }

fn base10(mut i: usize, len: usize) -> String {
    let mut w = vec![b'a'; len];
    for k in (0..len).rev() {
        w[k] = b'a' + (i % 10) as u8;
        i /= 10;
    }
    String::from_utf8(w).unwrap()
}
