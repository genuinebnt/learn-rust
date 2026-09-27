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

P.append(dict(
    slug="bytes-chars-char-indices", title="Bytes vs chars vs char_indices", level="medium", stage="understand",
    tags=["UTF-8", "chars", "char_indices"],
    teaches=["`len()` counts bytes; `chars().count()` counts Unicode scalar values.", "`char_indices` gives byte offsets you can slice at."],
    statement="""
        - `sizes` returns `(bytes, chars)` for `s`.
        - `positions` returns the byte offset of every occurrence of `target`.
        - `nth_char` returns the `n`th character, if there is one.
    """,
    examples=[('sizes("naïve")', "(6, 5)"), ("positions(\"añoño\", 'ñ')", "[1, 4]")],
    starter="""
        pub fn sizes(s: &str) -> (usize, usize) {
            todo!()
        }

        pub fn positions(s: &str, target: char) -> Vec<usize> {
            todo!()
        }

        pub fn nth_char(s: &str, n: usize) -> Option<char> {
            todo!()
        }
    """,
    solution="""
        pub fn sizes(s: &str) -> (usize, usize) {
            (s.len(), s.chars().count())
        }

        pub fn positions(s: &str, target: char) -> Vec<usize> {
            s.char_indices().filter(|&(_, c)| c == target).map(|(i, _)| i).collect()
        }

        pub fn nth_char(s: &str, n: usize) -> Option<char> {
            s.chars().nth(n)
        }
    """,
    visible=[
        T("naive", '"naïve"', 'sizes("naïve")', "(6, 5)"),
        T("byte_offsets", "\"añoño\", 'ñ'", "positions(\"añoño\", 'ñ')", "vec![1, 4]"),
        T("ascii_sizes", '"abc"', 'sizes("abc")', "(3, 3)"),
        T("nth_is_by_char", '"héllo", 2', 'nth_char("héllo", 2)', "Some('l')"),
        T("no_occurrence", "\"abc\", 'z'", "positions(\"abc\", 'z')", "Vec::<usize>::new()"),
    ],
    hidden=[
        T("emoji", '"🦀!"', 'sizes("🦀!")', "(5, 2)"),
        T("nth", '"héllo", 1 and 9', '(nth_char("héllo", 1), nth_char("héllo", 9))', "(Some('é'), None)"),
        T("offsets_slice_cleanly", "every offset from positions(\"x→y→z\", '→') is a char boundary", "ok", "true",
          setup="let s = \"x→y→z\";\nlet ok = positions(s, '→').iter().all(|&i| s.is_char_boundary(i) && s[i..].starts_with('→'));"),
        T("empty_everything", '""', "(sizes(\"\"), positions(\"\", 'a'), nth_char(\"\", 0))", "((0, 0), vec![], None)"),
        T("emoji_target", "\"🦀a🦀\", '🦀'", "positions(\"🦀a🦀\", '🦀')", "vec![0, 5]"),
        T("ascii_after_unicode", "\"éaéa\", 'a'", "positions(\"éaéa\", 'a')", "vec![2, 5]"),
        T("adjacent", "\"ññ\", 'ñ'", "positions(\"ññ\", 'ñ')", "vec![0, 2]"),
        T("nth_last_and_past", '"héllo", 4 and 5', '(nth_char("héllo", 4), nth_char("héllo", 5))', "(Some('o'), None)"),
        T("combining_mark", '"e\\u{301}" (e + combining acute)', 'sizes("e\\u{301}")', "(3, 2)"),
        """
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
            check!("s = \\"aéaé…\\" (200000 chars), target = 'é'", (p.len(), p[0], p[99_999], sizes(&s)), (100_000, 1, 299_998, (300_000, 200_000)));
        }
        """,
    ],
    wrong=dict(
        char_index_positions="""
            pub fn sizes(s: &str) -> (usize, usize) {
                (s.len(), s.chars().count())
            }

            pub fn positions(s: &str, target: char) -> Vec<usize> {
                s.chars().enumerate().filter(|&(_, c)| c == target).map(|(i, _)| i).collect()
            }

            pub fn nth_char(s: &str, n: usize) -> Option<char> {
                s.chars().nth(n)
            }
        """,
        byte_nth="""
            pub fn sizes(s: &str) -> (usize, usize) {
                (s.len(), s.chars().count())
            }

            pub fn positions(s: &str, target: char) -> Vec<usize> {
                s.char_indices().filter(|&(_, c)| c == target).map(|(i, _)| i).collect()
            }

            pub fn nth_char(s: &str, n: usize) -> Option<char> {
                s.as_bytes().get(n).map(|&b| b as char)
            }
        """,
        offsets_by_recounting="""
            pub fn sizes(s: &str) -> (usize, usize) {
                (s.len(), s.chars().count())
            }

            pub fn positions(s: &str, target: char) -> Vec<usize> {
                let mut out = Vec::new();
                for (k, c) in s.chars().enumerate() {
                    if c == target {
                        out.push(s.chars().take(k).map(char::len_utf8).sum());
                    }
                }
                out
            }

            pub fn nth_char(s: &str, n: usize) -> Option<char> {
                s.chars().nth(n)
            }
        """,
    ),
    hints=[("rust", "`str::len` is bytes. A character outside ASCII takes 2–4 bytes in UTF-8."),
           ("rust", "`char_indices()` yields `(byte_offset, char)`; offsets are always valid slice points.")],
    notes=("`chars().nth(n)` is O(n): UTF-8 has no random access by character. That's why `str` can't be indexed by position.", "O(n)", "O(k)"),
    follow_up="What does a user think of as one character that is several `char`s (grapheme clusters)?",
))

P.append(dict(
    slug="fix-slicing-mid-utf8", title="Fix: slicing mid-UTF-8 panics", mode="fix", level="medium", stage="understand",
    tags=["panic", "char boundaries"],
    teaches=["`&s[..n]` takes bytes and panics if `n` splits a character.", "Finding a byte offset with `char_indices().nth(n)`."],
    statement="`prefix` should return the first `n` characters of `s`. It panics on accented text. Fix it.",
    starter="""
        /// The first `n` characters of `s` (all of `s` if it's shorter).
        pub fn prefix(s: &str, n: usize) -> &str {
            if s.len() <= n {
                s
            } else {
                &s[..n]
            }
        }
    """,
    solution="""
        /// The first `n` characters of `s` (all of `s` if it's shorter).
        pub fn prefix(s: &str, n: usize) -> &str {
            match s.char_indices().nth(n) {
                Some((i, _)) => &s[..i],
                None => s,
            }
        }
    """,
    visible=[
        T("ascii", '"hello", 3', 'prefix("hello", 3)', '"hel"'),
        T("accented", '"héllo", 2', 'prefix("héllo", 2)', '"hé"'),
        T("shorter", '"hi", 5', 'prefix("hi", 5)', '"hi"'),
        T("exact_length", '"abc", 3', 'prefix("abc", 3)', '"abc"'),
        T("empty", '"", 2', 'prefix("", 2)', '""'),
    ],
    hidden=[
        T("emoji", '"🦀🦀🦀", 2', 'prefix("🦀🦀🦀", 2)', '"🦀🦀"'),
        T("zero", '"abc", 0', 'prefix("abc", 0)', '""'),
        T("shorter_in_chars_than_bytes", '"日本", 3', 'prefix("日本", 3)', '"日本"'),
        T("zero_unicode", '"é", 0', 'prefix("é", 0)', '""'),
        T("cjk", '"日本語", 2', 'prefix("日本語", 2)', '"日本"'),
        T("exact_char_count", '"日本", 2', 'prefix("日本", 2)', '"日本"'),
        T("mixed", '"a🦀b", 2', 'prefix("a🦀b", 2)', '"a🦀"'),
        T("combining_mark_is_a_char", '"e\\u{301}x", 1', 'prefix("e\\u{301}x", 1)', '"e"'),
        T("huge_n", '"abc", usize::MAX', 'prefix("abc", usize::MAX)', '"abc"'),
        T("borrows_input", "prefix points into its input", "prefix(&s, 2).as_ptr() == s.as_ptr()", "true", setup='let s = String::from("héllo");'),
        """
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
        """,
    ],
    wrong=dict(
        byte_budget="""
            /// The first `n` characters of `s` (all of `s` if it's shorter).
            pub fn prefix(s: &str, n: usize) -> &str {
                if s.len() <= n {
                    s
                } else {
                    let mut end = n;
                    while !s.is_char_boundary(end) {
                        end -= 1;
                    }
                    &s[..end]
                }
            }
        """,
        one_char_too_many="""
            /// The first `n` characters of `s` (all of `s` if it's shorter).
            pub fn prefix(s: &str, n: usize) -> &str {
                match s.char_indices().nth(n) {
                    Some((i, c)) => &s[..i + c.len_utf8()],
                    None => s,
                }
            }
        """,
    ),
    hints=[("rust", "`s.len()` and `&s[..n]` both count bytes, not characters."),
           ("rust", "The byte offset where character `n` starts is `s.char_indices().nth(n)`; if there isn't one, the whole string fits.")],
    notes=("Slicing is by byte offset and panics off a character boundary. `char_indices` only yields boundaries, so slicing at one is always safe.", "O(n)", "O(1)"),
    follow_up="When would you use `s.get(..n)` instead, and what does it return?",
))

P.append(dict(
    slug="fix-len-counts-bytes", title="Fix: len() counts bytes", mode="fix", level="medium", stage="understand",
    tags=["UTF-8", "chars().count()"],
    teaches=["Width calculations need a character count, not `len()`."],
    statement="`center` pads text to a width in characters. It gets accented text wrong. Fix it.",
    starter="""
        /// Centers `s` in a field `width` characters wide, padding with `fill`.
        /// Odd padding puts the extra character on the right.
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
    """,
    solution="""
        /// Centers `s` in a field `width` characters wide, padding with `fill`.
        /// Odd padding puts the extra character on the right.
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
    """,
    visible=[
        T("ascii", "\"ab\", 6, '*'", "center(\"ab\", 6, '*')", rs("**ab**")),
        T("accented", "\"né\", 4, '.'", "center(\"né\", 4, '.')", '".né.".to_string()'),
        T("even_padding", "\"abcd\", 8, '-'", "center(\"abcd\", 8, '-')", rs("--abcd--")),
        T("no_padding_needed", "\"abc\", 3, '*'", "center(\"abc\", 3, '*')", rs("abc")),
        T("odd_extra_right", "\"a\", 4, '*'", "center(\"a\", 4, '*')", rs("*a**")),
    ],
    hidden=[
        T("odd", "\"abc\", 6, '-'", "center(\"abc\", 6, '-')", rs("-abc--")),
        T("too_wide", "\"日本語\", 3, ' '", "center(\"日本語\", 3, ' ')", '"日本語".to_string()'),
        T("multibyte_fill", "\"x\", 3, '·'", "center(\"x\", 3, '·')", '"·x·".to_string()'),
        T("empty", "\"\", 3, 'x'", "center(\"\", 3, 'x')", rs("xxx")),
        T("width_zero", "\"ab\", 0, '*'", "center(\"ab\", 0, '*')", rs("ab")),
        T("emoji", "\"🦀\", 3, '.'", "center(\"🦀\", 3, '.')", '".🦀.".to_string()'),
        T("cjk", "\"日本\", 6, ' '", "center(\"日本\", 6, ' ')", '"  日本  ".to_string()'),
        T("fits_in_chars_not_bytes", "\"éé\", 3, '.'", "center(\"éé\", 3, '.')", '"éé.".to_string()'),
        T("inner_spaces", "\"a b\", 5, '*'", "center(\"a b\", 5, '*')", rs("*a b*")),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2210);
            for _ in 0..300 {
                let len = rng.below(6);
                let s = rng.string(len, "a é日");
                let width = rng.below(10);
                let fill = *rng.pick(&['*', '·']);
                let n = s.chars().count();
                let mut want = String::new();
                if n >= width {
                    want.push_str(&s);
                } else {
                    let left = (width - n) / 2;
                    for _ in 0..left {
                        want.push(fill);
                    }
                    want.push_str(&s);
                    for _ in 0..width - n - left {
                        want.push(fill);
                    }
                }
                check!(format!("s = {s:?}, width = {width}, fill = {fill:?}"), center(&s, width, fill), want);
            }
        }
        """,
    ],
    wrong=dict(
        ascii_only_count="""
            /// Centers `s` in a field `width` characters wide, padding with `fill`.
            /// Odd padding puts the extra character on the right.
            pub fn center(s: &str, width: usize, fill: char) -> String {
                let len = s.bytes().filter(u8::is_ascii).count();
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
        """,
        letters_only="""
            /// Centers `s` in a field `width` characters wide, padding with `fill`.
            /// Odd padding puts the extra character on the right.
            pub fn center(s: &str, width: usize, fill: char) -> String {
                let len = s.chars().filter(|c| c.is_alphanumeric()).count();
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
        """,
    ),
    hints=[("rust", "`\"né\".len()` is 3: `é` takes two bytes. The padding math wants 2.")],
    notes=("Counting chars fixes accented and CJK text. It still isn't display width: CJK characters usually take two terminal columns, and combining marks take none.", "O(n)", "O(n)"),
    follow_up="How would you center text by terminal display width?",
    rules=dict(lines=1),
))

P.append(dict(
    slug="reverse-each-word", title="Reverse each word, Unicode-safe", level="medium", stage="understand",
    tags=["chars().rev()", "collect::<String>"],
    teaches=["Reversing `chars()`, not bytes.", "Collecting chars straight into a `String`."],
    statement="Reverse the characters of each whitespace-separated word, keeping word order. Separate words with single spaces.",
    examples=[('"héllo wörld"', '"olléh dlröw"')],
    starter="""
        pub fn reverse_each_word(s: &str) -> String {
            todo!()
        }
    """,
    solution="""
        pub fn reverse_each_word(s: &str) -> String {
            s.split_whitespace()
                .map(|w| w.chars().rev().collect::<String>())
                .collect::<Vec<_>>()
                .join(" ")
        }
    """,
    visible=[
        T("accents", '"héllo wörld"', 'reverse_each_word("héllo wörld")', '"olléh dlröw".to_string()'),
        T("ascii", '"ab cd"', 'reverse_each_word("ab cd")', rs("ba dc")),
        T("leetcode_557_first", '"Let\'s take LeetCode contest"', 'reverse_each_word("Let\'s take LeetCode contest")', rs("s'teL ekat edoCteeL tsetnoc")),
        T("leetcode_557_second", '"Mr Ding"', 'reverse_each_word("Mr Ding")', rs("rM gniD")),
        T("one_word", '"hello"', 'reverse_each_word("hello")', rs("olleh")),
    ],
    hidden=[
        T("emoji", '"🦀x"', 'reverse_each_word("🦀x")', '"x🦀".to_string()'),
        T("extra_spaces", '"  a   bc "', 'reverse_each_word("  a   bc ")', rs("a cb")),
        T("empty", '""', 'reverse_each_word("")', "String::new()"),
        T("only_spaces", '"   "', 'reverse_each_word("   ")', "String::new()"),
        T("tabs_and_newlines", '"ab\\tcd\\nef"', 'reverse_each_word("ab\\tcd\\nef")', rs("ba dc fe")),
        T("palindrome", '"abba x"', 'reverse_each_word("abba x")', rs("abba x")),
        T("cjk", '"日本語 テスト"', 'reverse_each_word("日本語 テスト")', '"語本日 トステ".to_string()'),
        T("single_char", '"a"', 'reverse_each_word("a")', rs("a")),
        T("punctuation_moves", '"a1! b2?"', 'reverse_each_word("a1! b2?")', rs("!1a ?2b")),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2211);
            for _ in 0..300 {
                let len = rng.below(14);
                let s = rng.string(len, "abé🦀  \\t");
                let mut words: Vec<String> = Vec::new();
                let mut cur: Vec<char> = Vec::new();
                for c in s.chars().chain(std::iter::once(' ')) {
                    if c.is_whitespace() {
                        if !cur.is_empty() {
                            cur.reverse();
                            words.push(cur.iter().collect());
                            cur.clear();
                        }
                    } else {
                        cur.push(c);
                    }
                }
                check!(format!("s = {s:?}"), reverse_each_word(&s), words.join(" "));
            }
        }

        #[test]
        fn scale_200k_words() {
            let s = "abc ".repeat(200_000);
            let out = reverse_each_word(&s);
            check!("s = \\"abc abc …\\" (200000 words)", (out.len(), &out[..7]), (799_999, "cba cba"));
        }
        """,
    ],
    wrong=dict(
        reverses_bytes="""
            pub fn reverse_each_word(s: &str) -> String {
                s.split_whitespace()
                    .map(|w| String::from_utf8_lossy(&w.bytes().rev().collect::<Vec<u8>>()).into_owned())
                    .collect::<Vec<_>>()
                    .join(" ")
            }
        """,
        reverses_word_order_too="""
            pub fn reverse_each_word(s: &str) -> String {
                s.split_whitespace()
                    .rev()
                    .map(|w| w.chars().rev().collect::<String>())
                    .collect::<Vec<_>>()
                    .join(" ")
            }
        """,
        keeps_spacing="""
            pub fn reverse_each_word(s: &str) -> String {
                s.split(' ')
                    .map(|w| w.chars().rev().collect::<String>())
                    .collect::<Vec<_>>()
                    .join(" ")
            }
        """,
    ),
    hints=[("rust", "Reversing bytes would split multi-byte characters into invalid UTF-8. `chars().rev()` reverses whole characters."),
           ("rust", "`collect::<String>()` builds a String from an iterator of `char`.")],
    notes=("`chars().rev()` works because `Chars` is a `DoubleEndedIterator`: UTF-8 can be decoded backwards. Combining characters (e + ◌́) would still come out in the wrong order.", "O(n)", "O(n)"),
    follow_up="Which crate would you reach for to reverse by grapheme cluster?",
))

P.append(dict(
    slug="cow-str", title="Cow<str>: allocate only when needed", level="medium", stage="understand",
    tags=["Cow", "zero-copy"],
    teaches=["`Cow::Borrowed` when the input is already right, `Cow::Owned` when it had to change.", "Finding the first byte that needs work before allocating."],
    statement="""
        Escape `&`, `<`, `>`, `"` and `'` as `&amp;`, `&lt;`, `&gt;`, `&quot;` and `&#39;`. When the input
        contains none of them, return it borrowed, without allocating.
    """,
    examples=[('"a<b"', '"a&lt;b" (Owned)'), ('"plain"', '"plain" (Borrowed)')],
    starter="""
        use std::borrow::Cow;

        pub fn escape_html(s: &str) -> Cow<'_, str> {
            todo!()
        }
    """,
    solution="""
        use std::borrow::Cow;

        pub fn escape_html(s: &str) -> Cow<'_, str> {
            let special = |c: char| matches!(c, '&' | '<' | '>' | '"' | '\\'');
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
            Cow::Owned(out)
        }
    """,
    visible=[
        T("escapes", '"a<b"', 'escape_html("a<b").into_owned()', rs("a&lt;b")),
        T("borrows", '"plain"', 'matches!(escape_html("plain"), std::borrow::Cow::Borrowed("plain"))', "true"),
        T("ampersand", '"a&b"', 'escape_html("a&b").into_owned()', rs("a&amp;b")),
        T("already_escaped", '"&lt;"', 'escape_html("&lt;").into_owned()', rs("&amp;lt;")),
        T("quotes_and_gt", '"\\"x\\" > y"', 'escape_html("\\"x\\" > y").into_owned()', rs("&quot;x&quot; &gt; y")),
    ],
    hidden=[
        T("all_five", "\"&<>\\\"'\"", "escape_html(\"&<>\\\"'\").into_owned()", rs("&amp;&lt;&gt;&quot;&#39;")),
        T("owned_when_changed", '"x&y"', 'matches!(escape_html("x&y"), std::borrow::Cow::Owned(_))', "true"),
        T("unicode", '"é<é"', 'escape_html("é<é").into_owned()', '"é&lt;é".to_string()'),
        T("empty", '""', 'matches!(escape_html(""), std::borrow::Cow::Borrowed(""))', "true"),
        T("special_at_end", '"abc>"', 'escape_html("abc>").into_owned()', rs("abc&gt;")),
        T("special_at_start", '"<abc"', 'escape_html("<abc").into_owned()', rs("&lt;abc")),
        T("consecutive", '"<<>>"', 'escape_html("<<>>").into_owned()', rs("&lt;&lt;&gt;&gt;")),
        T("single_quote", "\"'\"", "escape_html(\"'\").into_owned()", rs("&#39;")),
        T("unicode_borrowed", '"日本語 ✓"', 'matches!(escape_html("日本語 ✓"), std::borrow::Cow::Borrowed(_))', "true"),
        T("borrowed_same_pointer", '"no specials here"', "escape_html(&s).as_ptr() == s.as_ptr()", "true", setup='let s = String::from("no specials here");'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2212);
            for _ in 0..300 {
                let len = rng.below(10);
                let s = rng.string(len, "a é&<>\\"'");
                let mut want = String::new();
                for c in s.chars() {
                    match c {
                        '&' => want += "&amp;",
                        '<' => want += "&lt;",
                        '>' => want += "&gt;",
                        '"' => want += "&quot;",
                        '\\'' => want += "&#39;",
                        _ => want.push(c),
                    }
                }
                let out = escape_html(&s);
                let borrowed = matches!(out, std::borrow::Cow::Borrowed(_));
                check!(format!("s = {s:?}"), (out.into_owned(), borrowed), (want.clone(), want == s));
            }
        }

        #[test]
        fn scale_200k() {
            let s = "a<b&".repeat(50_000);
            let out = escape_html(&s);
            check!("s = \\"a<b&…\\" (200000 chars)", (out.len(), &out[..12]), (550_000, "a&lt;b&amp;a"));
        }
        """,
    ],
    wrong=dict(
        amp_replaced_last="""
            use std::borrow::Cow;

            pub fn escape_html(s: &str) -> Cow<'_, str> {
                if !s.contains(['&', '<', '>', '"', '\\'']) {
                    return Cow::Borrowed(s);
                }
                Cow::Owned(s.replace('<', "&lt;").replace('>', "&gt;").replace('"', "&quot;").replace('\\'', "&#39;").replace('&', "&amp;"))
            }
        """,
        always_owned="""
            use std::borrow::Cow;

            pub fn escape_html(s: &str) -> Cow<'_, str> {
                Cow::Owned(s.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;").replace('"', "&quot;").replace('\\'', "&#39;"))
            }
        """,
        forgets_single_quote="""
            use std::borrow::Cow;

            pub fn escape_html(s: &str) -> Cow<'_, str> {
                if !s.contains(['&', '<', '>', '"']) {
                    return Cow::Borrowed(s);
                }
                Cow::Owned(s.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;").replace('"', "&quot;"))
            }
        """,
    ),
    hints=[("approach", "Most inputs need no escaping. Scan for the first special character before allocating anything."),
           ("rust", "`let Some(i) = s.find(pred) else { return Cow::Borrowed(s) };` handles the common case in one line."),
           ("rust", "Copy `&s[..first]` in one go, then handle characters from `first` on.")],
    notes=("The common case costs one scan and no allocation. Callers can treat both variants as `&str` via `Deref`, or call `into_owned` when they need a `String`.", "O(n)", "O(n) only when escaping"),
    follow_up="Where does std use `Cow<str>` (hint: `String::from_utf8_lossy`)?",
    related=["S1"],
))

P.append(dict(
    slug="display-vs-debug", title="Display vs Debug", level="medium", stage="understand",
    tags=["Display", "f.pad", "Formatter"],
    teaches=["`Display` is for users, `Debug` for programmers.", "`f.pad` makes your `Display` respect width and alignment."],
    statement="""
        Implement `Display` for `Money` as `<amount> <currency>` with two decimals, and a leading `-` for
        negative amounts. It must respect width and alignment, so `format!("{:>12}", m)` right-aligns it.
        `Debug` stays derived.
    """,
    examples=[("Money { cents: 1234, currency: \"USD\" }", '"12.34 USD"'), ("cents: -5", '"-0.05 USD"')],
    starter="""
        use std::fmt;

        #[derive(Debug)]
        pub struct Money {
            pub cents: i64,
            pub currency: &'static str,
        }

        impl fmt::Display for Money {
            fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                todo!()
            }
        }
    """,
    solution="""
        use std::fmt;

        #[derive(Debug)]
        pub struct Money {
            pub cents: i64,
            pub currency: &'static str,
        }

        impl fmt::Display for Money {
            fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                let sign = if self.cents < 0 { "-" } else { "" };
                let abs = self.cents.unsigned_abs();
                f.pad(&format!("{sign}{}.{:02} {}", abs / 100, abs % 100, self.currency))
            }
        }
    """,
    visible=[
        T("display", "12.34 USD", 'format!("{}", Money { cents: 1234, currency: "USD" })', rs("12.34 USD")),
        T("negative_cents", "-5 cents", 'format!("{}", Money { cents: -5, currency: "EUR" })', rs("-0.05 EUR")),
        T("whole_amount", "500 cents", 'format!("{}", Money { cents: 500, currency: "USD" })', rs("5.00 USD")),
        T("zero", "0 cents", 'format!("{}", Money { cents: 0, currency: "X" })', rs("0.00 X")),
        T("right_aligned", "{:>10} then |", 'format!("{:>10}|", Money { cents: 99, currency: "EUR" })', rs("  0.99 EUR|")),
    ],
    hidden=[
        T("width", "{:>12} then |", 'format!("{:>12}|", Money { cents: 1234, currency: "USD" })', rs("   12.34 USD|")),
        T("left", "{:<10} then |", 'format!("{:<10}|", Money { cents: 7, currency: "GBP" })', rs("0.07 GBP  |")),
        T("debug_unchanged", "{:?}", 'format!("{:?}", Money { cents: 1, currency: "USD" })', r'"Money { cents: 1, currency: \"USD\" }".to_string()'),
        T("min_value", "i64::MIN cents", 'format!("{}", Money { cents: i64::MIN, currency: "X" })', rs("-92233720368547758.08 X")),
        T("max_value", "i64::MAX cents", 'format!("{}", Money { cents: i64::MAX, currency: "X" })', rs("92233720368547758.07 X")),
        T("centered", "{:^12} then |", 'format!("{:^12}|", Money { cents: 1234, currency: "USD" })', rs(" 12.34 USD  |")),
        T("fill_char", "{:*<12}", 'format!("{:*<12}", Money { cents: 7, currency: "GBP" })', rs("0.07 GBP****")),
        T("width_too_small", "{:>3}", 'format!("{:>3}", Money { cents: 1234, currency: "USD" })', rs("12.34 USD")),
        T("negative_whole", "-100 cents", 'format!("{}", Money { cents: -100, currency: "USD" })', rs("-1.00 USD")),
        T("negative_padded", "{:>11} with -12345 cents", 'format!("{:>11}", Money { cents: -12345, currency: "USD" })', rs("-123.45 USD")),
        T("negative_width", "{:>12} with -5 cents", 'format!("{:>12}", Money { cents: -5, currency: "EUR" })', rs("   -0.05 EUR")),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2213);
            for _ in 0..300 {
                let cents = rng.int(-1_000_000_000_000, 1_000_000_000_000);
                let width = rng.below(24);
                let abs = cents.unsigned_abs();
                let mut plain = String::new();
                if cents < 0 {
                    plain.push('-');
                }
                plain += &(abs / 100).to_string();
                plain.push('.');
                if abs % 100 < 10 {
                    plain.push('0');
                }
                plain += &(abs % 100).to_string();
                plain += " JPY";
                let mut padded = " ".repeat(width.saturating_sub(plain.len()));
                padded += &plain;
                let m = Money { cents, currency: "JPY" };
                check!(format!("cents = {cents}, {{:>{width}}}"), (format!("{m}"), format!("{m:>width$}")), (plain, padded));
            }
        }
        """,
    ],
    wrong=dict(
        write_ignores_width="""
            use std::fmt;

            #[derive(Debug)]
            pub struct Money {
                pub cents: i64,
                pub currency: &'static str,
            }

            impl fmt::Display for Money {
                fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                    let sign = if self.cents < 0 { "-" } else { "" };
                    let abs = self.cents.unsigned_abs();
                    write!(f, "{sign}{}.{:02} {}", abs / 100, abs % 100, self.currency)
                }
            }
        """,
        sign_lost="""
            use std::fmt;

            #[derive(Debug)]
            pub struct Money {
                pub cents: i64,
                pub currency: &'static str,
            }

            impl fmt::Display for Money {
                fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                    f.pad(&format!("{}.{:02} {}", self.cents / 100, (self.cents % 100).abs(), self.currency))
                }
            }
        """,
        abs_overflows="""
            use std::fmt;

            #[derive(Debug)]
            pub struct Money {
                pub cents: i64,
                pub currency: &'static str,
            }

            impl fmt::Display for Money {
                fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                    let sign = if self.cents < 0 { "-" } else { "" };
                    let abs = self.cents.abs();
                    f.pad(&format!("{sign}{}.{:02} {}", abs / 100, abs % 100, self.currency))
                }
            }
        """,
    ),
    hints=[("rust", "`write!(f, ...)` ignores the caller's width. `f.pad(s)` applies width, fill and alignment to `s`."),
           ("edge case", "`-5 / 100` is `0`, so the sign must be handled separately. `unsigned_abs` also survives `i64::MIN`.")],
    notes=("Formatting the whole amount first, then padding once, keeps alignment correct. `unsigned_abs` avoids the overflow `abs()` hits on `i64::MIN`.", "O(1)", "O(1)"),
    follow_up="How would you honour `{:.1}` precision for Money without allocating?",
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
    notes=("`FromStr` plugs into `str::parse`, so callers get `\"...\".parse::<Setting>()` for free. Each check exits early with a specific error.", "O(n)", "O(n)"),
    follow_up="How would you add the line number to the errors when parsing a whole file?",
    related=["S1", "L4"],
))

P.append(dict(
    slug="unicode-safe-truncate", title="Unicode-safe truncate", level="medium", stage="understand",
    tags=["is_char_boundary", "byte budgets"],
    teaches=["Cutting to a byte budget at a character boundary.", "`let ... else` for an early return."],
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
            let Some(mut end) = max_bytes.checked_sub('…'.len_utf8()) else {
                return String::new();
            };
            while !s.is_char_boundary(end) {
                end -= 1;
            }
            format!("{}…", &s[..end])
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
    hints=[("approach", "Reserve 3 bytes for `…`, then walk the cut point back until it lands on a character boundary."),
           ("rust", "`s.is_char_boundary(i)` is true at 0, at `len()`, and between characters.")],
    notes=("At most three steps back, because a UTF-8 character is at most four bytes. `checked_sub` covers budgets smaller than the ellipsis.", "O(n)", "O(n)"),
    follow_up="Databases often limit by bytes and UIs by characters. How would you truncate to N characters instead?",
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
    notes=("Every field is a slice of the input, so parsing allocates only the query Vec. The `'_` in `Url<'_>` ties the result to `s`.", "O(n)", "O(q)"),
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
    notes=("Copying `self.rest` out (it's a `&'a str`, which is `Copy`) is what lets the items outlive the `&mut self` borrow. Using `Option` for 'finished' distinguishes an empty last piece from no piece.", "O(n) total", "O(1)"),
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
    notes=("A small scanner with one character of lookahead handles escapes, placeholders and errors in a single pass. `HashMap<&str, &str>::get` takes a `&str` directly.", "O(n)", "O(n)"),
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
