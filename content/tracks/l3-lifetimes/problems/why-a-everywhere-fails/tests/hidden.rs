use solution::*;

#[test]
fn no_sep() {
    check!(r#""abc", ",""#, Splitter::new("abc", ",").parts(), vec!["abc"]);
}

#[test]
fn empty_text() {
    check!(r#""", ",""#, (Splitter::new("", ",").first(), Splitter::new("", ",").parts()), ("", vec![""]));
}

#[test]
fn leading_sep() {
    check!(r#"",a", ",""#, (Splitter::new(",a", ",").first(), Splitter::new(",a", ",").parts()), ("", vec!["", "a"]));
}

#[test]
fn text_is_sep() {
    check!(r#""--", "--""#, Splitter::new("--", "--").parts(), vec!["", ""]);
}

#[test]
fn unicode_sep() {
    check!(r#""a→b→c", "→""#, Splitter::new("a→b→c", "→").parts(), vec!["a", "b", "c"]);
}

#[test]
fn overlapping_sep() {
    check!(r#""aaa", "aa""#, Splitter::new("aaa", "aa").parts(), vec!["", "a"]);
}

#[test]
fn both_outlive_sep() {
    let text = String::from("x;y z");
    let (first, parts);
    {
        let sep = String::from(";");
        let s = Splitter::new(&text, &sep);
        first = s.first();
        parts = s.parts();
    }
    check!(r#"first and parts, separator dropped"#, (first, parts), ("x", vec!["x", "y z"]));
}

#[test]
fn zero_copy() {
    let text = String::from("a,b");
    let parts = Splitter::new(&text, ",").parts();
    check!(r#"pieces point into the text"#, std::ptr::eq(parts[1].as_ptr(), text[2..].as_ptr()), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(309);
    for _ in 0..300 {
        let n = rng.below(10);
        let text = rng.string(n, "ab,");
        let sep = if rng.bool() { "," } else { "b," };
        // Reference: walk the text by hand.
        let mut want: Vec<&str> = Vec::new();
        let mut start = 0;
        let mut i = 0;
        while i + sep.len() <= text.len() {
            if &text[i..i + sep.len()] == sep {
                want.push(&text[start..i]);
                i += sep.len();
                start = i;
            } else {
                i += 1;
            }
        }
        want.push(&text[start..]);
        let s = Splitter::new(&text, sep);
        check!(format!("text = {text:?}, sep = {sep:?}"), (s.first(), s.parts()), (want[0], want.clone()));
    }
}
