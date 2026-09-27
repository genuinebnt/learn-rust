use solution::*;

#[test]
fn command_not_unicode_folded() {
    check!(r#""É", "é""#, is_command("É", "é"), false);
}

#[test]
fn command_inner_space() {
    check!(r#""qu it", "quit""#, is_command("qu it", "quit"), false);
}

#[test]
fn command_untrimmed_command() {
    check!(r#""QUIT", "quit ""#, is_command("QUIT", "quit "), false);
}

#[test]
fn empty_command() {
    check!(r#""  ", """#, is_command("  ", ""), true);
}

#[test]
fn command_no_allocation() {
    let (ok, n) = anneal_prelude::allocs(|| is_command("  HeLp  ", "help"));
    check!(r#"is_command("  HeLp  ", "help")"#, (ok, n.count), (true, 0));
}

#[test]
fn header_non_ascii_untouched() {
    let mut h = String::from("X-Ünïcode");
    normalize_header(&mut h);
    check!(r#""X-Ünïcode""#, h, "x-Ünïcode".to_string());
}

#[test]
fn header_no_allocation() {
    let mut h = String::from("ACCEPT-ENCODING");
    let ((), n) = anneal_prelude::allocs(|| normalize_header(&mut h));
    check!(r#""ACCEPT-ENCODING" in place"#, (h.as_str(), n.count), ("accept-encoding", 0));
}

#[test]
fn title_final_sigma() {
    check!(r#""ΟΔΟΣ ΣΑΣ""#, title_case("ΟΔΟΣ ΣΑΣ"), "Οδος Σας".to_string());
}

#[test]
fn title_whitespace_collapsed() {
    check!(r#""  a\tb \n c  ""#, title_case("  a\tb \n c  "), "A B C".to_string());
}

#[test]
fn title_empty() {
    check!(r#""" and "   ""#, (title_case(""), title_case("   ")), (String::new(), String::new()));
}

#[test]
fn title_ligature() {
    check!(r#""ﬁne""#, title_case("ﬁne"), "FIne".to_string());
}

#[test]
fn title_dotted_capital_i_in_the_rest() {
    check!(r#""AİR""#, title_case("AİR"), "Ai\u{307}r".to_string());
}

#[test]
fn title_digits_and_cjk() {
    check!(r#""3RD 日本語""#, title_case("3RD 日本語"), "3rd 日本語".to_string());
}

#[test]
fn title_already_title() {
    check!(r#""Hello World""#, title_case("Hello World"), "Hello World".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7204);
    for _ in 0..400 {
        let len = rng.below(10);
        let s = rng.string(len, "aBéÉßΣσ \t");
        let mut words = Vec::new();
        for w in s.split_whitespace() {
            let mut it = w.chars();
            let first: String = it.next().map(|c| c.to_uppercase().collect()).unwrap_or_default();
            words.push(first + &it.as_str().to_lowercase());
        }
        let mut h = s.clone();
        let want_h: String = s.chars().map(|c| if c.is_ascii_uppercase() { c.to_ascii_lowercase() } else { c }).collect();
        normalize_header(&mut h);
        let cmd = s.trim().to_ascii_uppercase();
        check!(format!("s = {s:?}"), (title_case(&s), h, is_command(&s, &cmd)), (words.join(" "), want_h, true));
    }
}

#[test]
fn scale_200k_words() {
    let s = "hELLO wORLD ".repeat(100_000);
    let out = title_case(&s);
    check!("s = \"hELLO wORLD …\" (200000 words)", (out.len(), &out[..12]), (1_199_999, "Hello World "));
}
