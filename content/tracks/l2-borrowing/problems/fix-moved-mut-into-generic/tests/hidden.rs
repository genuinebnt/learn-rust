use solution::*;

#[test]
fn every_line_alert() {
    check!(r#"lines "!a\n!b\n!c", header 1, with alerts"#, { let mut out = String::new(); let mut alerts = Vec::new(); let n = report(&mut out, "!a\n!b\n!c".lines(), 1, Some(&mut alerts)); (out, alerts, n) }, ("[!a]; !b; !c".to_string(), vec!["!b".to_string(), "!c".to_string(), "2 lines".to_string()], 2));
}

#[test]
fn bang_in_header_not_noted() {
    check!(r#"lines "!h\nx", header 1, with alerts"#, { let mut out = String::new(); let mut alerts = Vec::new(); let n = report(&mut out, "!h\nx".lines(), 1, Some(&mut alerts)); (out, alerts, n) }, ("[!h]; x".to_string(), vec!["1 lines".to_string()], 1));
}

#[test]
fn bang_not_first_char() {
    check!(r#"lines "h\na!\n !b", header 1, with alerts"#, { let mut out = String::new(); let mut alerts = Vec::new(); let n = report(&mut out, "h\na!\n !b".lines(), 1, Some(&mut alerts)); (out, alerts, n) }, ("[h]; a!;  !b".to_string(), vec!["2 lines".to_string()], 2));
}

#[test]
fn empty_lines() {
    check!(r#"lines "\n\nx\n", header 1, with alerts"#, { let mut out = String::new(); let mut alerts = Vec::new(); let n = report(&mut out, "\n\nx\n".lines(), 1, Some(&mut alerts)); (out, alerts, n) }, ("[]; ; x".to_string(), vec!["2 lines".to_string()], 2));
}

#[test]
fn unicode() {
    check!(r#"lines "日本\n!é", header 1, with alerts"#, { let mut out = String::new(); let mut alerts = Vec::new(); let n = report(&mut out, "日本\n!é".lines(), 1, Some(&mut alerts)); (out, alerts, n) }, ("[日本]; !é".to_string(), vec!["!é".to_string(), "1 lines".to_string()], 1));
}

#[test]
fn header_exactly_all() {
    check!(r#"lines "a\nb", header 2, with alerts"#, { let mut out = String::new(); let mut alerts = Vec::new(); let n = report(&mut out, "a\nb".lines(), 2, Some(&mut alerts)); (out, alerts, n) }, ("[a / b]".to_string(), vec!["0 lines".to_string()], 0));
}

#[test]
fn header_zero_empty() {
    check!(r#"lines "", header 0, with alerts"#, { let mut out = String::new(); let mut alerts = Vec::new(); let n = report(&mut out, "".lines(), 0, Some(&mut alerts)); (out, alerts, n) }, ("[]".to_string(), vec!["0 lines".to_string()], 0));
}

#[test]
fn keeps_existing_alerts() {
    check!(r#"alerts ["old"], lines "h\n!x", header 1"#, { let mut out = String::new(); let mut alerts = vec!["old".to_string()]; report(&mut out, "h\n!x".lines(), 1, Some(&mut alerts)); alerts }, vec!["old", "!x", "1 lines"]);
}

#[test]
fn any_iterator() {
    check!(r#"lines from a Vec, header 1"#, { let v = vec!["a", "!b"]; let mut out = String::new(); let n = report(&mut out, v.into_iter(), 1, None); (out, n) }, ("[a]; !b".to_string(), 1));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6211);
    for _ in 0..300 {
        let n = rng.below(7);
        let mut owned = Vec::new();
        for _ in 0..n {
            let len = rng.below(3);
            owned.push(rng.string(len, "!a"));
        }
        let header = rng.below(5);
        let lines: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
        let (head, rest) = lines.split_at(header.min(lines.len()));
        let mut want_out = format!("[{}]", head.join(" / "));
        let mut want_alerts: Vec<String> = Vec::new();
        for l in rest {
            want_out.push_str(&format!("; {l}"));
            if l.starts_with('!') {
                want_alerts.push(l.to_string());
            }
        }
        want_alerts.push(format!("{} lines", rest.len()));
        let mut out = String::new();
        let mut alerts = Vec::new();
        let got = report(&mut out, lines.iter().copied(), header, Some(&mut alerts));
        check!(format!("lines {lines:?}, header {header}"), (out, alerts, got), (want_out, want_alerts, rest.len()));
    }
}

#[test]
fn long_input() {
    let text = "x\n!y\n".repeat(50_000);
    let mut out = String::new();
    let mut alerts = Vec::new();
    let n = report(&mut out, text.lines(), 2, Some(&mut alerts));
    check!("100000 lines, header 2", (n, alerts.len(), out.len(), alerts[49_999].clone()), (99_998, 50_000, 350_001, "99998 lines".to_string()));
}
