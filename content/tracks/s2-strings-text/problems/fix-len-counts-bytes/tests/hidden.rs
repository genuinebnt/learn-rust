use solution::*;

#[test]
fn center_too_wide_in_chars() {
    check!(r#""日本語", 3, ' '"#, center("日本語", 3, ' '), "日本語".to_string());
}

#[test]
fn center_multibyte_fill() {
    check!(r#""x", 3, '·'"#, center("x", 3, '·'), "·x·".to_string());
}

#[test]
fn center_emoji() {
    check!(r#""🦀", 3, '.'"#, center("🦀", 3, '.'), ".🦀.".to_string());
}

#[test]
fn center_fits_in_chars_not_bytes() {
    check!(r#""éé", 3, '.'"#, center("éé", 3, '.'), "éé.".to_string());
}

#[test]
fn center_empty() {
    check!(r#""", 3, 'x'"#, center("", 3, 'x'), "xxx".to_string());
}

#[test]
fn indent_ideographic_space() {
    check!(r#""\u{3000}x""#, indent("\u{3000}x"), 1);
}

#[test]
fn indent_edges() {
    check!(r#""", "   ", "x  ""#, (indent(""), indent("   "), indent("x  ")), (0, 3, 0));
}

#[test]
fn indent_mixed() {
    check!(r#""\u{2003} \u{a0}é ""#, indent("\u{2003} \u{a0}é "), 3);
}

#[test]
fn wrap_ascii() {
    check!(r#""the quick brown fox", 10"#, wrap("the quick brown fox", 10), vec!["the quick", "brown fox"]);
}

#[test]
fn wrap_long_word_alone() {
    check!(r#""a verylongword b", 4"#, wrap("a verylongword b", 4), vec!["a", "verylongword", "b"]);
}

#[test]
fn wrap_cjk() {
    check!(r#""日本語 テキスト", 7"#, wrap("日本語 テキスト", 7), vec!["日本語", "テキスト"]);
}

#[test]
fn wrap_cjk_fits() {
    check!(r#""日本語 テキスト", 8"#, wrap("日本語 テキスト", 8), vec!["日本語 テキスト"]);
}

#[test]
fn wrap_exact_fit() {
    check!(r#""ab cd", 5"#, wrap("ab cd", 5), vec!["ab cd"]);
}

#[test]
fn wrap_width_zero() {
    check!(r#""a b", 0"#, wrap("a b", 0), vec!["a", "b"]);
}

#[test]
fn wrap_extra_whitespace() {
    check!(r#""  a \t b\n\nc  ", 3"#, wrap("  a \t b\n\nc  ", 3), vec!["a b", "c"]);
}

#[test]
fn wrap_empty() {
    check!(r#""", 5"#, wrap("", 5), Vec::<String>::new());
}

#[test]
fn wrap_accented_breaks_right() {
    check!(r#""é é é é", 3"#, wrap("é é é é", 3), vec!["é é", "é é"]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7209);
    for _ in 0..400 {
        let len = rng.below(14);
        let text = rng.string(len, "aé日 \t\u{a0}");
        let width = rng.below(8);
        let fill = *rng.pick(&['*', '·']);
        let chars: Vec<char> = text.chars().collect();
        let n = chars.len();
        let want_center = if n >= width {
            text.clone()
        } else {
            let left = (width - n) / 2;
            let mut s: String = std::iter::repeat(fill).take(left).collect();
            s.push_str(&text);
            s.extend(std::iter::repeat(fill).take(width - n - left));
            s
        };
        let want_indent = chars.iter().position(|c| !c.is_whitespace()).unwrap_or(n);
        let mut want_wrap: Vec<Vec<&str>> = Vec::new();
        let mut used = 0;
        for w in text.split_whitespace() {
            let wl = w.chars().count();
            if !want_wrap.is_empty() && used + 1 + wl <= width {
                want_wrap.last_mut().unwrap().push(w);
                used += 1 + wl;
            } else {
                want_wrap.push(vec![w]);
                used = wl;
            }
        }
        let want_wrap: Vec<String> = want_wrap.iter().map(|l| l.join(" ")).collect();
        check!(format!("text = {text:?}, width = {width}, fill = {fill:?}"),
               (center(&text, width, fill), indent(&text), wrap(&text, width)), (want_center, want_indent, want_wrap));
    }
}

#[test]
fn scale_400k_words_one_line() {
    let text = "éb ".repeat(400_000);
    let lines = wrap(&text, 10_000_000);
    check!("text = \"éb \" × 400000, width = 10000000", (lines.len(), lines[0].len()), (1, 400_000 * 4 - 1));
}
