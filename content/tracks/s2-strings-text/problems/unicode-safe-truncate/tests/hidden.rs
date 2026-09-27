use solution::*;

#[test]
fn mid_char() {
    check!(r#""héllo", 5"#, truncate("héllo", 5), "h…".to_string());
}

#[test]
fn cjk() {
    check!(r#""日本語テキスト", 10"#, truncate("日本語テキスト", 10), "日本…".to_string());
}

#[test]
fn no_room() {
    check!(r#""abc", 2"#, truncate("abc", 2), String::new());
}

#[test]
fn exact_fit() {
    check!(r#""abcd", 4"#, truncate("abcd", 4), "abcd".to_string());
}

#[test]
fn emoji() {
    check!(r#""🦀🦀🦀", 7"#, truncate("🦀🦀🦀", 7), "🦀…".to_string());
}

#[test]
fn emoji_back_to_zero() {
    check!(r#""🦀🦀", 6"#, truncate("🦀🦀", 6), "…".to_string());
}

#[test]
fn zero_budget() {
    check!(r#""a", 0"#, truncate("a", 0), String::new());
}

#[test]
fn one_over() {
    check!(r#""abcdef", 5"#, truncate("abcdef", 5), "ab…".to_string());
}

#[test]
fn unicode_fits() {
    check!(r#""é", 2"#, truncate("é", 2), "é".to_string());
}

#[test]
fn ellipsis_input() {
    check!(r#""……", 5"#, truncate("……", 5), "…".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2215);
    for _ in 0..400 {
        let len = rng.below(8);
        let s = rng.string(len, "aé日🦀");
        let max = rng.below(16);
        let want = if s.len() <= max {
            s.clone()
        } else if max < 3 {
            String::new()
        } else {
            let mut kept = String::new();
            for c in s.chars() {
                if kept.len() + c.len_utf8() > max - 3 {
                    break;
                }
                kept.push(c);
            }
            kept + "…"
        };
        check!(format!("s = {s:?}, max_bytes = {max}"), truncate(&s, max), want);
    }
}
