use solution::*;

#[test]
fn extra_spaces() {
    check!(r#"s = "  a  bb   ccc ""#, third_word_len("  a  bb   ccc "), Some(3));
}

#[test]
fn empty() {
    check!(r#"s = """#, third_word_len(""), None);
}

#[test]
fn only_spaces() {
    check!(r#"s = "     ""#, third_word_len("     "), None);
}

#[test]
fn two_words_trailing_space() {
    check!(r#"s = "a b ""#, third_word_len("a b "), None);
}

#[test]
fn length_in_bytes() {
    check!(r#"s = "a b héllo""#, third_word_len("a b héllo"), Some(6));
}

#[test]
fn punctuation_is_part_of_a_word() {
    check!(r#"s = "one, two, three!""#, third_word_len("one, two, three!"), Some(6));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1302);
    for _ in 0..400 {
        let len = rng.below(15);
        let s = rng.string(len, "ab é\t\n");
        let words: Vec<&str> = s.split(|c: char| c.is_whitespace()).filter(|w| !w.is_empty()).collect();
        check!(format!("s = {s:?}"), third_word_len(&s), words.get(2).map(|w| w.len()));
    }
}

#[test]
fn long_input() {
    let s = format!("x yy {} {}", "z".repeat(100_000), "w ".repeat(100_000));
    check!("s = \"x yy \" + 100000 × z + 100000 more words", third_word_len(&s), Some(100_000));
}
