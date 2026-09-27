use solution::*;

#[test]
fn empty_text() {
    check!(r#""""#, (Index::new("").longest_line(), Index::new("").into_lines().len()), ("", 0));
}

#[test]
fn longest_tie_first() {
    check!(r#""ab\ncd""#, Index::new("ab\ncd").longest_line(), "ab");
}

#[test]
fn lines_with_none() {
    check!(r#"no line contains "zz""#, Index::new("a\nb").lines_with("zz").len(), 0);
}

#[test]
fn lines_with_empty_word() {
    check!(r#"every line contains """#, Index::new("a\nb").lines_with(""), vec!["a", "b"]);
}

#[test]
fn results_point_into_text() {
    let text = String::from("fn main\nlet x\nfn helper\n");
    check!(r#"longest_line points into the text"#, Index::new(&text).longest_line().as_ptr() == text[14..].as_ptr(), true);
}

#[test]
fn iter_twice() {
    let text = String::from("fn main\nlet x\nfn helper\n");
    let ix = Index::new(&text);
    check!(r#"iter() twice while the index lives"#, (ix.iter().count(), ix.iter().last()), (3, Some("fn helper")));
}

#[test]
fn crlf() {
    check!(r#""a\r\nbb\r\n""#, Index::new("a\r\nbb\r\n").into_lines(), vec!["a", "bb"]);
}

#[test]
fn unicode_longest() {
    check!(r#""ééé\nabcd""#, Index::new("ééé\nabcd").longest_line(), "ééé");
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6307);
    for _ in 0..300 {
        let len = rng.below(14);
        let text = rng.string(len, "ab\n");
        let lines: Vec<&str> = text.lines().collect();
        let mut longest = "";
        for &l in &lines {
            if l.len() > longest.len() {
                longest = l;
            }
        }
        let with: Vec<&str> = lines.iter().copied().filter(|l| l.contains("ab")).collect();
        let got = {
            let ix = Index::new(&text);
            (ix.longest_line(), ix.lines_with("ab"), ix.iter().collect::<Vec<_>>())
        };
        check!(format!("text {text:?}"), got, (longest, with, lines.clone()));
    }
}
