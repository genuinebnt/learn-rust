use solution::*;

#[test]
fn cycle() {
    check!(r#"words = ["z", "x", "z"]"#, alien_order(&["z", "x", "z"]), None);
}

#[test]
fn unconstrained_letters() {
    check!(r#"words = ["ba", "bc"]"#, alien_order(&["ba", "bc"]), Some("abc".to_string()));
}

#[test]
fn single_word() {
    check!(r#"words = ["zy"]"#, alien_order(&["zy"]), Some("yz".to_string()));
}

#[test]
fn duplicate_words() {
    check!(r#"words = ["abc", "abc"]"#, alien_order(&["abc", "abc"]), Some("abc".to_string()));
}

#[test]
fn prefix_first_is_fine() {
    check!(r#"words = ["ab", "abc"]"#, alien_order(&["ab", "abc"]), Some("abc".to_string()));
}

#[test]
fn reverse_alphabet() {
    check!(r#"words = ["z", "y", "x"]"#, alien_order(&["z", "y", "x"]), Some("zyx".to_string()));
}

#[test]
fn prefix_later_in_the_list() {
    check!(r#"words = ["a", "bcd", "bc"]"#, alien_order(&["a", "bcd", "bc"]), None);
}

#[test]
fn two_letter_cycle() {
    check!(r#"words = ["ab", "ba", "aa"]"#, alien_order(&["ab", "ba", "aa"]), None);
}

#[test]
fn only_first_difference_counts() {
    check!(r#"words = ["ca", "db", "da"]"#, alien_order(&["ca", "db", "da"]), Some("bacd".to_string()));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(915);
    for _ in 0..400 {
        let n = 1 + rng.below(6);
        let mut words: Vec<String> = (0..n).map(|_| { let len = 1 + rng.below(3); rng.string(len, "abcd") }).collect();
        if rng.bool() {
            // Sort by a random alphabet so an answer exists.
            let mut rank: Vec<u8> = (0..4).collect();
            rng.shuffle(&mut rank);
            words.sort_by_key(|w| w.bytes().map(|b| rank[(b - b'a') as usize]).collect::<Vec<u8>>());
        }
        // Brute force: constraints from every pair of words, not just neighbours.
        let mut present = [false; 26];
        let mut before = [[false; 26]; 26];
        let mut valid = true;
        for i in 0..n {
            for b in words[i].bytes() {
                present[(b - b'a') as usize] = true;
            }
            for j in i + 1..n {
                let (a, b) = (words[i].as_bytes(), words[j].as_bytes());
                match a.iter().zip(b).find(|(x, y)| x != y) {
                    Some((&x, &y)) => before[(x - b'a') as usize][(y - b'a') as usize] = true,
                    None if a.len() > b.len() => valid = false,
                    None => {}
                }
            }
        }
        let mut out = String::new();
        let mut done = [false; 26];
        while valid {
            let next = (0..26).find(|&c| present[c] && !done[c] && (0..26).all(|p| !before[p][c] || done[p]));
            match next {
                Some(c) => {
                    done[c] = true;
                    out.push((b'a' + c as u8) as char);
                }
                None => break,
            }
        }
        let want = (valid && out.len() == present.iter().filter(|&&p| p).count()).then_some(out);
        let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
        check!(format!("words = {words:?}"), alien_order(&refs), want);
    }
}

#[test]
fn scale_200k_words() {
    // Four-letter words counting up in an alphabet that runs z, y, x, …, a.
    let words: Vec<String> = (0..200_000u32).map(|i| (0..4).rev().map(|k| (b'z' - (i / 26u32.pow(k) % 26) as u8) as char).collect()).collect();
    let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
    check!("200000 words zzzz, zzzy, …, sorted by a reversed alphabet", alien_order(&refs), Some("zyxwvutsrqponmlkjihgfedcba".to_string()));
}
