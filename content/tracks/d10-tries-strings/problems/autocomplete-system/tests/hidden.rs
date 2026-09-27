use solution::*;

fn typed(sys: &mut AutocompleteSystem, keys: &str) -> Vec<Vec<String>> {
    keys.chars().map(|c| sys.input(c)).collect()
}

#[test]
fn no_sentences() {
    let mut sys = AutocompleteSystem::new(&[], &[]);
    check!(r#"sentences = []; type "ab#a""#, typed(&mut sys, "ab#a"), vec![vec![], vec![], vec![], vec!["ab"]]);
}

#[test]
fn hash_first() {
    let mut sys = AutocompleteSystem::new(&["i love you", "island", "iroman", "i love leetcode"], &[5, 3, 2, 2]);
    check!(r##"LeetCode's system; type "#i""##, typed(&mut sys, "#i"), vec![vec![], vec!["i love you", "island", "i love leetcode"]]);
}

#[test]
fn miss_then_hash_stores_everything_typed() {
    let mut sys = AutocompleteSystem::new(&["i love you", "island", "iroman", "i love leetcode"], &[5, 3, 2, 2]);
    typed(&mut sys, "iz#");
    check!(r#"LeetCode's system; type "iz#", then "iz""#, typed(&mut sys, "iz"), vec![vec!["i love you", "island", "i love leetcode"], vec!["iz"]]);
}

#[test]
fn overtakes_the_leader() {
    let mut sys = AutocompleteSystem::new(&["i love you", "island", "iroman", "i love leetcode"], &[5, 3, 2, 2]);
    for _ in 0..3 {
        typed(&mut sys, "island#");
    }
    check!(r#"LeetCode's system; type "island#" three times, then "i""#, typed(&mut sys, "i"), vec![vec!["island", "i love you", "i love leetcode"]]);
}

#[test]
fn counts_past_u32() {
    let mut sys = AutocompleteSystem::new(&["ab", "aa"], &[u32::MAX, u32::MAX]);
    typed(&mut sys, "ab#");
    check!(r#"sentences = ["ab", "aa"], times = [u32::MAX, u32::MAX]; type "ab#", then "a""#, typed(&mut sys, "a"), vec![vec!["ab", "aa"]]);
}

#[test]
fn sentence_is_prefix_of_another() {
    let mut sys = AutocompleteSystem::new(&["i", "i love you"], &[1, 1]);
    check!(r#"sentences = ["i", "i love you"], times = [1, 1]; type "i ""#, typed(&mut sys, "i "), vec![vec!["i", "i love you"], vec!["i love you"]]);
}

#[test]
fn only_three() {
    let mut sys = AutocompleteSystem::new(&["xd", "xc", "xb", "xa"], &[1, 1, 1, 1]);
    check!(r#"sentences = ["d", "c", "b", "a"], each with 1 prefixed "x"; type "x""#, typed(&mut sys, "x"), vec![vec!["xa", "xb", "xc"]]);
}

#[test]
fn stored_sentences_are_suggested() {
    let mut sys = AutocompleteSystem::new(&["b"], &[1]);
    typed(&mut sys, "a#a#");
    check!(r#"sentences = ["b"], times = [1]; type "a#" twice, then "b#a""#, typed(&mut sys, "b#a"), vec![vec!["b"], vec![], vec!["a"]]);
}

#[test]
fn same_sentence_listed_twice() {
    let mut sys = AutocompleteSystem::new(&["ab", "ac", "ab"], &[1, 3, 3]);
    check!(r#"sentences = ["ab", "ac", "ab"], times = [1, 3, 3]; type "a" ("ab" totals 4)"#, typed(&mut sys, "a"), vec![vec!["ab", "ac"]]);
}

        #[test]
        fn random_vs_model() {
            use std::collections::HashMap;
            let mut rng = anneal_prelude::Rng::new(1019);
            for _ in 0..200 {
                let mut initial: Vec<String> = Vec::new();
                let mut times: Vec<u32> = Vec::new();
                for _ in 0..rng.below(6) {
                    let len = 1 + rng.below(3);
                    let s = rng.string(len, "ab ");
                    if !initial.contains(&s) {
                        initial.push(s);
                        times.push(1 + rng.below(3) as u32);
                    }
                }
                let refs: Vec<&str> = initial.iter().map(|s| s.as_str()).collect();
                let mut sys = AutocompleteSystem::new(&refs, &times);
                let mut model: HashMap<String, u64> = initial.iter().cloned().zip(times.iter().map(|&t| u64::from(t))).collect();
                let mut typed_so_far = String::new();
                let mut log = format!("sentences = {refs:?}, times = {times:?}; type ");
                for _ in 0..20 {
                    let c = *rng.pick(&['a', 'b', ' ', '#', '#']);
                    log.push(c);
                    let want: Vec<String> = if c == '#' {
                        *model.entry(std::mem::take(&mut typed_so_far)).or_insert(0) += 1;
                        Vec::new()
                    } else {
                        typed_so_far.push(c);
                        let mut m: Vec<(&String, u64)> = model.iter().filter(|(s, _)| s.starts_with(typed_so_far.as_str())).map(|(s, &n)| (s, n)).collect();
                        m.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(b.0)));
                        m.into_iter().take(3).map(|(s, _)| s.clone()).collect()
                    };
                    check!(log.clone(), sys.input(c), want);
                }
            }
        }

        #[test]
        fn scale_20k_sentences_shared_prefix() {
            // Every sentence starts with 60 a's, so every keystroke of the prefix matches all 20000 of them.
            let prefix = "a".repeat(60);
            let sentences: Vec<String> = (0..20_000).map(|i| format!("{prefix} {}", base10(i, 5))).collect();
            let times: Vec<u32> = (0..20_000u32).map(|i| i * 7919 % 20_000 + 1).collect();
            let refs: Vec<&str> = sentences.iter().map(|s| s.as_str()).collect();
            let mut sys = AutocompleteSystem::new(&refs, &times);
            let mut by_heat: Vec<usize> = (0..20_000).collect();
            by_heat.sort_by_key(|&i| std::cmp::Reverse(times[i]));
            let want: Vec<String> = by_heat[..3].iter().map(|&i| sentences[i].clone()).collect();
            let mut rows = 0;
            let mut all_match = true;
            for _ in 0..160 {
                for c in prefix.chars() {
                    rows += 1;
                    all_match &= sys.input(c) == want;
                }
                sys.input('#');
            }
            check!("20000 sentences 'a' × 60 + ' ' + five letters, distinct counts; type 'a' × 60 then '#', 160 times", (rows, all_match), (9600, true));
        }

fn base10(mut i: usize, len: usize) -> String {
    let mut w = vec![b'a'; len];
    for k in (0..len).rev() {
        w[k] = b'a' + (i % 10) as u8;
        i /= 10;
    }
    String::from_utf8(w).unwrap()
}
