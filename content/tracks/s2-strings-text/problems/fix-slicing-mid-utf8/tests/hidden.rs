use solution::*;

#[test]
fn preview_exactly_n_chars() {
    check!(r#""日本", 2"#, preview("日本", 2), "日本".to_string());
}

#[test]
fn preview_cjk() {
    check!(r#""日本語", 2"#, preview("日本語", 2), "日本…".to_string());
}

#[test]
fn preview_zero() {
    check!(r#""a", 0 and "", 0"#, (preview("a", 0), preview("", 0)), ("…".to_string(), String::new()));
}

#[test]
fn preview_emoji() {
    check!(r#""🦀🦀🦀", 2"#, preview("🦀🦀🦀", 2), "🦀🦀…".to_string());
}

#[test]
fn preview_combining_mark_counts() {
    check!(r#""e\u{301}x", 1"#, preview("e\u{301}x", 1), "e…".to_string());
}

#[test]
fn capitalize_empty() {
    check!(r#""""#, capitalize(""), String::new());
}

#[test]
fn capitalize_sharp_s() {
    check!(r#""ßtraße""#, capitalize("ßtraße"), "SStraße".to_string());
}

#[test]
fn capitalize_rest_unchanged() {
    check!(r#""éA bC""#, capitalize("éA bC"), "ÉA bC".to_string());
}

#[test]
fn capitalize_ascii_and_cjk() {
    check!(r#""hello" and "日本""#, (capitalize("hello"), capitalize("日本")), ("Hello".to_string(), "日本".to_string()));
}

#[test]
fn capitalize_ligature() {
    check!(r#""ﬂow""#, capitalize("ﬂow"), "FLow".to_string());
}

#[test]
fn mask_short() {
    check!(r#""1234", "12", """#, (mask("1234"), mask("12"), mask("")), ("1234".to_string(), "12".to_string(), String::new()));
}

#[test]
fn mask_multibyte() {
    check!(r#""ñññññ""#, mask("ñññññ"), "*ññññ".to_string());
}

#[test]
fn mask_cjk() {
    check!(r#""日本語テキスト""#, mask("日本語テキスト"), "***テキスト".to_string());
}

#[test]
fn mask_euro() {
    check!(r#""€1234""#, mask("€1234"), "*1234".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7208);
    for _ in 0..400 {
        let len = rng.below(10);
        let s = rng.string(len, "aéß日🦀");
        let n = rng.below(12);
        let chars: Vec<char> = s.chars().collect();
        let want_preview = if chars.len() <= n { s.clone() } else { chars[..n].iter().collect::<String>() + "…" };
        let want_cap = match chars.first() {
            None => String::new(),
            Some(&c) => c.to_uppercase().collect::<String>() + &chars[1..].iter().collect::<String>(),
        };
        let hidden = chars.len().saturating_sub(4);
        let want_mask: String = chars.iter().enumerate().map(|(i, &c)| if i < hidden { '*' } else { c }).collect();
        check!(format!("s = {s:?}, n = {n}"), (preview(&s, n), capitalize(&s), mask(&s)), (want_preview, want_cap, want_mask));
    }
}

#[test]
fn scale_1m_chars() {
    let s = "é".repeat(1_000_000);
    let p = preview(&s, 600_000);
    let m = mask(&s);
    check!("s = 1000000 × 'é', n = 600000", (p.len(), m.len(), &m[m.len() - 9..]), (1_200_003, 999_996 + 8, "*éééé"));
}
