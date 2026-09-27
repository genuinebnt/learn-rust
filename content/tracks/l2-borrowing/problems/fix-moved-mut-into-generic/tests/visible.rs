use solution::*;

#[test]
fn example() {
    check!(r#"lines "Title\nv1\nok\n!disk full", header 2, with alerts"#, { let mut out = String::new(); let mut alerts = Vec::new(); let n = report(&mut out, "Title\nv1\nok\n!disk full".lines(), 2, Some(&mut alerts)); (out, alerts, n) }, ("[Title / v1]; ok; !disk full".to_string(), vec!["!disk full".to_string(), "2 lines".to_string()], 2));
}

#[test]
fn no_header() {
    check!(r#"lines "a\n!b", header 0, with alerts"#, { let mut out = String::new(); let mut alerts = Vec::new(); let n = report(&mut out, "a\n!b".lines(), 0, Some(&mut alerts)); (out, alerts, n) }, ("[]; a; !b".to_string(), vec!["!b".to_string(), "2 lines".to_string()], 2));
}

#[test]
fn header_longer_than_input() {
    check!(r#"lines "a\nb", header 5, with alerts"#, { let mut out = String::new(); let mut alerts = Vec::new(); let n = report(&mut out, "a\nb".lines(), 5, Some(&mut alerts)); (out, alerts, n) }, ("[a / b]".to_string(), vec!["0 lines".to_string()], 0));
}

#[test]
fn without_alerts() {
    check!(r#"lines "h\n!x\ny", header 1, no alerts"#, { let mut out = String::new(); let n = report(&mut out, "h\n!x\ny".lines(), 1, None); (out, n) }, ("[h]; !x; y".to_string(), 2));
}

#[test]
fn empty_input() {
    check!(r#"lines "", header 1, with alerts"#, { let mut out = String::new(); let mut alerts = Vec::new(); let n = report(&mut out, "".lines(), 1, Some(&mut alerts)); (out, alerts, n) }, ("[]".to_string(), vec!["0 lines".to_string()], 0));
}

#[test]
fn appends_to_existing_output() {
    check!(r#"out = ">", lines "h\nb", header 1"#, { let mut out = String::from(">"); report(&mut out, "h\nb".lines(), 1, None); out }, ">[h]; b".to_string());
}
