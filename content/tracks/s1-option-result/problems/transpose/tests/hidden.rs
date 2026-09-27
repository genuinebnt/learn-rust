use solution::*;

fn err<T>(s: &str) -> Result<T, std::num::ParseIntError> {
    Err(s.parse::<i64>().unwrap_err())
}

#[test]
fn empty_string_is_an_error_not_none() {
    check!(r#"parse_optional(Some(""))"#, parse_optional(Some("")).map_err(|e| e.kind().clone()), Err(std::num::IntErrorKind::Empty));
}

#[test]
fn optional_bounds() {
    check!(r#"Some("-2147483648"), Some("2147483648")"#, (parse_optional(Some("-2147483648")), parse_optional(Some("2147483648")).map_err(|e| e.kind().clone())), (Ok(Some(i32::MIN)), Err(std::num::IntErrorKind::PosOverflow)));
}

#[test]
fn optional_is_not_trimmed() {
    check!(r#"Some(" 5")"#, parse_optional(Some(" 5")).is_err(), true);
}

#[test]
fn indented_comment() {
    check!(r#""  # x" and "\t""#, (parse_line("  # x"), parse_line("\t")), (Ok(None), Ok(None)));
}

#[test]
fn no_inline_comments() {
    check!(r#""5 # five""#, parse_line("5 # five"), err("5 # five"));
}

#[test]
fn hash_inside_a_number() {
    check!(r#""-#1""#, parse_line("-#1"), err("-#1"));
}

#[test]
fn crlf_line_endings() {
    check!(r#""1\r\n2\r\n""#, parse_file("1\r\n2\r\n"), Ok(vec![1, 2]));
}

#[test]
fn only_comments() {
    check!(r##""# a\n\n  # b""##, parse_file("# a\n\n  # b"), Ok(vec![]));
}

#[test]
fn line_numbers_count_skipped_lines() {
    check!(r##""# header\n\n5\nfive""##, parse_file("# header\n\n5\nfive"), err("five").map_err(|e| (4, e)));
}

#[test]
fn first_line_bad() {
    check!(r#""x\n1""#, parse_file("x\n1"), err("x").map_err(|e| (1, e)));
}

#[test]
fn i64_bounds() {
    check!(r#""-9223372036854775808\n9223372036854775807""#, parse_file("-9223372036854775808\n9223372036854775807"), Ok(vec![i64::MIN, i64::MAX]));
}

#[test]
fn overflow_is_an_error() {
    check!(r#""1\n9223372036854775808""#, parse_file("1\n9223372036854775808").map_err(|(n, e)| (n, e.kind().clone())), Err((2, std::num::IntErrorKind::PosOverflow)));
}

#[test]
fn unicode_digits() {
    check!(r#""٣""#, parse_file("٣"), err("٣").map_err(|e| (1, e)));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7106);
    let pieces = ["1", "-4", "20", "", "  ", "# c", " #", "x", "3 ", " 9", "+2", "#1", "1#"];
    for _ in 0..400 {
        let n = rng.below(6);
        let mut lines: Vec<&str> = Vec::new();
        for _ in 0..n {
            lines.push(*rng.pick(&pieces));
        }
        let text = lines.join("\n");
        let mut want: Result<Vec<i64>, (usize, std::num::ParseIntError)> = Ok(Vec::new());
        for (i, l) in text.lines().enumerate() {
            let t = l.trim();
            if t.is_empty() || t.starts_with('#') {
                continue;
            }
            match t.parse::<i64>() {
                Ok(v) => want.as_mut().unwrap().push(v),
                Err(e) => {
                    want = Err((i + 1, e));
                    break;
                }
            }
        }
        check!(format!("text = {text:?}"), parse_file(&text), want);
        let s = if rng.bool() { Some(*rng.pick(&pieces)) } else { None };
        check!(format!("parse_optional({s:?})"), parse_optional(s), s.map(|t| t.parse::<i32>()).transpose());
    }
}

#[test]
fn scale_bad_line_at_the_end() {
    let mut text: String = (0..200_000).map(|i| if i % 3 == 0 { "# c\n".to_string() } else { format!("{i}\n") }).collect();
    let want: Vec<i64> = (0..200_000).filter(|i| i % 3 != 0).collect();
    check!("200000 lines, every third a comment", parse_file(&text), Ok(want));
    text.push_str("oops\n");
    check!("the same, then \"oops\" on line 200001", parse_file(&text).map_err(|(n, _)| n), Err(200_001));
}
