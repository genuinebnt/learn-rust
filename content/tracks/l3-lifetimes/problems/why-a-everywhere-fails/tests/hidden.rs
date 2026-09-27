use solution::*;

#[test]
fn split_lines_empty() {
    check!(r#"split_lines("", ',')"#, split_lines("", ',').len(), 0);
}

#[test]
fn multi_char_separator() {
    check!(r#""a<>b<>c" on "<>""#, Splitter::new("a<>b<>c", "<>").collect::<Vec<_>>(), vec!["a", "b", "c"]);
}

#[test]
fn overlapping_separator() {
    check!(r#""aaa" on "aa""#, Splitter::new("aaa", "aa").collect::<Vec<_>>(), vec!["", "a"]);
}

#[test]
fn peek_many_separators() {
    check!(r#""a;b;c" on ";": peek"#, Splitter::new("a;b;c", ";").peek(), Some("a"));
}

#[test]
fn peek_after_end() {
    check!(r#""a": next, then peek"#, { let mut s = Splitter::new("a", ","); s.next(); (s.peek(), s.next()) }, (None, None));
}

#[test]
fn unicode_separator() {
    check!(r#""日→本→語" on "→""#, split_lines("日→本→語", '→'), vec!["日", "本", "語"]);
}

#[test]
fn split_lines_crlf() {
    check!(r#""a,b\r\nc""#, split_lines("a,b\r\nc", ','), vec!["a", "b", "c"]);
}

#[test]
fn pieces_point_into_text() {
    let t = String::from("a,b");
    check!(r#"the first piece is a slice of the text"#, Splitter::new(&t, ",").nth(1).unwrap().as_ptr() == t[2..].as_ptr(), true);
}

#[test]
fn peek_outlives_splitter() {
    let text = String::from("left|right");
    let p = { let sep = String::from("|"); Splitter::new(&text, &sep).peek() };
    check!(r#"peek's result used after the splitter is gone"#, p, Some("left"));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6308);
    for _ in 0..400 {
        let len = rng.below(10);
        let text = rng.string(len, "ab,\n");
        let slen = 1 + rng.below(2);
        let sep = rng.string(slen, "ab,");
        let want: Vec<&str> = text.split(sep.as_str()).collect();
        check!(format!("{text:?} on {sep:?}"), Splitter::new(&text, &sep).collect::<Vec<_>>(), want);
        let want: Vec<&str> = text.lines().flat_map(|l| l.split(',')).collect();
        check!(format!("split_lines({text:?}, ',')"), split_lines(&text, ','), want);
    }
}

#[test]
fn long_text() {
    let text = "ab,".repeat(100_000);
    let n = split_lines(&text, ',').len();
    check!("\"ab,\" x 100000", n, 100_001);
}
