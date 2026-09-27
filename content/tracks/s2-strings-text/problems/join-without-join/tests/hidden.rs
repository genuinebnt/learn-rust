use solution::*;

#[test]
fn join_empty() {
    let (s, n) = anneal_prelude::allocs(|| join_words(&[], "-"));
    check!(r#"words = [], sep = "-""#, (s.capacity(), n.count), (0, 0));
}

#[test]
fn join_empty_words_keep_separators() {
    check!(r#"words = ["", "", ""], sep = "-""#, join_words(&["", "", ""], "-"), "--".to_string());
}

#[test]
fn join_one_word() {
    check!(r#"words = ["solo"], sep = "-""#, join_words(&["solo"], "-"), "solo".to_string());
}

#[test]
fn join_unicode_exact_capacity() {
    let (s, n) = anneal_prelude::allocs(|| join_words(&["é", "日"], " → "));
    check!(r#"words = ["é", "日"], sep = " → ""#, (s.as_str(), s.len(), s.capacity(), n.count), ("é → 日", 10, 10, 1));
}

#[test]
fn join_empty_sep() {
    check!(r#"words = ["a", "b"], sep = """#, join_words(&["a", "b"], ""), "ab".to_string());
}

#[test]
fn squeeze_keeps_first_of_run() {
    let mut s = String::from("a\t b");
    squeeze(&mut s);
    check!(r#""a\t b""#, s, "a\tb".to_string());
}

#[test]
fn squeeze_only_spaces() {
    let mut s = String::from(" \t\n ");
    squeeze(&mut s);
    check!(r#"" \t\n ""#, s, "".to_string());
}

#[test]
fn squeeze_empty() {
    let mut s = String::from("");
    squeeze(&mut s);
    check!(r#""""#, s, "".to_string());
}

#[test]
fn squeeze_nothing_to_do() {
    let mut s = String::from("a b");
    squeeze(&mut s);
    check!(r#""a b""#, s, "a b".to_string());
}

#[test]
fn squeeze_unicode_whitespace() {
    let mut s = String::from("　a  b ");
    squeeze(&mut s);
    check!(r#""　a  b ""#, s, "a b".to_string());
}

#[test]
fn squeeze_trailing_run() {
    let mut s = String::from("x \n\n");
    squeeze(&mut s);
    check!(r#""x \n\n""#, s, "x".to_string());
}

#[test]
fn squeeze_in_place() {
    let mut s = String::from("  lots   of   space  ");
    let (ptr, cap) = (s.as_ptr(), s.capacity());
    let ((), n) = anneal_prelude::allocs(|| squeeze(&mut s));
    check!(r#""  lots   of   space  " in place"#, (s.as_str(), s.as_ptr() == ptr, s.capacity() == cap, n.count), ("lots of space", true, true, 0));
}

#[test]
fn pop_lines_in_order() {
    let mut buf = String::from("a\nb\r\n\nc");
    let (a, b, c, d) = (pop_line(&mut buf), pop_line(&mut buf), pop_line(&mut buf), pop_line(&mut buf));
    check!(r#""a\nb\r\n\nc""#, (a, b, c, d, buf.as_str()), (Some("a".to_string()), Some("b".to_string()), Some(String::new()), None, "c"));
}

#[test]
fn pop_bare_cr_kept_inside() {
    let mut buf = String::from("a\rb\n");
    check!(r#""a\rb\n""#, (pop_line(&mut buf), buf.as_str()), (Some("a\rb".to_string()), ""));
}

#[test]
fn pop_cr_without_lf_waits() {
    let mut buf = String::from("abc\r");
    check!(r#""abc\r""#, (pop_line(&mut buf), buf.as_str()), (None, "abc\r"));
}

#[test]
fn pop_unicode_line() {
    let mut buf = String::from("héllo 日本\nnext");
    check!(r#""héllo 日本\nnext""#, (pop_line(&mut buf), buf.as_str()), (Some("héllo 日本".to_string()), "next"));
}

#[test]
fn pop_empty_buffer() {
    let mut buf = String::new();
    check!(r#""""#, pop_line(&mut buf), None);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7206);
    for _ in 0..400 {
        let n = rng.below(6);
        let mut words = Vec::new();
        for _ in 0..n {
            let len = rng.below(4);
            words.push(rng.string(len, "ab日"));
        }
        let len = rng.below(3);
        let sep = rng.string(len, ",→");
        let refs: Vec<&str> = words.iter().map(|w| w.as_str()).collect();
        let mut want_join = String::new();
        for (i, w) in words.iter().enumerate() {
            if i > 0 {
                want_join += &sep;
            }
            want_join += w;
        }
        let len = rng.below(10);
        let text = rng.string(len, "a \t\né");
        let mut want_sq = String::new();
        let mut prev_space = true;
        for c in text.chars() {
            if !(c.is_whitespace() && prev_space) {
                want_sq.push(c);
            }
            prev_space = c.is_whitespace();
        }
        while want_sq.ends_with(char::is_whitespace) {
            want_sq.pop();
        }
        let mut got_sq = text.clone();
        squeeze(&mut got_sq);
        let len = rng.below(10);
        let raw = rng.string(len, "ab\r\n");
        let mut buf = raw.clone();
        let mut got_lines = Vec::new();
        while let Some(line) = pop_line(&mut buf) {
            got_lines.push(line);
        }
        let (mut want_lines, mut rest) = (Vec::new(), raw.as_str());
        while let Some(i) = rest.find('\n') {
            let line = &rest[..i];
            want_lines.push(line.strip_suffix('\r').unwrap_or(line).to_string());
            rest = &rest[i + 1..];
        }
        let got = join_words(&refs, &sep);
        check!(format!("words = {words:?}, sep = {sep:?}, squeeze {text:?}, buf = {raw:?}"),
               (got.capacity(), got, got_sq, got_lines, buf), (want_join.len(), want_join, want_sq, want_lines, rest.to_string()));
    }
}

#[test]
fn scale_500k() {
    let words = vec!["ab"; 500_000];
    let s = join_words(&words, ",");
    check!("words = [\"ab\"; 500000], sep = \",\"", (s.len(), s.capacity(), &s[..5]), (1_499_999, 1_499_999, "ab,ab"));
    let mut t = "a  \t ".repeat(200_000);
    squeeze(&mut t);
    check!("squeeze \"a  \\t a  \\t …\" (1000000 chars)", (t.len(), &t[..6]), (399_999, "a a a "));
}
