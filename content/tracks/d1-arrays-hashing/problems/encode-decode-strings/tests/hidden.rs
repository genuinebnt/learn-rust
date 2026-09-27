use solution::*;

#[test]
fn no_words() {
    check!(r#"[]"#, decode(&encode(&[])), Vec::<String>::new());
}

#[test]
fn unicode() {
    check!(r#"["héllo", "🦀#rust"]"#, decode(&encode(&["héllo", "🦀#rust"])), vec!["héllo", "🦀#rust"]);
}

#[test]
fn one_empty_string() {
    check!(r#"[""]"#, decode(&encode(&[""])), vec![""]);
}

#[test]
fn digits_only() {
    check!(r#"["123", "4", "56"]"#, decode(&encode(&["123", "4", "56"])), vec!["123", "4", "56"]);
}

#[test]
fn looks_like_a_frame() {
    check!(r#"["3#abc", "0#"]"#, decode(&encode(&["3#abc", "0#"])), vec!["3#abc", "0#"]);
}

#[test]
fn control_chars() {
    check!(r#"["a\nb", "\t", "\0"]"#, decode(&encode(&["a\nb", "\t", "\0"])), vec!["a\nb", "\t", "\0"]);
}

#[test]
fn long_word() {
    check!(r#"["x" × 1000, "y"]"#, decode(&encode(&["x".repeat(1000).as_str(), "y"])), vec!["x".repeat(1000), "y".to_string()]);
}

#[test]
fn empty_between() {
    check!(r#"["a", "", "b"]"#, decode(&encode(&["a", "", "b"])), vec!["a", "", "b"]);
}

#[test]
fn random_round_trip() {
    let mut rng = anneal_prelude::Rng::new(15);
    for _ in 0..300 {
        let n = rng.below(6);
        let owned: Vec<String> = (0..n).map(|_| { let len = rng.below(12); rng.string(len, "a#1é🦀") }).collect();
        let words: Vec<&str> = owned.iter().map(String::as_str).collect();
        check!(format!("{words:?}"), decode(&encode(&words)), owned.clone());
    }
}

#[test]
fn scale_200k_words() {
    let owned: Vec<String> = (0..200_000).map(|i| format!("{i}#")).collect();
    let words: Vec<&str> = owned.iter().map(String::as_str).collect();
    check!("[\"0#\", \"1#\", …, \"199999#\"]", decode(&encode(&words)) == owned, true);
}
