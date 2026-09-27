use solution::*;

#[test]
fn emoji() {
    check!(r#""🦀!""#, sizes("🦀!"), (5, 2));
}

#[test]
fn nth() {
    check!(r#""héllo", 1 and 9"#, (nth_char("héllo", 1), nth_char("héllo", 9)), (Some('é'), None));
}

#[test]
fn offsets_slice_cleanly() {
    let s = "x→y→z";
    let ok = positions(s, '→').iter().all(|&i| s.is_char_boundary(i) && s[i..].starts_with('→'));
    check!(r#"every offset from positions("x→y→z", '→') is a char boundary"#, ok, true);
}

#[test]
fn empty_everything() {
    check!(r#""""#, (sizes(""), positions("", 'a'), nth_char("", 0)), ((0, 0), vec![], None));
}

#[test]
fn emoji_target() {
    check!(r#""🦀a🦀", '🦀'"#, positions("🦀a🦀", '🦀'), vec![0, 5]);
}

#[test]
fn ascii_after_unicode() {
    check!(r#""éaéa", 'a'"#, positions("éaéa", 'a'), vec![2, 5]);
}

#[test]
fn adjacent() {
    check!(r#""ññ", 'ñ'"#, positions("ññ", 'ñ'), vec![0, 2]);
}

#[test]
fn nth_last_and_past() {
    check!(r#""héllo", 4 and 5"#, (nth_char("héllo", 4), nth_char("héllo", 5)), (Some('o'), None));
}

#[test]
fn combining_mark() {
    check!(r#""e\u{301}" (e + combining acute)"#, sizes("e\u{301}"), (3, 2));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2208);
    for _ in 0..300 {
        let len = rng.below(10);
        let s = rng.string(len, "aé🦀");
        let target = *rng.pick(&['a', 'é', '🦀']);
        let chars = s.bytes().filter(|b| b & 0xC0 != 0x80).count();
        let want_pos: Vec<usize> = (0..s.len()).filter(|&i| s.is_char_boundary(i) && s[i..].starts_with(target)).collect();
        let n = rng.below(12);
        let want_nth = s.chars().collect::<Vec<_>>().get(n).copied();
        check!(format!("s = {s:?}, target = {target:?}, n = {n}"), (sizes(&s), positions(&s, target), nth_char(&s, n)), ((s.len(), chars), want_pos, want_nth));
    }
}

#[test]
fn scale_200k_chars() {
    let s = "aé".repeat(100_000);
    let p = positions(&s, 'é');
    check!("s = \"aéaé…\" (200000 chars), target = 'é'", (p.len(), p[0], p[99_999], sizes(&s)), (100_000, 1, 299_998, (300_000, 200_000)));
}
