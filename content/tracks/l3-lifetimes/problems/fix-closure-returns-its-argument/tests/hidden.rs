use solution::*;

#[test]
fn trimmed_empty() {
    check!(r#"trimmed_lines("")"#, trimmed_lines("").len(), 0);
}

#[test]
fn first_fields_empty_line() {
    check!(r#"first_fields("\n")"#, first_fields("\n"), vec![""]);
}

#[test]
fn stripper_order() {
    check!(r#"" #x": whitespace first, so '#' stays"#, comment_stripper().run(" #x"), "#x");
}

#[test]
fn stripper_no_comment() {
    check!(r#""plain""#, comment_stripper().run("plain"), "plain");
}

#[test]
fn stripper_only_hashes() {
    check!(r####""###""####, comment_stripper().run("###"), "");
}

#[test]
fn empty_pipeline() {
    check!(r#"Pipeline::new().run(" x ")"#, Pipeline::new().run(" x "), " x ");
}

#[test]
fn custom_pipeline() {
    check!(r#"add inline closures: take 3 bytes, trim end"#, { let mut p = Pipeline::new(); p.add(|s| &s[..s.len().min(3)]); p.add(|s| s.trim_end()); p.run("ab cd") }, "ab");
}

#[test]
fn trimmed_unicode_spaces() {
    check!(r#"trimmed_lines("\u{3000}x\u{3000}")"#, trimmed_lines("\u{3000}x\u{3000}"), vec!["x"]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6316);
    let p = comment_stripper();
    for _ in 0..300 {
        let len = rng.below(10);
        let text = rng.string(len, "a #,\n");
        let want: Vec<&str> = text.lines().map(str::trim).filter(|l| !l.is_empty()).collect();
        check!(format!("trimmed_lines({text:?})"), trimmed_lines(&text), want);
        let want: Vec<&str> = text.lines().map(|l| l.split(',').next().unwrap_or("")).collect();
        check!(format!("first_fields({text:?})"), first_fields(&text), want);
        check!(format!("comment_stripper().run({text:?})"), p.run(&text), text.trim_start_matches('#').trim());
    }
}
