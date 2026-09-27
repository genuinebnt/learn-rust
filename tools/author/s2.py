from author import T, write_track

P = []


def rs(s: str) -> str:
    """A Rust string literal for `s` (ASCII only)."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '".to_string()'


def sub(s, old, new):
    """str.replace that fails loudly when `old` isn't there (a wrong solution that silently equals the reference)."""
    assert old in s, f"not found: {old[:60]!r}"
    return s.replace(old, new)


# ---------------------------------------------------------------- use (easy)

PATHS_SOL = r"""
        /// The extension of the last path component: "src/a.tar.gz" → Some("gz").
        /// A leading dot is part of the name (".bashrc" has none), and so is a trailing one ("notes." has none).
        pub fn extension(path: &str) -> Option<&str> {
            let name = path.rsplit_once('/').map_or(path, |(_, name)| name);
            let (stem, ext) = name.rsplit_once('.')?;
            (!stem.is_empty() && !ext.is_empty()).then_some(ext)
        }

        /// `s` without one pair of matching surrounding quotes, `"…"` or `'…'`; otherwise `s` unchanged.
        pub fn unquote(s: &str) -> &str {
            for q in ['"', '\''] {
                if let Some(inner) = s.strip_prefix(q).and_then(|rest| rest.strip_suffix(q)) {
                    return inner;
                }
            }
            s
        }

        /// Adds `key=value` to the query of `url`, in place. A `#fragment` stays at the end.
        pub fn add_param(url: &mut String, key: &str, value: &str) {
            let end = url.find('#').unwrap_or(url.len());
            let head = &url[..end];
            let sep = if !head.contains('?') {
                "?"
            } else if head.ends_with(['?', '&']) {
                ""
            } else {
                "&"
            };
            url.reserve(sep.len() + key.len() + 1 + value.len());
            let mut at = end;
            for piece in [sep, key, "=", value] {
                url.insert_str(at, piece);
                at += piece.len();
            }
        }
"""

PATHS_STARTER = r"""
        /// The extension of the last path component: "src/a.tar.gz" → Some("gz").
        /// A leading dot is part of the name (".bashrc" has none), and so is a trailing one ("notes." has none).
        pub fn extension(path: &str) -> Option<&str> {
            todo!()
        }

        /// `s` without one pair of matching surrounding quotes, `"…"` or `'…'`; otherwise `s` unchanged.
        pub fn unquote(s: &str) -> &str {
            todo!()
        }

        /// Adds `key=value` to the query of `url`, in place. A `#fragment` stays at the end.
        pub fn add_param(url: &mut String, key: &str, value: &str) {
            todo!()
        }
"""


def url_after(url, k, v):
    end = url.find("#")
    end = len(url) if end < 0 else end
    head = url[:end]
    sep = "?" if "?" not in head else ("" if head.endswith(("?", "&")) else "&")
    return url[:end] + sep + k + "=" + v + url[end:]


def ap(name, url, k, v):
    return T(name, f'url = "{url}", key = "{k}", value = "{v}"', "u", f'"{url_after(url, k, v)}".to_string()',
             setup=f'let mut u = String::from("{url}");\nadd_param(&mut u, "{k}", "{v}");')


P.append(dict(
    slug="string-vs-str", title="String vs &str: borrow the pieces", level="easy", stage="use",
    tags=["&str", "rsplit_once", "strip_prefix", "insert_str", "reserve"],
    teaches=[
        "Return `&str` when the answer is a piece of the input: no allocation, and the lifetime ties it to the input.",
        "`rsplit_once` splits at the last match; `strip_prefix`/`strip_suffix` remove exactly one occurrence, `trim_matches` removes all of them.",
        "Edit a `String` through `&mut String`: `reserve` once, then `insert_str` or `push_str`.",
    ],
    statement="""
        Three small helpers that a config or HTTP layer needs. The first two return a slice of their input;
        the third edits a `String` in place.

        - `extension(path)`: the extension of the last `/`-separated component. `"src/a.tar.gz"` → `Some("gz")`.
          A dot in a directory name doesn't count, a leading dot is part of the name (`".bashrc"` → `None`),
          and a trailing dot gives no extension (`"notes."` → `None`).
        - `unquote(s)`: `s` without **one** pair of matching surrounding quotes, `"…"` or `'…'`. Anything else is
          returned unchanged.
        - `add_param(url, key, value)`: adds `key=value` to the query string of `url`. Use `?` if the URL has no
          query yet, `&` otherwise, and no separator if the query already ends with `?` or `&`. A `#fragment`
          stays at the end, and a `?` inside the fragment doesn't start a query.
    """,
    examples=[('extension("src/a.tar.gz")', 'Some("gz")'), ("unquote(\"'it'\")", '"it"'),
              ('add_param on "http://h/p?a=1#top", "k", "v"', '"http://h/p?a=1&k=v#top"')],
    starter=PATHS_STARTER,
    solution=PATHS_SOL,
    visible=[
        T("extension_last_dot", '"src/archive.tar.gz"', 'extension("src/archive.tar.gz")', 'Some("gz")'),
        T("dotfile_has_no_extension", '".bashrc"', 'extension(".bashrc")', "None"),
        T("unquote_one_pair", '"\\"hi\\"" and "\'hi\'"', "(unquote(\"\\\"hi\\\"\"), unquote(\"'hi'\"))", '("hi", "hi")'),
        ap("first_param", "http://h/p", "k", "v"),
        ap("param_before_fragment", "http://h/p?a=1#top", "k", "v"),
    ],
    hidden=[
        T("dot_in_directory", '"v1.2/README"', 'extension("v1.2/README")', "None"),
        T("trailing_dot", '"notes."', 'extension("notes.")', "None"),
        T("hidden_file_with_extension", '"dir/.env.local"', 'extension("dir/.env.local")', 'Some("local")'),
        T("extension_edge_names", '"", "/", "..", "a/b/"', '[extension(""), extension("/"), extension(".."), extension("a/b/")]', "[None; 4]"),
        T("double_dot", '"a..b"', 'extension("a..b")', 'Some("b")'),
        T("unicode_extension", '"文書/報告.テキスト"', 'extension("文書/報告.テキスト")', 'Some("テキスト")'),
        T("extension_borrows_input", "extension points into its input", "extension(&s).map(|e| e.as_ptr()) == Some(s[4..].as_ptr())", "true",
          setup='let s = String::from("a/b.rs");'),
        T("lone_quote_is_not_a_pair", '"\\""', 'unquote("\\"")', '"\\""'),
        T("empty_quotes", '"\\"\\"" and "\'\'"', "(unquote(\"\\\"\\\"\"), unquote(\"''\"))", '("", "")'),
        T("only_one_pair_removed", '"\\"\\"a\\"\\""', 'unquote("\\"\\"a\\"\\"")', '"\\"a\\""'),
        T("mismatched_quotes", '"\\"a\'" and "\'a\\""', "(unquote(\"\\\"a'\"), unquote(\"'a\\\"\"))", "(\"\\\"a'\", \"'a\\\"\")"),
        T("inner_quotes_kept", "\"'it\\\"s'\"", "unquote(\"'it\\\"s'\")", "\"it\\\"s\""),
        T("unicode_quotes_untouched", '"«x»" and "é"', '(unquote("«x»"), unquote("é"))', '("«x»", "é")'),
        T("unquote_borrows_input", "unquote points into its input", "unquote(&s).as_ptr() == s[1..].as_ptr()", "true", setup="let s = String::from(\"'abc'\");"),
        ap("second_param", "http://h/p?a=1", "b", "2"),
        ap("query_ends_with_question_mark", "http://h/p?", "k", "v"),
        ap("query_ends_with_ampersand", "http://h/p?a=1&", "k", "v"),
        ap("question_mark_in_fragment", "http://h/p#a?b", "k", "v"),
        ap("empty_fragment", "http://h/#", "k", ""),
        ap("unicode_value", "http://h/", "q", "café"),
        T("add_twice", '"http://h" + a=1 + b=2', "u", '"http://h?a=1&b=2".to_string()',
          setup='let mut u = String::from("http://h");\nadd_param(&mut u, "a", "1");\nadd_param(&mut u, "b", "2");'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(7201);
            for _ in 0..400 {
                let len = rng.below(9);
                let path = rng.string(len, "a./é");
                let name = match path.rfind('/') {
                    Some(i) => &path[i + 1..],
                    None => &path[..],
                };
                let want_ext = match name.rfind('.') {
                    Some(i) if i > 0 && i + 1 < name.len() => Some(&name[i + 1..]),
                    _ => None,
                };
                let len = rng.below(6);
                let q = rng.string(len, "a\\"'");
                let b = q.as_bytes();
                let want_q = if b.len() >= 2 && (b[0] == b'"' || b[0] == b'\\'') && b[b.len() - 1] == b[0] { &q[1..q.len() - 1] } else { &q[..] };
                let len = rng.below(7);
                let url = rng.string(len, "h?&#=");
                let end = url.find('#').unwrap_or(url.len());
                let sep = if !url[..end].contains('?') { "?" } else if url[..end].ends_with('?') || url[..end].ends_with('&') { "" } else { "&" };
                let want_url = format!("{}{sep}k=v{}", &url[..end], &url[end..]);
                let mut got_url = url.clone();
                add_param(&mut got_url, "k", "v");
                check!(format!("path = {path:?}, s = {q:?}, url = {url:?}"), (extension(&path), unquote(&q), got_url), (want_ext, want_q, want_url));
            }
        }
        """,
    ],
    wrong=dict(
        splits_the_whole_path=sub(PATHS_SOL, "let name = path.rsplit_once('/').map_or(path, |(_, name)| name);", "let name = path;"),
        trims_every_quote=sub(PATHS_SOL, """for q in ['"', '\\''] {
                if let Some(inner) = s.strip_prefix(q).and_then(|rest| rest.strip_suffix(q)) {
                    return inner;
                }
            }
            s""", """s.trim_matches(|c| c == '"' || c == '\\'')"""),
        slices_by_hand=sub(PATHS_SOL, """for q in ['"', '\\''] {
                if let Some(inner) = s.strip_prefix(q).and_then(|rest| rest.strip_suffix(q)) {
                    return inner;
                }
            }
            s""", """let b = s.as_bytes();
            if !b.is_empty() && (b[0] == b'"' || b[0] == b'\\'') && b[b.len() - 1] == b[0] {
                return &s[1..s.len() - 1];
            }
            s"""),
        appends_after_fragment=sub(PATHS_SOL, "let end = url.find('#').unwrap_or(url.len());", "let end = url.len();"),
    ),
    hints=[("rust", "`path.rsplit_once('/')` gives the last component; `name.rsplit_once('.')` then splits off the extension. Check that neither side is empty."),
           ("rust", "`s.strip_prefix('\"').and_then(|r| r.strip_suffix('\"'))` removes exactly one quote from each end, and fails cleanly on a lone `\"`."),
           ("edge case", "`\"\\\"\"` is one character: slicing `&s[1..s.len() - 1]` is `&s[1..0]`, which panics.")],
    notes=("""Every answer that is a piece of the input is a `&str` into it: no allocation, and the signature `fn(&str) -> &str` says the result lives as long as the argument (lifetime elision). `trim_matches` is the wrong tool for quotes: it strips *every* leading and trailing match, so `""a""` loses both pairs. `add_param` works on the `String` in place: `reserve` once for the total, then `insert_str` before the fragment (which shifts only the fragment's bytes). Syntax to remember: `s.rsplit_once('/')` → `Option<(&str, &str)>` (split at the last match; `split_once` at the first), `s.strip_prefix(p)` / `strip_suffix(p)` → `Option<&str>`, `cond.then_some(v)`, `s.ends_with(['?', '&'])` (a char array is a pattern), `buf.insert_str(byte_idx, "…")`, `buf.reserve(additional)`.""", "O(n)", "O(1) extra"),
    follow_up="When is `impl Into<String>` a better parameter than `&str`, and when is `impl AsRef<str>` better than both?",
    related=["L1", "L3"],
))

CSV_SOL = r"""
        #[derive(Debug, PartialEq)]
        pub enum CsvError {
            /// Field `n` (counting from 1) is empty.
            Empty(usize),
            /// Field `n` isn't an integer; the trimmed text.
            Bad(usize, String),
            /// A running total doesn't fit in an `i64`.
            Overflow,
        }

        pub fn sum_csv(line: &str) -> Result<i64, CsvError> {
            let mut total = 0i64;
            for (i, field) in line.split_terminator(',').enumerate() {
                let field = field.trim();
                if field.is_empty() {
                    return Err(CsvError::Empty(i + 1));
                }
                let n: i64 = field.parse().map_err(|_| CsvError::Bad(i + 1, field.to_string()))?;
                total = total.checked_add(n).ok_or(CsvError::Overflow)?;
            }
            Ok(total)
        }

        #[derive(Debug, PartialEq)]
        pub struct LogLine<'a> {
            pub date: &'a str,
            pub time: &'a str,
            pub level: &'a str,
            pub message: &'a str,
            pub millis: Option<u64>,
        }

        pub fn parse_log(line: &str) -> Option<LogLine<'_>> {
            let mut parts = line.splitn(4, ' ');
            let (date, time, level) = (parts.next()?, parts.next()?, parts.next()?);
            if date.is_empty() || time.is_empty() || level.is_empty() {
                return None;
            }
            let message = parts.next().unwrap_or("");
            let millis = message
                .rsplitn(2, ' ')
                .next()
                .and_then(|word| word.strip_suffix("ms"))
                .filter(|n| !n.is_empty() && n.bytes().all(|b| b.is_ascii_digit()))
                .and_then(|n| n.parse().ok());
            Some(LogLine { date, time, level, message, millis })
        }
"""

CSV_STARTER = r"""
        #[derive(Debug, PartialEq)]
        pub enum CsvError {
            /// Field `n` (counting from 1) is empty.
            Empty(usize),
            /// Field `n` isn't an integer; the trimmed text.
            Bad(usize, String),
            /// A running total doesn't fit in an `i64`.
            Overflow,
        }

        pub fn sum_csv(line: &str) -> Result<i64, CsvError> {
            todo!()
        }

        #[derive(Debug, PartialEq)]
        pub struct LogLine<'a> {
            pub date: &'a str,
            pub time: &'a str,
            pub level: &'a str,
            pub message: &'a str,
            pub millis: Option<u64>,
        }

        pub fn parse_log(line: &str) -> Option<LogLine<'_>> {
            todo!()
        }
"""


def lg(date, time, level, message, millis):
    m = "None" if millis is None else f"Some({millis})"
    return f'Some(LogLine {{ date: "{date}", time: "{time}", level: "{level}", message: "{message}", millis: {m} }})'


P.append(dict(
    slug="split-trim-parse", title="split, trim, parse", level="easy", stage="use",
    tags=["split_terminator", "splitn", "rsplitn", "parse", "checked_add"],
    teaches=[
        "`split_terminator` forgives one trailing separator; `split` would yield an empty last field.",
        "`splitn(4, ' ')` stops splitting after three cuts, so the last piece keeps its spaces; `rsplitn` counts from the end and yields the last piece first.",
        "Errors that say where: `enumerate` + `map_err`, and `checked_add` for a total that can overflow.",
    ],
    statement="""
        **`sum_csv(line)`** adds up comma-separated integers. Fields are trimmed. A single trailing comma is
        allowed (`"1,2,"`), but any other empty field is `Empty(n)`, with fields counted from 1. A field that
        isn't an `i64` is `Bad(n, trimmed_text)`, and `Overflow` if the running total leaves `i64`. The first
        problem from the left wins. An empty line sums to 0.

        **`parse_log(line)`** splits `"<date> <time> <level> <message>"` on single spaces. The message is the
        rest of the line, spaces and all, and may be empty or missing. Date, time and level must be non-empty.
        `millis` is `Some(n)` when the message's last space-separated word is one or more ASCII digits followed
        by `ms` and `n` fits in a `u64`. The message itself is kept whole.
    """,
    examples=[('sum_csv("1, 2 ,3,")', "Ok(6)"), ('sum_csv("1,,3")', "Err(Empty(2))"),
              ('parse_log("2024-05-01 12:00:03 WARN slow query took 250ms")', 'level "WARN", message "slow query took 250ms", millis Some(250)')],
    starter=CSV_STARTER,
    solution=CSV_SOL,
    visible=[
        T("sums_trimmed_fields", '"1, 2 ,3"', 'sum_csv("1, 2 ,3")', "Ok(6)"),
        T("trailing_comma_allowed", '"1,2,"', 'sum_csv("1,2,")', "Ok(3)"),
        T("inner_empty_field", '"1,,3"', 'sum_csv("1,,3")', "Err(CsvError::Empty(2))"),
        T("bad_field_says_where", '"4, x1 ,5"', 'sum_csv("4, x1 ,5")', 'Err(CsvError::Bad(2, "x1".to_string()))'),
        T("log_message_keeps_spaces", '"2024-05-01 12:00:03 WARN slow query took 250ms"', 'parse_log("2024-05-01 12:00:03 WARN slow query took 250ms")',
          lg("2024-05-01", "12:00:03", "WARN", "slow query took 250ms", 250)),
    ],
    hidden=[
        T("empty_line", '""', 'sum_csv("")', "Ok(0)"),
        T("lone_comma", '","', 'sum_csv(",")', "Err(CsvError::Empty(1))"),
        T("two_trailing_commas", '"1,2,,"', 'sum_csv("1,2,,")', "Err(CsvError::Empty(3))"),
        T("trailing_comma_then_space", '"1,2, "', 'sum_csv("1,2, ")', "Err(CsvError::Empty(3))"),
        T("blank_field", '"   "', 'sum_csv("   ")', "Err(CsvError::Empty(1))"),
        T("first_problem_wins", '"1,x,,y"', 'sum_csv("1,x,,y")', 'Err(CsvError::Bad(2, "x".to_string()))'),
        T("float_is_bad", '"1.5"', 'sum_csv("1.5")', 'Err(CsvError::Bad(1, "1.5".to_string()))'),
        T("inner_space_is_bad", '"1 2,3"', 'sum_csv("1 2,3")', 'Err(CsvError::Bad(1, "1 2".to_string()))'),
        T("signs_and_tabs", '"\\t+5\\t,-7\\n"', 'sum_csv("\\t+5\\t,-7\\n")', "Ok(-2)"),
        T("beyond_i32", '"3000000000,3000000000"', 'sum_csv("3000000000,3000000000")', "Ok(6_000_000_000)"),
        T("i64_bounds", '"9223372036854775807,-9223372036854775808"', 'sum_csv("9223372036854775807,-9223372036854775808")', "Ok(-1)"),
        T("running_total_overflows", '"9223372036854775807,1,-1"', 'sum_csv("9223372036854775807,1,-1")', "Err(CsvError::Overflow)"),
        T("field_too_big", '"9223372036854775808"', 'sum_csv("9223372036854775808")', 'Err(CsvError::Bad(1, "9223372036854775808".to_string()))'),
        T("log_without_millis", '"d t INFO started"', 'parse_log("d t INFO started")', lg("d", "t", "INFO", "started", None)),
        T("log_missing_message", '"d t INFO"', 'parse_log("d t INFO")', lg("d", "t", "INFO", "", None)),
        T("log_empty_message", '"d t INFO "', 'parse_log("d t INFO ")', lg("d", "t", "INFO", "", None)),
        T("log_too_short", '"d t" and ""', '(parse_log("d t"), parse_log(""))', "(None, None)"),
        T("log_double_space", '"d  t INFO x" (empty time)', 'parse_log("d  t INFO x")', "None"),
        T("log_millis_only_message", '"d t DEBUG 7ms"', 'parse_log("d t DEBUG 7ms")', lg("d", "t", "DEBUG", "7ms", 7)),
        T("log_millis_must_be_last", '"d t INFO 5ms later"', 'parse_log("d t INFO 5ms later")', lg("d", "t", "INFO", "5ms later", None)),
        T("log_millis_digits_only", '"d t I x +5ms", "d t I x ms", "d t I x 5 ms"', '[parse_log("d t I x +5ms"), parse_log("d t I x ms"), parse_log("d t I x 5 ms")].map(|l| l.unwrap().millis)', "[None; 3]"),
        T("log_millis_too_big", '"d t I x 18446744073709551616ms"', 'parse_log("d t I x 18446744073709551616ms").unwrap().millis', "None"),
        T("log_millis_u64_max", '"d t I 18446744073709551615ms"', 'parse_log("d t I 18446744073709551615ms").unwrap().millis', "Some(u64::MAX)"),
        T("log_unicode_message", '"d t INFO café ☕ 3ms"', 'parse_log("d t INFO café ☕ 3ms")', lg("d", "t", "INFO", "café ☕ 3ms", 3)),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(7202);
            let pieces = ["", " ", "7", " -3 ", "12", "x", "0", "9223372036854775807"];
            for _ in 0..400 {
                let n = rng.below(6);
                let mut fields: Vec<&str> = Vec::new();
                for _ in 0..n {
                    fields.push(*rng.pick(&pieces));
                }
                let mut line = fields.join(",");
                if rng.bool() {
                    line.push(',');
                }
                let mut want = Ok(0i64);
                let mut cut: Vec<&str> = line.split(',').collect();
                if line.ends_with(',') {
                    cut.pop();
                }
                if line.is_empty() {
                    cut.clear();
                }
                for (i, f) in cut.iter().enumerate() {
                    let f = f.trim();
                    let step = if f.is_empty() {
                        Err(CsvError::Empty(i + 1))
                    } else {
                        match f.parse::<i64>() {
                            Err(_) => Err(CsvError::Bad(i + 1, f.to_string())),
                            Ok(v) => want.as_ref().ok().and_then(|t: &i64| t.checked_add(v)).ok_or(CsvError::Overflow),
                        }
                    };
                    match step {
                        Ok(t) => want = Ok(t),
                        Err(e) => {
                            want = Err(e);
                            break;
                        }
                    }
                }
                check!(format!("line = {line:?}"), sum_csv(&line), want);
            }
        }

        #[test]
        fn scale_200k_fields() {
            let line = "1, ".repeat(200_000);
            check!("line = \\"1, 1, …\\" (200000 fields, then a trailing space)", sum_csv(&line), Err(CsvError::Empty(200_001)));
            let line = "1,".repeat(200_000);
            check!("line = \\"1,1,…,\\" (200000 fields and a trailing comma)", sum_csv(&line), Ok(200_000));
        }
        """,
    ],
    wrong=dict(
        split_keeps_trailing_field=sub(CSV_SOL, "line.split_terminator(',')", "line.split(',')"),
        wrapping_total=sub(CSV_SOL, "total = total.checked_add(n).ok_or(CsvError::Overflow)?;", "total = total.wrapping_add(n);"),
        message_split_on_every_space=sub(CSV_SOL, """let mut parts = line.splitn(4, ' ');
            let (date, time, level) = (parts.next()?, parts.next()?, parts.next()?);""", """let mut parts = line.split(' ');
            let (date, time, level) = (parts.next()?, parts.next()?, parts.next()?);"""),
        rsplitn_order_misread=sub(CSV_SOL, """.rsplitn(2, ' ')
                .next()""", """.rsplitn(2, ' ')
                .last()"""),
        accepts_a_plus_sign=sub(CSV_SOL, ".filter(|n| !n.is_empty() && n.bytes().all(|b| b.is_ascii_digit()))\n", ""),
    ),
    hints=[("rust", "`\"1,2,\".split(',')` yields `[\"1\", \"2\", \"\"]`; `split_terminator(',')` yields `[\"1\", \"2\"]`, but only one trailing comma is forgiven."),
           ("rust", "`line.splitn(4, ' ')` yields at most 4 pieces; the 4th is everything after the third space. `s.rsplitn(2, ' ').next()` is the last word."),
           ("edge case", "`\"+5\".parse::<u64>()` is `Ok(5)`: check the digits yourself if a sign isn't allowed.")],
    notes=("""Both functions are one pass over borrowed pieces. `split_terminator` is `split` that forgives one trailing separator (think lines that end with `\\n`); `splitn(n, pat)` is the tool when the last field may contain the separator, and `rsplitn` counts from the right and yields right-to-left, so its first item is the *last* piece. Summing with `checked_add` makes the overflow a reported error instead of a debug-build panic or a silent wrap in release. `str::parse` for integers accepts a leading `+`, which is why the digits are checked first. Syntax to remember: `s.split_terminator(',')`, `s.splitn(4, ' ')`, `s.rsplitn(2, ' ')`, `.enumerate()`, `.map_err(|_| E::Bad(i + 1, f.to_string()))?`, `a.checked_add(b).ok_or(E::Overflow)?`, `s.bytes().all(|b| b.is_ascii_digit())`.""", "O(n)", "O(1)"),
    follow_up="Real CSV allows quoted fields that contain commas. Why does that rule out `split`, and what would a zero-copy field iterator return for a field with an escaped quote?",
    related=["S1"],
))

CSVW_SOL = r"""
        /// One CSV field. A field that contains a comma, a double quote, `\r` or `\n` is wrapped in double
        /// quotes, with each inner double quote doubled. Any other field is written as it is.
        pub fn csv_field(s: &str) -> String {
            if s.contains([',', '"', '\r', '\n']) {
                format!("\"{}\"", s.replace('"', "\"\""))
            } else {
                s.to_string()
            }
        }

        /// The fields as one CSV row, separated by commas.
        pub fn csv_row(fields: &[&str]) -> String {
            let mut row = String::new();
            for (i, f) in fields.iter().enumerate() {
                if i > 0 {
                    row.push(',');
                }
                row += &csv_field(f);
            }
            row
        }
"""

CSVW_STARTER = r"""
        /// One CSV field. A field that contains a comma, a double quote, `\r` or `\n` is wrapped in double
        /// quotes, with each inner double quote doubled. Any other field is written as it is.
        pub fn csv_field(s: &str) -> String {
            if s.contains(',') {
                '"' + s.replace('"', "\"\"") + '"'
            } else {
                s
            }
        }

        /// The fields as one CSV row, separated by commas.
        pub fn csv_row(fields: &[&str]) -> String {
            let mut row = String::new();
            for f in fields {
                if !row.is_empty() {
                    row += ',';
                }
                row = row + csv_field(f);
            }
            row
        }
"""

P.append(dict(
    slug="fix-string-plus-string", title="Fix: a CSV writer built with +", mode="fix", level="easy", stage="use",
    tags=["E0369", "E0308", "Add<&str>", "AddAssign<&str>", "CSV quoting"],
    teaches=[
        "`String + &str` is the only `+` for strings: the left side is an owned `String` (its buffer is reused), the right a `&str`. There's no `char + String` and no `+= char`.",
        "`&String` derefs to `&str`, so `row += &field` works; `row + field` with an owned `String` on the right doesn't.",
        "\"Is this the first item?\" is a question about the index, not about whether the output is empty so far.",
    ],
    statement="""
        A tiny CSV writer (RFC 4180 quoting). It doesn't compile, and once it does it still writes wrong rows.
        Make both functions match their doc comments.
    """,
    examples=[('csv_row(&["a", "b,c", "say \\"hi\\""])', '"a,\\"b,c\\",\\"say \\"\\"hi\\"\\"\\""'), ('csv_row(&["", "x"])', '",x"')],
    starter=CSVW_STARTER,
    solution=CSVW_SOL,
    visible=[
        T("plain_row", '["a", "b", "c"]', 'csv_row(&["a", "b", "c"])', '"a,b,c".to_string()'),
        T("comma_is_quoted", '"b,c"', 'csv_field("b,c")', '"\\"b,c\\"".to_string()'),
        T("quote_is_doubled", '"say \\"hi\\""', 'csv_field("say \\"hi\\"")', '"\\"say \\"\\"hi\\"\\"\\"".to_string()'),
        T("empty_first_field", '["", "x"]', 'csv_row(&["", "x"])', '",x".to_string()'),
        T("no_fields", "[]", "csv_row(&[])", "String::new()"),
    ],
    hidden=[
        T("newline_is_quoted", '"a\\nb"', 'csv_field("a\\nb")', '"\\"a\\nb\\"".to_string()'),
        T("carriage_return_is_quoted", '"a\\rb"', 'csv_field("a\\rb")', '"\\"a\\rb\\"".to_string()'),
        T("lone_quote", '"\\""', 'csv_field("\\"")', '"\\"\\"\\"\\"".to_string()'),
        T("plain_field_unchanged", '"hello world"', 'csv_field("hello world")', '"hello world".to_string()'),
        T("empty_field", '""', 'csv_field("")', "String::new()"),
        T("all_empty_fields", '["", "", ""]', 'csv_row(&["", "", ""])', '",,".to_string()'),
        T("one_empty_field", '[""]', 'csv_row(&[""])', "String::new()"),
        T("mixed_row", '["id", "a,b", "", "x\\"y"]', 'csv_row(&["id", "a,b", "", "x\\"y"])', '"id,\\"a,b\\",,\\"x\\"\\"y\\"".to_string()'),
        T("unicode_fields", '["café", "日本,語"]', 'csv_row(&["café", "日本,語"])', '"café,\\"日本,語\\"".to_string()'),
        T("single_quote_not_special", "\"it's\"", "csv_field(\"it's\")", "\"it's\".to_string()"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(7203);
            for _ in 0..400 {
                let n = rng.below(5);
                let mut fields = Vec::new();
                for _ in 0..n {
                    let len = rng.below(4);
                    fields.push(rng.string(len, "a,\\"\\né "));
                }
                let mut want = String::new();
                for (i, f) in fields.iter().enumerate() {
                    if i > 0 {
                        want.push(',');
                    }
                    if f.chars().any(|c| c == ',' || c == '"' || c == '\\n' || c == '\\r') {
                        want.push('"');
                        for c in f.chars() {
                            if c == '"' {
                                want.push('"');
                            }
                            want.push(c);
                        }
                        want.push('"');
                    } else {
                        want.push_str(f);
                    }
                }
                let refs: Vec<&str> = fields.iter().map(|f| f.as_str()).collect();
                check!(format!("fields = {fields:?}"), csv_row(&refs), want);
            }
        }

        #[test]
        fn scale_100k_fields() {
            let fields = vec!["a\\"b"; 100_000];
            let row = csv_row(&fields);
            check!("fields = [\\"a\\\\\\"b\\"; 100000]", (row.len(), &row[..13]), (100_000 * 7 - 1, "\\"a\\"\\"b\\",\\"a\\"\\"b\\""));
        }
        """,
    ],
    wrong=dict(
        only_commas_quoted=sub(CSVW_SOL, "s.contains([',', '\"', '\\r', '\\n'])", "s.contains(',')"),
        first_check_by_emptiness=sub(CSVW_SOL, """for (i, f) in fields.iter().enumerate() {
                if i > 0 {""", """for f in fields {
                if !row.is_empty() {"""),
        backslash_escapes=sub(CSVW_SOL, """s.replace('"', "\\"\\"")""", """s.replace('"', "\\\\\\"")"""),
    ),
    hints=[("rust", "`impl Add<&str> for String` is the whole story: `owned + &str`. A `char` goes in with `push`, another `String` with `+= &other`, and a mix with `format!`."),
           ("rust", "`s.contains([',', '\"', '\\r', '\\n'])`: an array of chars is a pattern that matches any of them."),
           ("edge case", "`csv_row(&[\"\", \"x\"])` must be `\",x\"`: after the first field the row is still empty.")],
    notes=("""`+` takes the left `String` by value so it can append into that buffer; the right side is only read, so it's a `&str`. That's why `'"' + s` (no `Add` for `char`), `row + csv_field(f)` (a `String` on the right) and `row += ','` (`AddAssign<&str>` only) don't compile. `&csv_field(f)` borrows the temporary as `&String`, which derefs to `&str`. The two logic bugs are the interesting part: quoting only on commas corrupts any field with a quote or newline, and `!row.is_empty()` confuses "nothing written yet" with "first field", so an empty first field loses its separator. Syntax to remember: `s.push(c)`, `s.push_str(t)`, `s += &t`, `s.contains([',', '"'])`, `s.replace('"', "\\"\\"")`, `format!("\\"{}\\"", x)`.""", "O(total length)", "O(total length)"),
    follow_up="`csv_row` allocates one `String` per field and then copies it. How would you write the quoted field straight into `row` instead?",
    rules=dict(lines=10),
))

CASE_SOL = r"""
        /// Does `input`, ignoring surrounding whitespace, name `command`, ignoring ASCII case? No allocation.
        pub fn is_command(input: &str, command: &str) -> bool {
            input.trim().eq_ignore_ascii_case(command)
        }

        /// Lower-cases an HTTP header name in place. Only ASCII letters change. No allocation.
        pub fn normalize_header(name: &mut String) {
            name.make_ascii_lowercase();
        }

        /// Each whitespace-separated word with its first character in upper case and the rest in lower case,
        /// by the full Unicode rules. Words are joined by single spaces.
        pub fn title_case(s: &str) -> String {
            let mut out = String::with_capacity(s.len());
            for word in s.split_whitespace() {
                if !out.is_empty() {
                    out.push(' ');
                }
                let mut chars = word.chars();
                if let Some(first) = chars.next() {
                    out.extend(first.to_uppercase());
                    out.push_str(&chars.as_str().to_lowercase());
                }
            }
            out
        }
"""

CASE_STARTER = r"""
        /// Does `input`, ignoring surrounding whitespace, name `command`, ignoring ASCII case? No allocation.
        pub fn is_command(input: &str, command: &str) -> bool {
            todo!()
        }

        /// Lower-cases an HTTP header name in place. Only ASCII letters change. No allocation.
        pub fn normalize_header(name: &mut String) {
            todo!()
        }

        /// Each whitespace-separated word with its first character in upper case and the rest in lower case,
        /// by the full Unicode rules. Words are joined by single spaces.
        pub fn title_case(s: &str) -> String {
            todo!()
        }
"""

P.append(dict(
    slug="compare-ignoring-case", title="Case: ASCII folding vs Unicode mapping", level="easy", stage="use",
    tags=["eq_ignore_ascii_case", "make_ascii_lowercase", "to_uppercase", "to_lowercase", "count_allocs"],
    teaches=[
        "Protocol text (commands, header names) is ASCII: `eq_ignore_ascii_case` and `make_ascii_lowercase` work in place and never allocate.",
        "Human text needs Unicode case mapping, which can change the length: `'ß'.to_uppercase()` is `\"SS\"`, so `char::to_uppercase` returns an iterator, not a `char`.",
        "`str::to_lowercase` knows context that per-char mapping doesn't: a word-final `Σ` becomes `ς`.",
    ],
    statement="""
        - `is_command(input, command)`: does `input`, with surrounding whitespace ignored, equal `command`,
          ignoring ASCII case? No allocation.
        - `normalize_header(name)`: lower-case an HTTP header name in place. Only ASCII letters change (header
          names are ASCII; leave anything else as it is). No allocation.
        - `title_case(s)`: for display. In each whitespace-separated word, the first character goes to upper
          case and the rest to lower case, by the full Unicode rules. Join the words with single spaces.
    """,
    examples=[('is_command("  QUIT\\n", "quit")', "true"), ('title_case("ÉCOLE straße")', '"École Straße"'), ('title_case("ßig")', '"SSig"')],
    starter=CASE_STARTER,
    solution=CASE_SOL,
    visible=[
        T("command_matches", '"  QUIT \\n", "quit"', 'is_command("  QUIT \\n", "quit")', "true"),
        T("prefix_is_not_the_command", '"quitter", "quit"', 'is_command("quitter", "quit")', "false"),
        T("header_lowercased", '"Content-Type"', "h", '"content-type".to_string()', setup='let mut h = String::from("Content-Type");\nnormalize_header(&mut h);'),
        T("title_accented", '"ÉCOLE maternelle"', 'title_case("ÉCOLE maternelle")', '"École Maternelle".to_string()'),
        T("title_sharp_s_expands", '"ßig"', 'title_case("ßig")', '"SSig".to_string()'),
    ],
    hidden=[
        T("command_not_unicode_folded", '"É", "é"', 'is_command("É", "é")', "false"),
        T("command_inner_space", '"qu it", "quit"', 'is_command("qu it", "quit")', "false"),
        T("command_untrimmed_command", '"QUIT", "quit "', 'is_command("QUIT", "quit ")', "false"),
        T("empty_command", '"  ", ""', 'is_command("  ", "")', "true"),
        T("command_no_allocation", 'is_command("  HeLp  ", "help")', "(ok, n.count)", "(true, 0)", setup='let (ok, n) = anneal_prelude::allocs(|| is_command("  HeLp  ", "help"));'),
        T("header_non_ascii_untouched", '"X-Ünïcode"', "h", '"x-Ünïcode".to_string()', setup='let mut h = String::from("X-Ünïcode");\nnormalize_header(&mut h);'),
        T("header_no_allocation", '"ACCEPT-ENCODING" in place', "(h.as_str(), n.count)", '("accept-encoding", 0)',
          setup='let mut h = String::from("ACCEPT-ENCODING");\nlet ((), n) = anneal_prelude::allocs(|| normalize_header(&mut h));'),
        T("title_final_sigma", '"ΟΔΟΣ ΣΑΣ"', 'title_case("ΟΔΟΣ ΣΑΣ")', '"Οδος Σας".to_string()'),
        T("title_whitespace_collapsed", '"  a\\tb \\n c  "', 'title_case("  a\\tb \\n c  ")', '"A B C".to_string()'),
        T("title_empty", '"" and "   "', '(title_case(""), title_case("   "))', "(String::new(), String::new())"),
        T("title_ligature", '"ﬁne"', 'title_case("ﬁne")', '"FIne".to_string()'),
        T("title_dotted_capital_i_in_the_rest", '"AİR"', 'title_case("AİR")', '"Ai\\u{307}r".to_string()'),
        T("title_digits_and_cjk", '"3RD 日本語"', 'title_case("3RD 日本語")', '"3rd 日本語".to_string()'),
        T("title_already_title", '"Hello World"', 'title_case("Hello World")', '"Hello World".to_string()'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(7204);
            for _ in 0..400 {
                let len = rng.below(10);
                let s = rng.string(len, "aBéÉßΣσ \\t");
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
            check!("s = \\"hELLO wORLD …\\" (200000 words)", (out.len(), &out[..12]), (1_199_999, "Hello World "));
        }
        """,
    ],
    wrong=dict(
        lowercase_allocates=sub(CASE_SOL, "input.trim().eq_ignore_ascii_case(command)", "input.trim().to_lowercase() == command.to_lowercase()"),
        header_rebuilt=sub(CASE_SOL, "name.make_ascii_lowercase();", "*name = name.to_lowercase();"),
        ascii_first_letter=sub(CASE_SOL, "out.extend(first.to_uppercase());", "out.push(first.to_ascii_uppercase());"),
        one_char_of_the_upper_case=sub(CASE_SOL, "out.extend(first.to_uppercase());", "out.extend(first.to_uppercase().next());"),
        rest_lowercased_per_char=sub(CASE_SOL, "out.push_str(&chars.as_str().to_lowercase());", "out.extend(chars.flat_map(char::to_lowercase));"),
    ),
    hints=[("rust", "`eq_ignore_ascii_case` compares without building copies; `make_ascii_lowercase` rewrites the bytes in place (ASCII case changes never change the length)."),
           ("rust", "`c.to_uppercase()` is an iterator of `char`s: `out.extend(c.to_uppercase())`. After `chars.next()`, `chars.as_str()` is the rest of the word, borrowed."),
           ("edge case", "Lower-case the rest of the word as a `&str`, not char by char: `\"ΟΔΟΣ\"` ends in a final sigma, `ς`.")],
    notes=("""Two different jobs share the word "case". Protocol identifiers are ASCII, so compare and fold them byte by byte: `eq_ignore_ascii_case`, `make_ascii_lowercase` and `to_ascii_lowercase` never allocate (except the last, which returns a copy) and never touch non-ASCII bytes. Human text needs Unicode case mapping, which is not one char to one char: `ß` → `SS`, `ﬁ` → `FI`, `İ` → `i̇` (two chars), and `Σ` lowercases to `ς` at the end of a word, which only `str::to_lowercase` knows (it looks at the neighbours). For case-insensitive *comparison* of human text you want case folding and normalisation (the `unicase` or `icu` crates), not `to_lowercase() ==`. Syntax to remember: `a.eq_ignore_ascii_case(b)`, `s.make_ascii_lowercase()` / `make_ascii_uppercase()`, `s.to_ascii_lowercase()` (new `String`), `c.to_uppercase()` → `ToUppercase` iterator, `s.to_lowercase()` → `String`, `chars.as_str()`.""", "O(n)", "O(n) for title_case, O(1) for the others"),
    follow_up="Why does `\"İ\".to_lowercase().len()` differ from `\"İ\".len()`, and what breaks if you lower-case a string and then slice it at offsets found in the original?",
    related=["S4"],
    perf=dict(allocs=True),
))


def receipt_table(rows, prec):
    nw = max((len(n) for n, _ in rows), default=0)
    vals = [f"{v:.{prec}f}" for _, v in rows]
    vw = max((len(v) for v in vals), default=0)
    return "".join(f"{n:<{nw}} | {v:>{vw}}\n" for (n, _), v in zip(rows, vals))


def rs_lit(s):
    return json_str(s) + ".to_string()"


def json_str(s):
    import json
    return json.dumps(s, ensure_ascii=False)


def register(v):
    b = v.to_bytes(4, "big")
    return f"{v:#010x} = " + "_".join(f"{x:08b}" for x in b)


def hexline(off, bs):
    h = ""
    for i, b in enumerate(bs):
        h += f"{b:02x} "
        if i == 7:
            h += " "
    a = "".join(chr(b) if 0x20 <= b < 0x7f else "." for b in bs)
    return f"{off:08x}  {h:<49} |{a}|"


def tb(name, desc, rows, prec):
    rust_rows = "&[" + ", ".join(f"({json_str(n)}, {v!r})" for n, v in rows) + "]"
    return T(name, desc, f"table({rust_rows}, {prec})", rs_lit(receipt_table(rows, prec)))


def hx(name, off, bs):
    lit = 'b"' + "".join(f"\\x{b:02x}" for b in bs) + '"'
    return T(name, f"offset {off:#x}, bytes {bytes(bs)!r}".replace('"', "'"), f"hexdump_line({off:#x}, {lit})", rs_lit(hexline(off, bs)))


FMT_SOL = r"""
        use std::fmt::Write;

        /// One line per row, each ending in '\n': the name left-aligned and padded to the longest name, " | ",
        /// then the value with `prec` decimals, right-aligned to the widest formatted value.
        pub fn table(rows: &[(&str, f64)], prec: usize) -> String {
            let name_w = rows.iter().map(|(name, _)| name.chars().count()).max().unwrap_or(0);
            let value_w = rows.iter().map(|(_, v)| format!("{v:.prec$}").len()).max().unwrap_or(0);
            let mut out = String::new();
            for (name, value) in rows {
                writeln!(out, "{name:<name_w$} | {value:>value_w$.prec$}").unwrap();
            }
            out
        }

        /// "0x" and 8 lowercase hex digits, " = ", then the 32 bits, most significant byte first, in four
        /// groups of 8 joined by '_'.
        pub fn register(value: u32) -> String {
            let [a, b, c, d] = value.to_be_bytes();
            format!("{value:#010x} = {a:08b}_{b:08b}_{c:08b}_{d:08b}")
        }

        /// One `hexdump -C` line for up to 16 bytes starting at `offset`.
        pub fn hexdump_line(offset: usize, bytes: &[u8]) -> String {
            let mut hex = String::with_capacity(49);
            for (i, b) in bytes.iter().enumerate() {
                write!(hex, "{b:02x} ").unwrap();
                if i == 7 {
                    hex.push(' ');
                }
            }
            let ascii: String = bytes.iter().map(|&b| if b.is_ascii_graphic() || b == b' ' { b as char } else { '.' }).collect();
            format!("{offset:08x}  {hex:<49} |{ascii}|")
        }
"""

FMT_STARTER = r"""
        use std::fmt::Write;

        /// One line per row, each ending in '\n': the name left-aligned and padded to the longest name, " | ",
        /// then the value with `prec` decimals, right-aligned to the widest formatted value.
        pub fn table(rows: &[(&str, f64)], prec: usize) -> String {
            todo!()
        }

        /// "0x" and 8 lowercase hex digits, " = ", then the 32 bits, most significant byte first, in four
        /// groups of 8 joined by '_'.
        pub fn register(value: u32) -> String {
            todo!()
        }

        /// One `hexdump -C` line for up to 16 bytes starting at `offset`.
        pub fn hexdump_line(offset: usize, bytes: &[u8]) -> String {
            todo!()
        }
"""

P.append(dict(
    slug="format-width-precision", title="format! specs: tables, registers, hexdump", level="easy", stage="use",
    tags=["format!", "writeln!", "{:>w$.p$}", "{:#010x}", "{:08b}", "{:02x}"],
    teaches=[
        "Widths and precisions can come from variables: `{v:>w$.p$}`. Width counts `char`s, not bytes.",
        "`{:#010x}`: `#` adds `0x` and the width 10 includes it. `{:08b}` zero-pads binary.",
        "`write!`/`writeln!` into a `String` needs `std::fmt::Write` in scope and returns a `fmt::Result`.",
    ],
    statement="""
        Three formatters. Use format specs for all the padding; no manual space counting.

        - `table(rows, prec)`: one line per row, each ending in `\\n`. The name is left-aligned and padded to the
          longest name (in characters), then `" | "`, then the value with `prec` decimals, right-aligned to the
          widest formatted value.
        - `register(value)`: `0x` and 8 lowercase hex digits, `" = "`, then the 32 bits, most significant byte
          first, as four groups of 8 joined by `_`.
        - `hexdump_line(offset, bytes)` (at most 16 bytes), as `hexdump -C` prints it: the offset as 8 hex
          digits, two spaces, then each byte as 2 lowercase hex digits and a space, with one extra space after
          the 8th byte. That hex part is padded with spaces to 49 columns. Then a space, `|`, each byte as its
          ASCII character if it's printable (graphic or a space) and `.` otherwise, and `|`.
    """,
    examples=[("table(&[(\"coffee\", 3.5), (\"tea\", 12.25)], 2)", json_str(receipt_table([("coffee", 3.5), ("tea", 12.25)], 2))),
              ("register(0xdead)", json_str(register(0xdead))),
              ('hexdump_line(0x10, b"Hi!\\n")', json_str(hexline(0x10, b"Hi!\n")))],
    starter=FMT_STARTER,
    solution=FMT_SOL,
    visible=[
        tb("table_two_rows", '[("coffee", 3.5), ("tea", 12.25)], prec 2', [("coffee", 3.5), ("tea", 12.25)], 2),
        tb("table_empty", "[], prec 2", [], 2),
        T("register_small", "0xdead", "register(0xdead)", rs_lit(register(0xdead))),
        hx("hexdump_short_line", 0x10, list(b"Hi!\n")),
        hx("hexdump_full_line", 0, list(b"0123456789abcdef")),
    ],
    hidden=[
        tb("table_unicode_names", '[("crème", 1.0), ("tea", 2.0)], prec 1: width in chars', [("crème", 1.0), ("tea", 2.0)], 1),
        tb("table_negative_value", '[("in", 10.0), ("out", -3.75)], prec 2', [("in", 10.0), ("out", -3.75)], 2),
        tb("table_prec_zero", '[("a", 3.25), ("bb", 100.0)], prec 0', [("a", 3.25), ("bb", 100.0)], 0),
        tb("table_prec_four", '[("pi", 3.14159265)], prec 4', [("pi", 3.14159265)], 4),
        tb("table_empty_name", '[("", 1.0), ("x", 22.5)], prec 1', [("", 1.0), ("x", 22.5)], 1),
        T("table_cjk_name", '[("日本", 1.0), ("abc", 1.0)], prec 0', 'table(&[("日本", 1.0), ("abc", 1.0)], 0)', '"日本  | 1\\nabc | 1\\n".to_string()'),
        T("register_zero_and_max", "0 and u32::MAX", "(register(0), register(u32::MAX))", f"({rs_lit(register(0))}, {rs_lit(register(0xffffffff))})"),
        T("register_byte_order", "0x01020304", "register(0x0102_0304)", rs_lit(register(0x01020304))),
        T("register_high_bit", "0x80000001", "register(0x8000_0001)", rs_lit(register(0x80000001))),
        hx("hexdump_empty", 0x20, []),
        hx("hexdump_eight_bytes", 0x8, list(b"ABCDEFGH")),
        hx("hexdump_nine_bytes", 0x8, list(b"ABCDEFGHI")),
        hx("hexdump_control_and_high_bytes", 0xFF, [0, 9, 0x1f, 0x7f, 0x80, 0xc3, 0xa9, 0xff, 0x20, 0x7e]),
        hx("hexdump_large_offset", 0x12345678, list(b"z")),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(7205);
            for _ in 0..300 {
                let n = rng.below(5);
                let mut names = Vec::new();
                let mut values = Vec::new();
                for _ in 0..n {
                    let len = rng.below(6);
                    names.push(rng.string(len, "abé日"));
                    values.push(rng.int(-100_000, 1_000_000) as f64 / 64.0);
                }
                let prec = rng.below(4);
                let rows: Vec<(&str, f64)> = names.iter().map(|s| s.as_str()).zip(values.iter().copied()).collect();
                let shown: Vec<String> = values.iter().map(|v| format!("{v:.prec$}")).collect();
                let nw = names.iter().map(|s| s.chars().count()).max().unwrap_or(0);
                let vw = shown.iter().map(|s| s.len()).max().unwrap_or(0);
                let mut want = String::new();
                for (name, v) in names.iter().zip(&shown) {
                    want += name;
                    want += &" ".repeat(nw - name.chars().count());
                    want += " | ";
                    want += &" ".repeat(vw - v.len());
                    want += v;
                    want.push('\\n');
                }
                let value = rng.next_u64() as u32;
                let mut reg = String::from("0x");
                for shift in (0..8).rev() {
                    reg.push(char::from_digit((value >> (shift * 4)) & 0xf, 16).unwrap());
                }
                reg += " = ";
                for bit in (0..32).rev() {
                    reg.push(if value >> bit & 1 == 1 { '1' } else { '0' });
                    if bit % 8 == 0 && bit > 0 {
                        reg.push('_');
                    }
                }
                let len = rng.below(17);
                let bytes: Vec<u8> = rng.vec(len, 0, 255);
                let offset = rng.below(1 << 20);
                let mut line = String::new();
                for shift in (0..8).rev() {
                    line.push(char::from_digit(((offset >> (shift * 4)) & 0xf) as u32, 16).unwrap());
                }
                line += "  ";
                let mut hex = String::new();
                for (i, b) in bytes.iter().enumerate() {
                    hex.push(char::from_digit((b >> 4) as u32, 16).unwrap());
                    hex.push(char::from_digit((b & 0xf) as u32, 16).unwrap());
                    hex.push(' ');
                    if i == 7 {
                        hex.push(' ');
                    }
                }
                while hex.len() < 49 {
                    hex.push(' ');
                }
                line += &hex;
                line += " |";
                for &b in &bytes {
                    line.push(if (0x20..0x7f).contains(&b) { b as char } else { '.' });
                }
                line.push('|');
                check!(format!("rows = {rows:?}, prec = {prec}, value = {value}, offset = {offset}, bytes = {bytes:?}"),
                       (table(&rows, prec), register(value), hexdump_line(offset, &bytes)), (want, reg, line));
            }
        }
        """,
    ],
    wrong=dict(
        width_in_bytes=sub(FMT_SOL, "name.chars().count()", "name.len()"),
        width_excludes_prefix=sub(FMT_SOL, "{value:#010x}", "{value:#08x}"),
        little_endian_bytes=sub(FMT_SOL, "value.to_be_bytes()", "value.to_le_bytes()"),
        hex_not_zero_padded=sub(FMT_SOL, 'write!(hex, "{b:02x} ")', 'write!(hex, "{b:x} ")'),
        latin1_ascii_column=sub(FMT_SOL, "if b.is_ascii_graphic() || b == b' ' { b as char } else { '.' }", "if b.is_ascii_control() { '.' } else { b as char }"),
    ),
    hints=[("rust", "`{name:<name_w$}` and `{value:>value_w$.prec$}` take the width and precision from variables. The widest value is the longest `format!(\"{v:.prec$}\")`."),
           ("rust", "`use std::fmt::Write;` then `writeln!(out, \"…\").unwrap()` (it can't fail on a `String`, but returns a `fmt::Result`). `value.to_be_bytes()` gives the bytes most significant first; `{a:08b}` prints one as 8 binary digits."),
           ("edge case", "`b as char` on a byte ≥ 0x80 gives a Latin-1 character like `é`, which is two bytes of UTF-8. Only ASCII graphic bytes and space are shown.")],
    notes=("""The format mini-language does all of it: `<`/`>`/`^` align, the number after them is a minimum width (in `char`s), `.p` is precision for floats (and truncation for strings), `0` pads numbers with zeros after the sign, `#` adds `0x`/`0b` and counts toward the width. `name$` takes an argument by name, so runtime widths need no string building. `write!` into a `String` goes through `fmt::Write`, which conflicts with `io::Write` if both are imported by name (import one `as _`). Syntax to remember: `{:<8}` `{:>8.2}` `{:^8}` `{:*>8}`, `{v:>w$.p$}`, `{:#010x}` `{:08b}` `{:02X}` `{:e}` `{:+}`, positional `{0} {1} {0}`, named `format!(\"{n}\", n = x)`, `{:?}` / `{:#?}`, `use std::fmt::Write; write!(s, …)?`.""", "O(total output)", "O(total output)"),
    follow_up="`format!(\"{v:.prec$}\")` allocates once per row just to measure the width. How would you measure it without allocating?",
    related=["L4"],
))

JOIN_SOL = r"""
        /// `words` joined by `sep`, in one allocation of exactly the final size.
        pub fn join_words(words: &[&str], sep: &str) -> String {
            let len = words.iter().map(|w| w.len()).sum::<usize>() + sep.len() * words.len().saturating_sub(1);
            let mut out = String::with_capacity(len);
            for (i, w) in words.iter().enumerate() {
                if i > 0 {
                    out.push_str(sep);
                }
                out.push_str(w);
            }
            out
        }

        /// Drops leading and trailing whitespace, and in each inner run of whitespace keeps only its first
        /// character. In place, no allocation.
        pub fn squeeze(s: &mut String) {
            let mut after_space = true;
            s.retain(|c| {
                let space = c.is_whitespace();
                let keep = !(space && after_space);
                after_space = space;
                keep
            });
            let end = s.trim_end().len();
            s.truncate(end);
        }

        /// Removes the first complete line from `buf` and returns it without its "\n" or "\r\n".
        /// `None`, with `buf` unchanged, when `buf` holds no '\n' yet.
        pub fn pop_line(buf: &mut String) -> Option<String> {
            let nl = buf.find('\n')?;
            let mut line: String = buf.drain(..=nl).collect();
            line.pop();
            if line.ends_with('\r') {
                line.pop();
            }
            Some(line)
        }
"""

JOIN_STARTER = r"""
        /// `words` joined by `sep`, in one allocation of exactly the final size.
        pub fn join_words(words: &[&str], sep: &str) -> String {
            todo!()
        }

        /// Drops leading and trailing whitespace, and in each inner run of whitespace keeps only its first
        /// character. In place, no allocation.
        pub fn squeeze(s: &mut String) {
            todo!()
        }

        /// Removes the first complete line from `buf` and returns it without its "\n" or "\r\n".
        /// `None`, with `buf` unchanged, when `buf` holds no '\n' yet.
        pub fn pop_line(buf: &mut String) -> Option<String> {
            todo!()
        }
"""


def sq(name, s, want):
    return T(name, json_str(s), "s", rs_lit(want), setup=f"let mut s = String::from({json_str(s)});\nsqueeze(&mut s);")


P.append(dict(
    slug="join-without-join", title="One allocation, then edit in place", level="easy", stage="use",
    tags=["with_capacity", "retain", "drain", "truncate", "count_allocs"],
    teaches=[
        "`String::with_capacity(exact)` when the final length is known: one allocation, then only copies.",
        "`String::retain` with a stateful closure edits in place; `truncate` after `trim_end().len()` drops the tail.",
        "`drain(..=i)` removes a prefix and hands it back, and shifts everything after it: fine for a small buffer, quadratic for a whole file.",
    ],
    statement="""
        - `join_words(words, sep)`: `words` with `sep` between them, without `join`, `concat`, `collect` or
          `fold`, in **one** allocation of exactly the final size (an empty result allocates nothing).
        - `squeeze(s)`: drop leading and trailing whitespace, and in each inner run of whitespace keep only its
          first character (`"a \\t b"` → `"a b"`, `"a\\t b"` → `"a\\tb"`). In place, no allocation.
        - `pop_line(buf)`: `buf` is a network read buffer. Remove the first complete line and return it
          without its `\\n` or `\\r\\n`; the rest stays in `buf`. If `buf` holds no `\\n` yet, return `None`
          and leave `buf` as it is.
    """,
    examples=[('join_words(&["a", "bc", "d"], ", ")', '"a, bc, d"'), ('squeeze on "  a \\t b  "', '"a b"'),
              ('pop_line on "GET /\\r\\nHost: x\\r\\npart"', 'Some("GET /"), then buf = "Host: x\\r\\npart"')],
    starter=JOIN_STARTER,
    solution=JOIN_SOL,
    visible=[
        T("join_three", 'words = ["a", "bc", "d"], sep = ", "', 'join_words(&["a", "bc", "d"], ", ")', rs("a, bc, d")),
        T("join_one_allocation", 'words = ["abc"; 10], sep = ", "', "(s.len(), s.capacity(), n.count)", "(48, 48, 1)",
          setup='let (s, n) = anneal_prelude::allocs(|| join_words(&["abc"; 10], ", "));'),
        sq("squeeze_runs", "  a \t b  c ", "a b c"),
        T("pop_crlf_line", '"GET /\\r\\nHost: x\\r\\npart"', "(first, buf.as_str())", '(Some("GET /".to_string()), "Host: x\\r\\npart")',
          setup='let mut buf = String::from("GET /\\r\\nHost: x\\r\\npart");\nlet first = pop_line(&mut buf);'),
        T("pop_incomplete_line", '"partial"', "(pop_line(&mut buf), buf.as_str())", '(None, "partial")', setup='let mut buf = String::from("partial");'),
    ],
    hidden=[
        T("join_empty", 'words = [], sep = "-"', "(s.capacity(), n.count)", "(0, 0)", setup='let (s, n) = anneal_prelude::allocs(|| join_words(&[], "-"));'),
        T("join_empty_words_keep_separators", 'words = ["", "", ""], sep = "-"', 'join_words(&["", "", ""], "-")', rs("--")),
        T("join_one_word", 'words = ["solo"], sep = "-"', 'join_words(&["solo"], "-")', rs("solo")),
        T("join_unicode_exact_capacity", 'words = ["é", "日"], sep = " → "', "(s.as_str(), s.len(), s.capacity(), n.count)", '("é → 日", 10, 10, 1)',
          setup='let (s, n) = anneal_prelude::allocs(|| join_words(&["é", "日"], " → "));'),
        T("join_empty_sep", 'words = ["a", "b"], sep = ""', 'join_words(&["a", "b"], "")', rs("ab")),
        sq("squeeze_keeps_first_of_run", "a\t b", "a\tb"),
        sq("squeeze_only_spaces", " \t\n ", ""),
        sq("squeeze_empty", "", ""),
        sq("squeeze_nothing_to_do", "a b", "a b"),
        sq("squeeze_unicode_whitespace", "\u3000a\u00a0\u00a0b\u2003", "a\u00a0b"),
        sq("squeeze_trailing_run", "x \n\n", "x"),
        T("squeeze_in_place", '"  lots   of   space  " in place', "(s.as_str(), s.as_ptr() == ptr, s.capacity() == cap, n.count)", '("lots of space", true, true, 0)',
          setup='let mut s = String::from("  lots   of   space  ");\nlet (ptr, cap) = (s.as_ptr(), s.capacity());\nlet ((), n) = anneal_prelude::allocs(|| squeeze(&mut s));'),
        T("pop_lines_in_order", '"a\\nb\\r\\n\\nc"', "(a, b, c, d, buf.as_str())", '(Some("a".to_string()), Some("b".to_string()), Some(String::new()), None, "c")',
          setup='let mut buf = String::from("a\\nb\\r\\n\\nc");\nlet (a, b, c, d) = (pop_line(&mut buf), pop_line(&mut buf), pop_line(&mut buf), pop_line(&mut buf));'),
        T("pop_bare_cr_kept_inside", '"a\\rb\\n"', "(pop_line(&mut buf), buf.as_str())", '(Some("a\\rb".to_string()), "")', setup='let mut buf = String::from("a\\rb\\n");'),
        T("pop_cr_without_lf_waits", '"abc\\r"', "(pop_line(&mut buf), buf.as_str())", '(None, "abc\\r")', setup='let mut buf = String::from("abc\\r");'),
        T("pop_unicode_line", '"héllo 日本\\nnext"', "(pop_line(&mut buf), buf.as_str())", '(Some("héllo 日本".to_string()), "next")', setup='let mut buf = String::from("héllo 日本\\nnext");'),
        T("pop_empty_buffer", '""', "pop_line(&mut buf)", "None", setup="let mut buf = String::new();"),
        """
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
                let text = rng.string(len, "a \\t\\né");
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
                let raw = rng.string(len, "ab\\r\\n");
                let mut buf = raw.clone();
                let mut got_lines = Vec::new();
                while let Some(line) = pop_line(&mut buf) {
                    got_lines.push(line);
                }
                let (mut want_lines, mut rest) = (Vec::new(), raw.as_str());
                while let Some(i) = rest.find('\\n') {
                    let line = &rest[..i];
                    want_lines.push(line.strip_suffix('\\r').unwrap_or(line).to_string());
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
            check!("words = [\\"ab\\"; 500000], sep = \\",\\"", (s.len(), s.capacity(), &s[..5]), (1_499_999, 1_499_999, "ab,ab"));
            let mut t = "a  \\t ".repeat(200_000);
            squeeze(&mut t);
            check!("squeeze \\"a  \\\\t a  \\\\t …\\" (1000000 chars)", (t.len(), &t[..6]), (399_999, "a a a "));
        }
        """,
    ],
    wrong=dict(
        grows_as_it_goes=sub(JOIN_SOL, "let mut out = String::with_capacity(len);", "let _ = len;\n            let mut out = String::new();"),
        squeeze_rebuilds=sub(JOIN_SOL, """let mut after_space = true;
            s.retain(|c| {
                let space = c.is_whitespace();
                let keep = !(space && after_space);
                after_space = space;
                keep
            });
            let end = s.trim_end().len();
            s.truncate(end);""", """let mut out = String::with_capacity(s.len());
            let mut after_space = true;
            for c in s.chars() {
                if !(c.is_whitespace() && after_space) {
                    out.push(c);
                }
                after_space = c.is_whitespace();
            }
            let end = out.trim_end().len();
            out.truncate(end);
            *s = out;"""),
        squeeze_keeps_one_leading=sub(JOIN_SOL, "let mut after_space = true;", "let mut after_space = false;"),
        newline_left_in_buffer=sub(JOIN_SOL, """let mut line: String = buf.drain(..=nl).collect();
            line.pop();""", """let mut line: String = buf.drain(..nl).collect();"""),
        cr_not_stripped=sub(JOIN_SOL, """if line.ends_with('\\r') {
                line.pop();
            }""", ""),
    ),
    hints=[("approach", "The joined length is the sum of the word lengths plus one separator between each pair (none for 0 or 1 words)."),
           ("rust", "`s.retain(|c| …)` visits each `char` once, in order, and the closure is `FnMut`, so it can remember whether the previous char was whitespace. Then `s.truncate(s.trim_end().len())`."),
           ("rust", "`buf.drain(..=nl)` removes bytes `0..=nl` and yields them as `char`s; `collect::<String>()` gathers them.")],
    notes=("""Lengths are bytes, which is what `String` capacity counts, so the separator count times `sep.len()` is exact for any text. `retain` and `truncate` rewrite the buffer in place: the pointer and capacity don't change. `drain(..=nl)` is the idiomatic "take a prefix", but it moves every remaining byte to the front, so popping every line of an n-byte buffer this way is O(n²). That's fine for a socket buffer that holds a few lines; for a whole file, keep a read offset (or use `BufRead::read_line`). Syntax to remember: `String::with_capacity(n)`, `s.retain(|c| keep)`, `s.truncate(byte_len)`, `s.drain(range)` (yields `char`s; the range is in bytes and must be on char boundaries), `s.split_off(at)` (returns the tail), `s.clear()` (keeps the capacity).""", "O(total length)", "O(total length) for join_words, O(1) extra for squeeze"),
    follow_up="How does `[&str]::join` compute its capacity, and why can `pop_line` not return a `&str` into `buf`?",
    perf=dict(allocs=True),
))

P.append(dict(
    slug="word-frequency", title="Word frequency", level="easy", stage="use",
    tags=["BufRead", "io::Result", "HashMap"], source="W22",
    teaches=["Reading lines from any `BufRead`, propagating `io::Error` with `?`.", "`trim_matches` with a closure to strip punctuation."],
    statement="""
        Count the words read from `input`. A word is a whitespace-separated piece with leading and trailing
        non-alphanumeric characters stripped, lowercased; pieces that end up empty don't count.

        Return `(word, count)` pairs sorted by count descending, then alphabetically. Invalid UTF-8 in the
        input is an error, not a panic.
    """,
    examples=[('"The cat. the DOG!\\ncat"', '[("cat", 2), ("the", 2), ("dog", 1)]')],
    starter="""
        use std::collections::HashMap;
        use std::io::{self, BufRead};

        pub fn word_frequencies<R: BufRead>(input: R) -> io::Result<Vec<(String, u32)>> {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashMap;
        use std::io::{self, BufRead};

        pub fn word_frequencies<R: BufRead>(input: R) -> io::Result<Vec<(String, u32)>> {
            let mut counts: HashMap<String, u32> = HashMap::new();
            for line in input.lines() {
                let line = line?;
                for raw in line.split_whitespace() {
                    let word = raw.trim_matches(|c: char| !c.is_alphanumeric());
                    if !word.is_empty() {
                        *counts.entry(word.to_lowercase()).or_insert(0) += 1;
                    }
                }
            }
            let mut pairs: Vec<(String, u32)> = counts.into_iter().collect();
            pairs.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));
            Ok(pairs)
        }
    """,
    visible=[
        T("counts", '"The cat. the DOG!\\ncat"', 'word_frequencies("The cat. the DOG!\\ncat".as_bytes()).unwrap()',
          'vec![("cat".to_string(), 2), ("the".to_string(), 2), ("dog".to_string(), 1)]'),
        T("empty", '""', 'word_frequencies("".as_bytes()).unwrap().len()', "0"),
        T("leetcode_692_first", '"i love leetcode i love coding"', 'word_frequencies("i love leetcode i love coding".as_bytes()).unwrap()',
          'vec![("i".to_string(), 2), ("love".to_string(), 2), ("coding".to_string(), 1), ("leetcode".to_string(), 1)]'),
        T("leetcode_692_second", '"the day is sunny the the the sunny is is"', 'word_frequencies("the day is sunny the the the sunny is is".as_bytes()).unwrap()',
          'vec![("the".to_string(), 4), ("is".to_string(), 3), ("sunny".to_string(), 2), ("day".to_string(), 1)]'),
        T("punctuation_stripped", '"(hi) hi! HI"', 'word_frequencies("(hi) hi! HI".as_bytes()).unwrap()', 'vec![("hi".to_string(), 3)]'),
    ],
    hidden=[
        T("invalid_utf8", 'b"ok \\xff"', 'word_frequencies(&b"ok \\xff"[..]).is_err()', "true"),
        T("punctuation_only", '"-- !! ..."', 'word_frequencies("-- !! ...".as_bytes()).unwrap().len()', "0"),
        T("inner_punctuation_kept", '"don\'t Don\'t"', 'word_frequencies("don\'t Don\'t".as_bytes()).unwrap()', 'vec![("don\'t".to_string(), 2)]'),
        T("unicode_lowercase", '"École école ÉCOLE"', 'word_frequencies("École école ÉCOLE".as_bytes()).unwrap()', 'vec![("école".to_string(), 3)]'),
        T("unicode_punctuation", '"«mot» ¡hola!"', 'word_frequencies("«mot» ¡hola!".as_bytes()).unwrap()', 'vec![("hola".to_string(), 1), ("mot".to_string(), 1)]'),
        T("digits_are_words", '"42 42 x"', 'word_frequencies("42 42 x".as_bytes()).unwrap()', 'vec![("42".to_string(), 2), ("x".to_string(), 1)]'),
        T("crlf_and_blank_lines", '"a\\r\\n\\r\\nb a\\n"', 'word_frequencies("a\\r\\n\\r\\nb a\\n".as_bytes()).unwrap()', 'vec![("a".to_string(), 2), ("b".to_string(), 1)]'),
        T("hyphen_inside_kept", '"well-known -well- known"', 'word_frequencies("well-known -well- known".as_bytes()).unwrap()', 'vec![("known".to_string(), 1), ("well".to_string(), 1), ("well-known".to_string(), 1)]'),
        T("invalid_utf8_later_line", 'b"fine\\nbad \\xc3\\x28"', 'word_frequencies(&b"fine\\nbad \\xc3\\x28"[..]).is_err()', "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2207);
            // Each piece and the word it counts as (None: it doesn't count).
            let pieces = [("Cat", Some("cat")), ("cat", Some("cat")), ("dog", Some("dog")), ("DOG!", Some("dog")), ("(cat)", Some("cat")),
                          ("--", None), ("bird.", Some("bird")), ("Émile", Some("émile")), ("b", Some("b"))];
            for _ in 0..300 {
                let n = rng.below(12);
                let mut text = String::new();
                let mut counts = std::collections::BTreeMap::new();
                for _ in 0..n {
                    let (piece, word) = *rng.pick(&pieces);
                    text.push_str(piece);
                    text.push_str(*rng.pick(&[" ", "\\n", "  "]));
                    if let Some(w) = word {
                        *counts.entry(w.to_string()).or_insert(0u32) += 1;
                    }
                }
                let mut want: Vec<(String, u32)> = counts.into_iter().collect();
                want.sort_by(|a, b| b.1.cmp(&a.1));
                check!(format!("input = {text:?}"), word_frequencies(text.as_bytes()).unwrap(), want);
            }
        }

        #[test]
        fn scale_50k_distinct() {
            let mut text = String::new();
            for _ in 0..4 {
                for i in 0..50_000 {
                    text.push_str(&format!("w{i:05} "));
                }
                text.push('\\n');
            }
            let out = word_frequencies(text.as_bytes()).unwrap();
            check!("w00000 … w49999, each 4 times (200000 words)", (out.len(), out[0].clone(), out[49_999].clone()), (50_000, ("w00000".to_string(), 4), ("w49999".to_string(), 4)));
        }
        """,
    ],
    wrong=dict(
        no_tiebreak="""
            use std::collections::HashMap;
            use std::io::{self, BufRead};

            pub fn word_frequencies<R: BufRead>(input: R) -> io::Result<Vec<(String, u32)>> {
                let mut counts: HashMap<String, u32> = HashMap::new();
                for line in input.lines() {
                    let line = line?;
                    for raw in line.split_whitespace() {
                        let word = raw.trim_matches(|c: char| !c.is_alphanumeric());
                        if !word.is_empty() {
                            *counts.entry(word.to_lowercase()).or_insert(0) += 1;
                        }
                    }
                }
                let mut pairs: Vec<(String, u32)> = counts.into_iter().collect();
                pairs.sort_by(|a, b| b.1.cmp(&a.1));
                Ok(pairs)
            }
        """,
        ascii_punctuation_only="""
            use std::collections::HashMap;
            use std::io::{self, BufRead};

            pub fn word_frequencies<R: BufRead>(input: R) -> io::Result<Vec<(String, u32)>> {
                let mut counts: HashMap<String, u32> = HashMap::new();
                for line in input.lines() {
                    let line = line?;
                    for raw in line.split_whitespace() {
                        let word = raw.trim_matches(|c: char| c.is_ascii_punctuation());
                        if !word.is_empty() {
                            *counts.entry(word.to_lowercase()).or_insert(0) += 1;
                        }
                    }
                }
                let mut pairs: Vec<(String, u32)> = counts.into_iter().collect();
                pairs.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));
                Ok(pairs)
            }
        """,
        linear_search="""
            use std::io::{self, BufRead};

            pub fn word_frequencies<R: BufRead>(input: R) -> io::Result<Vec<(String, u32)>> {
                let mut pairs: Vec<(String, u32)> = Vec::new();
                for line in input.lines() {
                    let line = line?;
                    for raw in line.split_whitespace() {
                        let word = raw.trim_matches(|c: char| !c.is_alphanumeric()).to_lowercase();
                        if word.is_empty() {
                            continue;
                        }
                        match pairs.iter().position(|(w, _)| *w == word) {
                            Some(i) => pairs[i].1 += 1,
                            None => pairs.push((word, 1)),
                        }
                    }
                }
                pairs.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));
                Ok(pairs)
            }
        """,
    ),
    hints=[("rust", "`BufRead::lines()` yields `io::Result<String>`; `let line = line?;` propagates a read or UTF-8 error."),
           ("rust", "`raw.trim_matches(|c: char| !c.is_alphanumeric())` strips punctuation from both ends only."),
           ("rust", "Sort with `b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0))` for count-descending, then alphabetical.")],
    notes=("Taking `R: BufRead` means the same code reads a file, stdin or a byte slice in tests. Memory grows with the number of distinct words, not the input size. `lines()` allocates a fresh `String` per line; a hot loop would reuse one buffer with `read_line(&mut buf)` and `buf.clear()`. Syntax to remember: `for line in input.lines() { let line = line?; … }`, `raw.trim_matches(|c: char| !c.is_alphanumeric())`, `*map.entry(k).or_insert(0) += 1`, `v.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)))`.", "O(n + k log k)", "O(k)"),
    follow_up="How would you find the top 10 words without sorting all k of them?",
    related=["S4", "S1"],
))

# ---------------------------------------------------------------- understand (medium)

LC_SOL = r"""
        /// 1-based (line, column) of byte offset `at` in `src`, with the column counted in chars.
        /// `at == src.len()` is the end of the text. `None` when `at` is past the end or inside a character.
        pub fn line_col(src: &str, at: usize) -> Option<(usize, usize)> {
            let before = src.get(..at)?;
            let line_start = before.rfind('\n').map_or(0, |i| i + 1);
            let line = before.matches('\n').count() + 1;
            Some((line, before[line_start..].chars().count() + 1))
        }

        /// The byte offset where char `n` starts, `s.len()` when `n` is the number of chars, `None` beyond that.
        pub fn char_to_byte(s: &str, n: usize) -> Option<usize> {
            s.char_indices().map(|(i, _)| i).chain(std::iter::once(s.len())).nth(n)
        }

        /// Every non-overlapping occurrence of `needle` (never empty), left to right, as (byte offset, char offset).
        pub fn find_all(s: &str, needle: &str) -> Vec<(usize, usize)> {
            let mut out = Vec::new();
            let (mut byte, mut chars) = (0, 0);
            for (i, _) in s.match_indices(needle) {
                chars += s[byte..i].chars().count();
                byte = i;
                out.push((i, chars));
            }
            out
        }
"""

LC_STARTER = r"""
        /// 1-based (line, column) of byte offset `at` in `src`, with the column counted in chars.
        /// `at == src.len()` is the end of the text. `None` when `at` is past the end or inside a character.
        pub fn line_col(src: &str, at: usize) -> Option<(usize, usize)> {
            todo!()
        }

        /// The byte offset where char `n` starts, `s.len()` when `n` is the number of chars, `None` beyond that.
        pub fn char_to_byte(s: &str, n: usize) -> Option<usize> {
            todo!()
        }

        /// Every non-overlapping occurrence of `needle` (never empty), left to right, as (byte offset, char offset).
        pub fn find_all(s: &str, needle: &str) -> Vec<(usize, usize)> {
            todo!()
        }
"""

P.append(dict(
    slug="bytes-chars-char-indices", title="Bytes vs chars: positions in source text", level="medium", stage="understand",
    tags=["char_indices", "match_indices", "str::get", "bytes", "UTF-8"],
    teaches=[
        "A compiler error carries a byte offset; an editor wants a line and a column in characters. Converting takes a scan, because UTF-8 has no random access by char.",
        "`s.get(..at)` returns `None` off a char boundary where `&s[..at]` panics.",
        "Scanning bytes for an ASCII byte like `\\n` is safe in UTF-8: no byte of a multi-byte character is below 0x80.",
        "`match_indices` finds non-overlapping matches; converting each to a char offset incrementally keeps it linear.",
    ],
    statement="""
        Byte offsets are what `str` methods return; people count characters. Write the conversions an error
        reporter needs:

        - `line_col(src, at)`: the 1-based line and column of byte offset `at`, with the column counted in
          characters. `at == src.len()` is valid (the end of the text). Return `None` when `at` is past the end or
          falls inside a character. Lines end at `\\n`; a `\\r` is an ordinary character.
        - `char_to_byte(s, n)`: the byte offset where character `n` (0-based) starts, `s.len()` when `n` equals
          the number of characters, and `None` beyond that.
        - `find_all(s, needle)`: every non-overlapping occurrence of the non-empty `needle`, left to right, as
          `(byte offset, char offset)`. It must stay linear in `s.len()`.
    """,
    examples=[('line_col("ab\\ncdé\\nf", 8)', "Some((3, 1))"), ('line_col("héllo", 2)', "None (inside 'é')"),
              ('find_all("é-é-é", "é")', "[(0, 0), (3, 2), (6, 4)]")],
    starter=LC_STARTER,
    solution=LC_SOL,
    visible=[
        T("line_and_column", '"ab\\ncdé\\nf", at 7 and 8', '(line_col("ab\\ncdé\\nf", 7), line_col("ab\\ncdé\\nf", 8))', "(Some((2, 4)), Some((3, 1)))"),
        T("inside_a_char", '"héllo", 2', 'line_col("héllo", 2)', "None"),
        T("char_to_byte_and_end", '"héllo", n = 2, 5, 6', '(char_to_byte("héllo", 2), char_to_byte("héllo", 5), char_to_byte("héllo", 6))', "(Some(3), Some(6), None)"),
        T("matches_do_not_overlap", '"aaaa", "aa"', 'find_all("aaaa", "aa")', "vec![(0, 0), (2, 2)]"),
        T("byte_and_char_offsets", '"é-é-é", "é"', 'find_all("é-é-é", "é")', "vec![(0, 0), (3, 2), (6, 4)]"),
    ],
    hidden=[
        T("empty_text", '"", 0 and 1', '(line_col("", 0), line_col("", 1))', "(Some((1, 1)), None)"),
        T("end_of_text", '"abc", 3 and 4', '(line_col("abc", 3), line_col("abc", 4))', "(Some((1, 4)), None)"),
        T("just_after_newline", '"a\\n", 2', 'line_col("a\\n", 2)', "Some((2, 1))"),
        T("carriage_return_is_a_column", '"a\\r\\nb", 2 and 3', '(line_col("a\\r\\nb", 2), line_col("a\\r\\nb", 3))', "(Some((1, 3)), Some((2, 1)))"),
        T("cjk_lines", '"日本\\n語x", 7, 10, 4', '(line_col("日本\\n語x", 7), line_col("日本\\n語x", 10), line_col("日本\\n語x", 4))', "(Some((2, 1)), Some((2, 2)), None)"),
        T("emoji_column", '"🦀x", 4 and 2', '(line_col("🦀x", 4), line_col("🦀x", 2))', "(Some((1, 2)), None)"),
        T("huge_offset", '"abc", usize::MAX', 'line_col("abc", usize::MAX)', "None"),
        T("char_to_byte_empty", '"", n = 0 and 1', '(char_to_byte("", 0), char_to_byte("", 1))', "(Some(0), None)"),
        T("char_to_byte_emoji", '"🦀a", n = 1 and 2', '(char_to_byte("🦀a", 1), char_to_byte("🦀a", 2))', "(Some(4), Some(5))"),
        T("char_to_byte_huge_n", '"ab", usize::MAX', 'char_to_byte("ab", usize::MAX)', "None"),
        T("no_match", '"abc", "d" and "", "a" and "ab", "abc"', '(find_all("abc", "d"), find_all("", "a"), find_all("ab", "abc"))', "(vec![], vec![], vec![])"),
        T("every_char_matches", '"aaa", "a"', 'find_all("aaa", "a")', "vec![(0, 0), (1, 1), (2, 2)]"),
        T("multi_char_needle", '"xéyéz", "yé"', 'find_all("xéyéz", "yé")', "vec![(3, 2)]"),
        T("emoji_needle_no_overlap", '"🦀🦀🦀", "🦀🦀"', 'find_all("🦀🦀🦀", "🦀🦀")', "vec![(0, 0)]"),
        r"""
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
        """,
    ],
    wrong=dict(
        slices_with_brackets=sub(LC_SOL, "let before = src.get(..at)?;", "let before = &src[..at.min(src.len())];"),
        column_in_bytes=sub(LC_SOL, "Some((line, before[line_start..].chars().count() + 1))", "Some((line, before.len() - line_start + 1))"),
        no_end_position=sub(LC_SOL, "s.char_indices().map(|(i, _)| i).chain(std::iter::once(s.len())).nth(n)", "s.char_indices().nth(n).map(|(i, _)| i)"),
        recounts_from_the_start=sub(LC_SOL, """chars += s[byte..i].chars().count();
                byte = i;
                out.push((i, chars));""", """let _ = (&mut byte, &mut chars);
                out.push((i, s[..i].chars().count()));"""),
        overlapping_matches=sub(LC_SOL, """for (i, _) in s.match_indices(needle) {
                chars += s[byte..i].chars().count();""", """for i in (0..s.len()).filter(|&i| s.is_char_boundary(i) && s[i..].starts_with(needle)) {
                chars += s[byte..i].chars().count();"""),
    ),
    hints=[("rust", "`src.get(..at)?` is `None` both past the end and inside a character. From there, lines are the `\\n` count plus one, and the column is the chars after the last `\\n`."),
           ("rust", "`s.match_indices(needle)` yields `(byte_offset, &str)` for non-overlapping matches. Keep a running char count and add only `s[prev..i].chars().count()` each time."),
           ("edge case", "`char_to_byte(s, count)` is `Some(s.len())`: chain `std::iter::once(s.len())` after the `char_indices` offsets.")],
    notes=("""`str` indexes by byte because that's O(1); anything "per character" is a scan. The conversions are cheap if you make one pass: `line_col` counts newlines with `matches('\\n')` (a byte scan would be just as safe, because every byte of a multi-byte UTF-8 character is ≥ 0x80) and chars only on the last line, and `find_all` converts each match incrementally, so the whole thing is O(n) instead of O(n) per match. `get` is the non-panicking twin of indexing for exactly this "maybe not a boundary" case. Real editors (LSP) want UTF-16 columns, which is `c.len_utf16()` summed instead of a char count. Syntax to remember: `s.get(a..b)` → `Option<&str>`, `s.char_indices()`, `s.match_indices(p)` / `rmatch_indices`, `s.matches(p).count()`, `s.bytes().filter(|&b| b == b'\\n').count()`, `s.rfind('\\n')`, `c.len_utf8()` / `len_utf16()`.""", "O(n)", "O(matches)"),
    follow_up="The Language Server Protocol counts columns in UTF-16 code units by default. What changes, and which characters make UTF-16 and char counts differ?",
))

PREV_STARTER = r"""
        /// The first `n` characters of `s`, followed by "…" if anything was cut.
        pub fn preview(s: &str, n: usize) -> String {
            if s.len() <= n {
                s.to_string()
            } else {
                format!("{}…", &s[..n])
            }
        }

        /// `s` with its first character in upper case (full Unicode rules); the rest unchanged.
        pub fn capitalize(s: &str) -> String {
            s[..1].to_uppercase() + &s[1..]
        }

        /// All but the last 4 characters of `s` replaced by '*'.
        pub fn mask(s: &str) -> String {
            let keep = s.len().saturating_sub(4);
            "*".repeat(keep) + &s[keep..]
        }
"""

PREV_SOL = r"""
        /// The first `n` characters of `s`, followed by "…" if anything was cut.
        pub fn preview(s: &str, n: usize) -> String {
            match s.char_indices().nth(n) {
                None => s.to_string(),
                Some((cut, _)) => format!("{}…", &s[..cut]),
            }
        }

        /// `s` with its first character in upper case (full Unicode rules); the rest unchanged.
        pub fn capitalize(s: &str) -> String {
            let mut chars = s.chars();
            match chars.next() {
                None => String::new(),
                Some(first) => first.to_uppercase().chain(chars).collect(),
            }
        }

        /// All but the last 4 characters of `s` replaced by '*'.
        pub fn mask(s: &str) -> String {
            let hidden = s.chars().count().saturating_sub(4);
            let keep = s.char_indices().nth(hidden).map_or(s.len(), |(i, _)| i);
            "*".repeat(hidden) + &s[keep..]
        }
"""

P.append(dict(
    slug="fix-slicing-mid-utf8", title="Fix: slicing mid-UTF-8 panics", mode="fix", level="medium", stage="understand",
    tags=["panic", "char boundaries", "char_indices", "to_uppercase"],
    teaches=[
        "`&s[..n]` takes `n` bytes and panics if that splits a character; `s.len()` is bytes too.",
        "The byte offset of character `n` is `s.char_indices().nth(n)`; `None` means the string is shorter.",
        "`&s[..1]` is not \"the first character\", and upper-casing it can produce several: `ß` → `SS`.",
    ],
    statement="""
        Three helpers for showing user text. They were tested on ASCII only: each one either panics or gives the
        wrong answer on accented text, emoji or `ß`. Fix them to match their doc comments, counting characters
        (Unicode scalar values), not bytes.
    """,
    examples=[('preview("héllo wörld", 2)', '"hé…"'), ('capitalize("ßtraße")', '"SStraße"'), ('mask("ñññññ")', '"*ññññ"')],
    starter=PREV_STARTER,
    solution=PREV_SOL,
    visible=[
        T("preview_ascii", '"hello world", 5', 'preview("hello world", 5)', '"hello…".to_string()'),
        T("preview_accented", '"héllo wörld", 2', 'preview("héllo wörld", 2)', '"hé…".to_string()'),
        T("preview_fits", '"short", 10', 'preview("short", 10)', '"short".to_string()'),
        T("capitalize_accented", '"école"', 'capitalize("école")', '"École".to_string()'),
        T("mask_card", '"4111111111111111"', 'mask("4111111111111111")', '"************1111".to_string()'),
    ],
    hidden=[
        T("preview_exactly_n_chars", '"日本", 2', 'preview("日本", 2)', '"日本".to_string()'),
        T("preview_cjk", '"日本語", 2', 'preview("日本語", 2)', '"日本…".to_string()'),
        T("preview_zero", '"a", 0 and "", 0', '(preview("a", 0), preview("", 0))', '("…".to_string(), String::new())'),
        T("preview_emoji", '"🦀🦀🦀", 2', 'preview("🦀🦀🦀", 2)', '"🦀🦀…".to_string()'),
        T("preview_combining_mark_counts", '"e\\u{301}x", 1', 'preview("e\\u{301}x", 1)', '"e…".to_string()'),
        T("capitalize_empty", '""', 'capitalize("")', "String::new()"),
        T("capitalize_sharp_s", '"ßtraße"', 'capitalize("ßtraße")', '"SStraße".to_string()'),
        T("capitalize_rest_unchanged", '"éA bC"', 'capitalize("éA bC")', '"ÉA bC".to_string()'),
        T("capitalize_ascii_and_cjk", '"hello" and "日本"', '(capitalize("hello"), capitalize("日本"))', '("Hello".to_string(), "日本".to_string())'),
        T("capitalize_ligature", '"ﬂow"', 'capitalize("ﬂow")', '"FLow".to_string()'),
        T("mask_short", '"1234", "12", ""', '(mask("1234"), mask("12"), mask(""))', '("1234".to_string(), "12".to_string(), String::new())'),
        T("mask_multibyte", '"ñññññ"', 'mask("ñññññ")', '"*ññññ".to_string()'),
        T("mask_cjk", '"日本語テキスト"', 'mask("日本語テキスト")', '"***テキスト".to_string()'),
        T("mask_euro", '"€1234"', 'mask("€1234")', '"*1234".to_string()'),
        r"""
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
        """,
    ],
    wrong=dict(
        preview_by_byte_budget=sub(PREV_SOL, """match s.char_indices().nth(n) {
                None => s.to_string(),
                Some((cut, _)) => format!("{}…", &s[..cut]),
            }""", """if s.len() <= n {
                s.to_string()
            } else {
                format!("{}…", &s[..s.floor_char_boundary(n)])
            }"""),
        ascii_uppercase_first=sub(PREV_SOL, "Some(first) => first.to_uppercase().chain(chars).collect(),", "Some(first) => std::iter::once(first.to_ascii_uppercase()).chain(chars).collect(),"),
        one_uppercase_char=sub(PREV_SOL, "Some(first) => first.to_uppercase().chain(chars).collect(),", "Some(first) => first.to_uppercase().take(1).chain(chars).collect(),"),
        mask_by_bytes=sub(PREV_SOL, """let hidden = s.chars().count().saturating_sub(4);
            let keep = s.char_indices().nth(hidden).map_or(s.len(), |(i, _)| i);""", """let keep = s.ceil_char_boundary(s.len().saturating_sub(4));
            let hidden = s[..keep].chars().count();"""),
    ),
    hints=[("rust", "`s.char_indices().nth(n)` is `Some((byte_offset, _))` of character `n`, or `None` if `s` has `n` characters or fewer, in which case nothing is cut."),
           ("rust", "Take the first char with `chars.next()`; `c.to_uppercase()` is an iterator, so `c.to_uppercase().chain(chars).collect()` builds the result."),
           ("edge case", "`capitalize(\"\")` must not panic, and `mask` hides by character count: `\"€1234\"` is 5 characters and 7 bytes.")],
    notes=("""All three bugs are the same assumption: one character is one byte. `s.len()` and `&s[..n]` count bytes, so the ASCII-tested code panics on the first `é` that straddles the cut (or silently miscounts when it doesn't). `char_indices().nth(n)` finds the byte offset of character `n` in one pass and only ever yields boundaries. `floor_char_boundary(n)` (stable since 1.91) is the tool for a *byte* budget, which is a different spec (see `unicode-safe-truncate`). Characters here are Unicode scalar values; what a user sees as one character can be several (`e` + combining acute), which needs grapheme segmentation (`unicode-segmentation`). Syntax to remember: `s.char_indices().nth(n)`, `s.chars().count()`, `c.to_uppercase()` (iterator), `iter.chain(rest).collect::<String>()`, `s.get(..n)` (non-panicking), `s.floor_char_boundary(i)` / `ceil_char_boundary(i)`.""", "O(n)", "O(n)"),
    follow_up="`preview` scans the whole prefix every call. In a UI that re-renders a long log line on every keystroke, what would you cache?",
    rules=dict(lines=16),
))

WRAP_STARTER = r"""
        /// Centers `s` in a field `width` characters wide, padding with `fill`.
        /// Odd padding puts the extra character on the right. Text of `width` characters or more is returned as is.
        pub fn center(s: &str, width: usize, fill: char) -> String {
            let len = s.len();
            if len >= width {
                return s.to_string();
            }
            let left = (width - len) / 2;
            let right = width - len - left;
            let mut out = String::new();
            out.extend(std::iter::repeat(fill).take(left));
            out.push_str(s);
            out.extend(std::iter::repeat(fill).take(right));
            out
        }

        /// The number of whitespace characters at the start of `line`.
        pub fn indent(line: &str) -> usize {
            line.len() - line.trim_start().len()
        }

        /// Greedy word wrap. Words are the whitespace-separated pieces of `text`. Each line holds as many words
        /// as fit in `width` characters, separated by single spaces; a word longer than `width` gets a line to itself.
        pub fn wrap(text: &str, width: usize) -> Vec<String> {
            let mut lines = Vec::new();
            let mut line = String::new();
            for word in text.split_whitespace() {
                if !line.is_empty() && line.len() + 1 + word.len() > width {
                    lines.push(std::mem::take(&mut line));
                }
                if !line.is_empty() {
                    line.push(' ');
                }
                line.push_str(word);
            }
            if !line.is_empty() {
                lines.push(line);
            }
            lines
        }
"""

WRAP_SOL = r"""
        /// Centers `s` in a field `width` characters wide, padding with `fill`.
        /// Odd padding puts the extra character on the right. Text of `width` characters or more is returned as is.
        pub fn center(s: &str, width: usize, fill: char) -> String {
            let len = s.chars().count();
            if len >= width {
                return s.to_string();
            }
            let left = (width - len) / 2;
            let right = width - len - left;
            let mut out = String::new();
            out.extend(std::iter::repeat(fill).take(left));
            out.push_str(s);
            out.extend(std::iter::repeat(fill).take(right));
            out
        }

        /// The number of whitespace characters at the start of `line`.
        pub fn indent(line: &str) -> usize {
            line.chars().take_while(|c| c.is_whitespace()).count()
        }

        /// Greedy word wrap. Words are the whitespace-separated pieces of `text`. Each line holds as many words
        /// as fit in `width` characters, separated by single spaces; a word longer than `width` gets a line to itself.
        pub fn wrap(text: &str, width: usize) -> Vec<String> {
            let mut lines = Vec::new();
            let mut line = String::new();
            let mut used = 0;
            for word in text.split_whitespace() {
                let w = word.chars().count();
                if used > 0 && used + 1 + w > width {
                    lines.push(std::mem::take(&mut line));
                    used = 0;
                }
                if used > 0 {
                    line.push(' ');
                    used += 1;
                }
                line.push_str(word);
                used += w;
            }
            if !line.is_empty() {
                lines.push(line);
            }
            lines
        }
"""


def wr(name, text, width, want):
    import json
    lit = "vec![" + ", ".join(json.dumps(x, ensure_ascii=False) for x in want) + "]"
    return T(name, f"{json.dumps(text, ensure_ascii=False)}, {width}", f"wrap({json.dumps(text, ensure_ascii=False)}, {width})",
             lit if want else "Vec::<String>::new()")


def py_wrap(text, width):
    lines, line = [], []
    used = 0
    for w in text.split():
        if used and used + 1 + len(w) > width:
            lines.append(" ".join(line))
            line, used = [], 0
        if used:
            used += 1
        line.append(w)
        used += len(w)
    if line:
        lines.append(" ".join(line))
    return lines


def wrc(name, text, width):
    return wr(name, text, width, py_wrap(text, width))


P.append(dict(
    slug="fix-len-counts-bytes", title="Fix: len() counts bytes", mode="fix", level="medium", stage="understand",
    tags=["UTF-8", "chars().count()", "word wrap", "O(n²)"],
    teaches=[
        "Layout math (padding, indentation, wrapping) wants a character count, not `len()`.",
        "`trim_start` is Unicode-aware, but `len() - trim_start().len()` measures what it trimmed in bytes.",
        "Replacing `line.len()` with `line.chars().count()` inside a loop turns an O(1) lookup into an O(line) scan: keep a running count.",
    ],
    statement="""
        A text-layout module that works on English and misbehaves on everything else. Fix the three functions to
        match their doc comments, measuring in characters. `wrap` must stay linear: it's called on long
        paragraphs with large widths.
    """,
    examples=[("center(\"né\", 4, '.')", '".né."'), ('indent("\\u{a0}\\u{a0}x")', "2"), ('wrap("héllo wörld", 11)', '["héllo wörld"]')],
    starter=WRAP_STARTER,
    solution=WRAP_SOL,
    visible=[
        T("center_accented", "\"né\", 4, '.'", "center(\"né\", 4, '.')", '".né.".to_string()'),
        T("center_odd_extra_right", "\"a\", 4, '*'", "center(\"a\", 4, '*')", '"*a**".to_string()'),
        T("indent_spaces_and_tabs", '"  \\tx"', 'indent("  \\tx")', "3"),
        T("indent_no_break_spaces", '"\\u{a0}\\u{a0}x"', 'indent("\\u{a0}\\u{a0}x")', "2"),
        wrc("wrap_accented_fits", "héllo wörld", 11),
    ],
    hidden=[
        T("center_too_wide_in_chars", "\"日本語\", 3, ' '", "center(\"日本語\", 3, ' ')", '"日本語".to_string()'),
        T("center_multibyte_fill", "\"x\", 3, '·'", "center(\"x\", 3, '·')", '"·x·".to_string()'),
        T("center_emoji", "\"🦀\", 3, '.'", "center(\"🦀\", 3, '.')", '".🦀.".to_string()'),
        T("center_fits_in_chars_not_bytes", "\"éé\", 3, '.'", "center(\"éé\", 3, '.')", '"éé.".to_string()'),
        T("center_empty", "\"\", 3, 'x'", "center(\"\", 3, 'x')", '"xxx".to_string()'),
        T("indent_ideographic_space", '"\\u{3000}x"', 'indent("\\u{3000}x")', "1"),
        T("indent_edges", '"", "   ", "x  "', '(indent(""), indent("   "), indent("x  "))', "(0, 3, 0)"),
        T("indent_mixed", '"\\u{2003} \\u{a0}é "', 'indent("\\u{2003} \\u{a0}é ")', "3"),
        wrc("wrap_ascii", "the quick brown fox", 10),
        wrc("wrap_long_word_alone", "a verylongword b", 4),
        wrc("wrap_cjk", "日本語 テキスト", 7),
        wrc("wrap_cjk_fits", "日本語 テキスト", 8),
        wrc("wrap_exact_fit", "ab cd", 5),
        wrc("wrap_width_zero", "a b", 0),
        wrc("wrap_extra_whitespace", "  a \t b\n\nc  ", 3),
        wr("wrap_empty", "", 5, []),
        wrc("wrap_accented_breaks_right", "é é é é", 3),
        r"""
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
        """,
    ],
    wrong=dict(
        recounts_the_line=sub(WRAP_SOL, """            let mut used = 0;
            for word in text.split_whitespace() {
                let w = word.chars().count();
                if used > 0 && used + 1 + w > width {
                    lines.push(std::mem::take(&mut line));
                    used = 0;
                }
                if used > 0 {
                    line.push(' ');
                    used += 1;
                }
                line.push_str(word);
                used += w;
            }""", """            for word in text.split_whitespace() {
                if !line.is_empty() && line.chars().count() + 1 + word.chars().count() > width {
                    lines.push(std::mem::take(&mut line));
                }
                if !line.is_empty() {
                    line.push(' ');
                }
                line.push_str(word);
            }"""),
        ascii_whitespace_indent=sub(WRAP_SOL, "line.chars().take_while(|c| c.is_whitespace()).count()", "line.bytes().take_while(u8::is_ascii_whitespace).count()"),
        center_counts_ascii_bytes=sub(WRAP_SOL, "let len = s.chars().count();", "let len = s.bytes().filter(u8::is_ascii).count();"),
    ),
    hints=[("rust", "`\"né\".len()` is 3. Every width in this file is a number of `char`s: `s.chars().count()`."),
           ("rust", "`line.chars().take_while(|c| c.is_whitespace()).count()` counts the indent in characters, including U+00A0 and U+3000."),
           ("approach", "In `wrap`, keep the current line's width in a variable and update it as you push, instead of measuring `line` again for every word.")],
    notes=("""Three flavours of the same bug. `center` and `wrap` compare byte lengths with a width in characters; `indent` gets the trimming right (`trim_start` knows U+00A0 and U+3000 are whitespace) and then measures the difference in bytes. The subtle one is the performance regression hiding in the obvious fix: `line.len()` is O(1), but `line.chars().count()` rescans the whole line for every word, which is O(n²) for a paragraph on one long line. A running count is the fix. Characters still aren't columns: CJK characters take two terminal cells and combining marks none, which is what `unicode-width` measures. Syntax to remember: `s.chars().count()`, `iter.take_while(|c| …).count()`, `c.is_whitespace()` (Unicode) vs `u8::is_ascii_whitespace`, `std::mem::take(&mut line)`, `out.extend(std::iter::repeat(c).take(n))`.""", "O(n)", "O(n)"),
    follow_up="How would you wrap by terminal display width, and what should happen to a word wider than the terminal?",
    rules=dict(lines=12),
))

REV_SOL = r"""
        /// A combining diacritical mark (U+0300..=U+036F).
        fn is_mark(c: char) -> bool {
            matches!(c, '\u{300}'..='\u{36f}')
        }

        pub fn reverse_each_word(s: &str) -> String {
            let mut out = String::with_capacity(s.len());
            let mut rest = s;
            while !rest.is_empty() {
                let body = rest.trim_start();
                out.push_str(&rest[..rest.len() - body.len()]);
                let end = body.find(char::is_whitespace).unwrap_or(body.len());
                let (word, tail) = body.split_at(end);
                let mut cut = word.len();
                for (i, c) in word.char_indices().rev() {
                    if !is_mark(c) || i == 0 {
                        out.push_str(&word[i..cut]);
                        cut = i;
                    }
                }
                rest = tail;
            }
            out
        }
"""

REV_STARTER = r"""
        pub fn reverse_each_word(s: &str) -> String {
            todo!()
        }
"""

P.append(dict(
    slug="reverse-each-word", title="Reverse each word, keeping accents attached", level="medium", stage="understand",
    tags=["char_indices().rev()", "combining marks", "split_at", "trim_start"],
    teaches=[
        "`chars().rev()` reverses scalar values, which detaches a combining accent from its letter: `e\\u{301}` must move as one unit.",
        "Walking `char_indices().rev()` and cutting slices at cluster starts copies whole clusters without collecting chars.",
        "Keeping the input's whitespace exactly means working with slices (`trim_start`, `find`, `split_at`), not `split_whitespace` + `join`.",
    ],
    statement="""
        Reverse the characters of each word, where words are the runs of non-whitespace. Keep every whitespace
        character exactly where it was.

        A combining mark (U+0300 to U+036F) belongs to the character before it and moves with it:
        `"e\\u{301}x"` (`éx`, written with a combining accent) becomes `"xe\\u{301}"`. A mark at the very start of
        a word has nothing to attach to, so it counts as a character on its own (with any marks that follow it).
    """,
    examples=[('"  héllo\\twörld "', '"  olléh\\tdlröw "'), ('"e\\u{301}x"', '"xe\\u{301}"')],
    starter=REV_STARTER,
    solution=REV_SOL,
    visible=[
        T("accented_words", '"héllo wörld"', 'reverse_each_word("héllo wörld")', '"olléh dlröw".to_string()'),
        T("whitespace_kept", '"  ab\\tcd "', 'reverse_each_word("  ab\\tcd ")', '"  ba\\tdc ".to_string()'),
        T("combining_mark_moves_with_letter", '"e\\u{301}x"', 'reverse_each_word("e\\u{301}x")', '"xe\\u{301}".to_string()'),
        T("leetcode_557", '"Let\'s take LeetCode contest"', 'reverse_each_word("Let\'s take LeetCode contest")', '"s\'teL ekat edoCteeL tsetnoc".to_string()'),
        T("empty", '""', 'reverse_each_word("")', "String::new()"),
    ],
    hidden=[
        T("emoji", '"🦀x"', 'reverse_each_word("🦀x")', '"x🦀".to_string()'),
        T("only_whitespace", '" \\t\\n "', 'reverse_each_word(" \\t\\n ")', '" \\t\\n ".to_string()'),
        T("two_marks", '"a\\u{301}\\u{302}b"', 'reverse_each_word("a\\u{301}\\u{302}b")', '"ba\\u{301}\\u{302}".to_string()'),
        T("leading_mark", '"\\u{301}ab"', 'reverse_each_word("\\u{301}ab")', '"ba\\u{301}".to_string()'),
        T("leading_marks_stay_together", '"\\u{301}\\u{302}a"', 'reverse_each_word("\\u{301}\\u{302}a")', '"a\\u{301}\\u{302}".to_string()'),
        T("marks_in_several_words", '"ne\\u{301}e n\\u{303}o"', 'reverse_each_word("ne\\u{301}e n\\u{303}o")', '"ee\\u{301}n on\\u{303}".to_string()'),
        T("cjk", '"日本語 テスト"', 'reverse_each_word("日本語 テスト")', '"語本日 トステ".to_string()'),
        T("crlf_between", '"ab\\r\\ncd"', 'reverse_each_word("ab\\r\\ncd")', '"ba\\r\\ndc".to_string()'),
        T("no_break_space_separates", '"ab\\u{a0}cd"', 'reverse_each_word("ab\\u{a0}cd")', '"ba\\u{a0}dc".to_string()'),
        T("precomposed_is_one_char", '"\\u{e9}t\\u{e9}"', 'reverse_each_word("\\u{e9}t\\u{e9}")', '"\\u{e9}t\\u{e9}".to_string()'),
        T("single_char_words", '"a b  c"', 'reverse_each_word("a b  c")', '"a b  c".to_string()'),
        r"""
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
        """,
    ],
    wrong=dict(
        reverses_scalar_values=sub(REV_SOL, """let mut cut = word.len();
                for (i, c) in word.char_indices().rev() {
                    if !is_mark(c) || i == 0 {
                        out.push_str(&word[i..cut]);
                        cut = i;
                    }
                }""", """out.extend(word.chars().rev());"""),
        normalizes_whitespace="""
            pub fn reverse_each_word(s: &str) -> String {
                s.split_whitespace()
                    .map(|w| {
                        let mut clusters: Vec<String> = Vec::new();
                        for c in w.chars() {
                            match clusters.last_mut() {
                                Some(last) if matches!(c, '\\u{300}'..='\\u{36f}') => last.push(c),
                                _ => clusters.push(c.to_string()),
                            }
                        }
                        clusters.into_iter().rev().collect::<String>()
                    })
                    .collect::<Vec<_>>()
                    .join(" ")
            }
        """,
        marks_attach_forward=sub(REV_SOL, "if !is_mark(c) || i == 0 {", "if !word[..i].ends_with(is_mark) || i == 0 {"),
    ),
    hints=[("approach", "Copy each whitespace run as is, then reverse the word after it cluster by cluster, until the input runs out."),
           ("rust", "`let body = rest.trim_start();` — the whitespace is `&rest[..rest.len() - body.len()]`. `body.find(char::is_whitespace)` ends the word, and `split_at` splits there."),
           ("rust", "Walk `word.char_indices().rev()`; each char that isn't a mark (or is at index 0) starts a cluster that runs to the previous cut. Push `&word[i..cut]`.")],
    notes=("""What a reader sees as one character can be several `char`s. Reversing `char`s moves a combining accent onto the wrong letter (or onto whitespace). This problem handles the common case, combining diacritics, by treating a base character plus the marks after it as one unit; the general rule is Unicode's extended grapheme clusters (UAX #29), which also covers emoji ZWJ sequences, flags and Hangul, and is what the `unicode-segmentation` crate implements. The slicing approach copies clusters straight from the input with no intermediate `Vec<char>`. Syntax to remember: `s.trim_start()`, `s.find(char::is_whitespace)`, `s.split_at(i)`, `word.char_indices().rev()`, `matches!(c, '\\u{300}'..='\\u{36f}')`.""", "O(n)", "O(n)"),
    follow_up="Which clusters does this still break? Think of 🇫🇷, 👩‍💻 and Korean jamo, and what `unicode-segmentation::graphemes(true)` would do instead.",
))

COW_STARTER = r"""
        use std::borrow::Cow;

        /// `s` with `&`, `<`, `>`, `"` and `'` escaped. Borrows `s` when there's nothing to escape.
        pub fn escape_html(s: &str) -> Cow<'_, str> {
            todo!()
        }

        /// `bytes` decoded as UTF-8 (each invalid sequence becomes U+FFFD), then escaped like `escape_html`.
        /// Borrows when nothing was replaced or escaped, and never copies the text more than it must.
        pub fn escape_bytes(bytes: &[u8]) -> Cow<'_, str> {
            todo!()
        }
"""

COW_SOL = r"""
        use std::borrow::Cow;

        /// `s` with `&`, `<`, `>`, `"` and `'` escaped. Borrows `s` when there's nothing to escape.
        pub fn escape_html(s: &str) -> Cow<'_, str> {
            let special = |c: char| matches!(c, '&' | '<' | '>' | '"' | '\'');
            let Some(first) = s.find(special) else {
                return Cow::Borrowed(s);
            };
            let mut out = String::with_capacity(s.len() + 8);
            out.push_str(&s[..first]);
            for c in s[first..].chars() {
                match c {
                    '&' => out.push_str("&amp;"),
                    '<' => out.push_str("&lt;"),
                    '>' => out.push_str("&gt;"),
                    '"' => out.push_str("&quot;"),
                    '\'' => out.push_str("&#39;"),
                    _ => out.push(c),
                }
            }
            Cow::Owned(out)
        }

        /// `bytes` decoded as UTF-8 (each invalid sequence becomes U+FFFD), then escaped like `escape_html`.
        /// Borrows when nothing was replaced or escaped, and never copies the text more than it must.
        pub fn escape_bytes(bytes: &[u8]) -> Cow<'_, str> {
            match String::from_utf8_lossy(bytes) {
                Cow::Borrowed(text) => escape_html(text),
                Cow::Owned(text) => match escape_html(&text) {
                    Cow::Borrowed(_) => Cow::Owned(text),
                    Cow::Owned(escaped) => Cow::Owned(escaped),
                },
            }
        }
"""

P.append(dict(
    slug="cow-str", title="Cow<str>: allocate only when needed", level="medium", stage="understand",
    tags=["Cow", "from_utf8_lossy", "zero-copy", "count_allocs"],
    teaches=[
        "`Cow::Borrowed` when the input is already right, `Cow::Owned` when it had to change; find the first byte that needs work before allocating.",
        "`String::from_utf8_lossy` returns `Cow<str>` for the same reason: valid input is borrowed.",
        "Chaining two `Cow` steps: a result borrowed from a local `String` can't be returned, but the local itself can be moved into `Cow::Owned`.",
    ],
    statement="""
        - `escape_html(s)`: escape `&`, `<`, `>`, `"` and `'` as `&amp;`, `&lt;`, `&gt;`, `&quot;` and `&#39;`.
          When there's nothing to escape, return `s` borrowed, without allocating.
        - `escape_bytes(bytes)`: decode `bytes` as UTF-8, replacing each invalid sequence with U+FFFD the way
          `String::from_utf8_lossy` does, then escape the text. Borrow when the bytes are valid UTF-8 with nothing
          to escape. When decoding had to allocate but there's nothing to escape, return the decoded `String`
          itself: don't copy it again.
    """,
    examples=[('escape_html("a<b")', '"a&lt;b" (Owned)'), ('escape_html("plain")', '"plain" (Borrowed)'), ('escape_bytes(b"a\\xffb")', '"a\\u{FFFD}b" (Owned, the decoded String itself)')],
    starter=COW_STARTER,
    solution=COW_SOL,
    visible=[
        T("escapes", '"a<b"', 'escape_html("a<b").into_owned()', '"a&lt;b".to_string()'),
        T("borrows", '"plain"', 'matches!(escape_html("plain"), std::borrow::Cow::Borrowed("plain"))', "true"),
        T("already_escaped", '"&lt;"', 'escape_html("&lt;").into_owned()', '"&amp;lt;".to_string()'),
        T("bytes_valid_and_plain_borrow", 'b"plain"', 'matches!(escape_bytes(b"plain"), std::borrow::Cow::Borrowed("plain"))', "true"),
        T("bytes_invalid_replaced", 'b"a\\xffb"', 'escape_bytes(b"a\\xffb").into_owned()', '"a\\u{FFFD}b".to_string()'),
    ],
    hidden=[
        T("all_five", "\"&<>\\\"'\"", "escape_html(\"&<>\\\"'\").into_owned()", '"&amp;&lt;&gt;&quot;&#39;".to_string()'),
        T("owned_when_changed", '"x&y"', 'matches!(escape_html("x&y"), std::borrow::Cow::Owned(_))', "true"),
        T("unicode", '"é<é"', 'escape_html("é<é").into_owned()', '"é&lt;é".to_string()'),
        T("empty", '""', 'matches!(escape_html(""), std::borrow::Cow::Borrowed(""))', "true"),
        T("special_at_ends", '"<abc>"', 'escape_html("<abc>").into_owned()', '"&lt;abc&gt;".to_string()'),
        T("borrowed_same_pointer", '"no specials here"', "escape_html(&s).as_ptr() == s.as_ptr()", "true", setup='let s = String::from("no specials here");'),
        T("borrow_allocates_nothing", '"日本語 ✓"', "(matches!(out, std::borrow::Cow::Borrowed(_)), n.count)", "(true, 0)",
          setup='let (out, n) = anneal_prelude::allocs(|| escape_html("日本語 ✓"));'),
        T("escape_allocates_once", '"a<b"', "(out.into_owned(), n.count)", '("a&lt;b".to_string(), 1)', setup='let (out, n) = anneal_prelude::allocs(|| escape_html("a<b"));'),
        T("bytes_borrow_allocates_nothing", 'b"ok"', "(out, n.count)", '(std::borrow::Cow::Borrowed("ok"), 0)', setup='let (out, n) = anneal_prelude::allocs(|| escape_bytes(b"ok"));'),
        T("bytes_valid_but_escaped", 'b"a&b"', "(out.into_owned(), n.count)", '("a&amp;b".to_string(), 1)', setup='let (out, n) = anneal_prelude::allocs(|| escape_bytes(b"a&b"));'),
        T("bytes_invalid_no_extra_copy", 'b"a\\xffb": no allocation beyond from_utf8_lossy\'s', "(out.into_owned(), n.count)", '("a\\u{FFFD}b".to_string(), lossy.count)',
          setup='let (_, lossy) = anneal_prelude::allocs(|| String::from_utf8_lossy(b"a\\xffb"));\nlet (out, n) = anneal_prelude::allocs(|| escape_bytes(b"a\\xffb"));'),
        T("bytes_invalid_and_escaped", 'b"<\\xff": from_utf8_lossy\'s allocations plus one', "(out.into_owned(), n.count)", '("&lt;\\u{FFFD}".to_string(), lossy.count + 1)',
          setup='let (_, lossy) = anneal_prelude::allocs(|| String::from_utf8_lossy(b"<\\xff"));\nlet (out, n) = anneal_prelude::allocs(|| escape_bytes(b"<\\xff"));'),
        T("bytes_truncated_sequence", 'b"x\\xe2\\x82"', 'escape_bytes(b"x\\xe2\\x82").into_owned()', '"x\\u{FFFD}".to_string()'),
        T("bytes_empty", 'b""', 'matches!(escape_bytes(b""), std::borrow::Cow::Borrowed(""))', "true"),
        r"""
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(7211);
            let pieces: [&[u8]; 8] = [b"a", "é".as_bytes(), b"&", b"<", b"'", b"\xff", b"\xc3", b"\""];
            for _ in 0..400 {
                let mut bytes = Vec::new();
                for _ in 0..rng.below(8) {
                    bytes.extend_from_slice(*rng.pick(&pieces));
                }
                let text = String::from_utf8_lossy(&bytes).into_owned();
                let mut want = String::new();
                for c in text.chars() {
                    match c {
                        '&' => want += "&amp;",
                        '<' => want += "&lt;",
                        '>' => want += "&gt;",
                        '"' => want += "&quot;",
                        '\'' => want += "&#39;",
                        _ => want.push(c),
                    }
                }
                let borrowed = std::str::from_utf8(&bytes).map_or(false, |s| s == want);
                let out = escape_bytes(&bytes);
                let got_borrowed = matches!(out, std::borrow::Cow::Borrowed(_));
                let html = std::str::from_utf8(&bytes).ok().map(|s| escape_html(s).into_owned());
                check!(format!("bytes = {bytes:?}"), (out.into_owned(), got_borrowed, html.clone()), (want.clone(), borrowed, html.map(|_| want)));
            }
        }

        #[test]
        fn scale_200k() {
            let s = "a<b&".repeat(50_000);
            let out = escape_html(&s);
            check!("s = \"a<b&…\" (200000 chars)", (out.len(), &out[..12]), (550_000, "a&lt;b&amp;a"));
        }
        """,
    ],
    wrong=dict(
        always_owned=sub(COW_SOL, """let Some(first) = s.find(special) else {
                return Cow::Borrowed(s);
            };""", """let first = s.find(special).unwrap_or(s.len());"""),
        amp_replaced_last=sub(COW_SOL, """let special = |c: char| matches!(c, '&' | '<' | '>' | '"' | '\\'');
            let Some(first) = s.find(special) else {
                return Cow::Borrowed(s);
            };
            let mut out = String::with_capacity(s.len() + 8);
            out.push_str(&s[..first]);
            for c in s[first..].chars() {
                match c {
                    '&' => out.push_str("&amp;"),
                    '<' => out.push_str("&lt;"),
                    '>' => out.push_str("&gt;"),
                    '"' => out.push_str("&quot;"),
                    '\\'' => out.push_str("&#39;"),
                    _ => out.push(c),
                }
            }
            Cow::Owned(out)""", """if !s.contains(['&', '<', '>', '"', '\\'']) {
                return Cow::Borrowed(s);
            }
            Cow::Owned(s.replace('<', "&lt;").replace('>', "&gt;").replace('"', "&quot;").replace('\\'', "&#39;").replace('&', "&amp;"))"""),
        copies_the_decoded_text=sub(COW_SOL, """Cow::Owned(text) => match escape_html(&text) {
                    Cow::Borrowed(_) => Cow::Owned(text),
                    Cow::Owned(escaped) => Cow::Owned(escaped),
                },""", """Cow::Owned(text) => Cow::Owned(escape_html(&text).into_owned()),"""),
        bytes_always_owned=sub(COW_SOL, "Cow::Borrowed(text) => escape_html(text),", "Cow::Borrowed(text) => Cow::Owned(escape_html(text).into_owned()),"),
    ),
    hints=[("approach", "Most inputs need no escaping. Scan for the first special character before allocating anything, then copy `&s[..first]` in one go."),
           ("rust", "`String::from_utf8_lossy(bytes)` is already a `Cow<str>`: match on it. In the `Owned(text)` arm you can't return `escape_html(&text)` (it borrows a local), but when that's `Borrowed` you can return `text` itself."),
           ("edge case", "`into_owned()` on a `Cow::Borrowed` allocates a copy. That's the second allocation the spec forbids.")],
    notes=("""The common case costs one scan and no allocation. `Cow` pushes the decision to the caller: both variants deref to `&str`, and `into_owned` turns either into a `String`, copying only if it was borrowed. `escape_bytes` is the interesting part: when decoding had to allocate, `escape_html(&text)` borrows `text`, a local, so it can't be returned; but a `Borrowed` result means "unchanged", and then the local `String` itself can be moved out as `Cow::Owned(text)` without copying it. Syntax to remember: `Cow<'a, str>`, `Cow::Borrowed(s)` / `Cow::Owned(string)`, `cow.into_owned()`, `cow.to_mut()` (clones on first write), `String::from_utf8_lossy(&bytes)` → `Cow<str>`, `let Some(i) = s.find(pred) else { return Cow::Borrowed(s) };`.""", "O(n)", "O(n) only when something changes"),
    follow_up="Where else does std hand back a `Cow`? (Look at `OsStr::to_string_lossy` and `Path::to_string_lossy`.) When is `Cow::to_mut` the right tool?",
    related=["S1"],
    perf=dict(allocs=True),
))

MONEY_HEAD = r"""
        use std::fmt;

        pub struct Money {
            pub cents: i64,
            pub currency: &'static str,
        }
"""

MONEY_SOL = MONEY_HEAD + r"""
        impl fmt::Display for Money {
            fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                let sign = if self.cents < 0 {
                    "-"
                } else if f.sign_plus() {
                    "+"
                } else {
                    ""
                };
                let abs = self.cents.unsigned_abs();
                f.pad(&format!("{sign}{}.{:02} {}", abs / 100, abs % 100, self.currency))
            }
        }

        impl fmt::Debug for Money {
            fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                f.debug_tuple("Money").field(&format_args!("{self}")).finish()
            }
        }
"""

MONEY_STARTER = MONEY_HEAD + r"""
        impl fmt::Display for Money {
            fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                todo!()
            }
        }

        impl fmt::Debug for Money {
            fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                todo!()
            }
        }
"""


def m(c, cur="USD"):
    return f'Money {{ cents: {c}, currency: "{cur}" }}'


P.append(dict(
    slug="display-vs-debug", title="Display vs Debug", level="medium", stage="understand",
    tags=["Display", "Debug", "f.pad", "debug_tuple", "format_args!"],
    teaches=[
        "`Display` is for users, `Debug` for programmers; `{:?}` and `{:#?}` both go through `Debug`.",
        "`f.pad` makes your `Display` respect width, fill and alignment; `write!(f, …)` ignores them.",
        "`debug_tuple`/`debug_struct` give `{:#?}` pretty-printing for free; `format_args!` shows a field through its `Display` without quotes or allocation.",
    ],
    statement="""
        Implement both formatting traits for `Money` by hand.

        - `Display`: `<amount> <currency>` with two decimals and a leading `-` for negative amounts
          (`12.34 USD`, `-0.05 EUR`). With `{:+}`, zero and positive amounts get a leading `+`. It must respect
          width, fill and alignment, so `format!("{:>12}", m)` right-aligns the whole thing.
        - `Debug`: `Money(12.34 USD)`, that is, a tuple struct whose one field is shown as its `Display`
          (no quotes). `{:#?}` gives the standard pretty form, `"Money(\\n    12.34 USD,\\n)"`.
    """,
    examples=[(m(1234), '"12.34 USD", {:?} "Money(12.34 USD)"'), ("cents: -5, {:>10}", '"  -0.05 USD"'), ("cents: 7, {:+}", '"+0.07 USD"')],
    starter=MONEY_STARTER,
    solution=MONEY_SOL,
    visible=[
        T("display", "12.34 USD", f'format!("{{}}", {m(1234)})', '"12.34 USD".to_string()'),
        T("negative_cents", "-5 cents", f'format!("{{}}", {m(-5, "EUR")})', '"-0.05 EUR".to_string()'),
        T("right_aligned", "{:>10} then |", f'format!("{{:>10}}|", {m(99, "EUR")})', '"  0.99 EUR|".to_string()'),
        T("plus_flag", "{:+} with 1234 cents", f'format!("{{:+}}", {m(1234)})', '"+12.34 USD".to_string()'),
        T("debug", "{:?}", f'format!("{{:?}}", {m(1234)})', '"Money(12.34 USD)".to_string()'),
    ],
    hidden=[
        T("zero", "0 cents", f'format!("{{}}", {m(0, "X")})', '"0.00 X".to_string()'),
        T("whole_amount", "500 cents", f'format!("{{}}", {m(500)})', '"5.00 USD".to_string()'),
        T("left", "{:<10} then |", f'format!("{{:<10}}|", {m(7, "GBP")})', '"0.07 GBP  |".to_string()'),
        T("centered", "{:^12} then |", f'format!("{{:^12}}|", {m(1234)})', '" 12.34 USD  |".to_string()'),
        T("fill_char", "{:*<12}", f'format!("{{:*<12}}", {m(7, "GBP")})', '"0.07 GBP****".to_string()'),
        T("width_too_small", "{:>3}", f'format!("{{:>3}}", {m(1234)})', '"12.34 USD".to_string()'),
        T("min_value", "i64::MIN cents", f'format!("{{}}", {m("i64::MIN", "X")})', '"-92233720368547758.08 X".to_string()'),
        T("max_value_plus", "{:+} with i64::MAX cents", f'format!("{{:+}}", {m("i64::MAX", "X")})', '"+92233720368547758.07 X".to_string()'),
        T("negative_width", "{:>12} with -5 cents", f'format!("{{:>12}}", {m(-5, "EUR")})', '"   -0.05 EUR".to_string()'),
        T("plus_zero", "{:+} with 0 cents", f'format!("{{:+}}", {m(0, "X")})', '"+0.00 X".to_string()'),
        T("plus_negative", "{:+} with -5 cents", f'format!("{{:+}}", {m(-5, "EUR")})', '"-0.05 EUR".to_string()'),
        T("plus_and_width", "{:>+12}", f'format!("{{:>+12}}", {m(1234)})', '"  +12.34 USD".to_string()'),
        T("debug_pretty", "{:#?}", f'format!("{{:#?}}", {m(-100)})', '"Money(\\n    -1.00 USD,\\n)".to_string()'),
        T("debug_in_a_vec", "{:?} of a Vec", f'format!("{{:?}}", vec![{m(100, "A")}, {m(-50, "B")}])', '"[Money(1.00 A), Money(-0.50 B)]".to_string()'),
        T("debug_pretty_nested", "{:#?} of Some(..)", f'format!("{{:#?}}", Some({m(1)}))', '"Some(\\n    Money(\\n        0.01 USD,\\n    ),\\n)".to_string()'),
        r"""
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(7212);
            for _ in 0..300 {
                let cents = rng.int(-1_000_000_000_000, 1_000_000_000_000);
                let width = rng.below(24);
                let abs = cents.unsigned_abs();
                let digits = format!("{}.{}{} JPY", abs / 100, abs % 100 / 10, abs % 10);
                let plain = if cents < 0 { format!("-{digits}") } else { digits.clone() };
                let plus = if cents < 0 { plain.clone() } else { format!("+{digits}") };
                let padded = " ".repeat(width.saturating_sub(plain.len())) + &plain;
                let m = Money { cents, currency: "JPY" };
                check!(format!("cents = {cents}, {{:>{width}}}"),
                       (format!("{m}"), format!("{m:>width$}"), format!("{m:+}"), format!("{m:?}")),
                       (plain.clone(), padded, plus, format!("Money({plain})")));
            }
        }
        """,
    ],
    wrong=dict(
        write_ignores_width=sub(MONEY_SOL, 'f.pad(&format!("{sign}{}.{:02} {}", abs / 100, abs % 100, self.currency))', 'write!(f, "{sign}{}.{:02} {}", abs / 100, abs % 100, self.currency)'),
        sign_lost=sub(MONEY_SOL, 'f.pad(&format!("{sign}{}.{:02} {}", abs / 100, abs % 100, self.currency))', 'let _ = (sign, abs);\n                f.pad(&format!("{}.{:02} {}", self.cents / 100, (self.cents % 100).abs(), self.currency))'),
        abs_overflows=sub(MONEY_SOL, "let abs = self.cents.unsigned_abs();", "let abs = self.cents.abs();"),
        plus_flag_ignored=sub(MONEY_SOL, """} else if f.sign_plus() {
                    "+"
                } else {""", """} else {"""),
        debug_field_quoted=sub(MONEY_SOL, '.field(&format_args!("{self}"))', ".field(&self.to_string())"),
        debug_written_flat=sub(MONEY_SOL, 'f.debug_tuple("Money").field(&format_args!("{self}")).finish()', 'write!(f, "Money({self})")'),
    ),
    hints=[("rust", "Build the whole text first, then `f.pad(&text)`: `pad` applies the caller's width, fill and alignment. `f.sign_plus()` says whether `{:+}` was used."),
           ("rust", "`f.debug_tuple(\"Money\").field(&x).finish()` handles `{:?}` and `{:#?}`. For `x`, `format_args!(\"{self}\")` is a value whose `Debug` prints your `Display` output, with no quotes and no `String`."),
           ("edge case", "`-5 / 100` is `0`, so the sign must be handled separately; `unsigned_abs` also survives `i64::MIN`.")],
    notes=("""Formatting the whole amount first, then padding once, keeps alignment right; `write!(f, …)` would ignore `{:>12}` entirely. The `Formatter` carries the caller's spec: `width()`, `precision()`, `fill()`, `align()`, `sign_plus()`, `alternate()`. The `debug_*` builders implement `{:#?}` (indentation, trailing commas) for you, including when your type is nested inside another pretty-printed value, which a hand-written `write!` can't do. `format_args!` builds an `Arguments` without allocating; its `Debug` is the formatted text itself. Syntax to remember: `f.pad(s)`, `f.sign_plus()`, `f.alternate()`, `f.debug_tuple("T").field(&x).finish()`, `f.debug_struct("T").field("name", &x).finish()`, `f.debug_list().entries(iter).finish()`, `format_args!("{x}")`, `x.unsigned_abs()`.""", "O(1)", "O(1)"),
    follow_up="How would you honour `{:.1}` precision for Money, and why can't you simply forward it to `f.pad`?",
    related=["L4"],
))

P.append(dict(
    slug="fromstr-setting", title="FromStr for a key = value line", level="medium", stage="understand",
    tags=["FromStr", "split_once", "error enums"],
    teaches=["`impl FromStr` so callers can write `line.parse::<Setting>()`.", "An error enum that says what went wrong."],
    statement="""
        Implement `FromStr` for `Setting`, parsing lines like `retries = 3`. Whitespace around the key and
        value is ignored. Errors: no `=` → `MissingEquals`, empty key → `EmptyKey`, value not an `i64` →
        `BadValue(value)` with the trimmed value text.
    """,
    starter="""
        use std::str::FromStr;

        #[derive(Debug, PartialEq)]
        pub struct Setting {
            pub key: String,
            pub value: i64,
        }

        #[derive(Debug, PartialEq)]
        pub enum SettingError {
            MissingEquals,
            EmptyKey,
            BadValue(String),
        }

        impl FromStr for Setting {
            type Err = SettingError;

            fn from_str(s: &str) -> Result<Self, Self::Err> {
                todo!()
            }
        }
    """,
    solution="""
        use std::str::FromStr;

        #[derive(Debug, PartialEq)]
        pub struct Setting {
            pub key: String,
            pub value: i64,
        }

        #[derive(Debug, PartialEq)]
        pub enum SettingError {
            MissingEquals,
            EmptyKey,
            BadValue(String),
        }

        impl FromStr for Setting {
            type Err = SettingError;

            fn from_str(s: &str) -> Result<Self, Self::Err> {
                let (key, value) = s.split_once('=').ok_or(SettingError::MissingEquals)?;
                let key = key.trim();
                if key.is_empty() {
                    return Err(SettingError::EmptyKey);
                }
                let value = value.trim();
                let value = value.parse().map_err(|_| SettingError::BadValue(value.to_string()))?;
                Ok(Setting { key: key.to_string(), value })
            }
        }
    """,
    visible=[
        T("parses", '"retries = 3"', '"retries = 3".parse::<Setting>()', 'Ok(Setting { key: "retries".to_string(), value: 3 })'),
        T("no_equals", '"retries"', '"retries".parse::<Setting>()', "Err(SettingError::MissingEquals)"),
        T("spaces_trimmed", '"  a   =   1  "', '"  a   =   1  ".parse::<Setting>()', 'Ok(Setting { key: "a".to_string(), value: 1 })'),
        T("bad_value_text", '"x = ten"', '"x = ten".parse::<Setting>()', 'Err(SettingError::BadValue("ten".to_string()))'),
        T("empty_key_visible", '"= 3"', '"= 3".parse::<Setting>()', "Err(SettingError::EmptyKey)"),
    ],
    hidden=[
        T("empty_key", '" = 3"', '" = 3".parse::<Setting>()', "Err(SettingError::EmptyKey)"),
        T("bad_value", '"a = x "', '"a = x ".parse::<Setting>()', 'Err(SettingError::BadValue("x".to_string()))'),
        T("second_equals_is_value", '"a=b=c"', '"a=b=c".parse::<Setting>()', 'Err(SettingError::BadValue("b=c".to_string()))'),
        T("negative", '"offset=-7"', '"offset=-7".parse::<Setting>()', 'Ok(Setting { key: "offset".to_string(), value: -7 })'),
        T("empty_line", '""', '"".parse::<Setting>()', "Err(SettingError::MissingEquals)"),
        T("just_equals", '"="', '"=".parse::<Setting>()', "Err(SettingError::EmptyKey)"),
        T("missing_value", '"a ="', '"a =".parse::<Setting>()', 'Err(SettingError::BadValue(String::new()))'),
        T("key_checked_first", '" = x"', '" = x".parse::<Setting>()', "Err(SettingError::EmptyKey)"),
        T("key_with_space", '"max retries = 2"', '"max retries = 2".parse::<Setting>()', 'Ok(Setting { key: "max retries".to_string(), value: 2 })'),
        T("plus_sign", '"a=+5"', '"a=+5".parse::<Setting>()', 'Ok(Setting { key: "a".to_string(), value: 5 })'),
        T("i64_min", '"a=-9223372036854775808"', '"a=-9223372036854775808".parse::<Setting>()', 'Ok(Setting { key: "a".to_string(), value: i64::MIN })'),
        T("too_big", '"a = 9223372036854775808"', '"a = 9223372036854775808".parse::<Setting>()', 'Err(SettingError::BadValue("9223372036854775808".to_string()))'),
        T("unicode_key_and_tabs", '"délai\\t=\\t5"', '"délai\\t=\\t5".parse::<Setting>()', 'Ok(Setting { key: "délai".to_string(), value: 5 })'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2214);
            let keys = ["", "k", " k ", "a b", "é"];
            let values = ["1", " -2 ", "x", "", "3=4", "+0"];
            for _ in 0..300 {
                let key = *rng.pick(&keys);
                let value = *rng.pick(&values);
                let line = if rng.below(5) == 0 { format!("{key}{value}") } else { format!("{key}={value}") };
                let want = match line.find('=') {
                    None => Err(SettingError::MissingEquals),
                    Some(i) => {
                        let (k, v) = (line[..i].trim(), line[i + 1..].trim());
                        if k.is_empty() {
                            Err(SettingError::EmptyKey)
                        } else {
                            match v.parse::<i64>() {
                                Ok(value) => Ok(Setting { key: k.to_string(), value }),
                                Err(_) => Err(SettingError::BadValue(v.to_string())),
                            }
                        }
                    }
                };
                check!(format!("line = {line:?}"), line.parse::<Setting>(), want);
            }
        }
        """,
    ],
    wrong=dict(
        splits_at_last_equals="""
            use std::str::FromStr;

            #[derive(Debug, PartialEq)]
            pub struct Setting {
                pub key: String,
                pub value: i64,
            }

            #[derive(Debug, PartialEq)]
            pub enum SettingError {
                MissingEquals,
                EmptyKey,
                BadValue(String),
            }

            impl FromStr for Setting {
                type Err = SettingError;

                fn from_str(s: &str) -> Result<Self, Self::Err> {
                    let (key, value) = s.rsplit_once('=').ok_or(SettingError::MissingEquals)?;
                    let key = key.trim();
                    if key.is_empty() {
                        return Err(SettingError::EmptyKey);
                    }
                    let value = value.trim();
                    let value = value.parse().map_err(|_| SettingError::BadValue(value.to_string()))?;
                    Ok(Setting { key: key.to_string(), value })
                }
            }
        """,
        value_checked_first="""
            use std::str::FromStr;

            #[derive(Debug, PartialEq)]
            pub struct Setting {
                pub key: String,
                pub value: i64,
            }

            #[derive(Debug, PartialEq)]
            pub enum SettingError {
                MissingEquals,
                EmptyKey,
                BadValue(String),
            }

            impl FromStr for Setting {
                type Err = SettingError;

                fn from_str(s: &str) -> Result<Self, Self::Err> {
                    let (key, value) = s.split_once('=').ok_or(SettingError::MissingEquals)?;
                    let value = value.trim();
                    let value = value.parse().map_err(|_| SettingError::BadValue(value.to_string()))?;
                    let key = key.trim();
                    if key.is_empty() {
                        return Err(SettingError::EmptyKey);
                    }
                    Ok(Setting { key: key.to_string(), value })
                }
            }
        """,
        untrimmed_error_text="""
            use std::str::FromStr;

            #[derive(Debug, PartialEq)]
            pub struct Setting {
                pub key: String,
                pub value: i64,
            }

            #[derive(Debug, PartialEq)]
            pub enum SettingError {
                MissingEquals,
                EmptyKey,
                BadValue(String),
            }

            impl FromStr for Setting {
                type Err = SettingError;

                fn from_str(s: &str) -> Result<Self, Self::Err> {
                    let (key, raw) = s.split_once('=').ok_or(SettingError::MissingEquals)?;
                    let key = key.trim();
                    if key.is_empty() {
                        return Err(SettingError::EmptyKey);
                    }
                    let value = raw.trim().parse().map_err(|_| SettingError::BadValue(raw.to_string()))?;
                    Ok(Setting { key: key.to_string(), value })
                }
            }
        """,
    ),
    hints=[("rust", "`s.split_once('=')` returns `Option<(&str, &str)>`; `.ok_or(SettingError::MissingEquals)?` turns `None` into the error."),
           ("rust", "`map_err` replaces the `ParseIntError` with your own variant, keeping the text that failed.")],
    notes=("`FromStr` plugs into `str::parse`, so callers get `\"...\".parse::<Setting>()` for free. Each check exits early with a specific error, and the order of the checks is part of the contract. `split_once` splits at the *first* `=`, so values may contain `=`; `rsplit_once` would split keys instead. Syntax to remember: `impl FromStr for T { type Err = E; fn from_str(s: &str) -> Result<Self, Self::Err> }`, `s.split_once('=')` → `Option<(&str, &str)>`, `.ok_or(E::Missing)?`, `.map_err(|_| E::Bad(v.to_string()))?`, `s.parse::<T>()`.", "O(n)", "O(n)"),
    follow_up="How would you add the line number to the errors when parsing a whole file?",
    related=["S1", "L4"],
))

P.append(dict(
    slug="unicode-safe-truncate", title="Unicode-safe truncate", level="medium", stage="understand",
    tags=["floor_char_boundary", "is_char_boundary", "byte budgets"],
    teaches=["Cutting to a byte budget at a character boundary: `floor_char_boundary`, or a short walk back with `is_char_boundary`.", "`checked_sub` + `let ... else` for a budget smaller than the ellipsis."],
    statement="""
        Fit `s` into `max_bytes` bytes. If it already fits, return it unchanged. Otherwise cut it at a
        character boundary and append `…` (3 bytes), so the whole result is at most `max_bytes` bytes. If
        there's no room even for `…`, return an empty string.
    """,
    examples=[('"hello world", 8', '"hello…"'), ('"héllo", 5', '"h…"')],
    starter="""
        pub fn truncate(s: &str, max_bytes: usize) -> String {
            todo!()
        }
    """,
    solution="""
        pub fn truncate(s: &str, max_bytes: usize) -> String {
            if s.len() <= max_bytes {
                return s.to_string();
            }
            let Some(budget) = max_bytes.checked_sub('…'.len_utf8()) else {
                return String::new();
            };
            format!("{}…", &s[..s.floor_char_boundary(budget)])
        }
    """,
    visible=[
        T("ascii", '"hello world", 8', 'truncate("hello world", 8)', '"hello…".to_string()'),
        T("fits", '"short", 10', 'truncate("short", 10)', rs("short")),
        T("only_room_for_ellipsis", '"abcd", 3', 'truncate("abcd", 3)', '"…".to_string()'),
        T("cut_before_accent", '"café au lait", 7', 'truncate("café au lait", 7)', '"caf…".to_string()'),
        T("empty_input", '"", 0', 'truncate("", 0)', "String::new()"),
    ],
    hidden=[
        T("mid_char", '"héllo", 5', 'truncate("héllo", 5)', '"h…".to_string()'),
        T("cjk", '"日本語テキスト", 10', 'truncate("日本語テキスト", 10)', '"日本…".to_string()'),
        T("no_room", '"abc", 2', 'truncate("abc", 2)', "String::new()"),
        T("exact_fit", '"abcd", 4', 'truncate("abcd", 4)', rs("abcd")),
        T("emoji", '"🦀🦀🦀", 7', 'truncate("🦀🦀🦀", 7)', '"🦀…".to_string()'),
        T("emoji_back_to_zero", '"🦀🦀", 6', 'truncate("🦀🦀", 6)', '"…".to_string()'),
        T("zero_budget", '"a", 0', 'truncate("a", 0)', "String::new()"),
        T("one_over", '"abcdef", 5', 'truncate("abcdef", 5)', '"ab…".to_string()'),
        T("unicode_fits", '"é", 2', 'truncate("é", 2)', '"é".to_string()'),
        T("ellipsis_input", '"……", 5', 'truncate("……", 5)', '"…".to_string()'),
        """
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
        """,
    ],
    wrong=dict(
        ellipsis_one_byte="""
            pub fn truncate(s: &str, max_bytes: usize) -> String {
                if s.len() <= max_bytes {
                    return s.to_string();
                }
                let Some(mut end) = max_bytes.checked_sub(1) else {
                    return String::new();
                };
                while !s.is_char_boundary(end) {
                    end -= 1;
                }
                format!("{}…", &s[..end])
            }
        """,
        counts_chars="""
            pub fn truncate(s: &str, max_bytes: usize) -> String {
                if s.chars().count() <= max_bytes {
                    return s.to_string();
                }
                if max_bytes == 0 {
                    return String::new();
                }
                let kept: String = s.chars().take(max_bytes - 1).collect();
                format!("{kept}…")
            }
        """,
        rounds_up_to_boundary="""
            pub fn truncate(s: &str, max_bytes: usize) -> String {
                if s.len() <= max_bytes {
                    return s.to_string();
                }
                let Some(mut end) = max_bytes.checked_sub('…'.len_utf8()) else {
                    return String::new();
                };
                while !s.is_char_boundary(end) {
                    end += 1;
                }
                format!("{}…", &s[..end])
            }
        """,
    ),
    hints=[("approach", "Reserve 3 bytes for `…`, then move the cut point back until it lands on a character boundary."),
           ("rust", "`s.floor_char_boundary(i)` (stable since Rust 1.91) is the largest boundary ≤ `i`. On older toolchains, loop `while !s.is_char_boundary(end) { end -= 1 }`.")],
    notes=("Byte budgets (database columns, protocol fields, log line limits) are a different spec from character counts: cut at the last boundary that fits. `floor_char_boundary` moves back at most three bytes, because a UTF-8 character is at most four; before 1.91 it was nightly-only, so older code has the `is_char_boundary` loop. `checked_sub` covers budgets smaller than the ellipsis. Syntax to remember: `s.floor_char_boundary(i)` / `ceil_char_boundary(i)`, `s.is_char_boundary(i)`, `'…'.len_utf8()`, `let Some(b) = n.checked_sub(3) else { return … };`.", "O(n) for the copy", "O(n)"),
    follow_up="Databases often limit by bytes and UIs by characters. How would you truncate to N characters instead?",
))

NAT_SOL = r"""
        use std::cmp::Ordering;

        /// Splits `s` after its leading run of ASCII digits.
        fn digits(s: &str) -> (&str, &str) {
            s.split_at(s.find(|c: char| !c.is_ascii_digit()).unwrap_or(s.len()))
        }

        /// Natural order: runs of ASCII digits compare by numeric value, everything else char by char.
        /// Strings that tie compare as plain strings, so the order is total.
        pub fn natural_cmp(a: &str, b: &str) -> Ordering {
            let (mut x, mut y) = (a, b);
            loop {
                match (x.chars().next(), y.chars().next()) {
                    (None, None) => return a.cmp(b),
                    (None, Some(_)) => return Ordering::Less,
                    (Some(_), None) => return Ordering::Greater,
                    (Some(c), Some(d)) if c.is_ascii_digit() && d.is_ascii_digit() => {
                        let ((nx, rx), (ny, ry)) = (digits(x), digits(y));
                        let (nx, ny) = (nx.trim_start_matches('0'), ny.trim_start_matches('0'));
                        let ord = nx.len().cmp(&ny.len()).then_with(|| nx.cmp(ny));
                        if ord != Ordering::Equal {
                            return ord;
                        }
                        (x, y) = (rx, ry);
                    }
                    (Some(c), Some(d)) => {
                        if c != d {
                            return c.cmp(&d);
                        }
                        (x, y) = (&x[c.len_utf8()..], &y[d.len_utf8()..]);
                    }
                }
            }
        }

        /// The Luhn check: spaces are ignored, anything else must be an ASCII digit, and there must be at
        /// least two digits.
        pub fn luhn_valid(s: &str) -> bool {
            let (mut sum, mut count) = (0, 0);
            for c in s.chars().rev().filter(|&c| c != ' ') {
                let Some(d) = c.to_digit(10) else {
                    return false;
                };
                sum += if count % 2 == 1 {
                    if d * 2 > 9 { d * 2 - 9 } else { d * 2 }
                } else {
                    d
                };
                count += 1;
            }
            count >= 2 && sum % 10 == 0
        }
"""

NAT_STARTER = r"""
        use std::cmp::Ordering;

        /// Natural order: runs of ASCII digits compare by numeric value, everything else char by char.
        /// Strings that tie compare as plain strings, so the order is total.
        pub fn natural_cmp(a: &str, b: &str) -> Ordering {
            todo!()
        }

        /// The Luhn check: spaces are ignored, anything else must be an ASCII digit, and there must be at
        /// least two digits.
        pub fn luhn_valid(s: &str) -> bool {
            todo!()
        }
"""


def nc(name, a, b, want):
    return T(name, f'"{a}" vs "{b}"', f'(natural_cmp("{a}", "{b}"), natural_cmp("{b}", "{a}"))', f"(Ordering::{want}, Ordering::{ {'Less': 'Greater', 'Greater': 'Less', 'Equal': 'Equal'}[want]})")


P.append(dict(
    slug="natural-order-compare", title="Digits in text: natural order and Luhn", level="medium", stage="understand",
    tags=["is_ascii_digit", "to_digit", "Ordering::then_with", "natural sort"],
    teaches=[
        "Compare digit runs as numbers without parsing them: strip leading zeros, then shorter is smaller, then compare the digits. No overflow, however long.",
        "`char::is_numeric` accepts `½`, `٣` and `Ⅻ`; `is_ascii_digit` and `to_digit(10)` accept `0`–`9` only.",
        "A comparator must be a total order: add a tie-break so `\"01\"` and `\"1\"` aren't `Equal` unless they're the same string.",
    ],
    statement="""
        - `natural_cmp(a, b)`: the order a file browser uses, so `"file9"` sorts before `"file10"`. Walk both
          strings together. Where both have a run of ASCII digits, compare the runs by numeric value (they can be
          any length). Otherwise compare one character at a time by code point; a string that runs out first is
          smaller. If everything compares equal, fall back to comparing `a` and `b` as plain strings, so
          `"x01"` < `"x1"` and only identical strings are `Equal`.
        - `luhn_valid(s)`: the Luhn checksum used by card numbers. Spaces are ignored; any other character that
          isn't an ASCII digit makes it invalid, and so do fewer than two digits. From the rightmost digit, double
          every second digit, subtracting 9 from any result above 9; the number is valid if the sum is a multiple
          of 10.
    """,
    examples=[('natural_cmp("file9", "file10")', "Less"), ('natural_cmp("x01", "x1")', "Less (tie-break)"), ('luhn_valid("4539 3195 0343 6467")', "true")],
    starter=NAT_STARTER,
    solution=NAT_SOL,
    use="use solution::*;\nuse std::cmp::Ordering;",
    visible=[
        nc("numbers_by_value", "file9", "file10", "Less"),
        nc("text_then_number", "a2b", "a10a", "Less"),
        nc("leading_zeros_tie_break", "x01", "x1", "Less"),
        T("sorts_a_listing", '["img12.png", "img10.png", "img2.png", "img1.png"]', "v", 'vec!["img1.png", "img2.png", "img10.png", "img12.png"]',
          setup='let mut v = vec!["img12.png", "img10.png", "img2.png", "img1.png"];\nv.sort_by(|a, b| natural_cmp(a, b));'),
        T("luhn_valid_card", '"4539 3195 0343 6467"', 'luhn_valid("4539 3195 0343 6467")', "true"),
    ],
    hidden=[
        nc("identical", "abc10", "abc10", "Equal"),
        nc("both_empty", "", "", "Equal"),
        nc("prefix_is_smaller", "a", "a1", "Less"),
        nc("plain_text", "abc", "abd", "Less"),
        nc("huge_numbers", "v99999999999999999999999", "v100000000000000000000000", "Less"),
        nc("zeros_do_not_count_as_digits", "007", "10", "Less"),
        nc("equal_value_then_rest_decides", "a1b", "a01a", "Greater"),
        nc("digit_vs_letter_by_code_point", "a1", "a-", "Greater"),
        nc("zeros_tie_break_comes_last", "x01b", "x1a", "Greater"),
        nc("case_sensitive", "IMG2", "img1", "Less"),
        nc("unicode_text", "é2", "é10", "Less"),
        nc("arabic_indic_digit_is_not_ascii", "a٣", "a2", "Greater"),
        nc("all_zeros", "0", "000", "Less"),
        nc("versions", "v1.10.0", "v1.9.2", "Greater"),
        T("luhn_small_valid", '"059", "59", "091", "0 0"', '[luhn_valid("059"), luhn_valid("59"), luhn_valid("091"), luhn_valid("0 0")]', "[true; 4]"),
        T("luhn_too_short", '"0", " 0", "", "   "', '[luhn_valid("0"), luhn_valid(" 0"), luhn_valid(""), luhn_valid("   ")]', "[false; 4]"),
        T("luhn_bad_checksum", '"8273 1232 7352 0569", "1234", "055 444 286"', '[luhn_valid("8273 1232 7352 0569"), luhn_valid("1234"), luhn_valid("055 444 286")]', "[false; 3]"),
        T("luhn_good_grouped", '"055 444 285", "4111 1111 1111 1111"', '[luhn_valid("055 444 285"), luhn_valid("4111 1111 1111 1111")]', "[true; 2]"),
        T("luhn_other_characters", '"055-444-285", "055a 444 285", "059\\t"', '[luhn_valid("055-444-285"), luhn_valid("055a 444 285"), luhn_valid("059\\t")]', "[false; 3]"),
        T("luhn_non_ascii_digits", '"٣٣", "①8", "0½", "6٣"', '[luhn_valid("٣٣"), luhn_valid("①8"), luhn_valid("0½"), luhn_valid("6٣")]', "[false; 4]"),
        T("luhn_long_zeros", '"0" × 100', 'luhn_valid(&"0".repeat(100))', "true"),
        r"""
        #[test]
        fn random_vs_brute_force() {
            #[derive(PartialEq, Eq, PartialOrd, Ord, Debug)]
            enum Tok {
                // Numbers sort between the characters below '0' and those above '9'.
                Low(char),
                Num(u128),
                High(char),
            }
            fn toks(s: &str) -> Vec<Tok> {
                let cs: Vec<char> = s.chars().collect();
                let mut out = Vec::new();
                let mut i = 0;
                while i < cs.len() {
                    if cs[i].is_ascii_digit() {
                        let mut v = 0u128;
                        while i < cs.len() && cs[i].is_ascii_digit() {
                            v = v * 10 + cs[i] as u128 - '0' as u128;
                            i += 1;
                        }
                        out.push(Tok::Num(v));
                    } else {
                        out.push(if cs[i] < '0' { Tok::Low(cs[i]) } else { Tok::High(cs[i]) });
                        i += 1;
                    }
                }
                out
            }
            let mut rng = anneal_prelude::Rng::new(7213);
            let pieces = ["a", "b", "0", "1", "9", "10", "007", "é", "-"];
            let sample = |rng: &mut anneal_prelude::Rng| {
                let mut s = String::new();
                for _ in 0..rng.below(6) {
                    s += *rng.pick(&pieces);
                }
                s
            };
            for _ in 0..400 {
                let (a, b) = (sample(&mut rng), sample(&mut rng));
                let want = toks(&a).cmp(&toks(&b)).then_with(|| a.cmp(&b));
                let digits: String = (0..rng.below(20)).map(|_| char::from(b'0' + rng.below(10) as u8)).collect();
                let spaced: String = digits.chars().flat_map(|c| [c, ' ']).collect();
                let mut sum = 0;
                for (i, c) in digits.chars().rev().enumerate() {
                    let d = c as u32 - '0' as u32;
                    sum += if i % 2 == 1 { (d * 2) / 10 + (d * 2) % 10 } else { d };
                }
                let want_luhn = digits.len() >= 2 && sum % 10 == 0;
                check!(format!("a = {a:?}, b = {b:?}, card = {spaced:?}"), (natural_cmp(&a, &b), luhn_valid(&spaced)), (want, want_luhn));
            }
        }

        #[test]
        fn scale_sort_100k_names() {
            let mut names: Vec<String> = (0..100_000).map(|i| format!("log{i}.txt")).collect();
            let mut rng = anneal_prelude::Rng::new(7214);
            rng.shuffle(&mut names);
            names.sort_by(|a, b| natural_cmp(a, b));
            let ok = names.iter().enumerate().all(|(i, n)| *n == format!("log{i}.txt"));
            check!("100000 shuffled names log0.txt … log99999.txt", ok, true);
            let (a, b) = ("1".repeat(1_000_000) + "a", "1".repeat(1_000_000) + "b");
            check!("two 1000001-char strings that differ at the end", natural_cmp(&a, &b), Ordering::Less);
        }
        """,
    ],
    wrong=dict(
        parses_into_u64=sub(NAT_SOL, """let (nx, ny) = (nx.trim_start_matches('0'), ny.trim_start_matches('0'));
                        let ord = nx.len().cmp(&ny.len()).then_with(|| nx.cmp(ny));""", """let ord = nx.parse::<u64>().unwrap().cmp(&ny.parse::<u64>().unwrap());"""),
        compares_run_lengths_with_zeros=sub(NAT_SOL, "let (nx, ny) = (nx.trim_start_matches('0'), ny.trim_start_matches('0'));\n", ""),
        no_tie_break=sub(NAT_SOL, "(None, None) => return a.cmp(b),", "(None, None) => return Ordering::Equal,"),
        tie_break_too_early=sub(NAT_SOL, """let (nx, ny) = (nx.trim_start_matches('0'), ny.trim_start_matches('0'));
                        let ord = nx.len().cmp(&ny.len()).then_with(|| nx.cmp(ny));""", """let (tx, ty) = (nx.trim_start_matches('0'), ny.trim_start_matches('0'));
                        let ord = tx.len().cmp(&ty.len()).then_with(|| tx.cmp(ty)).then_with(|| nx.cmp(ny));"""),
        is_numeric_digits=sub(NAT_SOL, """let Some(d) = c.to_digit(10) else {
                    return false;
                };""", """if !c.is_numeric() {
                    return false;
                }
                let d = c as u32 - '0' as u32;"""),
        counts_spaces_as_digits=sub(NAT_SOL, "count >= 2 && sum % 10 == 0", "s.len() >= 2 && sum % 10 == 0"),
    ),
    hints=[("approach", "Keep two `&str` cursors. When both start with a digit, split off each digit run, strip leading zeros, and compare by length then lexically. Otherwise compare one char and advance by `len_utf8`."),
           ("rust", "`s.find(|c: char| !c.is_ascii_digit()).unwrap_or(s.len())` ends a run; `ord.then_with(|| …)` chains comparisons. For Luhn, `c.to_digit(10)` is `None` for anything but `0`–`9`."),
           ("edge case", "`\"a1b\"` vs `\"a01a\"`: the numbers tie, so keep going (`b` > `a`); the plain-string tie-break is only for strings that compare equal all the way.")],
    notes=("""Parsing a digit run into `u64` is the classic bug: file names like `IMG_20240501123456789` overflow, and `unwrap` then panics inside `sort_by`. Comparing the zero-stripped digit strings, by length then lexically, is the same comparison with no limit. The tie-break matters because `sort_by`, `BTreeMap` and binary search assume a total order: without it `"01"` and `"1"` are `Equal` but not identical, and a comparator that isn't consistent can make `sort_by` panic ("user-provided comparison function does not correctly implement a total order"). For Luhn, the trap is `is_numeric`/`is_digit`-style checks that accept other scripts' digits; `to_digit(10)` returns the value and rejects them in one step. Syntax to remember: `c.is_ascii_digit()`, `c.to_digit(10)` → `Option<u32>`, `char::from_digit(d, 10)`, `s.trim_start_matches('0')`, `a.cmp(&b).then_with(|| …)`, `ord.reverse()`, `v.sort_by(|a, b| natural_cmp(a, b))`, `v.sort_by_key(|s| key(s))`.""", "O(n) per comparison", "O(1)"),
    follow_up="How would you make `natural_cmp` case-insensitive without allocating, and still a total order? What should `\"a\"` vs `\"A\"` return?",
    related=["S3"],
))

PATH_SOL = r"""
        use std::borrow::Cow;
        use std::ffi::OsStr;
        use std::path::{Path, PathBuf};

        /// The extension, ASCII-lowercased, if the file name has one that is valid UTF-8.
        pub fn ext_lower(path: &Path) -> Option<String> {
            Some(path.extension()?.to_str()?.to_ascii_lowercase())
        }

        /// The file name for display, with U+FFFD for bytes that aren't UTF-8; "" when there is no file name.
        pub fn display_name(path: &Path) -> Cow<'_, str> {
            path.file_name().map_or(Cow::Borrowed(""), OsStr::to_string_lossy)
        }

        /// The same path with ".bak" appended to the file name; `None` when there is no file name.
        pub fn backup_path(path: &Path) -> Option<PathBuf> {
            let mut name = path.file_name()?.to_os_string();
            name.push(".bak");
            Some(path.with_file_name(name))
        }

        /// The paths that are inside `root` (by whole components), relative to it and as UTF-8, in order.
        pub fn relative_to<'a>(paths: &'a [PathBuf], root: &Path) -> Vec<&'a str> {
            paths.iter().filter_map(|p| p.strip_prefix(root).ok()?.to_str()).collect()
        }
"""

PATH_STARTER = r"""
        use std::borrow::Cow;
        use std::ffi::OsStr;
        use std::path::{Path, PathBuf};

        /// The extension, ASCII-lowercased, if the file name has one that is valid UTF-8.
        pub fn ext_lower(path: &Path) -> Option<String> {
            todo!()
        }

        /// The file name for display, with U+FFFD for bytes that aren't UTF-8; "" when there is no file name.
        pub fn display_name(path: &Path) -> Cow<'_, str> {
            todo!()
        }

        /// The same path with ".bak" appended to the file name; `None` when there is no file name.
        pub fn backup_path(path: &Path) -> Option<PathBuf> {
            todo!()
        }

        /// The paths that are inside `root` (by whole components), relative to it and as UTF-8, in order.
        pub fn relative_to<'a>(paths: &'a [PathBuf], root: &Path) -> Vec<&'a str> {
            todo!()
        }
"""

PATH_TESTS = r"""
        use std::ffi::OsStr;
        use std::os::unix::ffi::OsStrExt;
        use std::path::{Path, PathBuf};

        /// A path from raw bytes, which need not be UTF-8 (Unix paths are bytes).
        fn raw(bytes: &[u8]) -> &Path {
            Path::new(OsStr::from_bytes(bytes))
        }

        fn bufs(paths: &[&str]) -> Vec<PathBuf> {
            paths.iter().map(PathBuf::from).collect()
        }
"""

P.append(dict(
    slug="paths-and-osstr", title="Paths are not strings", level="medium", stage="understand",
    tags=["Path", "OsStr", "to_string_lossy", "strip_prefix", "with_file_name"],
    teaches=[
        "A Unix path is bytes, not UTF-8: `OsStr::to_str` is an `Option`, `to_string_lossy` a `Cow`.",
        "`Path::strip_prefix` matches whole components, so `/data2/x` is not inside `/data`; `str::strip_prefix` says it is.",
        "`with_extension` replaces the extension (`notes.txt` → `notes.bak`); appending needs an `OsString` push and `with_file_name`.",
    ],
    statement="""
        File-handling helpers that must work on any Unix path, including names that aren't valid UTF-8. Work
        with `Path`, `OsStr` and `PathBuf`; converting a whole path to `&str` first gets several of these wrong.

        - `ext_lower(path)`: the file name's extension, ASCII-lowercased, if it has one and it's valid UTF-8.
          Use std's definition: `".bashrc"` has none, `"a.tar.gz"` has `"gz"`, `"file."` has `""`.
        - `display_name(path)`: the file name for display, with U+FFFD for bytes that aren't UTF-8; `""` when the
          path has no file name (`"/"`, `".."`). Borrow when it's valid UTF-8.
        - `backup_path(path)`: the same path with `.bak` appended to the file name (`"notes.txt"` →
          `"notes.txt.bak"`), even when the name isn't UTF-8. `None` when there's no file name.
        - `relative_to(paths, root)`: for each path inside `root`, compared by whole components, the rest of the
          path as `&str`, in order. Skip paths outside `root` and paths whose rest isn't UTF-8. `root` itself gives
          `""`.
    """,
    examples=[('ext_lower("IMG_01.JPG")', 'Some("jpg")'), ('backup_path("conf/notes.txt")', 'Some("conf/notes.txt.bak")'),
              ('relative_to(["/data/a.txt", "/data2/b"], "/data")', '["a.txt"]')],
    starter=PATH_STARTER,
    solution=PATH_SOL,
    visible=[
        PATH_TESTS,
        T("ext_lowercased", '"photos/IMG_01.JPG"', 'ext_lower(Path::new("photos/IMG_01.JPG"))', 'Some("jpg".to_string())'),
        T("dotfile_has_no_extension", '".bashrc"', 'ext_lower(Path::new(".bashrc"))', "None"),
        T("display_non_utf8_name", 'b"dir/caf\\xe9.txt" (Latin-1 é)', 'display_name(raw(b"dir/caf\\xe9.txt"))', '"caf\\u{FFFD}.txt"'),
        T("backup_appends", '"conf/notes.txt"', 'backup_path(Path::new("conf/notes.txt"))', 'Some(PathBuf::from("conf/notes.txt.bak"))'),
        T("relative_by_components", 'root "/data", paths ["/data/a.txt", "/data2/b", "/data/x/y"]', 'relative_to(&paths, Path::new("/data"))', 'vec!["a.txt", "x/y"]',
          setup='let paths = bufs(&["/data/a.txt", "/data2/b", "/data/x/y"]);'),
    ],
    hidden=[
        PATH_TESTS,
        T("ext_last_one_only", '"a.tar.GZ"', 'ext_lower(Path::new("a.tar.GZ"))', 'Some("gz".to_string())'),
        T("ext_trailing_dot_is_empty", '"file."', 'ext_lower(Path::new("file."))', 'Some(String::new())'),
        T("ext_dot_in_directory", '"dir.d/file"', 'ext_lower(Path::new("dir.d/file"))', "None"),
        T("ext_hidden_file_with_extension", '"x/.env.LOCAL"', 'ext_lower(Path::new("x/.env.LOCAL"))', 'Some("local".to_string())'),
        T("ext_not_utf8", 'b"a.t\\xffxt"', 'ext_lower(raw(b"a.t\\xffxt"))', "None"),
        T("ext_only_ascii_lowered", '"a.ÉTÉ"', 'ext_lower(Path::new("a.ÉTÉ"))', 'Some("ÉtÉ".to_string())'),
        T("ext_no_file_name", '"/" and ".."', '(ext_lower(Path::new("/")), ext_lower(Path::new("..")))', "(None, None)"),
        T("display_borrows_utf8", '"a/b/日本.txt"', 'matches!(display_name(Path::new("a/b/日本.txt")), std::borrow::Cow::Borrowed("日本.txt"))', "true"),
        T("display_no_file_name", '"/", "..", "a/..", ""', '[display_name(Path::new("/")), display_name(Path::new("..")), display_name(Path::new("a/..")), display_name(Path::new(""))]',
          '["", "", "", ""]'),
        T("display_trailing_slash", '"a/b/"', 'display_name(Path::new("a/b/"))', '"b"'),
        T("backup_not_with_extension", '"a/b.tar.gz"', 'backup_path(Path::new("a/b.tar.gz"))', 'Some(PathBuf::from("a/b.tar.gz.bak"))'),
        T("backup_no_extension", '"Makefile"', 'backup_path(Path::new("Makefile"))', 'Some(PathBuf::from("Makefile.bak"))'),
        T("backup_dotfile", '"~/.bashrc"', 'backup_path(Path::new("~/.bashrc"))', 'Some(PathBuf::from("~/.bashrc.bak"))'),
        T("backup_non_utf8", 'b"d/\\xff.log"', 'backup_path(raw(b"d/\\xff.log"))', 'Some(raw(b"d/\\xff.log.bak").to_path_buf())'),
        T("backup_no_file_name", '"/" and "x/.."', '(backup_path(Path::new("/")), backup_path(Path::new("x/..")))', "(None, None)"),
        T("backup_trailing_slash", '"logs/"', 'backup_path(Path::new("logs/"))', 'Some(PathBuf::from("logs.bak"))'),
        T("relative_root_itself_and_trailing_slash", 'root "/data/", paths ["/data", "/data/", "/database"]', 'relative_to(&paths, Path::new("/data/"))', 'vec!["", ""]',
          setup='let paths = bufs(&["/data", "/data/", "/database"]);'),
        T("relative_skips_non_utf8", 'root "/r", paths ["/r/ok", b"/r/\\xff", "/r/fine"]', 'relative_to(&paths, Path::new("/r"))', 'vec!["ok", "fine"]',
          setup='let paths = vec![PathBuf::from("/r/ok"), raw(b"/r/\\xff").to_path_buf(), PathBuf::from("/r/fine")];'),
        T("relative_relative_paths", 'root "src", paths ["src/lib.rs", "srcs/x", "./src/a", "src"]', 'relative_to(&paths, Path::new("src"))', 'vec!["lib.rs", ""]',
          setup='let paths = bufs(&["src/lib.rs", "srcs/x", "./src/a", "src"]);'),
        T("relative_borrows", "the result points into the input paths", "got[0].as_ptr() == paths[0].to_str().unwrap()[3..].as_ptr()", "true",
          setup='let paths = bufs(&["/r/abc"]);\nlet got = relative_to(&paths, Path::new("/r"));'),
        r"""
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(7215);
            let parts = ["a", "ab", "a.b", ".c", "d.", "X.Y"];
            for _ in 0..300 {
                let n = rng.below(4) + 1;
                let comps: Vec<&str> = (0..n).map(|_| *rng.pick(&parts)).collect();
                let path = comps.join("/");
                let name = *comps.last().unwrap();
                let want_ext = match name.rfind('.') {
                    Some(0) | None => None,
                    Some(i) => Some(name[i + 1..].to_ascii_lowercase()),
                };
                let want_bak = PathBuf::from(format!("{path}.bak"));
                let root_len = rng.below(n + 1);
                let root = comps[..root_len].join("/");
                let want_rel: Vec<String> = if root_len == 0 { vec![path.clone()] } else { vec![comps[root_len..].join("/")] };
                let paths = vec![PathBuf::from(&path)];
                let got_rel: Vec<String> = relative_to(&paths, Path::new(&root)).into_iter().map(String::from).collect();
                check!(format!("path = {path:?}, root = {root:?}"),
                       (ext_lower(Path::new(&path)), display_name(Path::new(&path)).into_owned(), backup_path(Path::new(&path)), got_rel),
                       (want_ext, name.to_string(), Some(want_bak), want_rel));
            }
        }
        """,
    ],
    wrong=dict(
        with_extension_replaces=sub(PATH_SOL, """let mut name = path.file_name()?.to_os_string();
            name.push(".bak");
            Some(path.with_file_name(name))""", """path.file_name()?;
            Some(path.with_extension("bak"))"""),
        string_prefix=sub(PATH_SOL, "paths.iter().filter_map(|p| p.strip_prefix(root).ok()?.to_str()).collect()",
                          "let root = root.to_str().unwrap_or(\"\").trim_end_matches('/');\n            paths.iter().filter_map(|p| Some(p.to_str()?.strip_prefix(root)?.trim_start_matches('/'))).collect()"),
        lossy_extension=sub(PATH_SOL, "Some(path.extension()?.to_str()?.to_ascii_lowercase())", "Some(path.extension()?.to_string_lossy().to_ascii_lowercase())"),
        unicode_lowercase=sub(PATH_SOL, "Some(path.extension()?.to_str()?.to_ascii_lowercase())", "Some(path.extension()?.to_str()?.to_lowercase())"),
        display_drops_non_utf8=sub(PATH_SOL, "path.file_name().map_or(Cow::Borrowed(\"\"), OsStr::to_string_lossy)", "Cow::Borrowed(path.file_name().and_then(OsStr::to_str).unwrap_or(\"\"))"),
    ),
    hints=[("rust", "`path.extension()` and `path.file_name()` return `Option<&OsStr>`; `.to_str()` is `Option<&str>` and `.to_string_lossy()` is `Cow<str>`."),
           ("rust", "`let mut name = path.file_name()?.to_os_string(); name.push(\".bak\");` then `path.with_file_name(name)`."),
           ("edge case", "`\"/data2/b\".strip_prefix(\"/data\")` is `Some(\"2/b\")`; `Path::new(\"/data2/b\").strip_prefix(\"/data\")` is an error.")],
    notes=("""On Unix a path is a byte string with no encoding (on Windows it's potentially ill-formed UTF-16), which is why std has `OsStr`/`OsString` and `Path`/`PathBuf` instead of using `str`. Each conversion to text is a decision: `to_str()` when the program can't go on without UTF-8, `to_string_lossy()` for display, `as_encoded_bytes()`/`OsStrExt::as_bytes()` when you need the bytes. `Path` methods work on components, so they get `/data2` vs `/data`, trailing slashes and `..` right where string code doesn't. Syntax to remember: `Path::new(s)`, `p.file_name()` / `file_stem()` / `extension()` → `Option<&OsStr>`, `p.parent()`, `p.join(x)`, `p.with_file_name(n)`, `p.with_extension(e)`, `p.strip_prefix(root)` → `Result<&Path, _>`, `p.components()`, `os.to_str()`, `os.to_string_lossy()`, `os.to_os_string()` + `push`, `p.to_path_buf()`, `p.display()` for `{}`.""", "O(path length)", "O(path length)"),
    follow_up="Why does `Path` implement `AsRef<Path>` for `&str`, `String` and `OsStr`, and what does `fn open(p: impl AsRef<Path>)` buy the caller?",
    related=["L4"],
))

UTF8_SOL = r"""
        /// Decodes UTF-8 that arrives in chunks, such as reads from a socket.
        #[derive(Default)]
        pub struct Utf8Decoder {
            /// The start of a character the last chunk ended in the middle of (at most 3 bytes).
            pending: Vec<u8>,
        }

        impl Utf8Decoder {
            pub fn new() -> Self {
                Self::default()
            }

            /// Decodes `chunk` onto `out`. Each invalid sequence becomes U+FFFD, as `String::from_utf8_lossy`
            /// would do it; a character cut off at the end of the chunk waits for the next one.
            pub fn push(&mut self, chunk: &[u8], out: &mut String) {
                let joined;
                let mut input = chunk;
                if !self.pending.is_empty() {
                    self.pending.extend_from_slice(chunk);
                    joined = std::mem::take(&mut self.pending);
                    input = &joined;
                }
                loop {
                    match std::str::from_utf8(input) {
                        Ok(text) => {
                            out.push_str(text);
                            return;
                        }
                        Err(e) => {
                            let (good, bad) = input.split_at(e.valid_up_to());
                            out.push_str(std::str::from_utf8(good).unwrap());
                            match e.error_len() {
                                Some(len) => {
                                    out.push(char::REPLACEMENT_CHARACTER);
                                    input = &bad[len..];
                                }
                                None => {
                                    self.pending.extend_from_slice(bad);
                                    return;
                                }
                            }
                        }
                    }
                }
            }

            /// The end of the input: a character that was never finished becomes U+FFFD.
            pub fn finish(self, out: &mut String) {
                if !self.pending.is_empty() {
                    out.push(char::REPLACEMENT_CHARACTER);
                }
            }
        }
"""

UTF8_STARTER = r"""
        /// Decodes UTF-8 that arrives in chunks, such as reads from a socket.
        #[derive(Default)]
        pub struct Utf8Decoder {
            // Your state here.
        }

        impl Utf8Decoder {
            pub fn new() -> Self {
                Self::default()
            }

            /// Decodes `chunk` onto `out`. Each invalid sequence becomes U+FFFD, as `String::from_utf8_lossy`
            /// would do it; a character cut off at the end of the chunk waits for the next one.
            pub fn push(&mut self, chunk: &[u8], out: &mut String) {
                todo!()
            }

            /// The end of the input: a character that was never finished becomes U+FFFD.
            pub fn finish(self, out: &mut String) {
                todo!()
            }
        }
"""

UTF8_TESTS = r"""
        /// Feeds `chunks` through one decoder, then finishes it.
        fn decode(chunks: &[&[u8]]) -> String {
            let mut d = Utf8Decoder::new();
            let mut out = String::new();
            for c in chunks {
                d.push(c, &mut out);
            }
            d.finish(&mut out);
            out
        }
"""


def dc(name, desc, chunks, want):
    return T(name, desc, "decode(&[" + ", ".join(chunks) + "])", want)


P.append(dict(
    slug="utf8-chunk-decoder", title="Decode UTF-8 that arrives in chunks", level="medium", stage="understand",
    tags=["from_utf8", "Utf8Error", "valid_up_to", "error_len", "from_utf8_lossy"],
    teaches=[
        "`str::from_utf8` fails with a `Utf8Error` that says how much was valid (`valid_up_to`) and whether the rest is bad (`error_len() == Some(n)`) or just cut short (`None`).",
        "A character split across two reads is not an error: keep its first bytes until the next chunk arrives.",
        "Decoding each chunk with `from_utf8_lossy` on its own corrupts every character that straddles a boundary.",
    ],
    statement="""
        Bytes from a socket arrive in arbitrary chunks, so a multi-byte character can be split between two reads.
        Write a streaming decoder:

        - `push(chunk, out)` appends the decoded text of `chunk` to `out`. Invalid bytes become U+FFFD exactly as
          `String::from_utf8_lossy` replaces them. If the chunk ends partway through a character, hold those bytes
          and finish the character with the next chunk.
        - `finish(out)` ends the input: if a character was left unfinished, append one U+FFFD.

        Whatever the chunking, the output must equal `String::from_utf8_lossy` of all the bytes joined together.
    """,
    examples=[('push([0xC3]), push([0xA9]), finish', '"é"'), ('push(b"a\\xffb"), finish', '"a\\u{FFFD}b"'), ('push([0x61, 0xE2, 0x82]), finish', '"a\\u{FFFD}"')],
    starter=UTF8_STARTER,
    solution=UTF8_SOL,
    visible=[
        UTF8_TESTS,
        dc("whole_chunk", 'b"hello"', ['b"hello"'], '"hello".to_string()'),
        dc("char_split_in_two", "[0xC3] then [0xA9]", ['&[0xC3]', '&[0xA9]'], '"é".to_string()'),
        dc("invalid_byte_replaced", 'b"a\\xffb"', ['b"a\\xffb"'], '"a\\u{FFFD}b".to_string()'),
        dc("unfinished_at_the_end", 'b"ab\\xe2\\x82", then finish', ['b"ab\\xe2\\x82"'], '"ab\\u{FFFD}".to_string()'),
        dc("emoji_one_byte_at_a_time", "🦀 as four 1-byte chunks", ['&[0xF0]', '&[0x9F]', '&[0xA6]', '&[0x80]'], '"🦀".to_string()'),
    ],
    hidden=[
        UTF8_TESTS,
        dc("nothing", "no chunks", [], "String::new()"),
        dc("empty_chunks", "[], b\"a\", []", ['&[]', 'b"a"', '&[]'], '"a".to_string()'),
        dc("split_then_bad_continuation", "[0xE2] then b\"A\"", ['&[0xE2]', 'b"A"'], '"\\u{FFFD}A".to_string()'),
        dc("two_bytes_of_three_then_bad", "[0xE2, 0x82] then b\"A\"", ['&[0xE2, 0x82]', 'b"A"'], '"\\u{FFFD}A".to_string()'),
        dc("completes_and_leaves_a_new_tail", "[0xC3], [0xA9, 0xE6], [0x97, 0xA5]", ['&[0xC3]', '&[0xA9, 0xE6]', '&[0x97, 0xA5]'], '"é日".to_string()'),
        dc("tail_then_text", "[0xF0, 0x9F] then [0xA6, 0x80, b'x']", ['&[0xF0, 0x9F]', "&[0xA6, 0x80, b'x']"], '"🦀x".to_string()'),
        dc("surrogate_bytes", "[0xED, 0xA0, 0x80]", ['&[0xED, 0xA0, 0x80]'], '"\\u{FFFD}\\u{FFFD}\\u{FFFD}".to_string()'),
        dc("overlong_encoding", "[0xC0, 0x80]", ['&[0xC0, 0x80]'], '"\\u{FFFD}\\u{FFFD}".to_string()'),
        dc("stray_continuation_bytes", "[0x80, 0x80] then b\"ok\"", ['&[0x80, 0x80]', 'b"ok"'], '"\\u{FFFD}\\u{FFFD}ok".to_string()'),
        dc("lead_byte_then_lead_byte", "[0xC3] then [0xC3, 0xA9]", ['&[0xC3]', '&[0xC3, 0xA9]'], '"\\u{FFFD}é".to_string()'),
        dc("invalid_then_split", 'b"\\xff\\xc3" then [0xA9]', ['b"\\xff\\xc3"', '&[0xA9]'], '"\\u{FFFD}é".to_string()'),
        T("output_is_appended", "out already holds \"> \"", "out", '"> é".to_string()',
          setup="let mut d = Utf8Decoder::new();\nlet mut out = String::from(\"> \");\nd.push(&[0xC3], &mut out);\nd.push(&[0xA9], &mut out);\nd.finish(&mut out);"),
        T("nothing_emitted_until_complete", "after pushing only [0xE6, 0x97]", "out", "String::new()",
          setup="let mut d = Utf8Decoder::new();\nlet mut out = String::new();\nd.push(&[0xE6, 0x97], &mut out);"),
        r"""
        #[test]
        fn random_vs_from_utf8_lossy() {
            let mut rng = anneal_prelude::Rng::new(7216);
            let alphabet = [0x41u8, 0xC3, 0xA9, 0xE6, 0x97, 0xA5, 0xF0, 0x9F, 0xA6, 0x80, 0xFF, 0xED, 0xA0, 0xC0];
            for _ in 0..500 {
                let len = rng.below(16);
                let bytes: Vec<u8> = (0..len).map(|_| *rng.pick(&alphabet)).collect();
                let mut cuts: Vec<usize> = (0..rng.below(5)).map(|_| rng.below(len + 1)).collect();
                cuts.sort();
                let mut chunks: Vec<&[u8]> = Vec::new();
                let mut at = 0;
                for &c in &cuts {
                    chunks.push(&bytes[at..c]);
                    at = c;
                }
                chunks.push(&bytes[at..]);
                check!(format!("chunks = {chunks:x?}"), decode(&chunks), String::from_utf8_lossy(&bytes).into_owned());
            }
        }

        #[test]
        fn scale_1mb_in_small_chunks() {
            let text = "aé日🦀".repeat(100_000);
            let bytes = text.as_bytes();
            for size in [1, 3, 7] {
                let chunks: Vec<&[u8]> = bytes.chunks(size).collect();
                check!(format!("\"aé日🦀\" × 100000 in {size}-byte chunks"), decode(&chunks) == text, true);
            }
        }
        """,
    ],
    wrong=dict(
        each_chunk_on_its_own="""
            #[derive(Default)]
            pub struct Utf8Decoder {}

            impl Utf8Decoder {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn push(&mut self, chunk: &[u8], out: &mut String) {
                    out.push_str(&String::from_utf8_lossy(chunk));
                }

                pub fn finish(self, _out: &mut String) {}
            }
        """,
        finish_drops_the_tail=sub(UTF8_SOL, """if !self.pending.is_empty() {
                    out.push(char::REPLACEMENT_CHARACTER);
                }""", "let _ = out;"),
        every_error_waits=sub(UTF8_SOL, """match e.error_len() {
                                Some(len) => {
                                    out.push(char::REPLACEMENT_CHARACTER);
                                    input = &bad[len..];
                                }
                                None => {
                                    self.pending.extend_from_slice(bad);
                                    return;
                                }
                            }""", """self.pending.extend_from_slice(bad);
                            return;"""),
        one_replacement_per_byte=sub(UTF8_SOL, "input = &bad[len..];", "input = &bad[1..];\n                                    let _ = len;"),
    ),
    hints=[("rust", "`std::str::from_utf8(bytes)` → `Err(e)`: `&bytes[..e.valid_up_to()]` is valid UTF-8. `e.error_len()` is `Some(n)` for `n` bad bytes to replace and skip, `None` when the input just ended mid-character."),
           ("approach", "Keep the unfinished bytes in a small `Vec<u8>`. On the next push, put them in front of the new chunk and decode from there."),
           ("edge case", "The held bytes may turn out invalid once the next byte arrives (`[0xE2]` then `b\"A\"` is `\"\\u{FFFD}A\"`): decode them, don't assume they'll complete.")],
    notes=("""`from_utf8` doesn't just say "invalid": `valid_up_to()` is how many bytes are fine, and `error_len()` distinguishes a real error (`Some(n)`: replace and skip `n` bytes, which is how `from_utf8_lossy` produces one U+FFFD per maximal invalid subpart) from a truncated character (`None`: wait for more). That second case is the whole job of a streaming decoder, and the difference between this and calling `from_utf8_lossy` on each read. This version copies the chunk behind the held bytes when there are any; a tighter one completes just the held character from the first 1–3 bytes of the chunk and decodes the rest in place. `BufRead::read_line` has the same problem and solves it by buffering. Syntax to remember: `std::str::from_utf8(&b)` → `Result<&str, Utf8Error>`, `String::from_utf8(vec)` (takes ownership, `into_bytes()` on the error gives it back), `e.valid_up_to()`, `e.error_len()`, `String::from_utf8_lossy(&b)` → `Cow<str>`, `char::REPLACEMENT_CHARACTER`, `std::str::from_utf8_unchecked` (unsafe).""", "O(n) over all chunks", "O(1) held between chunks"),
    follow_up="`std::str::from_utf8(good).unwrap()` re-validates bytes that were just validated. When is `from_utf8_unchecked` justified here, and what would you write in its `// SAFETY:` comment?",
    related=["S1"],
))


# ---------------------------------------------------------------- build (hard)

P.append(dict(
    slug="parse-url-borrowed", title="Parse a URL into borrowed parts", level="hard", stage="build",
    tags=["split_once", "lifetimes", "zero-copy"],
    teaches=["A struct of `&'a str` fields borrowing one input.", "`?` on `Option` for each required piece."],
    statement="""
        Parse `scheme://host[:port][/path][?query]` into borrowed parts.

        - `scheme` and `host` must be non-empty.
        - `port`, if present, must be a valid `u16`.
        - `path` defaults to `"/"`.
        - `query` is split on `&` into `(key, value)` pairs; empty pieces are skipped, and a piece with no `=`
          has value `""`.

        Return `None` for anything malformed.
    """,
    examples=[('"https://example.com:8080/a/b?x=1&y=2"', 'scheme "https", host "example.com", port 8080, path "/a/b", query [("x","1"), ("y","2")]')],
    starter="""
        #[derive(Debug, PartialEq)]
        pub struct Url<'a> {
            pub scheme: &'a str,
            pub host: &'a str,
            pub port: Option<u16>,
            pub path: &'a str,
            pub query: Vec<(&'a str, &'a str)>,
        }

        pub fn parse_url(s: &str) -> Option<Url<'_>> {
            todo!()
        }
    """,
    solution="""
        #[derive(Debug, PartialEq)]
        pub struct Url<'a> {
            pub scheme: &'a str,
            pub host: &'a str,
            pub port: Option<u16>,
            pub path: &'a str,
            pub query: Vec<(&'a str, &'a str)>,
        }

        pub fn parse_url(s: &str) -> Option<Url<'_>> {
            let (scheme, rest) = s.split_once("://")?;
            let (rest, query) = rest.split_once('?').unwrap_or((rest, ""));
            let (authority, path) = match rest.find('/') {
                Some(i) => rest.split_at(i),
                None => (rest, "/"),
            };
            let (host, port) = match authority.split_once(':') {
                Some((h, p)) => (h, Some(p.parse().ok()?)),
                None => (authority, None),
            };
            if scheme.is_empty() || host.is_empty() {
                return None;
            }
            let query = query
                .split('&')
                .filter(|kv| !kv.is_empty())
                .map(|kv| kv.split_once('=').unwrap_or((kv, "")))
                .collect();
            Some(Url { scheme, host, port, path, query })
        }
    """,
    visible=[
        T("full", '"https://example.com:8080/a/b?x=1&y=2"', 'parse_url("https://example.com:8080/a/b?x=1&y=2")',
          'Some(Url { scheme: "https", host: "example.com", port: Some(8080), path: "/a/b", query: vec![("x", "1"), ("y", "2")] })'),
        T("minimal", '"http://h"', 'parse_url("http://h")', 'Some(Url { scheme: "http", host: "h", port: None, path: "/", query: vec![] })'),
        T("port_no_path", '"http://h:80"', 'parse_url("http://h:80")', 'Some(Url { scheme: "http", host: "h", port: Some(80), path: "/", query: vec![] })'),
        T("path_no_port", '"https://ex.org/docs"', 'parse_url("https://ex.org/docs")', 'Some(Url { scheme: "https", host: "ex.org", port: None, path: "/docs", query: vec![] })'),
        T("bad_port", '"http://h:abc"', 'parse_url("http://h:abc")', "None"),
    ],
    hidden=[
        T("empty_host", '"ftp://:21/"', 'parse_url("ftp://:21/")', "None"),
        T("port_too_big", '"http://h:99999/"', 'parse_url("http://h:99999/")', "None"),
        T("no_scheme", '"example.com/x"', 'parse_url("example.com/x")', "None"),
        T("flag_query", '"http://h?flag&&a="', 'parse_url("http://h?flag&&a=").map(|u| (u.path, u.query))', 'Some(("/", vec![("flag", ""), ("a", "")]))'),
        T("borrows_input", "host points into the input", "same", "true",
          setup='let s = String::from("http://host/p");\nlet u = parse_url(&s).unwrap();\nlet same = std::ptr::eq(u.host.as_ptr(), s[7..].as_ptr());'),
        T("empty_scheme", '"://h"', 'parse_url("://h")', "None"),
        T("empty_port", '"http://h:/"', 'parse_url("http://h:/")', "None"),
        T("port_bounds", '"http://h:0", "http://h:65535", "http://h:65536"', '(parse_url("http://h:0").map(|u| u.port), parse_url("http://h:65535").map(|u| u.port), parse_url("http://h:65536"))', "(Some(Some(0)), Some(Some(65535)), None)"),
        T("query_without_path", '"http://h?a=1"', 'parse_url("http://h?a=1").map(|u| (u.path, u.query))', 'Some(("/", vec![("a", "1")]))'),
        T("value_with_equals", '"http://h/?a=b=c"', 'parse_url("http://h/?a=b=c").map(|u| u.query)', 'Some(vec![("a", "b=c")])'),
        T("empty_query", '"http://h/p?"', 'parse_url("http://h/p?").map(|u| (u.path, u.query))', 'Some(("/p", vec![]))'),
        T("question_mark_in_query", '"http://h?a=?&b"', 'parse_url("http://h?a=?&b").map(|u| u.query)', 'Some(vec![("a", "?"), ("b", "")])'),
        T("trailing_slash_path", '"http://h/a/"', 'parse_url("http://h/a/").map(|u| u.path)', 'Some("/a/")'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2216);
            let schemes = ["http", "ftp", "a"];
            let hosts = ["h", "ex.org", "1.2.3.4"];
            let paths = ["", "/", "/a", "/a/b.c"];
            let keys = ["k", "x"];
            let values = ["", "1", "v=w"];
            for _ in 0..300 {
                let (scheme, host, path) = (*rng.pick(&schemes), *rng.pick(&hosts), *rng.pick(&paths));
                let port = if rng.bool() { Some(rng.below(65_536) as u16) } else { None };
                let mut s = format!("{scheme}://{host}");
                if let Some(p) = port {
                    s += &format!(":{p}");
                }
                s += path;
                let mut query = Vec::new();
                if rng.bool() {
                    let mut parts = Vec::new();
                    for _ in 0..rng.below(4) {
                        let (k, v) = (*rng.pick(&keys), *rng.pick(&values));
                        query.push((k, v));
                        parts.push(if v.is_empty() && rng.bool() { k.to_string() } else { format!("{k}={v}") });
                    }
                    s += "?";
                    s += &parts.join("&");
                }
                let want = Url { scheme, host, port, path: if path.is_empty() { "/" } else { path }, query };
                check!(format!("s = {s:?}"), parse_url(&s), Some(want));
            }
        }
        """,
    ],
    wrong=dict(
        path_without_slash="""
            #[derive(Debug, PartialEq)]
            pub struct Url<'a> {
                pub scheme: &'a str,
                pub host: &'a str,
                pub port: Option<u16>,
                pub path: &'a str,
                pub query: Vec<(&'a str, &'a str)>,
            }

            pub fn parse_url(s: &str) -> Option<Url<'_>> {
                let (scheme, rest) = s.split_once("://")?;
                let (rest, query) = rest.split_once('?').unwrap_or((rest, ""));
                let (authority, path) = rest.split_once('/').unwrap_or((rest, "/"));
                let (host, port) = match authority.split_once(':') {
                    Some((h, p)) => (h, Some(p.parse().ok()?)),
                    None => (authority, None),
                };
                if scheme.is_empty() || host.is_empty() {
                    return None;
                }
                let query = query
                    .split('&')
                    .filter(|kv| !kv.is_empty())
                    .map(|kv| kv.split_once('=').unwrap_or((kv, "")))
                    .collect();
                Some(Url { scheme, host, port, path, query })
            }
        """,
        port_wraps="""
            #[derive(Debug, PartialEq)]
            pub struct Url<'a> {
                pub scheme: &'a str,
                pub host: &'a str,
                pub port: Option<u16>,
                pub path: &'a str,
                pub query: Vec<(&'a str, &'a str)>,
            }

            pub fn parse_url(s: &str) -> Option<Url<'_>> {
                let (scheme, rest) = s.split_once("://")?;
                let (rest, query) = rest.split_once('?').unwrap_or((rest, ""));
                let (authority, path) = match rest.find('/') {
                    Some(i) => rest.split_at(i),
                    None => (rest, "/"),
                };
                let (host, port) = match authority.split_once(':') {
                    Some((h, p)) => (h, Some(p.parse::<u32>().ok()? as u16)),
                    None => (authority, None),
                };
                if scheme.is_empty() || host.is_empty() {
                    return None;
                }
                let query = query
                    .split('&')
                    .filter(|kv| !kv.is_empty())
                    .map(|kv| kv.split_once('=').unwrap_or((kv, "")))
                    .collect();
                Some(Url { scheme, host, port, path, query })
            }
        """,
        keeps_empty_query_pieces="""
            #[derive(Debug, PartialEq)]
            pub struct Url<'a> {
                pub scheme: &'a str,
                pub host: &'a str,
                pub port: Option<u16>,
                pub path: &'a str,
                pub query: Vec<(&'a str, &'a str)>,
            }

            pub fn parse_url(s: &str) -> Option<Url<'_>> {
                let (scheme, rest) = s.split_once("://")?;
                let (rest, query) = match rest.split_once('?') {
                    Some((r, q)) => (r, Some(q)),
                    None => (rest, None),
                };
                let (authority, path) = match rest.find('/') {
                    Some(i) => rest.split_at(i),
                    None => (rest, "/"),
                };
                let (host, port) = match authority.split_once(':') {
                    Some((h, p)) => (h, Some(p.parse().ok()?)),
                    None => (authority, None),
                };
                if scheme.is_empty() || host.is_empty() {
                    return None;
                }
                let query = match query {
                    Some(q) => q.split('&').map(|kv| kv.split_once('=').unwrap_or((kv, ""))).collect(),
                    None => Vec::new(),
                };
                Some(Url { scheme, host, port, path, query })
            }
        """,
    ),
    hints=[("rust", "Peel pieces off with `split_once`: `\"://\"`, then `'?'`, then the first `/`, then `':'`."),
           ("rust", "`p.parse().ok()?` inside a match arm returns `None` from the whole function on a bad port."),
           ("rust", "`split_at(i)` keeps the `/` in the path, which is what you want.")],
    notes=("Every field is a slice of the input, so parsing allocates only the query Vec. The `'_` in `Url<'_>` ties the result to `s`. Syntax to remember: `s.split_once(\"://\")?`, `rest.split_once('?').unwrap_or((rest, \"\"))`, `s.split_at(i)` (keeps the delimiter on the right), `p.parse().ok()?`, `pair.split_once('=').unwrap_or((pair, \"\"))`.", "O(n)", "O(q)"),
    follow_up="Real URLs percent-encode. Where would decoding force a `Cow<'a, str>`?",
    related=["L3"],
))

P.append(dict(
    slug="zero-copy-split-iterator", title="Zero-copy split iterator", level="hard", stage="build",
    tags=["Iterator", "DoubleEndedIterator", "lifetimes"],
    teaches=["`type Item = &'a str`: items borrow the text, not the iterator.", "Two ends sharing one remaining slice."],
    statement="""
        Implement `split_on(s, delim)` with exactly the behaviour of `s.split(delim)`, from both ends: it
        yields `&str` pieces of `s`, including empty ones. Don't call any of `str`'s split methods.
    """,
    examples=[('split_on("a,b,,c", \',\')', '["a", "b", "", "c"]'), ('split_on("", \',\')', '[""]')],
    starter="""
        pub struct SplitOn<'a> {
            /// What hasn't been yielded yet; `None` once both ends have met.
            rest: Option<&'a str>,
            delim: char,
        }

        pub fn split_on(s: &str, delim: char) -> SplitOn<'_> {
            SplitOn { rest: Some(s), delim }
        }

        impl<'a> Iterator for SplitOn<'a> {
            type Item = &'a str;

            fn next(&mut self) -> Option<&'a str> {
                todo!()
            }
        }

        impl DoubleEndedIterator for SplitOn<'_> {
            fn next_back(&mut self) -> Option<Self::Item> {
                todo!()
            }
        }
    """,
    solution="""
        pub struct SplitOn<'a> {
            /// What hasn't been yielded yet; `None` once both ends have met.
            rest: Option<&'a str>,
            delim: char,
        }

        pub fn split_on(s: &str, delim: char) -> SplitOn<'_> {
            SplitOn { rest: Some(s), delim }
        }

        impl<'a> Iterator for SplitOn<'a> {
            type Item = &'a str;

            fn next(&mut self) -> Option<&'a str> {
                let rest = self.rest?;
                match rest.find(self.delim) {
                    Some(i) => {
                        self.rest = Some(&rest[i + self.delim.len_utf8()..]);
                        Some(&rest[..i])
                    }
                    None => {
                        self.rest = None;
                        Some(rest)
                    }
                }
            }
        }

        impl DoubleEndedIterator for SplitOn<'_> {
            fn next_back(&mut self) -> Option<Self::Item> {
                let rest = self.rest?;
                match rest.rfind(self.delim) {
                    Some(i) => {
                        self.rest = Some(&rest[..i]);
                        Some(&rest[i + self.delim.len_utf8()..])
                    }
                    None => {
                        self.rest = None;
                        Some(rest)
                    }
                }
            }
        }
    """,
    visible=[
        T("pieces", "\"a,b,,c\", ','", "split_on(\"a,b,,c\", ',').collect::<Vec<_>>()", 'vec!["a", "b", "", "c"]'),
        T("empty_input", "\"\", ','", "split_on(\"\", ',').collect::<Vec<_>>()", 'vec![""]'),
        T("no_delimiter", "\"abc\", ','", "split_on(\"abc\", ',').collect::<Vec<_>>()", 'vec!["abc"]'),
        T("only_delimiter", "\",\", ','", "split_on(\",\", ',').collect::<Vec<_>>()", 'vec!["", ""]'),
        T("from_the_back", "\"a,b\", ',' reversed", "split_on(\"a,b\", ',').rev().collect::<Vec<_>>()", 'vec!["b", "a"]'),
    ],
    hidden=[
        T("trailing", "\"a,\", ','", "split_on(\"a,\", ',').collect::<Vec<_>>()", 'vec!["a", ""]'),
        T("reversed", "\"a,b,c\", ',' reversed", "split_on(\"a,b,c\", ',').rev().collect::<Vec<_>>()", 'vec!["c", "b", "a"]'),
        T("both_ends", "\"1-2-3-4\": next, next_back, next, next_back, next", "(it.next(), it.next_back(), it.next(), it.next_back(), it.next())",
          '(Some("1"), Some("4"), Some("2"), Some("3"), None)', setup="let mut it = split_on(\"1-2-3-4\", '-');"),
        T("unicode_delim", "\"x→y→\", '→'", "split_on(\"x→y→\", '→').collect::<Vec<_>>()", 'vec!["x", "y", ""]'),
        T("items_outlive_iterator", "keep the first piece after dropping the iterator", "first", 'Some("ab")',
          setup="let text = String::from(\"ab cd\");\nlet first;\n{\n    let mut it = split_on(&text, ' ');\n    first = it.next();\n}"),
        T("matches_std", "same as str::split on a mixed string", "ours == theirs", "true",
          setup="let s = \";;a;bc;;d;\";\nlet ours: Vec<&str> = split_on(s, ';').collect();\nlet theirs: Vec<&str> = s.split(';').collect();"),
        T("leading", "\",a\", ','", "split_on(\",a\", ',').collect::<Vec<_>>()", 'vec!["", "a"]'),
        T("two_delimiters", "\",,\", ','", "split_on(\",,\", ',').collect::<Vec<_>>()", 'vec!["", "", ""]'),
        T("ends_meet_on_empty", "\",\": next, next_back, next", "(it.next(), it.next_back(), it.next())", '(Some(""), Some(""), None)', setup="let mut it = split_on(\",\", ',');"),
        T("stays_done", "\"a\": next, next, next_back", "(it.next(), it.next(), it.next_back())", '(Some("a"), None, None)', setup="let mut it = split_on(\"a\", ',');"),
        T("unicode_delim_at_ends", "\"→a→\", '→'", "split_on(\"→a→\", '→').rev().collect::<Vec<_>>()", 'vec!["", "a", ""]'),
        T("unicode_pieces", "\"é,日本,🦀\", ','", "split_on(\"é,日本,🦀\", ',').collect::<Vec<_>>()", 'vec!["é", "日本", "🦀"]'),
        """
        #[test]
        fn random_vs_std() {
            let mut rng = anneal_prelude::Rng::new(2217);
            for _ in 0..400 {
                let len = rng.below(10);
                let s = rng.string(len, "a,é→");
                let delim = *rng.pick(&[',', '→']);
                let mut ours = split_on(&s, delim);
                let mut theirs = s.split(delim);
                let mut steps = Vec::new();
                for _ in 0..8 {
                    let back = rng.bool();
                    steps.push(if back { "next_back" } else { "next" });
                    let (a, b) = if back { (ours.next_back(), theirs.next_back()) } else { (ours.next(), theirs.next()) };
                    check!(format!("s = {s:?}, delim = {delim:?}, calls = {steps:?}"), a, b);
                }
            }
        }

        #[test]
        fn scale_200k_pieces() {
            let s = "ab,".repeat(200_000);
            let pieces: Vec<&str> = split_on(&s, ',').collect();
            check!("s = \\"ab,ab,…\\" (200001 pieces)", (pieces.len(), pieces[199_999], pieces[200_000]), (200_001, "ab", ""));
        }
        """,
    ],
    wrong=dict(
        steps_one_byte="""
            pub struct SplitOn<'a> {
                /// What hasn't been yielded yet; `None` once both ends have met.
                rest: Option<&'a str>,
                delim: char,
            }

            pub fn split_on(s: &str, delim: char) -> SplitOn<'_> {
                SplitOn { rest: Some(s), delim }
            }

            impl<'a> Iterator for SplitOn<'a> {
                type Item = &'a str;

                fn next(&mut self) -> Option<&'a str> {
                    let rest = self.rest?;
                    match rest.find(self.delim) {
                        Some(i) => {
                            self.rest = Some(&rest[i + 1..]);
                            Some(&rest[..i])
                        }
                        None => {
                            self.rest = None;
                            Some(rest)
                        }
                    }
                }
            }

            impl DoubleEndedIterator for SplitOn<'_> {
                fn next_back(&mut self) -> Option<Self::Item> {
                    let rest = self.rest?;
                    match rest.rfind(self.delim) {
                        Some(i) => {
                            self.rest = Some(&rest[..i]);
                            Some(&rest[i + 1..])
                        }
                        None => {
                            self.rest = None;
                            Some(rest)
                        }
                    }
                }
            }
        """,
        empty_means_done="""
            pub struct SplitOn<'a> {
                /// What hasn't been yielded yet; `None` once both ends have met.
                rest: Option<&'a str>,
                delim: char,
            }

            pub fn split_on(s: &str, delim: char) -> SplitOn<'_> {
                SplitOn { rest: Some(s), delim }
            }

            impl<'a> Iterator for SplitOn<'a> {
                type Item = &'a str;

                fn next(&mut self) -> Option<&'a str> {
                    let rest = self.rest.filter(|r| !r.is_empty())?;
                    match rest.find(self.delim) {
                        Some(i) => {
                            self.rest = Some(&rest[i + self.delim.len_utf8()..]);
                            Some(&rest[..i])
                        }
                        None => {
                            self.rest = None;
                            Some(rest)
                        }
                    }
                }
            }

            impl DoubleEndedIterator for SplitOn<'_> {
                fn next_back(&mut self) -> Option<Self::Item> {
                    let rest = self.rest.filter(|r| !r.is_empty())?;
                    match rest.rfind(self.delim) {
                        Some(i) => {
                            self.rest = Some(&rest[..i]);
                            Some(&rest[i + self.delim.len_utf8()..])
                        }
                        None => {
                            self.rest = None;
                            Some(rest)
                        }
                    }
                }
            }
        """,
    ),
    hints=[("rust", "`next` returns `Option<&'a str>`, not a borrow of `self`: slice `rest` (a `&'a str` you copied out), never `self`."),
           ("approach", "`find` for the front, `rfind` for the back. When no delimiter is left, yield all of `rest` and set it to `None`."),
           ("edge case", "Step past the delimiter by `delim.len_utf8()`, not 1.")],
    notes=("Copying `self.rest` out (it's a `&'a str`, which is `Copy`) is what lets the items outlive the `&mut self` borrow. Using `Option` for 'finished' distinguishes an empty last piece from no piece. Syntax to remember: `impl<'a> Iterator for SplitOn<'a> { type Item = &'a str; fn next(&mut self) -> Option<&'a str> }`, `impl DoubleEndedIterator` with `next_back`, `let rest = self.rest?;` (a `&str` is `Copy`), `s.find(c)` / `s.rfind(c)`, `c.len_utf8()`.", "O(n) total", "O(1)"),
    follow_up="Generalise the delimiter to any `Pattern`-like trait: what would its methods be?",
    rules=dict(methods=["split", "rsplit", "splitn", "rsplitn", "split_terminator", "rsplit_terminator", "split_once", "rsplit_once", "split_inclusive", "split_whitespace", "split_ascii_whitespace", "lines"]),
    related=["L3", "L5"],
))

P.append(dict(
    slug="template-formatter", title="A tiny {name} template formatter", level="hard", stage="build",
    tags=["char_indices", "Peekable", "error positions"],
    teaches=["A hand-written scanner over `char_indices().peekable()`.", "`next_if` to consume `{{` and `}}` escapes."],
    statement="""
        Render `template`, replacing `{name}` with `vars[name]`. `{{` and `}}` are a literal `{` and `}`.

        Errors carry the byte offset where they start:

        - `Unknown(name)` for a name not in `vars`.
        - `Unclosed(pos)` for a `{` with no closing `}`.
        - `StrayBrace(pos)` for a lone `}`.
    """,
    examples=[('"Hi {name}!", {name: "Ada"}', 'Ok("Hi Ada!")'), ('"{{x}}"', 'Ok("{x}")')],
    starter="""
        use std::collections::HashMap;

        #[derive(Debug, PartialEq)]
        pub enum TemplateError {
            Unknown(String),
            Unclosed(usize),
            StrayBrace(usize),
        }

        pub fn render(template: &str, vars: &HashMap<&str, &str>) -> Result<String, TemplateError> {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashMap;

        #[derive(Debug, PartialEq)]
        pub enum TemplateError {
            Unknown(String),
            Unclosed(usize),
            StrayBrace(usize),
        }

        pub fn render(template: &str, vars: &HashMap<&str, &str>) -> Result<String, TemplateError> {
            let mut out = String::with_capacity(template.len());
            let mut chars = template.char_indices().peekable();
            while let Some((i, c)) = chars.next() {
                match c {
                    '{' => {
                        if chars.next_if(|&(_, n)| n == '{').is_some() {
                            out.push('{');
                            continue;
                        }
                        let close = i + template[i..].find('}').ok_or(TemplateError::Unclosed(i))?;
                        let name = &template[i + 1..close];
                        let value = vars.get(name).ok_or_else(|| TemplateError::Unknown(name.to_string()))?;
                        out.push_str(value);
                        while chars.next_if(|&(j, _)| j <= close).is_some() {}
                    }
                    '}' => {
                        if chars.next_if(|&(_, n)| n == '}').is_none() {
                            return Err(TemplateError::StrayBrace(i));
                        }
                        out.push('}');
                    }
                    _ => out.push(c),
                }
            }
            Ok(out)
        }
    """,
    visible=[
        T("fills", '"Hi {name}, welcome to {lang}!"', 'render("Hi {name}, welcome to {lang}!", &vars)', 'Ok("Hi Ada, welcome to Rust!".to_string())',
          setup='let vars = std::collections::HashMap::from([("name", "Ada"), ("lang", "Rust")]);'),
        T("escapes", '"{{literal}}"', 'render("{{literal}}", &vars)', 'Ok("{literal}".to_string())',
          setup="let vars = std::collections::HashMap::new();"),
        T("no_placeholders", '"plain text"', 'render("plain text", &vars)', 'Ok("plain text".to_string())', setup="let vars = std::collections::HashMap::new();"),
        T("closing_escape", '"}} and {{"', 'render("}} and {{", &vars)', 'Ok("} and {".to_string())', setup="let vars = std::collections::HashMap::new();"),
        T("same_name_twice", '"{a}-{a}", a = "1"', 'render("{a}-{a}", &vars)', 'Ok("1-1".to_string())', setup='let vars = std::collections::HashMap::from([("a", "1")]);'),
    ],
    hidden=[
        T("unknown", '"{missing}"', 'render("{missing}", &vars)', 'Err(TemplateError::Unknown("missing".to_string()))', setup='let vars = std::collections::HashMap::from([("name", "Ada")]);'),
        T("unclosed", '"oops {name"', 'render("oops {name", &vars)', "Err(TemplateError::Unclosed(5))", setup='let vars = std::collections::HashMap::from([("name", "Ada")]);'),
        T("stray", '"a } b"', 'render("a } b", &vars)', "Err(TemplateError::StrayBrace(2))", setup="let vars = std::collections::HashMap::new();"),
        T("unicode_offsets", '"é}"', 'render("é}", &vars)', "Err(TemplateError::StrayBrace(2))", setup="let vars = std::collections::HashMap::new();"),
        T("adjacent", '"{a}{b}{{"', 'render("{a}{b}{{", &vars)', 'Ok("12{".to_string())', setup='let vars = std::collections::HashMap::from([("a", "1"), ("b", "2")]);'),
        T("empty_name", '"{}"', 'render("{}", &vars)', 'Err(TemplateError::Unknown(String::new()))', setup="let vars = std::collections::HashMap::new();"),
        T("value_not_rerendered", '"{a}", a = "{b}"', 'render("{a}", &vars)', 'Ok("{b}".to_string())', setup='let vars = std::collections::HashMap::from([("a", "{b}"), ("b", "no")]);'),
        T("escaped_name", '"{{name}}"', 'render("{{name}}", &vars)', 'Ok("{name}".to_string())', setup='let vars = std::collections::HashMap::from([("name", "Ada")]);'),
        T("unclosed_after_unicode", '"é{x"', 'render("é{x", &vars)', "Err(TemplateError::Unclosed(2))", setup="let vars = std::collections::HashMap::new();"),
        T("stray_at_end", '"abc}"', 'render("abc}", &vars)', "Err(TemplateError::StrayBrace(3))", setup="let vars = std::collections::HashMap::new();"),
        T("three_closing", '"}}}"', 'render("}}}", &vars)', "Err(TemplateError::StrayBrace(2))", setup="let vars = std::collections::HashMap::new();"),
        T("braces_around_placeholder", '"{{{a}}}", a = "1"', 'render("{{{a}}}", &vars)', 'Ok("{1}".to_string())', setup='let vars = std::collections::HashMap::from([("a", "1")]);'),
        T("empty_template", '""', 'render("", &vars)', "Ok(String::new())", setup="let vars = std::collections::HashMap::new();"),
        T("spaces_in_name", '"{ a }"', 'render("{ a }", &vars)', 'Err(TemplateError::Unknown(" a ".to_string()))', setup='let vars = std::collections::HashMap::from([("a", "1")]);'),
        T("unicode_name_and_value", '"{名前}さん", 名前 = "太郎"', 'render("{名前}さん", &vars)', 'Ok("太郎さん".to_string())', setup='let vars = std::collections::HashMap::from([("名前", "太郎")]);'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2218);
            let vars = std::collections::HashMap::from([("a", "1"), ("bb", "22")]);
            let pieces = [("{a}", "1"), ("{bb}", "22"), ("{{", "{"), ("}}", "}"), ("x", "x"), ("é", "é")];
            for _ in 0..400 {
                let mut template = String::new();
                let mut want = String::new();
                for _ in 0..rng.below(8) {
                    let (t, w) = *rng.pick(&pieces);
                    template += t;
                    want += w;
                }
                let want = if rng.below(4) == 0 {
                    let at = template.len();
                    template.push('}');
                    Err(TemplateError::StrayBrace(at))
                } else {
                    Ok(want)
                };
                check!(format!("template = {template:?}, vars = {{a: 1, bb: 22}}"), render(&template, &vars), want);
            }
        }

        #[test]
        fn scale_200k_placeholders() {
            let vars = std::collections::HashMap::from([("a", "x")]);
            let template = "{a}".repeat(200_000);
            check!("template = \\"{a}{a}…\\" (200000 placeholders)", render(&template, &vars).map(|s| s.len()), Ok(200_000));
        }
        """,
    ],
    wrong=dict(
        lone_close_is_literal="""
            use std::collections::HashMap;

            #[derive(Debug, PartialEq)]
            pub enum TemplateError {
                Unknown(String),
                Unclosed(usize),
                StrayBrace(usize),
            }

            pub fn render(template: &str, vars: &HashMap<&str, &str>) -> Result<String, TemplateError> {
                let mut out = String::with_capacity(template.len());
                let mut chars = template.char_indices().peekable();
                while let Some((i, c)) = chars.next() {
                    match c {
                        '{' => {
                            if chars.next_if(|&(_, n)| n == '{').is_some() {
                                out.push('{');
                                continue;
                            }
                            let close = i + template[i..].find('}').ok_or(TemplateError::Unclosed(i))?;
                            let name = &template[i + 1..close];
                            let value = vars.get(name).ok_or_else(|| TemplateError::Unknown(name.to_string()))?;
                            out.push_str(value);
                            while chars.next_if(|&(j, _)| j <= close).is_some() {}
                        }
                        '}' => {
                            chars.next_if(|&(_, n)| n == '}');
                            out.push('}');
                        }
                        _ => out.push(c),
                    }
                }
                Ok(out)
            }
        """,
        char_positions="""
            use std::collections::HashMap;

            #[derive(Debug, PartialEq)]
            pub enum TemplateError {
                Unknown(String),
                Unclosed(usize),
                StrayBrace(usize),
            }

            pub fn render(template: &str, vars: &HashMap<&str, &str>) -> Result<String, TemplateError> {
                let chars: Vec<char> = template.chars().collect();
                let mut out = String::with_capacity(template.len());
                let mut i = 0;
                while i < chars.len() {
                    match chars[i] {
                        '{' if chars.get(i + 1) == Some(&'{') => {
                            out.push('{');
                            i += 2;
                        }
                        '{' => {
                            let close = (i..chars.len()).find(|&j| chars[j] == '}').ok_or(TemplateError::Unclosed(i))?;
                            let name: String = chars[i + 1..close].iter().collect();
                            let value = vars.get(name.as_str()).ok_or(TemplateError::Unknown(name.clone()))?;
                            out.push_str(value);
                            i = close + 1;
                        }
                        '}' if chars.get(i + 1) == Some(&'}') => {
                            out.push('}');
                            i += 2;
                        }
                        '}' => return Err(TemplateError::StrayBrace(i)),
                        c => {
                            out.push(c);
                            i += 1;
                        }
                    }
                }
                Ok(out)
            }
        """,
    ),
    hints=[("rust", "`char_indices().peekable()` gives byte offsets for errors, and `next_if(|&(_, c)| c == '{')` consumes an escape only if it's there."),
           ("approach", "At a `{`, find the matching `}` with `template[i..].find('}')`, look the name up, then skip the iterator past the `}`."),
           ("edge case", "Report byte offsets, not character counts: `\"é}\"` has its `}` at offset 2.")],
    notes=("A small scanner with one character of lookahead handles escapes, placeholders and errors in a single pass. `HashMap<&str, &str>::get` takes a `&str` directly. Syntax to remember: `let mut it = s.char_indices().peekable();`, `while let Some((i, c)) = it.next()`, `it.next_if(|&(_, c)| c == '{')`, `it.peek()`, `s[i..].find('}')`, `map.get(name).ok_or_else(|| E::Unknown(name.to_string()))?`.", "O(n)", "O(n)"),
    follow_up="Add `{name:>8}` style alignment. Where would you parse the spec, and how would you apply it?",
    related=["S1", "S4"],
))

# The validator only accepts rules on fix problems; write problems state their limits in prose.
for p in P:
    if p.get("mode", "write") == "write":
        p.pop("rules", None)

STAGES = [
    ("use", "Use", "easy"),
    ("understand", "Understand", "medium"),
    ("build", "Build", "hard"),
]

if __name__ == "__main__":
    n = write_track("s2-strings-text", "S2", "Strings & text", "S", "core", 2,
                    "Text is UTF-8 bytes: borrow `&str`, own `String`, and never index by position.",
                    STAGES, P)
    print("S2", n)
