use solution::*;

#[test]
fn unicode() {
    check!(r#""héllo hi", 4"#, long_words("héllo hi", 4).collect::<Vec<_>>(), vec!["héllo".to_string()]);
}

#[test]
fn chars_not_bytes() {
    check!(r#""héllo", 5"#, long_words("héllo", 5).count(), 0);
}

#[test]
fn emoji() {
    check!(r#""😀😀 a", 1"#, long_words("😀😀 a", 1).collect::<Vec<_>>(), vec!["😀😀".to_string()]);
}

#[test]
fn tabs_and_newlines() {
    check!(r#""alpha\tbeta\ngamma", 4"#, long_words("alpha\tbeta\ngamma", 4).collect::<Vec<_>>(), vec!["alpha".to_string(), "gamma".to_string()]);
}

#[test]
fn only_spaces() {
    check!(r#""   ", 0"#, long_words("   ", 0).count(), 0);
}

#[test]
fn order_kept() {
    check!(r#""ccc a bbb", 2"#, long_words("ccc a bbb", 2).collect::<Vec<_>>(), vec!["ccc".to_string(), "bbb".to_string()]);
}

#[test]
fn words_outlive_text() {
    let words: Vec<String>;
    {
        let text = String::from("a longer b");
        words = long_words(&text, 2).collect();
    }
    check!(r#"collect, then drop the text"#, words, vec!["longer".to_string()]);
}

#[test]
fn lazy() {
    check!(r#""one three five", 3: take(1)"#, long_words("one three five", 3).take(1).collect::<Vec<_>>(), vec!["three".to_string()]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(305);
    for _ in 0..300 {
        let n = rng.below(14);
        let text = rng.string(n, "aé ");
        let min = rng.below(4);
        let want: Vec<String> = text.split(' ').filter(|w| !w.is_empty() && w.chars().count() > min).map(String::from).collect();
        check!(format!("text = {text:?}, min = {min}"), long_words(&text, min).collect::<Vec<_>>(), want);
    }
}
