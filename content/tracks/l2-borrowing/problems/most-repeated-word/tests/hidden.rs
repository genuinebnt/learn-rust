use solution::*;

#[test]
fn only_spaces() {
    check!(r#""   ""#, most_repeated("   "), None);
}

#[test]
fn tabs_and_newlines() {
    check!(r#""a\tb\nb  a\n\nb""#, most_repeated("a\tb\nb  a\n\nb"), Some("b"));
}

#[test]
fn unicode() {
    check!(r#""café naïve café""#, most_repeated("café naïve café"), Some("café"));
}

#[test]
fn punctuation_kept() {
    check!(r#""hi, hi hi,""#, most_repeated("hi, hi hi,"), Some("hi,"));
}

#[test]
fn three_way_tie() {
    check!(r#""c b a""#, most_repeated("c b a"), Some("a"));
}

#[test]
fn borrows_the_input() {
    check!(r#""x y x""#, { let t = String::from("x y x"); let w = most_repeated(&t).unwrap(); t.as_bytes().as_ptr_range().contains(&w.as_ptr()) }, true);
}

#[test]
fn leading_trailing_space() {
    check!(r#""  z z y  ""#, most_repeated("  z z y  "), Some("z"));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2004);
    for _ in 0..300 {
        let len = rng.below(16);
        let text = rng.string(len, "ab c");
        let words: Vec<&str> = text.split_whitespace().collect();
        let mut want: Option<(usize, &str)> = None;
        for &w in &words {
            let c = words.iter().filter(|&&x| x == w).count();
            if want.map_or(true, |(bc, bw)| c > bc || (c == bc && w < bw)) {
                want = Some((c, w));
            }
        }
        check!(format!("text = {text:?}"), most_repeated(&text), want.map(|(_, w)| w));
    }
}

#[test]
fn scale_200k_words() {
    let mut text = String::new();
    for i in 0..200_000 {
        text.push_str(&format!("w{} ", i % 100_000));
    }
    text.push_str("w77777");
    check!("200000 words, 100000 distinct, then w77777 once more", most_repeated(&text), Some("w77777"));
}
