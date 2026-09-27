use solution::*;

#[test]
fn first_word_empty() {
    check!(r#"first_word("") and first_word(" \t ")"#, (first_word(""), first_word(" \t ")), ("", ""));
}

#[test]
fn first_word_from_string() {
    let s = String::from("one two");
    check!(r#"first_word(&String "one two")"#, first_word(&s), "one");
}

#[test]
fn first_word_tabs() {
    check!(r#"first_word("\n\tfoo\tbar")"#, first_word("\n\tfoo\tbar"), "foo");
}

#[test]
fn extension_slices_input() {
    let s = "archive.zip";
    check!(r#"extension("archive.zip") points into the input"#, extension(s).map(|e| e.as_ptr() == s[8..].as_ptr()), Some(true));
}

#[test]
fn extension_more() {
    check!(r#""..bashrc", "a/.b/c", "a/b/.git", "noext", "", "/""#, ["..bashrc", "a/.b/c", "a/b/.git", "noext", "", "/"].map(extension), [Some("bashrc"), None, None, None, None, None]);
}

#[test]
fn extension_unicode() {
    check!(r#""日本.txt" and "é.日""#, (extension("日本.txt"), extension("é.日")), (Some("txt"), Some("日")));
}

#[test]
fn join_all_empty() {
    check!(r#"join_nonempty(["", ""], ",") and of []"#, (join_nonempty(&["", ""], ","), join_nonempty::<&str>(&[], ",")), (String::new(), String::new()));
}

#[test]
fn join_cows() {
    use std::borrow::Cow;
    check!(r#"join_nonempty of Cows [Borrowed "a", Owned "b"]"#, join_nonempty(&[Cow::Borrowed("a"), Cow::Owned("b".to_string())], "+"), "a+b");
}

#[test]
fn count_slice_of_str() {
    check!(r#"count_word(["x", "X", "y"].iter(), "x")"#, count_word(["x", "X", "y"].iter(), "x"), 2);
}

#[test]
fn count_ascii_case_only() {
    check!(r#"count_word(["É", "é"], "é") (ASCII case only)"#, count_word(["É", "é"], "é"), 1);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6107);
    for _ in 0..400 {
        let len = rng.below(9);
        let path = rng.string(len, "ab./");
        let name = match path.rfind('/') {
            Some(i) => &path[i + 1..],
            None => &path[..],
        };
        let want = match name.rfind('.') {
            Some(0) | None => None,
            Some(i) => Some(&name[i + 1..]),
        };
        check!(format!("extension({path:?})"), extension(&path), want);
        let len = rng.below(8);
        let text = rng.string(len, "aA \t");
        let mut chars = text.char_indices().skip_while(|(_, c)| c.is_whitespace());
        let want = match chars.next() {
            Some((i, _)) => {
                let end = text[i..].find(char::is_whitespace).map_or(text.len(), |j| i + j);
                &text[i..end]
            }
            None => "",
        };
        check!(format!("first_word({text:?})"), first_word(&text), want);
        let n = text.split(' ').filter(|w| w.eq_ignore_ascii_case("a")).count();
        check!(format!("count_word({text:?}.split(' '), \"a\")"), count_word(text.split(' '), "a"), n);
        let parts: Vec<String> = text.split(' ').map(String::from).collect();
        let want = parts.iter().filter(|p| !p.is_empty()).cloned().collect::<Vec<_>>().join("|");
        check!(format!("join_nonempty({parts:?}, \"|\")"), join_nonempty(&parts, "|"), want);
    }
}

#[test]
fn long_input() {
    let text = "word ".repeat(200_000);
    check!("200000 × \"word \"", (count_word(text.split_whitespace(), "WORD"), first_word(&text).len()), (200_000, 4));
}
