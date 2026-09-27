use solution::*;

#[test]
fn one_step() {
    check!(r#"begin = "a", end = "c", words = ["a","b","c"]"#, ladder_length("a", "c", &["a", "b", "c"]), 2);
}

#[test]
fn disconnected() {
    check!(r#"begin = "ab", end = "xy", words = ["xy"]"#, ladder_length("ab", "xy", &["xy"]), 0);
}

#[test]
fn many_words() {
    let words: Vec<String> = (0..5000u32).map(|i| { let b = [b'a' + (i % 26) as u8, b'a' + (i / 26 % 26) as u8, b'a' + (i / 676 % 26) as u8]; String::from_utf8(b.to_vec()).unwrap() }).collect();
    let mut refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
    refs.push("zzz");
    check!(r#"5000 three-letter words"#, ladder_length("aaa", "zzz", &refs), 4);
}

#[test]
fn shorter_of_two_routes() {
    check!(r#"begin = "aaa", end = "ccc", words = ["aab","abb","bbb","bbc","bcc","ccc","aca","acc"]"#, ladder_length("aaa", "ccc", &["aab", "abb", "bbb", "bbc", "bcc", "ccc", "aca", "acc"]), 4);
}

#[test]
fn through_listed_words_only() {
    check!(r#"begin = "hit", end = "cog", words = ["hot","cot","cog"]"#, ladder_length("hit", "cog", &["hot", "cot", "cog"]), 4);
}

#[test]
fn ten_letter_words() {
    check!(r#"begin = "abcdefghij", end = "abcdefghiz", words = ["abcdefghiz"]"#, ladder_length("abcdefghij", "abcdefghiz", &["abcdefghiz"]), 2);
}

#[test]
fn duplicate_words() {
    check!(r#"begin = "ab", end = "cb", words = ["cb","cb","ab"]"#, ladder_length("ab", "cb", &["cb", "cb", "ab"]), 2);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(911);
    for _ in 0..300 {
        let len = 1 + rng.below(3);
        let n = rng.below(12);
        let words: Vec<String> = (0..n).map(|_| rng.string(len, "abc")).collect();
        let begin = rng.string(len, "abc");
        let end = if n > 0 && rng.below(4) > 0 { words[rng.below(n)].clone() } else { rng.string(len, "abc") };
        // Brute force: BFS comparing every pair of words letter by letter.
        let differ_by_one = |a: &str, b: &str| a.bytes().zip(b.bytes()).filter(|(x, y)| x != y).count() == 1;
        let mut dist: Vec<Option<usize>> = vec![None; n];
        let mut queue: Vec<(String, usize)> = vec![(begin.clone(), 1)];
        let mut want = 0;
        let mut i = 0;
        if words.contains(&end) {
            while i < queue.len() {
                let (w, d) = queue[i].clone();
                i += 1;
                if w == end {
                    want = d;
                    break;
                }
                for j in 0..n {
                    if dist[j].is_none() && words[j] != begin && differ_by_one(&w, &words[j]) {
                        dist[j] = Some(d + 1);
                        queue.push((words[j].clone(), d + 1));
                    }
                }
            }
        }
        let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
        check!(format!("begin = {begin:?}, end = {end:?}, words = {words:?}"), ladder_length(&begin, &end, &refs), want);
    }
}

#[test]
fn scale_110k_words() {
    // 10⁴ reachable words ("????a" over a..j) plus 10⁵ filler words over q..z that differ from them in every letter.
    let spell = |mut i: u32, base: u8, len: usize| -> String { (0..len).map(|_| { let c = (base + (i % 10) as u8) as char; i /= 10; c }).collect() };
    let mut words: Vec<String> = (0..10_000).map(|i| spell(i, b'a', 4) + "a").collect();
    words.extend((0..100_000).map(|i| spell(i, b'q', 5)));
    let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
    check!("10000 words ????a over a..j plus 100000 filler words over q..z, begin = \"aaaaa\", end = \"jjjja\"", ladder_length("aaaaa", "jjjja", &refs), 5);
}
