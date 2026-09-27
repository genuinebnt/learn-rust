use solution::*;

#[test]
fn emoji() {
    check!(r#""🦀🦀🦀", 2"#, prefix("🦀🦀🦀", 2), "🦀🦀");
}

#[test]
fn zero() {
    check!(r#""abc", 0"#, prefix("abc", 0), "");
}

#[test]
fn shorter_in_chars_than_bytes() {
    check!(r#""日本", 3"#, prefix("日本", 3), "日本");
}

#[test]
fn zero_unicode() {
    check!(r#""é", 0"#, prefix("é", 0), "");
}

#[test]
fn cjk() {
    check!(r#""日本語", 2"#, prefix("日本語", 2), "日本");
}

#[test]
fn exact_char_count() {
    check!(r#""日本", 2"#, prefix("日本", 2), "日本");
}

#[test]
fn mixed() {
    check!(r#""a🦀b", 2"#, prefix("a🦀b", 2), "a🦀");
}

#[test]
fn combining_mark_is_a_char() {
    check!(r#""e\u{301}x", 1"#, prefix("e\u{301}x", 1), "e");
}

#[test]
fn huge_n() {
    check!(r#""abc", usize::MAX"#, prefix("abc", usize::MAX), "abc");
}

#[test]
fn borrows_input() {
    let s = String::from("héllo");
    check!(r#"prefix points into its input"#, prefix(&s, 2).as_ptr() == s.as_ptr(), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2209);
    for _ in 0..300 {
        let len = rng.below(10);
        let s = rng.string(len, "aé日🦀");
        let n = rng.below(12);
        let want: String = s.chars().take(n).collect();
        check!(format!("s = {s:?}, n = {n}"), prefix(&s, n), want.as_str());
    }
}

#[test]
fn scale_200k_chars() {
    let s = "é".repeat(200_000);
    check!("s = 200000 × 'é', n = 150000", prefix(&s, 150_000).len(), 300_000);
}
