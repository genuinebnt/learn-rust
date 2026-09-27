use solution::*;

#[test]
fn empty_text() {
    check!(r#""", 0 and 1"#, (line_col("", 0), line_col("", 1)), (Some((1, 1)), None));
}

#[test]
fn end_of_text() {
    check!(r#""abc", 3 and 4"#, (line_col("abc", 3), line_col("abc", 4)), (Some((1, 4)), None));
}

#[test]
fn just_after_newline() {
    check!(r#""a\n", 2"#, line_col("a\n", 2), Some((2, 1)));
}

#[test]
fn carriage_return_is_a_column() {
    check!(r#""a\r\nb", 2 and 3"#, (line_col("a\r\nb", 2), line_col("a\r\nb", 3)), (Some((1, 3)), Some((2, 1))));
}

#[test]
fn cjk_lines() {
    check!(r#""日本\n語x", 7, 10, 4"#, (line_col("日本\n語x", 7), line_col("日本\n語x", 10), line_col("日本\n語x", 4)), (Some((2, 1)), Some((2, 2)), None));
}

#[test]
fn emoji_column() {
    check!(r#""🦀x", 4 and 2"#, (line_col("🦀x", 4), line_col("🦀x", 2)), (Some((1, 2)), None));
}

#[test]
fn huge_offset() {
    check!(r#""abc", usize::MAX"#, line_col("abc", usize::MAX), None);
}

#[test]
fn char_to_byte_empty() {
    check!(r#""", n = 0 and 1"#, (char_to_byte("", 0), char_to_byte("", 1)), (Some(0), None));
}

#[test]
fn char_to_byte_emoji() {
    check!(r#""🦀a", n = 1 and 2"#, (char_to_byte("🦀a", 1), char_to_byte("🦀a", 2)), (Some(4), Some(5)));
}

#[test]
fn char_to_byte_huge_n() {
    check!(r#""ab", usize::MAX"#, char_to_byte("ab", usize::MAX), None);
}

#[test]
fn no_match() {
    check!(r#""abc", "d" and "", "a" and "ab", "abc""#, (find_all("abc", "d"), find_all("", "a"), find_all("ab", "abc")), (vec![], vec![], vec![]));
}

#[test]
fn every_char_matches() {
    check!(r#""aaa", "a""#, find_all("aaa", "a"), vec![(0, 0), (1, 1), (2, 2)]);
}

#[test]
fn multi_char_needle() {
    check!(r#""xéyéz", "yé""#, find_all("xéyéz", "yé"), vec![(3, 2)]);
}

#[test]
fn emoji_needle_no_overlap() {
    check!(r#""🦀🦀🦀", "🦀🦀""#, find_all("🦀🦀🦀", "🦀🦀"), vec![(0, 0)]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7207);
    let needles = ["a", "é", "aa", "é🦀", "🦀", "\na"];
    for _ in 0..400 {
        let len = rng.below(10);
        let s = rng.string(len, "aé🦀\n");
        let at = rng.below(s.len() + 2);
        let want_lc = if at > s.len() || !s.is_char_boundary(at) {
            None
        } else {
            let (mut line, mut col) = (1, 1);
            for c in s[..at].chars() {
                if c == '\n' {
                    line += 1;
                    col = 1;
                } else {
                    col += 1;
                }
            }
            Some((line, col))
        };
        let n = rng.below(12);
        let mut starts: Vec<usize> = (0..s.len()).filter(|&i| s.is_char_boundary(i)).collect();
        starts.push(s.len());
        let want_cb = starts.get(n).copied();
        let needle = *rng.pick(&needles);
        let chars: Vec<char> = s.chars().collect();
        let pat: Vec<char> = needle.chars().collect();
        let mut want_find = Vec::new();
        let mut k = 0;
        while k + pat.len() <= chars.len() {
            if chars[k..k + pat.len()] == pat[..] {
                want_find.push((starts[k], k));
                k += pat.len();
            } else {
                k += 1;
            }
        }
        check!(format!("s = {s:?}, at = {at}, n = {n}, needle = {needle:?}"),
               (line_col(&s, at), char_to_byte(&s, n), find_all(&s, needle)), (want_lc, want_cb, want_find));
    }
}

#[test]
fn scale_1m_matches() {
    let s = "é".repeat(1_000_000);
    let got = find_all(&s, "é");
    check!("s = 1000000 × 'é', needle = \"é\"", (got.len(), got[999_999]), (1_000_000, (1_999_998, 999_999)));
    let text = "ab\n".repeat(200_000);
    check!("text = \"ab\\n\" × 200000, at the end", line_col(&text, text.len()), Some((200_001, 1)));
}
