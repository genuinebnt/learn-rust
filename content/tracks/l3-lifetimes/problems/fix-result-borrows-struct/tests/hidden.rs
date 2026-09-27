use solution::*;

#[test]
fn tie() {
    check!(r#""ab\ncd""#, Document::new("ab\ncd").longest_line(), "ab");
}

#[test]
fn single_line() {
    check!(r#""only""#, Document::new("only").longest_line(), "only");
}

#[test]
fn crlf() {
    let d = Document::new("ab\r\nc");
    check!(r#""ab\r\nc""#, (d.longest_line(), d.lines_with("b")), ("ab", vec!["ab"]));
}

#[test]
fn trailing_newline() {
    check!(r#""a\nbb\n""#, Document::new("a\nbb\n").lines_with(""), vec!["a", "bb"]);
}

#[test]
fn case_sensitive() {
    check!(r#""Rust\nrust", word "rust""#, Document::new("Rust\nrust").lines_with("rust"), vec!["rust"]);
}

#[test]
fn unicode() {
    check!(r#""éé\nabc", longest by bytes"#, Document::new("éé\nabc").longest_line(), "éé");
}

#[test]
fn blank_lines() {
    check!(r#""\n\nx\n""#, Document::new("\n\nx\n").longest_line(), "x");
}

#[test]
fn word_in_the_middle() {
    check!(r#""one two\nthree", word "tw""#, Document::new("one two\nthree").lines_with("tw"), vec!["one two"]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(308);
    for _ in 0..300 {
        let n = rng.below(10);
        let text = rng.string(n, "ab\n");
        let lines: Vec<&str> = text.split('\n').collect();
        let lines = if text.ends_with('\n') { &lines[..lines.len() - 1] } else { &lines[..] };
        let mut longest = "";
        for l in lines {
            if l.len() > longest.len() {
                longest = l;
            }
        }
        let with_b: Vec<&str> = lines.iter().copied().filter(|l| l.contains('b')).collect();
        let d = Document::new(&text);
        check!(format!("text = {text:?}"), (d.longest_line(), d.lines_with("b")), (longest, with_b));
    }
}
