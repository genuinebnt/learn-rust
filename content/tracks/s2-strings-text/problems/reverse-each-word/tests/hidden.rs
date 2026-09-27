use solution::*;

#[test]
fn emoji() {
    check!(r#""🦀x""#, reverse_each_word("🦀x"), "x🦀".to_string());
}

#[test]
fn only_whitespace() {
    check!(r#"" \t\n ""#, reverse_each_word(" \t\n "), " \t\n ".to_string());
}

#[test]
fn two_marks() {
    check!(r#""a\u{301}\u{302}b""#, reverse_each_word("a\u{301}\u{302}b"), "ba\u{301}\u{302}".to_string());
}

#[test]
fn leading_mark() {
    check!(r#""\u{301}ab""#, reverse_each_word("\u{301}ab"), "ba\u{301}".to_string());
}

#[test]
fn leading_marks_stay_together() {
    check!(r#""\u{301}\u{302}a""#, reverse_each_word("\u{301}\u{302}a"), "a\u{301}\u{302}".to_string());
}

#[test]
fn marks_in_several_words() {
    check!(r#""ne\u{301}e n\u{303}o""#, reverse_each_word("ne\u{301}e n\u{303}o"), "ee\u{301}n on\u{303}".to_string());
}

#[test]
fn cjk() {
    check!(r#""日本語 テスト""#, reverse_each_word("日本語 テスト"), "語本日 トステ".to_string());
}

#[test]
fn crlf_between() {
    check!(r#""ab\r\ncd""#, reverse_each_word("ab\r\ncd"), "ba\r\ndc".to_string());
}

#[test]
fn no_break_space_separates() {
    check!(r#""ab\u{a0}cd""#, reverse_each_word("ab\u{a0}cd"), "ba\u{a0}dc".to_string());
}

#[test]
fn precomposed_is_one_char() {
    check!(r#""\u{e9}t\u{e9}""#, reverse_each_word("\u{e9}t\u{e9}"), "\u{e9}t\u{e9}".to_string());
}

#[test]
fn single_char_words() {
    check!(r#""a b  c""#, reverse_each_word("a b  c"), "a b  c".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7210);
    for _ in 0..400 {
        let len = rng.below(14);
        let s = rng.string(len, "ab é\u{301}\u{302}\t🦀");
        let mut want = String::new();
        let mut word: Vec<String> = Vec::new();
        let flush = |word: &mut Vec<String>, want: &mut String| {
            for cluster in word.drain(..).rev() {
                want.push_str(&cluster);
            }
        };
        for c in s.chars() {
            if c.is_whitespace() {
                flush(&mut word, &mut want);
                want.push(c);
            } else if ('\u{300}'..='\u{36f}').contains(&c) && !word.is_empty() {
                word.last_mut().unwrap().push(c);
            } else {
                word.push(c.to_string());
            }
        }
        flush(&mut word, &mut want);
        check!(format!("s = {s:?}"), reverse_each_word(&s), want);
    }
}

#[test]
fn scale_200k_words() {
    let s = "abe\u{301} ".repeat(200_000);
    let out = reverse_each_word(&s);
    check!("s = \"abe\\u{301} \" × 200000", (out.len(), &out[..5]), (s.len(), "e\u{301}ba"));
}
