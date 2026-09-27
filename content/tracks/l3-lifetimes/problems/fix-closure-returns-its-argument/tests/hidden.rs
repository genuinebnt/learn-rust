use solution::*;

#[test]
fn all_blank() {
    check!(r#"" \n\t\n""#, trimmed_lines(" \n\t\n").len(), 0);
}

#[test]
fn single_line() {
    check!(r#""solo""#, trimmed_lines("solo"), vec!["solo"]);
}

#[test]
fn tabs() {
    check!(r#""\ta\t\n\tb""#, trimmed_lines("\ta\t\n\tb"), vec!["a", "b"]);
}

#[test]
fn crlf() {
    check!(r#""a \r\n b\r\n""#, trimmed_lines("a \r\n b\r\n"), vec!["a", "b"]);
}

#[test]
fn unicode_whitespace() {
    check!(r#""\u{3000}é\u{a0}""#, trimmed_lines("\u{3000}é\u{a0}"), vec!["é"]);
}

#[test]
fn order_kept() {
    check!(r#""c\nb\na""#, trimmed_lines("c\nb\na"), vec!["c", "b", "a"]);
}

#[test]
fn points_into_input() {
    let input = String::from("  hi  ");
    let lines = trimmed_lines(&input);
    check!(r#"the trimmed line points into the String"#, std::ptr::eq(lines[0].as_ptr(), input[2..].as_ptr()), true);
}

#[test]
fn many_lines() {
    let input: String = (0..1000).map(|i| format!("  {i}  \n")).collect();
    let lines = trimmed_lines(&input);
    check!(r#"1000 lines "  n  ""#, (lines.len(), lines[999]), (1000, "999"));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(319);
    for _ in 0..300 {
        let n = rng.below(12);
        let text = rng.string(n, "ab \n");
        let want: Vec<&str> = text.split('\n').map(|l| l.trim_matches(' ')).filter(|l| !l.is_empty()).collect();
        check!(format!("text = {text:?}"), trimmed_lines(&text), want);
    }
}
