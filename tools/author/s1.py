from author import T, write_track

P = []

P.append(dict(
    slug="config-port", title="Read a port from config", level="easy", stage="use-it", tags=["ok_or", "map_err", "and_then"],
    teaches=["`ok_or` turns a missing value into an error.", "`and_then` chains a second fallible step; `map_err` shapes the error."],
    statement="""
        Read the `"port"` key from `cfg` and parse it as a `u16`.
        Return `Err("missing port")` if the key is absent and `Err("invalid port: <value>")` if it doesn't parse.
    """,
    starter="""
        use std::collections::HashMap;

        pub fn port(cfg: &HashMap<String, String>) -> Result<u16, String> {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashMap;

        pub fn port(cfg: &HashMap<String, String>) -> Result<u16, String> {
            cfg.get("port")
                .ok_or_else(|| "missing port".to_string())
                .and_then(|v| v.parse().map_err(|_| format!("invalid port: {v}")))
        }
    """,
    visible=[
        T("valid", "port = \"8080\"", 'port(&std::collections::HashMap::from([("port".to_string(), "8080".to_string())]))', "Ok(8080)"),
        T("missing", "no port key", "port(&std::collections::HashMap::new())", 'Err("missing port".to_string())'),
        T("not_a_number", "port = \"abc\"", 'port(&std::collections::HashMap::from([("port".to_string(), "abc".to_string())]))', 'Err("invalid port: abc".to_string())'),
        T("zero", "port = \"0\"", 'port(&std::collections::HashMap::from([("port".to_string(), "0".to_string())]))', "Ok(0)"),
        T("too_big_for_u16", "port = \"65536\"", 'port(&std::collections::HashMap::from([("port".to_string(), "65536".to_string())]))', 'Err("invalid port: 65536".to_string())'),
    ],
    hidden=[
        T("out_of_range", "port = \"70000\"", 'port(&std::collections::HashMap::from([("port".to_string(), "70000".to_string())]))', 'Err("invalid port: 70000".to_string())'),
        T("largest", "port = \"65535\"", 'port(&std::collections::HashMap::from([("port".to_string(), "65535".to_string())]))', "Ok(65535)"),
        T("negative", "port = \"-1\"", 'port(&std::collections::HashMap::from([("port".to_string(), "-1".to_string())]))', 'Err("invalid port: -1".to_string())'),
        T("surrounding_space", "port = \" 80\"", 'port(&std::collections::HashMap::from([("port".to_string(), " 80".to_string())]))', 'Err("invalid port:  80".to_string())'),
        T("empty_value", "port = \"\"", 'port(&std::collections::HashMap::from([("port".to_string(), "".to_string())]))', 'Err("invalid port: ".to_string())'),
        T("other_keys_only", "host = \"localhost\", Port = \"80\"", 'port(&std::collections::HashMap::from([("host".to_string(), "localhost".to_string()), ("Port".to_string(), "80".to_string())]))', 'Err("missing port".to_string())'),
        T("unicode_digits", "port = \"８０\" (full-width digits)", 'port(&std::collections::HashMap::from([("port".to_string(), "８０".to_string())]))', 'Err("invalid port: ８０".to_string())'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1301);
            for _ in 0..400 {
                let len = rng.below(7);
                let v = rng.string(len, "0123456789012345678x-");
                let mut cfg = std::collections::HashMap::new();
                let present = rng.below(5) > 0;
                if present {
                    cfg.insert("port".to_string(), v.clone());
                }
                // Brute force: digits only, no sign, value at most 65535.
                let want = if !present {
                    Err("missing port".to_string())
                } else if !v.is_empty() && v.bytes().all(|b| b.is_ascii_digit()) && v.bytes().fold(0u64, |n, b| (n * 10 + u64::from(b - b'0')).min(1 << 20)) <= 65_535 {
                    Ok(v.bytes().fold(0u16, |n, b| n * 10 + u16::from(b - b'0')))
                } else {
                    Err(format!("invalid port: {v}"))
                };
                check!(format!("cfg = {cfg:?}"), port(&cfg), want);
            }
        }
        """,
    ],
    wrong=dict(
        parse_wide_then_cast="""
            use std::collections::HashMap;

            pub fn port(cfg: &HashMap<String, String>) -> Result<u16, String> {
                cfg.get("port")
                    .ok_or_else(|| "missing port".to_string())
                    .and_then(|v| v.parse::<u32>().map(|p| p as u16).map_err(|_| format!("invalid port: {v}")))
            }
        """,
        trims_the_value="""
            use std::collections::HashMap;

            pub fn port(cfg: &HashMap<String, String>) -> Result<u16, String> {
                cfg.get("port")
                    .ok_or_else(|| "missing port".to_string())
                    .and_then(|v| v.trim().parse().map_err(|_| format!("invalid port: {v}")))
            }
        """,
        missing_is_zero="""
            use std::collections::HashMap;

            pub fn port(cfg: &HashMap<String, String>) -> Result<u16, String> {
                let v = cfg.get("port").map(String::as_str).unwrap_or("0");
                v.parse().map_err(|_| format!("invalid port: {v}"))
            }
        """,
    ),
    hints=[("rust", "`HashMap<String, _>::get` accepts a `&str` key."), ("rust", "`ok_or_else`, then `and_then`, then `map_err` inside.")],
    notes=("The chain reads top to bottom as the three outcomes. `ok_or_else` avoids building the error string on the happy path.", "O(1)", "O(1)"),
    follow_up="When would you return a custom error enum instead of `String`?",
    related=["L8", "S4"],
))

P.append(dict(
    slug="question-mark-on-option", title="? on Option", level="easy", stage="use-it", tags=["?", "Option"],
    teaches=["`?` works on `Option` in a function that returns `Option`.", "Chaining lookups without nested `match`."],
    statement="Return the length of the third whitespace-separated word of `s`, or `None` if there are fewer than three.",
    examples=[("s = \"the quick brown fox\"", "Some(5)")],
    starter="""
        pub fn third_word_len(s: &str) -> Option<usize> {
            todo!()
        }
    """,
    solution="""
        pub fn third_word_len(s: &str) -> Option<usize> {
            Some(s.split_whitespace().nth(2)?.len())
        }
    """,
    visible=[
        T("four_words", "s = \"the quick brown fox\"", 'third_word_len("the quick brown fox")', "Some(5)"),
        T("two_words", "s = \"hi there\"", 'third_word_len("hi there")', "None"),
        T("exactly_three", "s = \"a bb ccc\"", 'third_word_len("a bb ccc")', "Some(3)"),
        T("empty_string", "s = \"\"", 'third_word_len("")', "None"),
        T("tabs_and_newlines_separate_words", "s = \"a\\tbb\\nccc\"", 'third_word_len("a\\tbb\\nccc")', "Some(3)"),
    ],
    hidden=[
        T("extra_spaces", "s = \"  a  bb   ccc \"", 'third_word_len("  a  bb   ccc ")', "Some(3)"),
        T("empty", "s = \"\"", 'third_word_len("")', "None"),
        T("only_spaces", "s = \"     \"", 'third_word_len("     ")', "None"),
        T("two_words_trailing_space", "s = \"a b \"", 'third_word_len("a b ")', "None"),
        T("length_in_bytes", "s = \"a b héllo\"", 'third_word_len("a b héllo")', "Some(6)"),
        T("punctuation_is_part_of_a_word", "s = \"one, two, three!\"", 'third_word_len("one, two, three!")', "Some(6)"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1302);
            for _ in 0..400 {
                let len = rng.below(15);
                let s = rng.string(len, "ab é\\t\\n");
                let words: Vec<&str> = s.split(|c: char| c.is_whitespace()).filter(|w| !w.is_empty()).collect();
                check!(format!("s = {s:?}"), third_word_len(&s), words.get(2).map(|w| w.len()));
            }
        }

        #[test]
        fn long_input() {
            let s = format!("x yy {} {}", "z".repeat(100_000), "w ".repeat(100_000));
            check!("s = \\"x yy \\" + 100000 × z + 100000 more words", third_word_len(&s), Some(100_000));
        }
        """,
    ],
    wrong=dict(
        split_on_single_spaces="""
            pub fn third_word_len(s: &str) -> Option<usize> {
                Some(s.split(' ').nth(2)?.len())
            }
        """,
        counts_chars="""
            pub fn third_word_len(s: &str) -> Option<usize> {
                Some(s.split_whitespace().nth(2)?.chars().count())
            }
        """,
        nth_counts_from_one="""
            pub fn third_word_len(s: &str) -> Option<usize> {
                Some(s.split_whitespace().nth(3)?.len())
            }
        """,
    ),
    hints=[("rust", "`nth(2)` returns an `Option<&str>`. What does `?` do with `None`?")],
    notes=("`?` returns `None` early, so the happy path is one line.", "O(n)", "O(1)"),
    follow_up="How does `?` decide what to return when used on a `Result` inside a function returning `Option`?",
    related=["S6"],
))

P.append(dict(
    slug="sentinel-to-option", title="Wrap a sentinel API in Option", level="easy", stage="use-it", tags=["TryFrom", "Option"],
    teaches=["Convert `-1`-style sentinels to `Option` at the boundary.", "`usize::try_from(i32)` rejects negatives for you."],
    statement="""
        `legacy_find` returns an index, or `-1` if the value isn't there. Write `find`, which returns
        `Option<usize>`, by calling `legacy_find`. Don't rewrite the search.
    """,
    starter="""
        /// Legacy code: the index of `x` in `v`, or -1. Leave it as it is.
        fn legacy_find(v: &[i32], x: i32) -> i32 {
            v.iter().position(|&y| y == x).map_or(-1, |i| i as i32)
        }

        /// The index of `x` in `v`, or `None`.
        pub fn find(v: &[i32], x: i32) -> Option<usize> {
            todo!()
        }
    """,
    solution="""
        /// Legacy code: the index of `x` in `v`, or -1. Leave it as it is.
        fn legacy_find(v: &[i32], x: i32) -> i32 {
            v.iter().position(|&y| y == x).map_or(-1, |i| i as i32)
        }

        /// The index of `x` in `v`, or `None`.
        pub fn find(v: &[i32], x: i32) -> Option<usize> {
            usize::try_from(legacy_find(v, x)).ok()
        }
    """,
    visible=[
        T("found", "v = [4, 8, 15], x = 8", "find(&[4, 8, 15], 8)", "Some(1)"),
        T("missing", "v = [4, 8, 15], x = 16", "find(&[4, 8, 15], 16)", "None"),
        T("empty_slice", "v = [], x = 0", "find(&[], 0)", "None"),
        T("index_zero_is_found", "v = [7, 3], x = 7", "find(&[7, 3], 7)", "Some(0)"),
        T("searching_for_minus_one", "v = [5, -1], x = -1", "find(&[5, -1], -1)", "Some(1)"),
    ],
    hidden=[
        T("empty", "v = [], x = 1", "find(&[], 1)", "None"),
        T("first", "v = [-1, -1], x = -1", "find(&[-1, -1], -1)", "Some(0)"),
        T("last", "v = [1, 2, 3], x = 3", "find(&[1, 2, 3], 3)", "Some(2)"),
        T("extremes", "v = [i32::MIN, i32::MAX], x = i32::MAX", "find(&[i32::MIN, i32::MAX], i32::MAX)", "Some(1)"),
        T("single_missing", "v = [0], x = 1", "find(&[0], 1)", "None"),
        T("duplicates_give_the_first", "v = [2, 5, 5, 5], x = 5", "find(&[2, 5, 5, 5], 5)", "Some(1)"),
        T("minus_one_absent", "v = [0, 1], x = -1", "find(&[0, 1], -1)", "None"),
        T("large_index", "v = 0..10⁶, x = 999999", "find(&v, 999_999)", "Some(999_999)", setup="let v: Vec<i32> = (0..1_000_000).collect();"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1303);
            for _ in 0..400 {
                let n = rng.below(8);
                let v: Vec<i32> = rng.vec(n, -3, 3);
                let x = rng.int(-4, 4) as i32;
                check!(format!("v = {v:?}, x = {x}"), find(&v, x), v.iter().position(|&y| y == x));
            }
        }
        """,
    ],
    wrong=dict(
        cast_the_sentinel="""
            /// Legacy code: the index of `x` in `v`, or -1. Leave it as it is.
            fn legacy_find(v: &[i32], x: i32) -> i32 {
                v.iter().position(|&y| y == x).map_or(-1, |i| i as i32)
            }

            /// The index of `x` in `v`, or `None`.
            pub fn find(v: &[i32], x: i32) -> Option<usize> {
                Some(legacy_find(v, x) as usize)
            }
        """,
        positive_means_found="""
            /// Legacy code: the index of `x` in `v`, or -1. Leave it as it is.
            fn legacy_find(v: &[i32], x: i32) -> i32 {
                v.iter().position(|&y| y == x).map_or(-1, |i| i as i32)
            }

            /// The index of `x` in `v`, or `None`.
            pub fn find(v: &[i32], x: i32) -> Option<usize> {
                let i = legacy_find(v, x);
                (i > 0).then_some(i as usize)
            }
        """,
    ),
    hints=[("rust", "A negative `i32` can't become a `usize`. Which conversion reports that?")],
    notes=("`try_from` fails exactly on the sentinel, so there's no magic number in the new code.", "O(n)", "O(1)"),
    follow_up="Where else do sentinels hide in std or C APIs, and how do their Rust wrappers expose them?",
    related=["S8", "Y3"],
))

P.append(dict(
    slug="order-total", title="Sum into Option: an order total", level="easy", stage="use-it", tags=["try_fold", "zip", "checked_mul"],
    teaches=["`try_fold` (or `sum::<Option<_>>()`) stops at the first `None`.", "`ok()` + `zip` + `checked_*` keep every failure an `Option` instead of a panic."],
    statement="""
        Each line is `(price_cents, qty)` as text. Return the sum of `price * qty` over all lines, or `None` if
        any field isn't a `u64` or any product or the running total doesn't fit in a `u64`.
    """,
    examples=[("lines = [(\"250\", \"4\"), (\"100\", \"1\")]", "Some(1100)"), ("lines = [(\"5\", \"2\"), (\"oops\", \"1\")]", "None")],
    constraints=["Fields are parsed exactly as `str::parse::<u64>` does: no trimming."],
    starter="""
        pub fn order_total(lines: &[(&str, &str)]) -> Option<u64> {
            todo!()
        }
    """,
    solution="""
        pub fn order_total(lines: &[(&str, &str)]) -> Option<u64> {
            lines.iter().try_fold(0u64, |total, &(price, qty)| {
                let (p, q) = price.parse::<u64>().ok().zip(qty.parse::<u64>().ok())?;
                total.checked_add(p.checked_mul(q)?)
            })
        }
    """,
    visible=[
        T("two_lines", "lines = [(\"250\", \"4\"), (\"100\", \"1\")]", 'order_total(&[("250", "4"), ("100", "1")])', "Some(1100)"),
        T("empty_order", "lines = []", "order_total(&[])", "Some(0)"),
        T("bad_qty", "lines = [(\"250\", \"x\")]", 'order_total(&[("250", "x")])', "None"),
        T("one_bad_line_spoils_the_total", "lines = [(\"5\", \"2\"), (\"oops\", \"1\")]", 'order_total(&[("5", "2"), ("oops", "1")])', "None"),
        T("product_overflow_is_none", "lines = [(\"4294967296\", \"4294967296\")]", 'order_total(&[("4294967296", "4294967296")])', "None"),
    ],
    hidden=[
        T("zero_qty", "lines = [(\"999\", \"0\"), (\"1\", \"1\")]", 'order_total(&[("999", "0"), ("1", "1")])', "Some(1)"),
        T("product_exactly_max", "lines = [(\"4294967295\", \"4294967297\")]", 'order_total(&[("4294967295", "4294967297")])', "Some(u64::MAX)"),
        T("sum_exactly_max", "lines = [(\"18446744073709551614\", \"1\"), (\"1\", \"1\")]", 'order_total(&[("18446744073709551614", "1"), ("1", "1")])', "Some(u64::MAX)"),
        T("sum_overflow_is_none", "lines = [(\"18446744073709551615\", \"1\"), (\"1\", \"1\")]", 'order_total(&[("18446744073709551615", "1"), ("1", "1")])', "None"),
        T("field_too_big", "lines = [(\"18446744073709551616\", \"1\")]", 'order_total(&[("18446744073709551616", "1")])', "None"),
        T("negative_price", "lines = [(\"-1\", \"1\")]", 'order_total(&[("-1", "1")])', "None"),
        T("empty_field", "lines = [(\"\", \"1\")]", 'order_total(&[("", "1")])', "None"),
        T("plus_sign_parses", "lines = [(\"+5\", \"2\")]", 'order_total(&[("+5", "2")])', "Some(10)"),
        T("spaces_do_not_parse", "lines = [(\"5\", \" 2\")]", 'order_total(&[("5", " 2")])', "None"),
        T("full_width_digits", "lines = [(\"５\", \"2\")]", 'order_total(&[("５", "2")])', "None"),
        T("bad_line_first", "lines = [(\"x\", \"1\"), (\"5\", \"2\")]", 'order_total(&[("x", "1"), ("5", "2")])', "None"),
        """
        fn brute(s: &str) -> Option<u128> {
            let digits = s.strip_prefix('+').unwrap_or(s);
            if digits.is_empty() || !digits.bytes().all(|b| b.is_ascii_digit()) {
                return None;
            }
            let n = digits.bytes().fold(0u128, |n, b| (n * 10 + u128::from(b - b'0')).min(1 << 70));
            (n <= u128::from(u64::MAX)).then_some(n)
        }

        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1311);
            let field = |rng: &mut anneal_prelude::Rng| match rng.below(6) {
                0 => {
                    let len = rng.below(4);
                    rng.string(len, "012+x")
                }
                1 => rng.int(0, i64::MAX).to_string(),
                2 => (u64::MAX - rng.below(3) as u64).to_string(),
                _ => rng.int(0, 1000).to_string(),
            };
            for _ in 0..400 {
                let n = rng.below(5);
                let mut owned: Vec<(String, String)> = Vec::new();
                for _ in 0..n {
                    let p = field(&mut rng);
                    let q = field(&mut rng);
                    owned.push((p, q));
                }
                let lines: Vec<(&str, &str)> = owned.iter().map(|(p, q)| (p.as_str(), q.as_str())).collect();
                let mut want = Some(0u128);
                for (p, q) in &lines {
                    want = match (want, brute(p), brute(q)) {
                        (Some(t), Some(p), Some(q)) if p * q <= u128::from(u64::MAX) && t + p * q <= u128::from(u64::MAX) => Some(t + p * q),
                        _ => None,
                    };
                }
                check!(format!("lines = {lines:?}"), order_total(&lines), want.map(|t| t as u64));
            }
        }

        #[test]
        fn scale_many_lines() {
            let owned: Vec<(String, String)> = (0..200_000u64).map(|i| (i.to_string(), "2".to_string())).collect();
            let lines: Vec<(&str, &str)> = owned.iter().map(|(p, q)| (p.as_str(), q.as_str())).collect();
            check!("200000 lines (i, 2) for i below 200000", order_total(&lines), Some(39_999_800_000u64));
        }
        """,
    ],
    wrong=dict(
        sum_panics_on_overflow="""
            pub fn order_total(lines: &[(&str, &str)]) -> Option<u64> {
                lines
                    .iter()
                    .map(|&(price, qty)| {
                        let (p, q) = price.parse::<u64>().ok().zip(qty.parse::<u64>().ok())?;
                        p.checked_mul(q)
                    })
                    .sum()
            }
        """,
        skips_bad_lines="""
            pub fn order_total(lines: &[(&str, &str)]) -> Option<u64> {
                lines
                    .iter()
                    .filter_map(|&(price, qty)| price.parse::<u64>().ok().zip(qty.parse::<u64>().ok()))
                    .try_fold(0u64, |total, (p, q)| total.checked_add(p.checked_mul(q)?))
            }
        """,
        saturates="""
            pub fn order_total(lines: &[(&str, &str)]) -> Option<u64> {
                lines.iter().try_fold(0u64, |total, &(price, qty)| {
                    let (p, q) = price.parse::<u64>().ok().zip(qty.parse::<u64>().ok())?;
                    Some(total.saturating_add(p.saturating_mul(q)))
                })
            }
        """,
    ),
    hints=[("approach", "One bad line makes the whole answer `None`, so the loop has to stop early with `None`."),
           ("rust", "`iter.try_fold(0u64, |acc, x| -> Option<u64> { ... })` stops at the first `None`, and `?` works inside the closure. `a.ok().zip(b.ok())?` gets both fields or bails."),
           ("edge case", "`sum::<Option<u64>>()` short-circuits too, but its `+` panics on overflow in debug builds. Use `checked_mul` and `checked_add`.")],
    notes=("`try_fold` threads the running total and stops at the first `None`, whether it came from a parse, a product or the sum. API reminder: `Option<T>` and `Result<T, E>` implement `Sum` and `Product` (`iter.sum::<Option<u64>>()`), `x.ok()` drops an error, `a.zip(b)` is `Some((x, y))` only when both are `Some`, and `checked_add`/`checked_mul` return `Option`.", "O(total length of the fields)", "O(1)"),
    follow_up="How would you report which line failed and why, instead of just `None`?",
    related=["S4", "L8"],
))

THEME_GUARD = """
        /// The chosen colour, else the palette's first colour, else "black".
        pub fn theme<'a>(chosen: Option<&'a str>, palette: &[&'a str]) -> &'a str {
            if chosen.is_none() && palette.is_empty() {
                return "black";
            }
            chosen.unwrap_or(palette[0])
        }

        /// The byte length of the colour `theme` would pick, but 0 instead of "black".
        pub fn theme_len(chosen: Option<&str>, palette: &[&str]) -> usize {
            if chosen.is_none() && palette.is_empty() {
                return 0;
            }
            chosen.map_or(palette[0].len(), str::len)
        }
"""

P.append(dict(
    slug="fix-eager-unwrap-or", title="Fix: unwrap_or and map_or panic on a Some", mode="fix", level="easy", stage="use-it", tags=["unwrap_or_else", "map_or_else", "lazy evaluation"],
    teaches=["Arguments to `unwrap_or` and `map_or` are evaluated before the call, even when the `Option` is `Some`.", "The `_else` variants take closures and run them only on `None`; `map_or_else` takes the default closure first."],
    statement="""
        Both functions panic with *index out of bounds* when a colour was chosen but the palette is empty,
        although neither needs the palette then. Fix them.
    """,
    examples=[("theme(Some(\"red\"), [])", "\"red\""), ("theme_len(Some(\"red\"), [])", "3"), ("theme_len(None, [\"blue\"])", "4")],
    starter=THEME_GUARD,
    solution=THEME_GUARD.replace("chosen.unwrap_or(palette[0])", "chosen.unwrap_or_else(|| palette[0])").replace("chosen.map_or(palette[0].len(), str::len)", "chosen.map_or_else(|| palette[0].len(), str::len)"),
    rules=dict(lines=10),
    visible=[
        T("chosen_wins", "chosen = Some(\"red\"), palette = [\"blue\", \"green\"]", '(theme(Some("red"), &["blue", "green"]), theme_len(Some("red"), &["blue", "green"]))', '("red", 3)'),
        T("first_of_palette", "chosen = None, palette = [\"blue\", \"green\"]", '(theme(None, &["blue", "green"]), theme_len(None, &["blue", "green"]))', '("blue", 4)'),
        T("nothing_at_all", "chosen = None, palette = []", "(theme(None, &[]), theme_len(None, &[]))", '("black", 0)'),
        T("theme_with_empty_palette", "chosen = Some(\"red\"), palette = []", 'theme(Some("red"), &[])', '"red"'),
        T("theme_len_with_empty_palette", "chosen = Some(\"red\"), palette = []", 'theme_len(Some("red"), &[])', "3"),
    ],
    hidden=[
        T("empty_choice_is_still_a_choice", "chosen = Some(\"\"), palette = [\"blue\"]", '(theme(Some(""), &["blue"]), theme_len(Some(""), &["blue"]))', '("", 0)'),
        T("single_colour", "chosen = None, palette = [\"teal\"]", '(theme(None, &["teal"]), theme_len(None, &["teal"]))', '("teal", 4)'),
        T("chosen_black", "chosen = Some(\"black\"), palette = []", '(theme(Some("black"), &[]), theme_len(Some("black"), &[]))', '("black", 5)'),
        T("chosen_in_palette", "chosen = Some(\"green\"), palette = [\"blue\", \"green\"]", 'theme(Some("green"), &["blue", "green"])', '"green"'),
        T("empty_first_colour", "chosen = None, palette = [\"\", \"blue\"]", '(theme(None, &["", "blue"]), theme_len(None, &["", "blue"]))', '("", 0)'),
        T("unicode_choice_empty_palette", "chosen = Some(\"青\"), palette = []", '(theme(Some("青"), &[]), theme_len(Some("青"), &[]))', '("青", 3)'),
        T("unicode_palette_length_in_bytes", "chosen = None, palette = [\"rosé\", \"青\"]", '(theme(None, &["rosé", "青"]), theme_len(None, &["rosé", "青"]))', '("rosé", 5)'),
        T("empty_choice_empty_palette", "chosen = Some(\"\"), palette = []", '(theme(Some(""), &[]), theme_len(Some(""), &[]))', '("", 0)'),
        T("returns_the_chosen_str", "chosen = Some(c), palette = []", "std::ptr::eq(theme(Some(c), &[]).as_ptr(), c.as_ptr())", "true", setup='let c = "crimson";'),
        T("long_palette", "chosen = None, palette = 100000 colours", "(theme(None, &palette), theme_len(None, &palette))", '("c0", 2)', setup='let names: Vec<String> = (0..100_000).map(|i| format!("c{i}")).collect();\nlet palette: Vec<&str> = names.iter().map(|s| s.as_str()).collect();'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1312);
            let colours = ["red", "blue", "", "black", "青"];
            for _ in 0..300 {
                let chosen = if rng.bool() { Some(*rng.pick(&colours)) } else { None };
                let n = rng.below(4);
                let mut palette: Vec<&str> = Vec::new();
                for _ in 0..n {
                    palette.push(*rng.pick(&colours));
                }
                let want = match (chosen, palette.first()) {
                    (Some(c), _) => Some(c),
                    (None, Some(&p)) => Some(p),
                    (None, None) => None,
                };
                let desc = format!("chosen = {chosen:?}, palette = {palette:?}");
                check!(format!("theme, {desc}"), theme(chosen, &palette), want.unwrap_or("black"));
                check!(format!("theme_len, {desc}"), theme_len(chosen, &palette), want.map_or(0, str::len));
            }
        }
        """,
    ],
    wrong=dict(
        empty_palette_ignores_the_choice=THEME_GUARD.replace("if chosen.is_none() && palette.is_empty() {", "if palette.is_empty() {"),
        palette_wins=THEME_GUARD.replace("chosen.unwrap_or(palette[0])", "palette.first().copied().or(chosen).unwrap_or(\"black\")").replace("chosen.map_or(palette[0].len(), str::len)", "palette.first().or(chosen.as_ref()).map_or(0, |s| s.len())"),
        only_theme_fixed=THEME_GUARD.replace("chosen.unwrap_or(palette[0])", "chosen.unwrap_or_else(|| palette[0])"),
    ),
    hints=[("approach", "The panic comes from `palette[0]`, which runs before `unwrap_or` or `map_or` even look at `chosen`."),
           ("rust", "`unwrap_or_else(|| ...)` and `map_or_else(|| default, f)` only run the default closure on `None`. Note the order: default first, then `f`.")],
    notes=("Arguments are evaluated before a call, so `unwrap_or(palette[0])` indexes even when it isn't needed. API reminder: `unwrap_or` / `unwrap_or_else(|| ..)` / `unwrap_or_default()`, `map_or(default, f)` / `map_or_else(|| default, f)`, `or(opt)` / `or_else(|| opt)`. Clippy's `or_fun_call` lint flags the eager forms when the default is a call. The idiomatic `theme` is `chosen.or_else(|| palette.first().copied()).unwrap_or(\"black\")`.", "O(1)", "O(1)"),
    follow_up="When is the eager `unwrap_or` the better choice, and why does `map_or_else` put the default closure first?",
    related=["S4"],
))

P.append(dict(
    slug="as-ref-as-mut-as-deref", title="as_ref, as_mut and as_deref", level="medium", stage="understand-it", tags=["as_deref", "as_mut"],
    teaches=["`as_deref` turns `&Option<String>` into `Option<&str>`.", "`as_mut` edits the value inside an `Option` in place."],
    statement="""
        Write `display_name`, which returns the nickname if there is one and the name otherwise, and
        `shout_nickname`, which uppercases the nickname in place. Neither may clone.
    """,
    starter="""
        pub struct User {
            pub name: String,
            pub nickname: Option<String>,
        }

        pub fn display_name(user: &User) -> &str {
            todo!()
        }

        pub fn shout_nickname(user: &mut User) {
            todo!()
        }
    """,
    solution="""
        pub struct User {
            pub name: String,
            pub nickname: Option<String>,
        }

        pub fn display_name(user: &User) -> &str {
            user.nickname.as_deref().unwrap_or(&user.name)
        }

        pub fn shout_nickname(user: &mut User) {
            if let Some(n) = user.nickname.as_mut() {
                n.make_ascii_uppercase();
            }
        }
    """,
    visible=[
        T("nickname_wins", "name \"Ada\", nickname \"ace\"", "display_name(&u)", '"ace"', setup='let u = User { name: "Ada".into(), nickname: Some("ace".into()) };'),
        T("falls_back", "name \"Ada\", no nickname", "display_name(&u)", '"Ada"', setup='let u = User { name: "Ada".into(), nickname: None };'),
        T("shout", "nickname \"ace\"", '{ let mut u = User { name: "Ada".into(), nickname: Some("ace".into()) }; shout_nickname(&mut u); u.nickname }', 'Some("ACE".to_string())'),
        T("empty_nickname_still_wins", "name \"Ada\", nickname \"\"", "display_name(&u)", '""', setup='let u = User { name: "Ada".into(), nickname: Some(String::new()) };'),
        T("shout_leaves_the_name_alone", "name \"Ada\", nickname \"ace\"", '{ let mut u = User { name: "Ada".into(), nickname: Some("ace".into()) }; shout_nickname(&mut u); (u.nickname, u.name) }', '(Some("ACE".to_string()), "Ada".to_string())'),
    ],
    hidden=[
        T("shout_none", "no nickname", '{ let mut u = User { name: "Ada".into(), nickname: None }; shout_nickname(&mut u); (u.nickname, u.name) }', '(None, "Ada".to_string())'),
        T("empty_name_no_nickname", "name \"\", no nickname", "display_name(&u)", '""', setup='let u = User { name: String::new(), nickname: None };'),
        T("unicode_nickname", "name \"Ada\", nickname \"zoë 🦀\"", "display_name(&u)", '"zoë 🦀"', setup='let u = User { name: "Ada".into(), nickname: Some("zoë 🦀".into()) };'),
        T("shout_mixed", "nickname \"a1-bC d\"", '{ let mut u = User { name: "x".into(), nickname: Some("a1-bC d".into()) }; shout_nickname(&mut u); u.nickname }', 'Some("A1-BC D".to_string())'),
        T("shout_twice", "nickname \"ace\", shouted twice", '{ let mut u = User { name: "x".into(), nickname: Some("ace".into()) }; shout_nickname(&mut u); shout_nickname(&mut u); u.nickname }', 'Some("ACE".to_string())'),
        T("shout_empty_nickname", "nickname \"\"", '{ let mut u = User { name: "Ada".into(), nickname: Some(String::new()) }; shout_nickname(&mut u); (u.nickname, u.name) }', '(Some(String::new()), "Ada".to_string())'),
        T("borrows_the_nickname", "name \"Ada\", nickname \"ace\"", "std::ptr::eq(display_name(&u).as_ptr(), u.nickname.as_ref().map_or(std::ptr::null(), |n| n.as_ptr()))", "true", setup='let u = User { name: "Ada".into(), nickname: Some("ace".into()) };'),
        T("borrows_the_name", "name \"Ada\", no nickname", "std::ptr::eq(display_name(&u).as_ptr(), u.name.as_ptr())", "true", setup='let u = User { name: "Ada".into(), nickname: None };'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1304);
            for _ in 0..300 {
                let len = rng.below(4);
                let name = rng.string(len, "abZ ");
                let has = rng.bool();
                let len = rng.below(4);
                let nick = rng.string(len, "xyQ!");
                let nickname = if has { Some(nick.clone()) } else { None };
                let mut u = User { name: name.clone(), nickname: nickname.clone() };
                let desc = format!("name = {name:?}, nickname = {nickname:?}");
                let want = if has { nick.clone() } else { name.clone() };
                check!(desc.clone(), display_name(&u).to_string(), want);
                shout_nickname(&mut u);
                check!(format!("shout: {desc}"), (u.nickname, u.name), (nickname.map(|n| n.to_ascii_uppercase()), name));
            }
        }
        """,
    ],
    wrong=dict(
        empty_nickname_falls_back="""
            pub struct User {
                pub name: String,
                pub nickname: Option<String>,
            }

            pub fn display_name(user: &User) -> &str {
                user.nickname.as_deref().filter(|n| !n.is_empty()).unwrap_or(&user.name)
            }

            pub fn shout_nickname(user: &mut User) {
                if let Some(n) = user.nickname.as_mut() {
                    n.make_ascii_uppercase();
                }
            }
        """,
        shout_fills_in_the_name="""
            pub struct User {
                pub name: String,
                pub nickname: Option<String>,
            }

            pub fn display_name(user: &User) -> &str {
                user.nickname.as_deref().unwrap_or(&user.name)
            }

            pub fn shout_nickname(user: &mut User) {
                let n = user.nickname.get_or_insert_with(|| user.name.clone());
                n.make_ascii_uppercase();
            }
        """,
    ),
    hints=[("rust", "`user.nickname.map(..)` would move out of a borrowed struct. Convert `&Option<String>` to `Option<&str>` first.")],
    notes=("`as_deref` borrows through the `Option` and derefs `String` to `str`; the result's lifetime is tied to `user`.", "O(1)", "O(1)"),
    follow_up="What's the difference between `Option<&T>` and `&Option<T>` as a parameter type?",
    related=["S7", "L2"],
))

P.append(dict(
    slug="option-ref-to-str", title="Option<&String> to Option<&str>", level="medium", stage="understand-it", tags=["Option", "lifetimes"],
    teaches=["`map(String::as_str)` and `map_or` over borrowed values.", "One lifetime for a map and a default."],
    statement="Write `label`, which looks up a label by id, and `label_or`, which falls back to `default`. Neither may allocate.",
    starter="""
        use std::collections::HashMap;

        pub fn label(labels: &HashMap<u32, String>, id: u32) -> Option<&str> {
            todo!()
        }

        pub fn label_or<'a>(labels: &'a HashMap<u32, String>, id: u32, default: &'a str) -> &'a str {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashMap;

        pub fn label(labels: &HashMap<u32, String>, id: u32) -> Option<&str> {
            labels.get(&id).map(String::as_str)
        }

        pub fn label_or<'a>(labels: &'a HashMap<u32, String>, id: u32, default: &'a str) -> &'a str {
            label(labels, id).unwrap_or(default)
        }
    """,
    visible=[
        T("found", "labels = {1: \"one\"}, id = 1", "label(&m, 1)", 'Some("one")', setup='let m = std::collections::HashMap::from([(1, "one".to_string())]);'),
        T("missing", "labels = {}, id = 7", "label(&m, 7)", "None", setup="let m = std::collections::HashMap::new();"),
        T("default", "labels = {}, id = 7, default = \"?\"", 'label_or(&m, 7, "?")', '"?"', setup="let m = std::collections::HashMap::new();"),
        T("default_not_used_when_found", "labels = {1: \"one\", 2: \"two\"}, id = 2, default = \"?\"", 'label_or(&m, 2, "?")', '"two"', setup='let m = std::collections::HashMap::from([(1, "one".to_string()), (2, "two".to_string())]);'),
        T("empty_label_is_still_a_label", "labels = {3: \"\"}, id = 3, default = \"?\"", '(label(&m, 3), label_or(&m, 3, "?"))', '(Some(""), "")', setup='let m = std::collections::HashMap::from([(3, String::new())]);'),
    ],
    hidden=[
        T("default_unused", "labels = {2: \"two\"}, id = 2", 'label_or(&m, 2, "?")', '"two"', setup='let m = std::collections::HashMap::from([(2, "two".to_string())]);'),
        T("other_id", "labels = {1: \"one\"}, id = 2", "label(&m, 2)", "None", setup='let m = std::collections::HashMap::from([(1, "one".to_string())]);'),
        T("id_zero", "labels = {0: \"zero\"}, id = 0", "label(&m, 0)", 'Some("zero")', setup='let m = std::collections::HashMap::from([(0, "zero".to_string())]);'),
        T("id_max", "labels = {u32::MAX: \"max\"}, id = u32::MAX", 'label_or(&m, u32::MAX, "?")', '"max"', setup='let m = std::collections::HashMap::from([(u32::MAX, "max".to_string())]);'),
        T("empty_default", "labels = {}, id = 1, default = \"\"", 'label_or(&m, 1, "")', '""', setup="let m = std::collections::HashMap::new();"),
        T("unicode_label", "labels = {5: \"café ☕\"}, id = 5", "label(&m, 5)", 'Some("café ☕")', setup='let m = std::collections::HashMap::from([(5, "café ☕".to_string())]);'),
        T("borrows_from_the_map", "labels = {1: \"one\"}, id = 1", 'std::ptr::eq(label_or(&m, 1, "?").as_ptr(), m[&1].as_ptr())', "true", setup='let m = std::collections::HashMap::from([(1, "one".to_string())]);'),
        T("returns_the_default_itself", "labels = {}, id = 1, default = d", "std::ptr::eq(label_or(&m, 1, d).as_ptr(), d.as_ptr())", "true", setup='let m = std::collections::HashMap::new(); let d = "fallback";'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1305);
            for _ in 0..300 {
                let n = rng.below(6);
                let mut m = std::collections::HashMap::new();
                let mut pairs: Vec<(u32, String)> = Vec::new();
                for _ in 0..n {
                    let k = rng.below(8) as u32;
                    let len = rng.below(3);
                    let v = rng.string(len, "ab");
                    m.insert(k, v.clone());
                    pairs.retain(|(pk, _)| *pk != k);
                    pairs.push((k, v));
                }
                let id = rng.below(8) as u32;
                let want = pairs.iter().find(|(k, _)| *k == id).map(|(_, v)| v.as_str());
                check!(format!("labels = {m:?}, id = {id}"), label(&m, id), want);
                check!(format!("labels = {m:?}, id = {id}, default = \\"-\\""), label_or(&m, id, "-"), want.unwrap_or("-"));
            }
        }

        #[test]
        fn scale_many_lookups() {
            let n: u32 = 200_000;
            let m: std::collections::HashMap<u32, String> = (0..n).map(|i| (i * 2, "x".to_string())).collect();
            let mut found = 0usize;
            for id in 0..2 * n {
                if label_or(&m, id, "").len() == 1 {
                    found += 1;
                }
            }
            check!("200000 labels (even ids), look up every id below 400000", found, 200_000);
        }
        """,
    ],
    wrong=dict(
        empty_label_is_missing="""
            use std::collections::HashMap;

            pub fn label(labels: &HashMap<u32, String>, id: u32) -> Option<&str> {
                labels.get(&id).map(String::as_str).filter(|s| !s.is_empty())
            }

            pub fn label_or<'a>(labels: &'a HashMap<u32, String>, id: u32, default: &'a str) -> &'a str {
                label(labels, id).unwrap_or(default)
            }
        """,
        linear_scan="""
            use std::collections::HashMap;

            pub fn label(labels: &HashMap<u32, String>, id: u32) -> Option<&str> {
                labels.iter().find(|(k, _)| **k == id).map(|(_, v)| v.as_str())
            }

            pub fn label_or<'a>(labels: &'a HashMap<u32, String>, id: u32, default: &'a str) -> &'a str {
                label(labels, id).unwrap_or(default)
            }
        """,
    ),
    hints=[("rust", "`get` gives `Option<&String>`. `String::as_str` turns `&String` into `&str`.")],
    notes=("`label_or` needs both inputs to outlive the result, so they share `'a`.", "O(1)", "O(1)"),
    follow_up="Why can't `label_or` return `&str` without naming a lifetime?",
    related=["L3", "S4"],
))

P.append(dict(
    slug="transpose", title="Option<Result> and transpose", level="medium", stage="understand-it", tags=["transpose", "ParseIntError"],
    teaches=["`transpose` swaps `Option<Result<T, E>>` and `Result<Option<T>, E>`.", "`map(str::parse)` on an `Option`."],
    statement="Parse an optional string. No input is `Ok(None)`; a valid number is `Ok(Some(n))`; anything else is an error.",
    starter="""
        use std::num::ParseIntError;

        pub fn parse_optional(s: Option<&str>) -> Result<Option<i32>, ParseIntError> {
            todo!()
        }
    """,
    solution="""
        use std::num::ParseIntError;

        pub fn parse_optional(s: Option<&str>) -> Result<Option<i32>, ParseIntError> {
            s.map(str::parse).transpose()
        }
    """,
    visible=[
        T("none", "s = None", "parse_optional(None)", "Ok(None)"),
        T("number", "s = Some(\"42\")", 'parse_optional(Some("42"))', "Ok(Some(42))"),
        T("bad", "s = Some(\"x\")", 'parse_optional(Some("x")).is_err()', "true"),
        T("empty_string_is_an_error_not_none", "s = Some(\"\")", 'parse_optional(Some("")).is_err()', "true"),
        T("too_big_for_i32", "s = Some(\"2147483648\")", 'parse_optional(Some("2147483648")).is_err()', "true"),
    ],
    hidden=[
        T("negative", "s = Some(\"-7\")", 'parse_optional(Some("-7"))', "Ok(Some(-7))"),
        T("empty_string", "s = Some(\"\")", 'parse_optional(Some("")).is_err()', "true"),
        T("zero", "s = Some(\"0\")", 'parse_optional(Some("0"))', "Ok(Some(0))"),
        T("i32_max", "s = Some(\"2147483647\")", 'parse_optional(Some("2147483647"))', "Ok(Some(i32::MAX))"),
        T("i32_min", "s = Some(\"-2147483648\")", 'parse_optional(Some("-2147483648"))', "Ok(Some(i32::MIN))"),
        T("below_i32_min", "s = Some(\"-2147483649\")", 'parse_optional(Some("-2147483649"))', 'Err("-2147483649".parse::<i32>().unwrap_err())'),
        T("leading_space", "s = Some(\" 5\")", 'parse_optional(Some(" 5"))', 'Err(" 5".parse::<i32>().unwrap_err())'),
        T("decimal", "s = Some(\"1.0\")", 'parse_optional(Some("1.0"))', 'Err("1.0".parse::<i32>().unwrap_err())'),
        T("keeps_the_parse_error", "s = Some(\"\")", 'parse_optional(Some("")).map_err(|e| e.kind().clone())', "Err(std::num::IntErrorKind::Empty)"),
        T("full_width_digits", "s = Some(\"４２\")", 'parse_optional(Some("４２")).is_err()', "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1306);
            for _ in 0..400 {
                let s = match rng.below(4) {
                    0 => None,
                    1 => {
                        let len = rng.below(5);
                        Some(rng.string(len, "01-+ x9"))
                    }
                    2 => Some(rng.int(-3_000_000_000, 3_000_000_000).to_string()),
                    _ => Some((i64::from(i32::MAX) + rng.int(-2, 2)).to_string()),
                };
                let want = match &s {
                    None => Ok(None),
                    Some(t) => t.parse::<i32>().map(Some),
                };
                check!(format!("s = {s:?}"), parse_optional(s.as_deref()), want);
            }
        }
        """,
    ],
    wrong=dict(
        empty_is_none="""
            use std::num::ParseIntError;

            pub fn parse_optional(s: Option<&str>) -> Result<Option<i32>, ParseIntError> {
                match s {
                    None | Some("") => Ok(None),
                    Some(t) => t.parse().map(Some),
                }
            }
        """,
        trims_first="""
            use std::num::ParseIntError;

            pub fn parse_optional(s: Option<&str>) -> Result<Option<i32>, ParseIntError> {
                s.map(|t| t.trim().parse()).transpose()
            }
        """,
        parse_wide_then_cast="""
            use std::num::ParseIntError;

            pub fn parse_optional(s: Option<&str>) -> Result<Option<i32>, ParseIntError> {
                s.map(|t| t.parse::<i64>().map(|n| n as i32)).transpose()
            }
        """,
    ),
    hints=[("rust", "`s.map(str::parse)` has type `Option<Result<i32, _>>`. Which way round do you need it?")],
    notes=("`transpose` exists for exactly this: the caller can then use `?` on the result.", "O(n)", "O(1)"),
    follow_up="Where do you hit `Option<Result<..>>` in real code?",
    related=["L8"],
))

STORE = """
        use std::collections::HashMap;

        #[derive(Debug, PartialEq, Eq)]
        pub enum StoreError {
            Corrupt(String),
            Missing(String),
        }

        pub struct Store {
            data: HashMap<String, String>,
        }

        impl Store {
            pub fn new(pairs: &[(&str, &str)]) -> Store {
                Store { data: pairs.iter().map(|&(k, v)| (k.to_string(), v.to_string())).collect() }
            }

            /// `Ok(None)` if `key` is absent, `Err(Corrupt(key))` if its value isn't an integer.
            pub fn get(&self, key: &str) -> Result<Option<i64>, StoreError> {
                match self.data.get(key) {
                    None => Ok(None),
                    Some(v) => v.parse().map(Some).map_err(|_| StoreError::Corrupt(key.to_string())),
                }
            }
        }
"""

P.append(dict(
    slug="result-of-option", title="Result<Option<T>> and ?", level="medium", stage="understand-it", tags=["?", "Option", "err"],
    teaches=["`?` on a `Result<Option<T>, E>` leaves the `Option` for you to handle.", "`.ok()` would silently turn an error into \"missing\"; `.err()` keeps only the error."],
    statement="""
        `Store::get` returns `Ok(None)` for a missing key and `Err(Corrupt(key))` for a value that isn't an integer.
        Write `require`, which reports a missing key as `Err(Missing(key))`, and `sum_or_zero`, which adds up
        `keys` and counts missing ones as 0. Both pass the first `Corrupt` error straight through.
        Then write `first_corrupt`, which returns the error of the first corrupt key in `keys`, or `None`.
    """,
    examples=[("store = {a: \"5\", b: \"x\"}, require(\"c\")", "Err(Missing(\"c\"))"), ("store = {a: \"5\", b: \"x\"}, sum_or_zero([\"a\", \"c\"])", "Ok(5)")],
    constraints=["Values fit in an `i64`, and so does every sum."],
    starter=STORE + """
        pub fn require(store: &Store, key: &str) -> Result<i64, StoreError> {
            todo!()
        }

        pub fn sum_or_zero(store: &Store, keys: &[&str]) -> Result<i64, StoreError> {
            todo!()
        }

        pub fn first_corrupt(store: &Store, keys: &[&str]) -> Option<StoreError> {
            todo!()
        }
    """,
    solution=STORE + """
        pub fn require(store: &Store, key: &str) -> Result<i64, StoreError> {
            store.get(key)?.ok_or_else(|| StoreError::Missing(key.to_string()))
        }

        pub fn sum_or_zero(store: &Store, keys: &[&str]) -> Result<i64, StoreError> {
            let mut total = 0;
            for key in keys {
                total += store.get(key)?.unwrap_or(0);
            }
            Ok(total)
        }

        pub fn first_corrupt(store: &Store, keys: &[&str]) -> Option<StoreError> {
            keys.iter().find_map(|k| store.get(k).err())
        }
    """,
    visible=[
        T("require_present", "store = {a: \"5\"}, require(\"a\")", 'require(&Store::new(&[("a", "5")]), "a")', "Ok(5)"),
        T("require_missing", "store = {a: \"5\"}, require(\"b\")", 'require(&Store::new(&[("a", "5")]), "b")', 'Err(StoreError::Missing("b".to_string()))'),
        T("require_corrupt", "store = {a: \"x\"}, require(\"a\")", 'require(&Store::new(&[("a", "x")]), "a")', 'Err(StoreError::Corrupt("a".to_string()))'),
        T("sum_counts_missing_as_zero", "store = {a: \"5\", b: \"-2\"}, sum_or_zero([\"a\", \"b\", \"c\"])", 'sum_or_zero(&Store::new(&[("a", "5"), ("b", "-2")]), &["a", "b", "c"])', "Ok(3)"),
        T("sum_stops_at_corrupt", "store = {a: \"1\", b: \"x\"}, sum_or_zero([\"a\", \"b\"])", 'sum_or_zero(&Store::new(&[("a", "1"), ("b", "x")]), &["a", "b"])', 'Err(StoreError::Corrupt("b".to_string()))'),
    ],
    hidden=[
        T("first_corrupt_none", "store = {a: \"1\", b: \"x\"}, first_corrupt([\"a\", \"c\"])", 'first_corrupt(&Store::new(&[("a", "1"), ("b", "x")]), &["a", "c"])', "None"),
        T("first_corrupt_first_wins", "store = {a: \"x\", b: \"y\"}, first_corrupt([\"c\", \"b\", \"a\"])", 'first_corrupt(&Store::new(&[("a", "x"), ("b", "y")]), &["c", "b", "a"])', 'Some(StoreError::Corrupt("b".to_string()))'),
        T("first_corrupt_no_keys", "store = {a: \"x\"}, first_corrupt([])", 'first_corrupt(&Store::new(&[("a", "x")]), &[])', "None"),
        T("sum_no_keys", "store = {a: \"x\"}, sum_or_zero([])", 'sum_or_zero(&Store::new(&[("a", "x")]), &[])', "Ok(0)"),
        T("sum_all_missing", "store = {}, sum_or_zero([\"a\", \"b\"])", 'sum_or_zero(&Store::new(&[]), &["a", "b"])', "Ok(0)"),
        T("sum_repeated_key", "store = {a: \"5\"}, sum_or_zero([\"a\", \"a\"])", 'sum_or_zero(&Store::new(&[("a", "5")]), &["a", "a"])', "Ok(10)"),
        T("sum_first_corrupt_wins", "store = {a: \"x\", b: \"y\"}, sum_or_zero([\"c\", \"b\", \"a\"])", 'sum_or_zero(&Store::new(&[("a", "x"), ("b", "y")]), &["c", "b", "a"])', 'Err(StoreError::Corrupt("b".to_string()))'),
        T("sum_corrupt_key_not_asked", "store = {a: \"2\", b: \"x\"}, sum_or_zero([\"a\"])", 'sum_or_zero(&Store::new(&[("a", "2"), ("b", "x")]), &["a"])', "Ok(2)"),
        T("require_empty_value", "store = {a: \"\"}, require(\"a\")", 'require(&Store::new(&[("a", "")]), "a")', 'Err(StoreError::Corrupt("a".to_string()))'),
        T("require_zero_is_present", "store = {a: \"0\"}, require(\"a\")", 'require(&Store::new(&[("a", "0")]), "a")', "Ok(0)"),
        T("require_i64_bounds", "store = {lo: \"-9223372036854775808\", hi: \"9223372036854775807\"}", '(require(&s, "lo"), require(&s, "hi"))', "(Ok(i64::MIN), Ok(i64::MAX))", setup='let s = Store::new(&[("lo", "-9223372036854775808"), ("hi", "9223372036854775807")]);'),
        T("require_empty_key", "store = {a: \"1\"}, require(\"\")", 'require(&Store::new(&[("a", "1")]), "")', 'Err(StoreError::Missing(String::new()))'),
        T("require_unicode_key", "store = {ключ: \"7\"}, require(\"ключ\"), require(\"клю\")", '(require(&s, "ключ"), require(&s, "клю"))', '(Ok(7), Err(StoreError::Missing("клю".to_string())))', setup='let s = Store::new(&[("ключ", "7")]);'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1313);
            let names = ["a", "b", "c", "d"];
            let values = ["1", "-3", "10", "x", "", "7"];
            for _ in 0..400 {
                let mut pairs: Vec<(&str, &str)> = Vec::new();
                for &k in &names {
                    if rng.bool() {
                        pairs.push((k, *rng.pick(&values)));
                    }
                }
                let store = Store::new(&pairs);
                let n = rng.below(5);
                let mut keys: Vec<&str> = Vec::new();
                for _ in 0..n {
                    keys.push(*rng.pick(&names));
                }
                let lookup = |k: &str| pairs.iter().find(|(pk, _)| *pk == k).map(|(_, v)| *v);
                let key = *rng.pick(&names);
                let want_one = match lookup(key) {
                    None => Err(StoreError::Missing(key.to_string())),
                    Some(v) => v.parse::<i64>().map_err(|_| StoreError::Corrupt(key.to_string())),
                };
                check!(format!("store = {pairs:?}, require({key:?})"), require(&store, key), want_one);
                let mut want: Result<i64, StoreError> = Ok(0);
                for &k in &keys {
                    match lookup(k).map(|v| v.parse::<i64>()) {
                        None => {}
                        Some(Ok(v)) => {
                            if let Ok(t) = &mut want {
                                *t += v;
                            }
                        }
                        Some(Err(_)) => {
                            want = Err(StoreError::Corrupt(k.to_string()));
                            break;
                        }
                    }
                }
                check!(format!("store = {pairs:?}, sum_or_zero({keys:?})"), sum_or_zero(&store, &keys), want);
                let want_first = keys.iter().find(|&&k| lookup(k).is_some_and(|v| v.parse::<i64>().is_err())).map(|k| StoreError::Corrupt(k.to_string()));
                check!(format!("store = {pairs:?}, first_corrupt({keys:?})"), first_corrupt(&store, &keys), want_first);
            }
        }
        """,
    ],
    wrong=dict(
        corrupt_reads_as_missing=STORE + """
        pub fn require(store: &Store, key: &str) -> Result<i64, StoreError> {
            store.get(key).ok().flatten().ok_or_else(|| StoreError::Missing(key.to_string()))
        }

        pub fn sum_or_zero(store: &Store, keys: &[&str]) -> Result<i64, StoreError> {
            let mut total = 0;
            for key in keys {
                total += store.get(key)?.unwrap_or(0);
            }
            Ok(total)
        }

        pub fn first_corrupt(store: &Store, keys: &[&str]) -> Option<StoreError> {
            keys.iter().find_map(|k| store.get(k).err())
        }
        """,
        sum_skips_corrupt=STORE + """
        pub fn require(store: &Store, key: &str) -> Result<i64, StoreError> {
            store.get(key)?.ok_or_else(|| StoreError::Missing(key.to_string()))
        }

        pub fn sum_or_zero(store: &Store, keys: &[&str]) -> Result<i64, StoreError> {
            Ok(keys.iter().map(|k| store.get(k).ok().flatten().unwrap_or(0)).sum())
        }

        pub fn first_corrupt(store: &Store, keys: &[&str]) -> Option<StoreError> {
            keys.iter().find_map(|k| store.get(k).err())
        }
        """,
        require_defaults_to_zero=STORE + """
        pub fn require(store: &Store, key: &str) -> Result<i64, StoreError> {
            Ok(store.get(key)?.unwrap_or(0))
        }

        pub fn sum_or_zero(store: &Store, keys: &[&str]) -> Result<i64, StoreError> {
            let mut total = 0;
            for key in keys {
                total += store.get(key)?.unwrap_or(0);
            }
            Ok(total)
        }

        pub fn first_corrupt(store: &Store, keys: &[&str]) -> Option<StoreError> {
            keys.iter().find_map(|k| store.get(k).err())
        }
        """,
        first_corrupt_reports_the_last=STORE + """
        pub fn require(store: &Store, key: &str) -> Result<i64, StoreError> {
            store.get(key)?.ok_or_else(|| StoreError::Missing(key.to_string()))
        }

        pub fn sum_or_zero(store: &Store, keys: &[&str]) -> Result<i64, StoreError> {
            let mut total = 0;
            for key in keys {
                total += store.get(key)?.unwrap_or(0);
            }
            Ok(total)
        }

        pub fn first_corrupt(store: &Store, keys: &[&str]) -> Option<StoreError> {
            keys.iter().filter_map(|k| store.get(k).err()).last()
        }
        """,
    ),
    hints=[("rust", "`store.get(key)?` has type `Option<i64>`: the `?` deals with the error layer, then you deal with the option layer."),
           ("edge case", "`store.get(key).ok().flatten()` compiles, but it turns `Corrupt` into \"missing\". Keep the two layers apart.")],
    notes=("`Result<Option<T>, E>` means \"the lookup can fail, and a successful lookup can find nothing\". `?` peels the `Result`; `ok_or_else` or `unwrap_or` decides what absence means for each caller. API reminder: `r.ok()` is `Option<T>`, `r.err()` is `Option<E>`, `find_map` returns the first `Some`, and `transpose` flips `Result<Option<T>, E>` and `Option<Result<T, E>>`.", "O(k) for k keys", "O(1)"),
    follow_up="Why do database and cache clients return `Result<Option<T>, E>` rather than an error variant for \"not found\"?",
    related=["S6", "L8"],
))

P.append(dict(
    slug="collect-into-result", title="Collect into Result<Vec<_>, _>", level="medium", stage="understand-it", tags=["collect", "FromIterator"],
    teaches=["`collect::<Result<Vec<_>, _>>()` stops at the first error.", "`map_err` to add context per item."],
    statement="Parse every item as an `i32`. Return all of them, or `Err(\"bad number: <item>\")` for the first one that doesn't parse.",
    starter="""
        pub fn parse_all(items: &[&str]) -> Result<Vec<i32>, String> {
            todo!()
        }
    """,
    solution="""
        pub fn parse_all(items: &[&str]) -> Result<Vec<i32>, String> {
            items
                .iter()
                .map(|s| s.parse().map_err(|_| format!("bad number: {s}")))
                .collect()
        }
    """,
    visible=[
        T("all_good", "[\"1\", \"2\", \"3\"]", 'parse_all(&["1", "2", "3"])', "Ok(vec![1, 2, 3])"),
        T("first_bad", "[\"1\", \"x\", \"y\"]", 'parse_all(&["1", "x", "y"])', 'Err("bad number: x".to_string())'),
        T("no_items", "[]", "parse_all(&[])", "Ok(vec![])"),
        T("signs", "[\"-1\", \"+2\"]", 'parse_all(&["-1", "+2"])', "Ok(vec![-1, 2])"),
        T("empty_item_is_bad", "[\"1\", \"\"]", 'parse_all(&["1", ""])', 'Err("bad number: ".to_string())'),
    ],
    hidden=[
        T("empty", "[]", "parse_all(&[])", "Ok(vec![])"),
        T("overflow", "[\"99999999999\"]", 'parse_all(&["99999999999"])', 'Err("bad number: 99999999999".to_string())'),
        T("bounds", "[\"-2147483648\", \"2147483647\"]", 'parse_all(&["-2147483648", "2147483647"])', "Ok(vec![i32::MIN, i32::MAX])"),
        T("just_past_max", "[\"2147483648\"]", 'parse_all(&["2147483648"])', 'Err("bad number: 2147483648".to_string())'),
        T("spaces_are_bad", "[\"1\", \" 2\"]", 'parse_all(&["1", " 2"])', 'Err("bad number:  2".to_string())'),
        T("last_is_bad", "[\"1\", \"2\", \"3.5\"]", 'parse_all(&["1", "2", "3.5"])', 'Err("bad number: 3.5".to_string())'),
        T("order_and_duplicates_kept", "[\"3\", \"1\", \"3\"]", 'parse_all(&["3", "1", "3"])', "Ok(vec![3, 1, 3])"),
        T("unicode_item", "[\"7\", \"٣\"]", 'parse_all(&["7", "٣"])', 'Err("bad number: ٣".to_string())'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1307);
            for _ in 0..400 {
                let n = rng.below(6);
                let mut items: Vec<String> = Vec::new();
                for _ in 0..n {
                    if rng.below(5) == 0 {
                        let len = rng.below(3);
                        items.push(rng.string(len, "x1-"));
                    } else {
                        items.push(rng.int(-99, 99).to_string());
                    }
                }
                let refs: Vec<&str> = items.iter().map(|s| s.as_str()).collect();
                let mut want: Result<Vec<i32>, String> = Ok(Vec::new());
                for s in &refs {
                    match s.parse::<i32>() {
                        Ok(v) => {
                            if let Ok(out) = &mut want {
                                out.push(v);
                            }
                        }
                        Err(_) => {
                            want = Err(format!("bad number: {s}"));
                            break;
                        }
                    }
                }
                check!(format!("items = {refs:?}"), parse_all(&refs), want);
            }
        }

        #[test]
        fn scale_bad_item_at_the_end() {
            let mut items: Vec<String> = (0..200_000).map(|i: i32| (i - 100_000).to_string()).collect();
            let refs: Vec<&str> = items.iter().map(|s| s.as_str()).collect();
            let want: Vec<i32> = (0..200_000).map(|i| i - 100_000).collect();
            check!("200000 numbers from -100000 up", parse_all(&refs), Ok(want));
            items.push("oops".to_string());
            let refs: Vec<&str> = items.iter().map(|s| s.as_str()).collect();
            check!("the same 200000 numbers, then \\"oops\\"", parse_all(&refs), Err("bad number: oops".to_string()));
        }
        """,
    ],
    wrong=dict(
        reports_the_last_bad_item="""
            pub fn parse_all(items: &[&str]) -> Result<Vec<i32>, String> {
                let mut out = Vec::new();
                let mut err = None;
                for s in items {
                    match s.parse() {
                        Ok(n) => out.push(n),
                        Err(_) => err = Some(format!("bad number: {s}")),
                    }
                }
                match err {
                    Some(e) => Err(e),
                    None => Ok(out),
                }
            }
        """,
        skips_blank_items="""
            pub fn parse_all(items: &[&str]) -> Result<Vec<i32>, String> {
                items
                    .iter()
                    .filter(|s| !s.is_empty())
                    .map(|s| s.parse().map_err(|_| format!("bad number: {s}")))
                    .collect()
            }
        """,
        trims_items="""
            pub fn parse_all(items: &[&str]) -> Result<Vec<i32>, String> {
                items
                    .iter()
                    .map(|s| s.trim().parse().map_err(|_| format!("bad number: {s}")))
                    .collect()
            }
        """,
    ),
    hints=[("rust", "`Result<Vec<T>, E>` implements `FromIterator<Result<T, E>>`.")],
    notes=("`collect` short-circuits on the first `Err`, so later items aren't parsed.", "O(n)", "O(n)"),
    follow_up="How would you collect every error instead of just the first?",
    related=["S6", "L8"],
))

WORKER_HEAD = """
        #[derive(Debug, Default)]
        pub struct Worker {
            pub current: Option<String>,
            pub done: Vec<String>,
        }
"""

P.append(dict(
    slug="fix-move-out-of-option", title="Fix: move out of an Option behind &mut", mode="fix", level="medium", stage="understand-it", tags=["take", "replace", "as_deref_mut"],
    teaches=["You can't move a value out of `&mut self`; you can swap something else in.", "`Option::take` leaves `None`; `Option::replace` leaves the new value. Both return the old one.", "`as_deref_mut` turns `&mut Option<String>` into `Option<&mut str>` without moving."],
    statement="""
        `start` begins a task and returns the one it interrupted, `finish` moves the current task to `done`, and
        `current_mut` lets the caller edit the current task in place. None of them compile:
        *cannot move out of `self.current`* (E0507). Fix them without cloning.
    """,
    examples=[("start(\"a\"), start(\"b\")", "second call returns Some(\"a\"); current = Some(\"b\")"), ("start(\"a\"), finish()", "true; current = None, done = [\"a\"]")],
    starter=WORKER_HEAD + """
        impl Worker {
            /// Starts `task` and returns the task it interrupted, if any.
            pub fn start(&mut self, task: String) -> Option<String> {
                let old = self.current;
                self.current = Some(task);
                old
            }

            /// Moves the current task to `done`. Returns false if there was none.
            pub fn finish(&mut self) -> bool {
                match self.current {
                    Some(task) => {
                        self.done.push(task);
                        true
                    }
                    None => false,
                }
            }

            /// The current task, for editing in place.
            pub fn current_mut(&mut self) -> Option<&mut str> {
                self.current.map(|mut s| s.as_mut_str())
            }
        }
    """,
    solution=WORKER_HEAD + """
        impl Worker {
            /// Starts `task` and returns the task it interrupted, if any.
            pub fn start(&mut self, task: String) -> Option<String> {
                self.current.replace(task)
            }

            /// Moves the current task to `done`. Returns false if there was none.
            pub fn finish(&mut self) -> bool {
                match self.current.take() {
                    Some(task) => {
                        self.done.push(task);
                        true
                    }
                    None => false,
                }
            }

            /// The current task, for editing in place.
            pub fn current_mut(&mut self) -> Option<&mut str> {
                self.current.as_deref_mut()
            }
        }
    """,
    rules=dict(methods=["clone", "cloned", "to_owned", "to_string"], lines=5),
    visible=[
        T("start_when_idle", "start(\"a\") on a new worker", '{ let mut w = Worker::default(); let r = w.start("a".into()); (r, w.current) }', '(None, Some("a".to_string()))'),
        T("start_interrupts", "start(\"a\"), start(\"b\")", '{ let mut w = Worker::default(); w.start("a".into()); let r = w.start("b".into()); (r, w.current) }', '(Some("a".to_string()), Some("b".to_string()))'),
        T("finish_moves_to_done", "start(\"a\"), finish()", '{ let mut w = Worker::default(); w.start("a".into()); let r = w.finish(); (r, w.current, w.done) }', '(true, None, vec!["a".to_string()])'),
        T("finish_when_idle", "finish() on a new worker", "{ let mut w = Worker::default(); let r = w.finish(); (r, w.current, w.done) }", "(false, None, Vec::<String>::new())"),
        T("finish_twice", "start(\"a\"), finish(), finish()", '{ let mut w = Worker::default(); w.start("a".into()); (w.finish(), w.finish(), w.done) }', '(true, false, vec!["a".to_string()])'),
    ],
    hidden=[
        T("current_mut_edits_in_place", "start(\"ab\"), uppercase through current_mut()", '{ let mut w = Worker::default(); w.start("ab".into()); if let Some(s) = w.current_mut() { s.make_ascii_uppercase(); } w.current }', 'Some("AB".to_string())'),
        T("current_mut_when_idle", "current_mut() on a new worker", "Worker::default().current_mut().is_none()", "true"),
        T("current_mut_then_finish", "start(\"a\"), uppercase through current_mut(), finish()", '{ let mut w = Worker::default(); w.start("a".into()); if let Some(s) = w.current_mut() { s.make_ascii_uppercase(); } w.finish(); (w.current, w.done) }', '(None, vec!["A".to_string()])'),
        T("interrupted_task_is_not_done", "start(\"a\"), start(\"b\"), finish()", '{ let mut w = Worker::default(); w.start("a".into()); w.start("b".into()); w.finish(); (w.current, w.done) }', '(None, vec!["b".to_string()])'),
        T("empty_task_name", "start(\"\"), finish(), finish()", '{ let mut w = Worker::default(); w.start(String::new()); (w.finish(), w.finish(), w.current, w.done) }', '(true, false, None, vec![String::new()])'),
        T("restart_after_finish", "start(\"a\"), finish(), start(\"b\")", '{ let mut w = Worker::default(); w.start("a".into()); w.finish(); let r = w.start("b".into()); (r, w.current, w.done) }', '(None, Some("b".to_string()), vec!["a".to_string()])'),
        T("done_keeps_order", "a, b, c each started and finished", '{ let mut w = Worker::default(); for t in ["a", "b", "c"] { w.start(t.into()); w.finish(); } w.done }', 'vec!["a".to_string(), "b".to_string(), "c".to_string()]'),
        T("same_task_twice", "start(\"a\"), start(\"a\")", '{ let mut w = Worker::default(); w.start("a".into()); let r = w.start("a".into()); (r, w.current) }', '(Some("a".to_string()), Some("a".to_string()))'),
        T("unicode_task", "start(\"修复 🦀\"), finish()", '{ let mut w = Worker::default(); w.start("修复 🦀".into()); (w.finish(), w.done) }', '(true, vec!["修复 🦀".to_string()])'),
        T("start_keeps_done", "done = [\"x\"], start(\"a\")", '{ let mut w = Worker { current: None, done: vec!["x".into()] }; w.start("a".into()); w.done }', 'vec!["x".to_string()]'),
        T("start_moves_not_copies", "start(t) returns the same buffer later", "{ let mut w = Worker::default(); w.start(t); w.start(\"b\".into()).map(|s| s.as_ptr()) }", "Some(p)", setup='let t = String::from("a");\nlet p = t.as_ptr();'),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(1314);
            let names = ["a", "b", "", "ç"];
            for _ in 0..300 {
                let mut w = Worker::default();
                let mut cur: Option<String> = None;
                let mut done: Vec<String> = Vec::new();
                let mut log: Vec<String> = Vec::new();
                let n = rng.below(8);
                for _ in 0..n {
                    if rng.bool() {
                        let t = rng.pick(&names).to_string();
                        log.push(format!("start({t:?})"));
                        let want = std::mem::replace(&mut cur, Some(t.clone()));
                        check!(log.join(", "), w.start(t), want);
                    } else {
                        log.push("finish()".to_string());
                        let want = match std::mem::take(&mut cur) {
                            Some(t) => {
                                done.push(t);
                                true
                            }
                            None => false,
                        };
                        check!(log.join(", "), w.finish(), want);
                    }
                }
                check!(format!("state after {}", log.join(", ")), (w.current, w.done), (cur, done));
            }
        }

        #[test]
        fn many_tasks() {
            let mut w = Worker::default();
            for i in 0..100_000 {
                w.start(i.to_string());
                w.finish();
            }
            check!("100000 tasks started and finished", (w.current, w.done.len(), w.done[99_999].clone()), (None, 100_000, "99999".to_string()));
        }
        """,
    ],
    wrong=dict(
        finish_leaves_an_empty_string=WORKER_HEAD + """
        impl Worker {
            /// Starts `task` and returns the task it interrupted, if any.
            pub fn start(&mut self, task: String) -> Option<String> {
                self.current.replace(task)
            }

            /// Moves the current task to `done`. Returns false if there was none.
            pub fn finish(&mut self) -> bool {
                match self.current.as_mut() {
                    Some(task) => {
                        self.done.push(std::mem::take(task));
                        true
                    }
                    None => false,
                }
            }

            /// The current task, for editing in place.
            pub fn current_mut(&mut self) -> Option<&mut str> {
                self.current.as_deref_mut()
            }
        }
        """,
        start_ignored_when_busy=WORKER_HEAD + """
        impl Worker {
            /// Starts `task` and returns the task it interrupted, if any.
            pub fn start(&mut self, task: String) -> Option<String> {
                if self.current.is_some() {
                    return Some(task);
                }
                self.current = Some(task);
                None
            }

            /// Moves the current task to `done`. Returns false if there was none.
            pub fn finish(&mut self) -> bool {
                match self.current.take() {
                    Some(task) => {
                        self.done.push(task);
                        true
                    }
                    None => false,
                }
            }

            /// The current task, for editing in place.
            pub fn current_mut(&mut self) -> Option<&mut str> {
                self.current.as_deref_mut()
            }
        }
        """,
    ),
    hints=[("approach", "Moving out would leave `self.current` holding nothing, which Rust doesn't allow behind a reference. Put a value back in the same step."),
           ("rust", "`self.current.take()` returns the old `Option` and leaves `None`; `self.current.replace(x)` leaves `Some(x)`. To borrow instead of move, go through `as_mut()` or `as_deref_mut()`.")],
    notes=("`take` and `replace` are `mem::replace` specialised for `Option`: they move the old value out and put a valid one back, so `&mut self` is never left half-empty. `current_mut` never needed to move at all. API reminder: `take()`, `replace(v)`, `insert(v) -> &mut T`, `get_or_insert_with(f) -> &mut T`, `as_mut()`, `as_deref_mut()`.", "O(1)", "O(1)"),
    follow_up="How do `take` and `replace` relate to `std::mem::take` and `std::mem::replace`? When would you reach for `mem::swap`?",
    related=["L2", "L3"],
))

SIZE_HEAD = """
        use std::num::{ParseFloatError, ParseIntError};

        #[derive(Debug, PartialEq)]
        pub enum SizeError {
            Missing(&'static str),
            BadInt(ParseIntError),
            BadFloat(ParseFloatError),
        }
"""

SIZE_TAIL = """
        fn field<'a>(s: &'a str, name: &'static str) -> Result<&'a str, SizeError> {
            s.split(';')
                .find_map(|kv| kv.strip_prefix(name)?.strip_prefix('='))
                .ok_or(SizeError::Missing(name))
        }

        /// Parses "width=80;height=24;scale=1.5" into (80, 24, 1.5). The scale is optional and defaults to 1.0.
        pub fn size(s: &str) -> Result<(u32, u32, f64), SizeError> {
            let w = field(s, "width")?.parse::<u32>()?;
            let h = field(s, "height")?.parse::<u32>()?;
            let scale = match field(s, "scale") {
                Ok(v) => v.parse::<f64>()?,
                Err(_) => 1.0,
            };
            Ok((w, h, scale))
        }
"""

SIZE_FROM = """
        impl From<ParseIntError> for SizeError {
            fn from(e: ParseIntError) -> Self {
                SizeError::BadInt(e)
            }
        }

        impl From<ParseFloatError> for SizeError {
            fn from(e: ParseFloatError) -> Self {
                SizeError::BadFloat(e)
            }
        }
"""

P.append(dict(
    slug="fix-question-mark-from", title="Fix: ? can't convert the error", mode="fix", level="medium", stage="understand-it", tags=["?", "From", "E0277"],
    teaches=["`?` converts the error with `From::from` before returning it.", "One `impl From` per source error type makes every `?` on it work."],
    statement="""
        `size` parses `"width=80;height=24;scale=1.5"`. It doesn't compile: *`?` couldn't convert the error to `SizeError`*
        (E0277), three times. Make it compile without touching `size` or `field`, keeping each parse error in its variant.
    """,
    examples=[("s = \"width=80;height=24\"", "Ok((80, 24, 1.0))"), ("s = \"width=80;height=24;scale=big\"", "Err(BadFloat(..))")],
    starter=SIZE_HEAD + SIZE_TAIL,
    solution=SIZE_HEAD + SIZE_FROM + SIZE_TAIL,
    rules=dict(methods=["map_err", "unwrap", "expect", "ok", "unwrap_or"], lines=12),
    visible=[
        T("all_fields", "s = \"width=80;height=24;scale=1.5\"", 'size("width=80;height=24;scale=1.5")', "Ok((80, 24, 1.5))"),
        T("scale_defaults_to_one", "s = \"height=24;width=80\"", 'size("height=24;width=80")', "Ok((80, 24, 1.0))"),
        T("missing_height", "s = \"width=80\"", 'size("width=80")', 'Err(SizeError::Missing("height"))'),
        T("bad_width", "s = \"width=abc;height=1\"", 'size("width=abc;height=1")', 'Err(SizeError::BadInt("abc".parse::<u32>().unwrap_err()))'),
        T("bad_scale", "s = \"width=1;height=1;scale=big\"", 'size("width=1;height=1;scale=big")', 'Err(SizeError::BadFloat("big".parse::<f64>().unwrap_err()))'),
    ],
    hidden=[
        T("empty_input", "s = \"\"", 'size("")', 'Err(SizeError::Missing("width"))'),
        T("empty_value", "s = \"width=;height=1\"", 'size("width=;height=1")', 'Err(SizeError::BadInt("".parse::<u32>().unwrap_err()))'),
        T("negative_height", "s = \"width=80;height=-1\"", 'size("width=80;height=-1")', 'Err(SizeError::BadInt("-1".parse::<u32>().unwrap_err()))'),
        T("width_overflows", "s = \"width=4294967296;height=1\"", 'size("width=4294967296;height=1")', 'Err(SizeError::BadInt("4294967296".parse::<u32>().unwrap_err()))'),
        T("bounds", "s = \"width=4294967295;height=0;scale=-0.5\"", 'size("width=4294967295;height=0;scale=-0.5")', "Ok((u32::MAX, 0, -0.5))"),
        T("empty_scale", "s = \"width=1;height=2;scale=\"", 'size("width=1;height=2;scale=")', 'Err(SizeError::BadFloat("".parse::<f64>().unwrap_err()))'),
        T("int_scale_is_fine", "s = \"scale=3;width=1;height=2\"", 'size("scale=3;width=1;height=2")', "Ok((1, 2, 3.0))"),
        T("bad_width_before_missing_height", "s = \"width=x\"", 'size("width=x")', 'Err(SizeError::BadInt("x".parse::<u32>().unwrap_err()))'),
        T("missing_width_before_bad_height", "s = \"height=x\"", 'size("height=x")', 'Err(SizeError::Missing("width"))'),
        T("int_error_before_float_error", "s = \"scale=z;width=1;height=y\"", 'size("scale=z;width=1;height=y")', 'Err(SizeError::BadInt("y".parse::<u32>().unwrap_err()))'),
        T("first_width_wins", "s = \"width=1;width=2;height=3\"", 'size("width=1;width=2;height=3")', "Ok((1, 3, 1.0))"),
        T("full_width_digit", "s = \"width=８;height=1\"", 'size("width=８;height=1")', 'Err(SizeError::BadInt("８".parse::<u32>().unwrap_err()))'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1315);
            let values = ["0", "7", "42", "-1", "", "x", "4294967295", "4294967296", "+3", "2.5", "1e3"];
            for _ in 0..300 {
                let w = rng.bool().then(|| *rng.pick(&values));
                let h = rng.bool().then(|| *rng.pick(&values));
                let sc = rng.bool().then(|| *rng.pick(&values));
                let mut parts: Vec<String> = Vec::new();
                for (name, v) in [("width", w), ("height", h), ("scale", sc)] {
                    if let Some(v) = v {
                        parts.push(format!("{name}={v}"));
                    }
                }
                rng.shuffle(&mut parts);
                let s = parts.join(";");
                let int = |v: Option<&str>, name: &'static str| v.ok_or(SizeError::Missing(name))?.parse::<u32>().map_err(SizeError::BadInt);
                let want = int(w, "width").and_then(|x| {
                    let y = int(h, "height")?;
                    let z = sc.map_or(Ok(1.0), |v| v.parse::<f64>().map_err(SizeError::BadFloat))?;
                    Ok((x, y, z))
                });
                check!(format!("s = {s:?}"), size(&s), want);
            }
        }
        """,
    ],
    wrong=dict(
        float_error_becomes_missing=SIZE_HEAD + SIZE_FROM.replace("SizeError::BadFloat(e)", "SizeError::Missing(\"scale\")").replace("fn from(e: ParseFloatError)", "fn from(_: ParseFloatError)") + SIZE_TAIL,
        bad_number_becomes_zero=SIZE_HEAD + SIZE_FROM + SIZE_TAIL.replace("let w = field(s, \"width\")?.parse::<u32>()?;\n            let h = field(s, \"height\")?.parse::<u32>()?;", "let w = field(s, \"width\")?.parse::<u32>().unwrap_or(0);\n            let h = field(s, \"height\")?.parse::<u32>().unwrap_or(0);"),
    ),
    hints=[("approach", "`x?` on `Err(e)` returns `Err(From::from(e))`. Which `From` impls are missing?"),
           ("rust", "`impl From<ParseIntError> for SizeError { fn from(e: ParseIntError) -> Self { SizeError::BadInt(e) } }`, and the same for `ParseFloatError`.")],
    notes=("Each `From` impl is written once, and every `?` on that error type in a function returning `SizeError` uses it. `map_err` at each call site works too but repeats itself; `thiserror`'s `#[from]` generates exactly these impls. API reminder: `?` needs `From<SourceError> for TargetError`; on `Option` it needs the function to return `Option`.", "O(n)", "O(1)"),
    follow_up="When would you prefer `map_err` at the call site over a `From` impl? What goes wrong with two variants that wrap the same source type?",
    related=["L8", "L10"],
))

P.append(dict(
    slug="fix-unwrap-on-input", title="Fix: unwrap on user input", mode="fix", level="medium", stage="understand-it", tags=["unwrap", "Result", "?"],
    teaches=["`unwrap` on input you don't control is a crash waiting for a user.", "Return errors that say what was wrong."],
    statement="""
        `average` takes comma-separated numbers like `"1, 2, 3"`. It panics on anything unexpected.
        Return `Err("no numbers")` for blank input and `Err("not a number: <item>")` for a bad item.
    """,
    starter="""
        /// The average of comma-separated numbers, e.g. "1, 2, 3".
        pub fn average(input: &str) -> Result<f64, String> {
            let nums: Vec<f64> = input.split(',').map(|s| s.trim().parse().unwrap()).collect();
            Ok(nums.iter().sum::<f64>() / nums.len() as f64)
        }
    """,
    solution="""
        /// The average of comma-separated numbers, e.g. "1, 2, 3".
        pub fn average(input: &str) -> Result<f64, String> {
            if input.trim().is_empty() {
                return Err("no numbers".into());
            }
            let nums = input
                .split(',')
                .map(|s| {
                    let s = s.trim();
                    s.parse::<f64>().map_err(|_| format!("not a number: {s}"))
                })
                .collect::<Result<Vec<f64>, String>>()?;
            Ok(nums.iter().sum::<f64>() / nums.len() as f64)
        }
    """,
    rules=dict(methods=["unwrap", "expect"]),
    visible=[
        T("three", "\"1, 2, 3\"", 'average("1, 2, 3")', "Ok(2.0)"),
        T("bad_item", "\"1, x\"", 'average("1, x")', 'Err("not a number: x".to_string())'),
        T("blank", "\"\"", 'average("")', 'Err("no numbers".to_string())'),
        T("single", "\"5\"", 'average("5")', "Ok(5.0)"),
        T("empty_item_is_not_a_number", "\"1,,2\"", 'average("1,,2")', 'Err("not a number: ".to_string())'),
    ],
    hidden=[
        T("whitespace_only", "\"   \"", 'average("   ")', 'Err("no numbers".to_string())'),
        T("trailing_comma", "\"4,\"", 'average("4,")', 'Err("not a number: ".to_string())'),
        T("negatives_and_decimals", "\"-1.5, 2.5\"", 'average("-1.5, 2.5")', "Ok(0.5)"),
        T("no_spaces", "\"1,2\"", 'average("1,2")', "Ok(1.5)"),
        T("spaces_around_items", "\"  1 ,\\t2  \"", 'average("  1 ,\\t2  ")', "Ok(1.5)"),
        T("message_is_trimmed", "\"1,   x  \"", 'average("1,   x  ")', 'Err("not a number: x".to_string())'),
        T("first_bad_item_wins", "\"a, b\"", 'average("a, b")', 'Err("not a number: a".to_string())'),
        T("only_a_comma", "\",\"", 'average(",")', 'Err("not a number: ".to_string())'),
        T("unicode_item", "\"1, ２\"", 'average("1, ２")', 'Err("not a number: ２".to_string())'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1308);
            for _ in 0..400 {
                let n = rng.below(6);
                let mut items: Vec<String> = Vec::new();
                for _ in 0..n {
                    let item = if rng.below(8) == 0 { (*rng.pick(&["x", "", "1x"])).to_string() } else { rng.int(-9, 9).to_string() };
                    let pad = rng.below(3);
                    items.push(format!("{}{}{}", " ".repeat(pad), item, " ".repeat(2 - pad)));
                }
                let input = items.join(",");
                let want = if input.trim().is_empty() {
                    Err("no numbers".to_string())
                } else if let Some(bad) = items.iter().map(|s| s.trim()).find(|s| s.parse::<i32>().is_err()) {
                    Err(format!("not a number: {bad}"))
                } else {
                    let sum: i32 = items.iter().map(|s| s.trim().parse::<i32>().unwrap_or(0)).sum();
                    Ok(f64::from(sum) / items.len() as f64)
                };
                check!(format!("input = {input:?}"), average(&input), want);
            }
        }
        """,
    ],
    wrong=dict(
        blank_check_after_parsing="""
            /// The average of comma-separated numbers, e.g. "1, 2, 3".
            pub fn average(input: &str) -> Result<f64, String> {
                let nums = input
                    .split(',')
                    .map(|s| {
                        let s = s.trim();
                        s.parse::<f64>().map_err(|_| format!("not a number: {s}"))
                    })
                    .collect::<Result<Vec<f64>, String>>()?;
                if nums.is_empty() {
                    return Err("no numbers".into());
                }
                Ok(nums.iter().sum::<f64>() / nums.len() as f64)
            }
        """,
        skips_empty_items="""
            /// The average of comma-separated numbers, e.g. "1, 2, 3".
            pub fn average(input: &str) -> Result<f64, String> {
                let nums = input
                    .split(',')
                    .map(str::trim)
                    .filter(|s| !s.is_empty())
                    .map(|s| s.parse::<f64>().map_err(|_| format!("not a number: {s}")))
                    .collect::<Result<Vec<f64>, String>>()?;
                if nums.is_empty() {
                    return Err("no numbers".into());
                }
                Ok(nums.iter().sum::<f64>() / nums.len() as f64)
            }
        """,
        untrimmed_message="""
            /// The average of comma-separated numbers, e.g. "1, 2, 3".
            pub fn average(input: &str) -> Result<f64, String> {
                if input.trim().is_empty() {
                    return Err("no numbers".into());
                }
                let nums = input
                    .split(',')
                    .map(|s| s.trim().parse::<f64>().map_err(|_| format!("not a number: {s}")))
                    .collect::<Result<Vec<f64>, String>>()?;
                Ok(nums.iter().sum::<f64>() / nums.len() as f64)
            }
        """,
    ),
    hints=[("rust", "Turn each parse into a `Result` with a message, then collect into `Result<Vec<_>, _>` and use `?`."),
           ("edge case", "Blank input would otherwise divide by zero or fail on the empty item.")],
    notes=("Every failure path now returns a message instead of panicking. The blank check has to come first, or `\"\"` reports `not a number: `.", "O(n)", "O(n)"),
    follow_up="Which unwraps in a codebase are fine, and how would you document them?",
    related=["L8"],
))

MY_OPTION = """
        #[derive(Debug, PartialEq, Eq, Clone, Copy)]
        pub enum MyOption<T> {
            Some(T),
            None,
        }

        impl<T> MyOption<T> {
            pub fn is_some(&self) -> bool {
                matches!(self, MyOption::Some(_))
            }
            pub fn is_none(&self) -> bool {
                !self.is_some()
            }
            pub fn unwrap_or(self, default: T) -> T {
                match self {
                    MyOption::Some(v) => v,
                    MyOption::None => default,
                }
            }
            pub fn unwrap_or_else(self, f: impl FnOnce() -> T) -> T {
                match self {
                    MyOption::Some(v) => v,
                    MyOption::None => f(),
                }
            }
            pub fn map<U>(self, f: impl FnOnce(T) -> U) -> MyOption<U> {
                match self {
                    MyOption::Some(v) => MyOption::Some(f(v)),
                    MyOption::None => MyOption::None,
                }
            }
            pub fn and_then<U>(self, f: impl FnOnce(T) -> MyOption<U>) -> MyOption<U> {
                match self {
                    MyOption::Some(v) => f(v),
                    MyOption::None => MyOption::None,
                }
            }
            pub fn or(self, other: MyOption<T>) -> MyOption<T> {
                match self {
                    MyOption::Some(_) => self,
                    MyOption::None => other,
                }
            }
            pub fn ok_or<E>(self, err: E) -> Result<T, E> {
                match self {
                    MyOption::Some(v) => Ok(v),
                    MyOption::None => Err(err),
                }
            }
            pub fn filter(self, keep: impl FnOnce(&T) -> bool) -> MyOption<T> {
                match self {
                    MyOption::Some(v) if keep(&v) => MyOption::Some(v),
                    _ => MyOption::None,
                }
            }
            pub fn take(&mut self) -> MyOption<T> {
                std::mem::replace(self, MyOption::None)
            }
        }
    """

P.append(dict(
    slug="my-option", title="Build MyOption<T>", level="hard", stage="build-it", tags=["enum", "generics", "mem::replace"],
    teaches=["Every combinator is a `match` on two variants.", "`take` needs `mem::replace` to move out of `&mut self`."],
    statement="""
        Implement `MyOption<T>`, a copy of `Option<T>`, with ten methods:
        `is_some`, `is_none`, `unwrap_or`, `unwrap_or_else`, `map`, `and_then`, `or`, `ok_or`, `filter`, `take`.
        Each should behave like std's version.
    """,
    starter="""
        #[derive(Debug, PartialEq, Eq, Clone, Copy)]
        pub enum MyOption<T> {
            Some(T),
            None,
        }

        impl<T> MyOption<T> {
            pub fn is_some(&self) -> bool { todo!() }
            pub fn is_none(&self) -> bool { todo!() }
            pub fn unwrap_or(self, default: T) -> T { todo!() }
            pub fn unwrap_or_else(self, f: impl FnOnce() -> T) -> T { todo!() }
            pub fn map<U>(self, f: impl FnOnce(T) -> U) -> MyOption<U> { todo!() }
            pub fn and_then<U>(self, f: impl FnOnce(T) -> MyOption<U>) -> MyOption<U> { todo!() }
            pub fn or(self, other: MyOption<T>) -> MyOption<T> { todo!() }
            pub fn ok_or<E>(self, err: E) -> Result<T, E> { todo!() }
            pub fn filter(self, keep: impl FnOnce(&T) -> bool) -> MyOption<T> { todo!() }
            pub fn take(&mut self) -> MyOption<T> { todo!() }
        }
    """,
    solution=MY_OPTION,
    visible=[
        T("is_some_none", "Some(1), None", "(MyOption::Some(1).is_some(), MyOption::<i32>::None.is_none())", "(true, true)"),
        T("map_and_then", "Some(2)", "MyOption::Some(2).map(|x| x * 10).and_then(|x| if x > 5 { MyOption::Some(x + 1) } else { MyOption::None })", "MyOption::Some(21)"),
        T("unwrap_or", "None", "MyOption::None.unwrap_or(7)", "7"),
        T("take", "Some(\"a\")", '{ let mut o = MyOption::Some("a"); let t = o.take(); (t, o) }', '(MyOption::Some("a"), MyOption::None)'),
        T("or_keeps_the_first", "Some(1) or Some(2)", "MyOption::Some(1).or(MyOption::Some(2))", "MyOption::Some(1)"),
    ],
    hidden=[
        T("or", "None or Some(3)", "MyOption::None.or(MyOption::Some(3))", "MyOption::Some(3)"),
        T("ok_or", "None", 'MyOption::<u8>::None.ok_or("missing")', 'Err("missing")'),
        T("filter", "Some(4), Some(5)", "(MyOption::Some(4).filter(|x| x % 2 == 0), MyOption::Some(5).filter(|x| x % 2 == 0))", "(MyOption::Some(4), MyOption::None)"),
        T("unwrap_or_else_lazy", "Some(1)", "MyOption::Some(1).unwrap_or_else(|| panic!(\"should not run\"))", "1"),
        T("is_some_is_none_false", "None, Some(1)", "(MyOption::<i32>::None.is_some(), MyOption::Some(1).is_none())", "(false, false)"),
        T("unwrap_or_some", "Some(5)", "MyOption::Some(5).unwrap_or(7)", "5"),
        T("unwrap_or_else_none", "None", "MyOption::None.unwrap_or_else(|| 9)", "9"),
        T("map_changes_type", "Some(\"abc\")", "MyOption::Some(\"abc\").map(str::len)", "MyOption::Some(3)"),
        T("map_none_skips_f", "None", "MyOption::<i32>::None.map(|x| -> i32 { panic!(\"should not run: {x}\") })", "MyOption::None"),
        T("and_then_none_skips_f", "None", "MyOption::<i32>::None.and_then(|x| -> MyOption<i32> { panic!(\"should not run: {x}\") })", "MyOption::None"),
        T("and_then_to_none", "Some(1)", "MyOption::Some(1).and_then(|_| MyOption::<i32>::None)", "MyOption::None"),
        T("or_both_none", "None or None", "MyOption::<i32>::None.or(MyOption::None)", "MyOption::None"),
        T("ok_or_some", "Some(3)", 'MyOption::Some(3).ok_or("missing")', "Ok(3)"),
        T("filter_none_skips_keep", "None", "MyOption::<i32>::None.filter(|x| panic!(\"should not run: {x}\"))", "MyOption::None"),
        T("take_none", "None", "{ let mut o = MyOption::<i32>::None; let t = o.take(); (t, o) }", "(MyOption::None, MyOption::None)"),
        T("take_moves_a_string", "Some(String::from(\"hi\"))", '{ let mut o = MyOption::Some(String::from("hi")); let t = o.take(); (t, o) }', '(MyOption::Some("hi".to_string()), MyOption::None)'),
        """
        fn mine(o: Option<i32>) -> MyOption<i32> {
            match o {
                Some(v) => MyOption::Some(v),
                None => MyOption::None,
            }
        }

        #[test]
        fn random_vs_std_option() {
            let mut rng = anneal_prelude::Rng::new(1309);
            for _ in 0..300 {
                let a = if rng.bool() { Some(rng.int(-5, 5) as i32) } else { None };
                let b = if rng.bool() { Some(rng.int(-5, 5) as i32) } else { None };
                let d = rng.int(-5, 5) as i32;
                let desc = format!("a = {a:?}, b = {b:?}, default = {d}");
                check!(format!("is_some/is_none, {desc}"), (mine(a).is_some(), mine(a).is_none()), (a.is_some(), a.is_none()));
                check!(format!("unwrap_or, {desc}"), mine(a).unwrap_or(d), a.unwrap_or(d));
                check!(format!("unwrap_or_else, {desc}"), mine(a).unwrap_or_else(|| d * 2), a.unwrap_or_else(|| d * 2));
                check!(format!("map(x + d), {desc}"), mine(a).map(|x| x + d), mine(a.map(|x| x + d)));
                check!(format!("and_then(positive), {desc}"), mine(a).and_then(|x| if x > 0 { MyOption::Some(x * 3) } else { MyOption::None }), mine(a.and_then(|x| if x > 0 { Some(x * 3) } else { None })));
                check!(format!("a.or(b), {desc}"), mine(a).or(mine(b)), mine(a.or(b)));
                check!(format!("ok_or(d), {desc}"), mine(a).ok_or(d), a.ok_or(d));
                check!(format!("filter(even), {desc}"), mine(a).filter(|x| x % 2 == 0), mine(a.filter(|x| x % 2 == 0)));
                let mut m = mine(a);
                let mut s = a;
                check!(format!("take, {desc}"), (m.take(), m), (mine(s.take()), mine(s)));
            }
        }
        """,
    ],
    wrong=dict(
        or_prefers_the_other=MY_OPTION.replace("match self {\n                    MyOption::Some(_) => self,\n                    MyOption::None => other,", "match other {\n                    MyOption::Some(_) => other,\n                    MyOption::None => self,"),
        eager_unwrap_or_else=MY_OPTION.replace("MyOption::None => f(),", "MyOption::None => d,").replace("-> T) -> T {\n                match self {", "-> T) -> T {\n                let d = f();\n                match self {"),
        filter_drops_matches=MY_OPTION.replace("if keep(&v)", "if !keep(&v)"),
    ),
    hints=[("approach", "Each method is one `match` on `Some(v)` / `None`."),
           ("rust", "`take` has `&mut self` and must return the old value. `std::mem::replace` swaps in `None`.")],
    notes=("`filter` uses a match guard to keep ownership of `v`. `unwrap_or_else` only calls `f` on `None`, which is the point of the `_else` variants.", "O(1) each", "O(1)"),
    follow_up="Why does `Option<&T>` have the same size as `&T`?",
    related=["L7", "L6", "Y1"],
))

MY_OPTION_BORROW = """
        #[derive(Debug, PartialEq, Eq, Clone, Copy)]
        pub enum MyOption<T> {
            Some(T),
            None,
        }

        impl<T> MyOption<T> {
            pub fn as_ref(&self) -> MyOption<&T> {
                match self {
                    MyOption::Some(v) => MyOption::Some(v),
                    MyOption::None => MyOption::None,
                }
            }
            pub fn as_mut(&mut self) -> MyOption<&mut T> {
                match self {
                    MyOption::Some(v) => MyOption::Some(v),
                    MyOption::None => MyOption::None,
                }
            }
            pub fn insert(&mut self, value: T) -> &mut T {
                *self = MyOption::Some(value);
                match self {
                    MyOption::Some(v) => v,
                    MyOption::None => unreachable!(),
                }
            }
            pub fn replace(&mut self, value: T) -> MyOption<T> {
                std::mem::replace(self, MyOption::Some(value))
            }
            pub fn get_or_insert_with(&mut self, f: impl FnOnce() -> T) -> &mut T {
                if let MyOption::None = self {
                    *self = MyOption::Some(f());
                }
                match self {
                    MyOption::Some(v) => v,
                    MyOption::None => unreachable!(),
                }
            }
            pub fn zip<U>(self, other: MyOption<U>) -> MyOption<(T, U)> {
                match (self, other) {
                    (MyOption::Some(a), MyOption::Some(b)) => MyOption::Some((a, b)),
                    _ => MyOption::None,
                }
            }
            pub fn xor(self, other: MyOption<T>) -> MyOption<T> {
                match (self, other) {
                    (MyOption::Some(a), MyOption::None) => MyOption::Some(a),
                    (MyOption::None, MyOption::Some(b)) => MyOption::Some(b),
                    _ => MyOption::None,
                }
            }
            pub fn map_or_else<U>(self, default: impl FnOnce() -> U, f: impl FnOnce(T) -> U) -> U {
                match self {
                    MyOption::Some(v) => f(v),
                    MyOption::None => default(),
                }
            }
        }

        impl<T> MyOption<MyOption<T>> {
            pub fn flatten(self) -> MyOption<T> {
                match self {
                    MyOption::Some(inner) => inner,
                    MyOption::None => MyOption::None,
                }
            }
        }

        impl<T: Copy> MyOption<&T> {
            pub fn copied(self) -> MyOption<T> {
                match self {
                    MyOption::Some(&v) => MyOption::Some(v),
                    MyOption::None => MyOption::None,
                }
            }
        }
    """

P.append(dict(
    slug="my-option-borrowing", title="MyOption: borrowing and in-place methods", level="hard", stage="build-it", tags=["enum", "borrowing", "impl blocks"],
    teaches=["`as_ref` / `as_mut` turn `&MyOption<T>` into `MyOption<&T>` by matching on a reference.", "`get_or_insert_with` must fill the slot first and borrow second, or the borrow checker objects.", "`flatten` and `copied` exist only for some `T`, so they live in `impl` blocks for `MyOption<MyOption<T>>` and `MyOption<&T>`."],
    statement="""
        Implement ten more `Option` methods on `MyOption`, each behaving like std's: `as_ref`, `as_mut`, `insert`,
        `replace`, `get_or_insert_with`, `zip`, `xor`, `map_or_else`, and `flatten` and `copied` in their own `impl` blocks.
        Closures must run only when std's would.
    """,
    starter="""
        #[derive(Debug, PartialEq, Eq, Clone, Copy)]
        pub enum MyOption<T> {
            Some(T),
            None,
        }

        impl<T> MyOption<T> {
            pub fn as_ref(&self) -> MyOption<&T> { todo!() }
            pub fn as_mut(&mut self) -> MyOption<&mut T> { todo!() }
            pub fn insert(&mut self, value: T) -> &mut T { todo!() }
            pub fn replace(&mut self, value: T) -> MyOption<T> { todo!() }
            pub fn get_or_insert_with(&mut self, f: impl FnOnce() -> T) -> &mut T { todo!() }
            pub fn zip<U>(self, other: MyOption<U>) -> MyOption<(T, U)> { todo!() }
            pub fn xor(self, other: MyOption<T>) -> MyOption<T> { todo!() }
            pub fn map_or_else<U>(self, default: impl FnOnce() -> U, f: impl FnOnce(T) -> U) -> U { todo!() }
        }

        impl<T> MyOption<MyOption<T>> {
            pub fn flatten(self) -> MyOption<T> { todo!() }
        }

        impl<T: Copy> MyOption<&T> {
            pub fn copied(self) -> MyOption<T> { todo!() }
        }
    """,
    solution=MY_OPTION_BORROW,
    visible=[
        T("as_ref_borrows", "Some(String::from(\"hi\"))", '{ let o = MyOption::Some(String::from("hi")); let r = o.as_ref() == MyOption::Some(&"hi".to_string()); (r, o) }', '(true, MyOption::Some("hi".to_string()))'),
        T("as_mut_edits_in_place", "Some(String::from(\"hi\")), push '!'", "{ let mut o = MyOption::Some(String::from(\"hi\")); if let MyOption::Some(s) = o.as_mut() { s.push('!'); } o }", 'MyOption::Some("hi!".to_string())'),
        T("replace_returns_the_old_value", "Some(1), replace(2)", "{ let mut o = MyOption::Some(1); let old = o.replace(2); (old, o) }", "(MyOption::Some(1), MyOption::Some(2))"),
        T("get_or_insert_with_fills_none", "None, get_or_insert_with(|| 5), then += 1", "{ let mut o = MyOption::None; *o.get_or_insert_with(|| 5) += 1; o }", "MyOption::Some(6)"),
        T("zip_xor_map_or_else", "Some(1), Some(\"a\"), None", '(MyOption::Some(1).zip(MyOption::Some("a")), MyOption::Some(1).xor(MyOption::Some(2)), MyOption::<i32>::None.map_or_else(|| -1, |x| x * 2))', '(MyOption::Some((1, "a")), MyOption::None, -1)'),
    ],
    hidden=[
        T("as_ref_none", "None", "MyOption::<String>::None.as_ref()", "MyOption::None"),
        T("as_ref_points_inside", "Some(String::from(\"x\"))", "{ let o = MyOption::Some(String::from(\"x\")); let same = match (o.as_ref(), &o) { (MyOption::Some(r), MyOption::Some(s)) => std::ptr::eq(r, s), _ => false }; same }", "true"),
        T("as_mut_none", "None", "{ let mut o = MyOption::<i32>::None; let r = o.as_mut() == MyOption::None; (r, o) }", "(true, MyOption::None)"),
        T("insert_overwrites", "Some(1), insert(2), then += 10", "{ let mut o = MyOption::Some(1); *o.insert(2) += 10; o }", "MyOption::Some(12)"),
        T("insert_into_none", "None, insert(String::from(\"a\")), push 'b'", '{ let mut o = MyOption::None; o.insert(String::from("a")).push(\'b\'); o }', 'MyOption::Some("ab".to_string())'),
        T("flatten_all_shapes", "Some(Some(1)), Some(None), None", "(MyOption::Some(MyOption::Some(1)).flatten(), MyOption::Some(MyOption::<i32>::None).flatten(), MyOption::<MyOption<i32>>::None.flatten())", "(MyOption::Some(1), MyOption::None, MyOption::None)"),
        T("flatten_one_level_only", "Some(Some(Some(1)))", "MyOption::Some(MyOption::Some(MyOption::Some(1))).flatten()", "MyOption::Some(MyOption::Some(1))"),
        T("copied_from_as_ref", "Some(7).as_ref().copied(), None", "{ let o = MyOption::Some(7); (o.as_ref().copied(), MyOption::<&u8>::None.copied(), o) }", "(MyOption::Some(7), MyOption::None, MyOption::Some(7))"),
        T("replace_none", "None, replace(\"a\")", '{ let mut o = MyOption::None; let old = o.replace("a"); (old, o) }', '(MyOption::None, MyOption::Some("a"))'),
        T("get_or_insert_with_keeps_some", "Some(3), get_or_insert_with(panics)", "{ let mut o = MyOption::Some(3); let v = *o.get_or_insert_with(|| panic!(\"should not run\")); (v, o) }", "(3, MyOption::Some(3))"),
        T("get_or_insert_with_calls_once", "None, get_or_insert_with twice", "{ let mut calls = 0; let mut o = MyOption::None; o.get_or_insert_with(|| { calls += 1; 7 }); o.get_or_insert_with(|| { calls += 1; 8 }); (o, calls) }", "(MyOption::Some(7), 1)"),
        T("get_or_insert_with_returns_the_slot", "Some(vec![1]), push 2 through the reference", "{ let mut o = MyOption::Some(vec![1]); o.get_or_insert_with(Vec::new).push(2); o }", "MyOption::Some(vec![1, 2])"),
        T("zip_with_none", "Some(1) zip None, None zip Some(1)", "(MyOption::Some(1).zip(MyOption::<u8>::None), MyOption::<u8>::None.zip(MyOption::Some(1)))", "(MyOption::None, MyOption::None)"),
        T("xor_exactly_one", "Some(1) xor None, None xor Some(2), None xor None", "(MyOption::Some(1).xor(MyOption::None), MyOption::None.xor(MyOption::Some(2)), MyOption::<i32>::None.xor(MyOption::None))", "(MyOption::Some(1), MyOption::Some(2), MyOption::None)"),
        T("map_or_else_some_skips_default", "Some(4)", "MyOption::Some(4).map_or_else(|| panic!(\"should not run\"), |x| x * 2)", "8"),
        T("map_or_else_none_skips_f", "None", "MyOption::<i32>::None.map_or_else(|| 0, |x| -> i32 { panic!(\"should not run: {x}\") })", "0"),
        T("map_or_else_moves_the_value", "Some(String::from(\"abc\"))", 'MyOption::Some(String::from("abc")).map_or_else(String::new, |s| s + "!")', '"abc!".to_string()'),
        """
        fn mine<T>(o: Option<T>) -> MyOption<T> {
            match o {
                Some(v) => MyOption::Some(v),
                None => MyOption::None,
            }
        }

        #[test]
        fn random_vs_std_option() {
            let mut rng = anneal_prelude::Rng::new(1316);
            for _ in 0..300 {
                let a = if rng.bool() { Some(rng.int(-5, 5) as i32) } else { None };
                let b = if rng.bool() { Some(rng.int(-5, 5) as i32) } else { None };
                let d = rng.int(-5, 5) as i32;
                let desc = format!("a = {a:?}, b = {b:?}, d = {d}");
                let m = mine(a);
                check!(format!("as_ref, {desc}"), m.as_ref(), mine(a.as_ref()));
                let (mut m, mut s) = (mine(a), a);
                if let MyOption::Some(x) = m.as_mut() {
                    *x += d;
                }
                if let Some(x) = s.as_mut() {
                    *x += d;
                }
                check!(format!("as_mut then += d, {desc}"), m, mine(s));
                let (mut m, mut s) = (mine(a), a);
                check!(format!("replace(d), {desc}"), (m.replace(d), m), (mine(s.replace(d)), mine(s)));
                let (mut m, mut s) = (mine(a), a);
                let (mut calls_m, mut calls_s) = (0, 0);
                let got = *m.get_or_insert_with(|| { calls_m += 1; d });
                let want = *s.get_or_insert_with(|| { calls_s += 1; d });
                check!(format!("get_or_insert_with(d), {desc}"), (got, m, calls_m), (want, mine(s), calls_s));
                check!(format!("a.zip(b), {desc}"), mine(a).zip(mine(b)), mine(a.zip(b)));
                check!(format!("a.xor(b), {desc}"), mine(a).xor(mine(b)), mine(a.xor(b)));
                check!(format!("map_or_else(d, x * 3), {desc}"), mine(a).map_or_else(|| d, |x| x * 3), a.map_or_else(|| d, |x| x * 3));
                let (mut m, mut s) = (mine(a), a);
                check!(format!("insert(d), {desc}"), (*m.insert(d), m), (*s.insert(d), mine(s)));
                let nested = if rng.bool() { Some(b) } else { None };
                check!(format!("flatten, nested = {nested:?}"), mine(nested.map(mine)).flatten(), mine(nested.flatten()));
                check!(format!("as_ref().copied(), {desc}"), mine(a).as_ref().copied(), mine(a.as_ref().copied()));
            }
        }
        """,
    ],
    wrong=dict(
        eager_get_or_insert_with=MY_OPTION_BORROW.replace("if let MyOption::None = self {\n                    *self = MyOption::Some(f());", "let v = f();\n                if let MyOption::None = self {\n                    *self = MyOption::Some(v);"),
        xor_keeps_the_first=MY_OPTION_BORROW.replace("(MyOption::Some(a), MyOption::None) => MyOption::Some(a),", "(MyOption::Some(a), _) => MyOption::Some(a),"),
        insert_keeps_the_old_value=MY_OPTION_BORROW.replace("*self = MyOption::Some(value);\n                match self {", "if let MyOption::None = self {\n                    *self = MyOption::Some(value);\n                }\n                match self {"),
    ),
    hints=[("rust", "Matching on `&self` binds `v` as `&T` (match ergonomics), so `as_ref` is the same two-arm `match` as `map`."),
           ("rust", "In `get_or_insert_with`, first write `*self = MyOption::Some(f())` if it's `None`, then `match self` and return the `&mut` from the `Some` arm."),
           ("edge case", "`insert` always overwrites; only `get_or_insert_with` keeps an existing value. `xor` is `Some` only when exactly one side is.")],
    notes=("`as_ref` and `as_mut` are why most combinators can take `self` by value: borrow first, then consume the borrowed option. `get_or_insert_with` fills the slot before borrowing it, because returning a borrow from one arm while assigning in the other is a case today's borrow checker rejects. API reminder: `insert(v)` overwrites, `get_or_insert(v)` / `get_or_insert_with(f)` keep what's there; `copied()` / `cloned()` turn `Option<&T>` into `Option<T>`; `flatten()` removes one level of `Option<Option<T>>`.", "O(1) each", "O(1)"),
    follow_up="Why does std's `get_or_insert_with` use `unreachable_unchecked` (or an equivalent) for the `None` arm, and is `unreachable!()` good enough here?",
    related=["L2", "L6"],
))

MY_RESULT = """
        #[derive(Debug, PartialEq, Eq)]
        pub enum MyResult<T, E> {
            Ok(T),
            Err(E),
        }

        impl<T, E> MyResult<T, E> {
            pub fn map<U>(self, f: impl FnOnce(T) -> U) -> MyResult<U, E> {
                match self {
                    MyResult::Ok(v) => MyResult::Ok(f(v)),
                    MyResult::Err(e) => MyResult::Err(e),
                }
            }
            pub fn map_err<F>(self, f: impl FnOnce(E) -> F) -> MyResult<T, F> {
                match self {
                    MyResult::Ok(v) => MyResult::Ok(v),
                    MyResult::Err(e) => MyResult::Err(f(e)),
                }
            }
            pub fn and_then<U>(self, f: impl FnOnce(T) -> MyResult<U, E>) -> MyResult<U, E> {
                match self {
                    MyResult::Ok(v) => f(v),
                    MyResult::Err(e) => MyResult::Err(e),
                }
            }
        }

        /// Like `?` for `MyResult`: the value on `Ok`, an early return on `Err`.
        #[macro_export]
        macro_rules! try_my {
            ($e:expr) => {
                match $e {
                    $crate::MyResult::Ok(v) => v,
                    $crate::MyResult::Err(e) => return $crate::MyResult::Err(::core::convert::From::from(e)),
                }
            };
        }
    """

P.append(dict(
    slug="my-result-and-try", title="Build MyResult and a ? macro", level="hard", stage="build-it", tags=["macro_rules!", "From", "early return"],
    teaches=["`?` is a match plus an early return plus `From::from` on the error.", "`#[macro_export]` and `$crate` paths."],
    statement="""
        Implement `map`, `map_err` and `and_then` on `MyResult<T, E>`, and a macro `try_my!(expr)`
        that evaluates to the value on `Ok` and otherwise returns `MyResult::Err(From::from(e))` from
        the enclosing function, like `?`.
    """,
    starter="""
        #[derive(Debug, PartialEq, Eq)]
        pub enum MyResult<T, E> {
            Ok(T),
            Err(E),
        }

        impl<T, E> MyResult<T, E> {
            pub fn map<U>(self, f: impl FnOnce(T) -> U) -> MyResult<U, E> { todo!() }
            pub fn map_err<F>(self, f: impl FnOnce(E) -> F) -> MyResult<T, F> { todo!() }
            pub fn and_then<U>(self, f: impl FnOnce(T) -> MyResult<U, E>) -> MyResult<U, E> { todo!() }
        }

        /// Like `?` for `MyResult`: the value on `Ok`, an early return on `Err`.
        #[macro_export]
        macro_rules! try_my {
            ($e:expr) => {
                match $e {
                    $crate::MyResult::Ok(v) => v,
                    $crate::MyResult::Err(_) => todo!("return the error, converted with From"),
                }
            };
        }
    """,
    solution=MY_RESULT,
    visible=[
        """
        fn add(a: MyResult<i32, String>, b: MyResult<i32, String>) -> MyResult<i32, String> {
            let x = try_my!(a);
            let y = try_my!(b);
            MyResult::Ok(x + y)
        }

        #[test]
        fn try_passes_values_through() {
            check!("Ok(2) + Ok(3)", add(MyResult::Ok(2), MyResult::Ok(3)), MyResult::Ok(5));
        }

        #[test]
        fn try_returns_early() {
            check!("Ok(2) + Err(\\"no\\")", add(MyResult::Ok(2), MyResult::Err("no".into())), MyResult::Err("no".to_string()));
        }
        """,
        T("map", "Ok(2)", "MyResult::<i32, ()>::Ok(2).map(|x| x * 3)", "MyResult::Ok(6)"),
        T("map_err_leaves_ok_alone", "Ok(2)", "MyResult::<i32, i32>::Ok(2).map_err(|e| e + 1)", "MyResult::Ok(2)"),
        T("and_then_chains", "Ok(2)", "MyResult::<i32, String>::Ok(2).and_then(|v| MyResult::Ok(v * 10))", "MyResult::Ok(20)"),
    ],
    hidden=[
        """
        #[derive(Debug, PartialEq)]
        struct AppError(String);

        impl From<&'static str> for AppError {
            fn from(s: &'static str) -> Self {
                AppError(s.to_string())
            }
        }

        fn converts(r: MyResult<u8, &'static str>) -> MyResult<u8, AppError> {
            let v = try_my!(r);
            MyResult::Ok(v)
        }

        #[test]
        fn try_converts_the_error_with_from() {
            check!("Err(\\"bad\\")", converts(MyResult::Err("bad")), MyResult::Err(AppError("bad".into())));
        }
        """,
        T("map_err", "Err(4)", "MyResult::<(), i32>::Err(4).map_err(|e| e + 1)", "MyResult::Err(5)"),
        T("and_then_short_circuits", "Err(\"x\")", 'MyResult::<i32, &str>::Err("x").and_then(|v| MyResult::Ok(v + 1))', 'MyResult::Err("x")'),
        T("map_leaves_err_alone", "Err(\"x\")", 'MyResult::<i32, &str>::Err("x").map(|v| -> i32 { panic!("should not run: {v}") })', 'MyResult::Err("x")'),
        T("map_err_skips_f_on_ok", "Ok(1)", 'MyResult::<i32, i32>::Ok(1).map_err(|e| -> i32 { panic!("should not run: {e}") })', "MyResult::Ok(1)"),
        T("and_then_ok_to_err", "Ok(1)", 'MyResult::<i32, &str>::Ok(1).and_then(|_| MyResult::<i32, &str>::Err("late"))', 'MyResult::Err("late")'),
        T("map_changes_type", "Ok(\"abc\")", 'MyResult::<&str, ()>::Ok("abc").map(str::len)', "MyResult::Ok(3)"),
        """
        fn sum3(a: MyResult<i32, String>, b: MyResult<i32, String>, c: MyResult<i32, String>, steps: &mut u32) -> MyResult<i32, String> {
            let x = try_my!(a);
            *steps += 1;
            let y = try_my!(b);
            *steps += 1;
            let z = try_my!(c);
            *steps += 1;
            MyResult::Ok(x + y + z)
        }

        fn once(r: MyResult<i32, String>, calls: &mut u32) -> MyResult<i32, String> {
            *calls += 1;
            r
        }

        fn inline(a: MyResult<i32, String>, b: MyResult<i32, String>) -> MyResult<i32, String> {
            MyResult::Ok(try_my!(a) * 10 + try_my!(b))
        }

        #[test]
        fn try_first_error_wins() {
            let mut steps = 0;
            let got = sum3(MyResult::Ok(1), MyResult::Err("b".into()), MyResult::Err("c".into()), &mut steps);
            check!("Ok(1), Err(\\"b\\"), Err(\\"c\\")", (got, steps), (MyResult::Err("b".to_string()), 1));
        }

        #[test]
        fn try_stops_at_the_first_error() {
            let mut steps = 0;
            let got = sum3(MyResult::Err("a".into()), MyResult::Ok(2), MyResult::Ok(3), &mut steps);
            check!("Err(\\"a\\"), Ok(2), Ok(3)", (got, steps), (MyResult::Err("a".to_string()), 0));
        }

        #[test]
        fn try_evaluates_its_argument_once() {
            fn run(calls: &mut u32) -> MyResult<i32, String> {
                let v = try_my!(once(MyResult::Ok(4), calls));
                MyResult::Ok(v)
            }
            let mut calls = 0;
            let got = run(&mut calls);
            check!("try_my!(once(Ok(4)))", (got, calls), (MyResult::Ok(4), 1));
        }

        #[test]
        fn try_inside_an_expression() {
            check!("Ok(Ok(4) * 10 + Ok(2))", inline(MyResult::Ok(4), MyResult::Ok(2)), MyResult::Ok(42));
            check!("Ok(Ok(4) * 10 + Err(\\"b\\"))", inline(MyResult::Ok(4), MyResult::Err("b".into())), MyResult::Err("b".to_string()));
        }

        fn add_mine(a: MyResult<i32, String>, b: MyResult<i32, String>) -> MyResult<i32, String> {
            MyResult::Ok(try_my!(a) + try_my!(b))
        }

        fn add_std(a: Result<i32, String>, b: Result<i32, String>) -> Result<i32, String> {
            Ok(a? + b?)
        }

        fn mine(r: Result<i32, String>) -> MyResult<i32, String> {
            match r {
                Ok(v) => MyResult::Ok(v),
                Err(e) => MyResult::Err(e),
            }
        }

        #[test]
        fn random_vs_std_result() {
            let mut rng = anneal_prelude::Rng::new(1310);
            for _ in 0..300 {
                let a: Result<i32, String> = if rng.below(3) > 0 { Ok(rng.int(-9, 9) as i32) } else { Err(rng.string(1, "xyz")) };
                let b: Result<i32, String> = if rng.below(3) > 0 { Ok(rng.int(-9, 9) as i32) } else { Err(rng.string(1, "xyz")) };
                let desc = format!("a = {a:?}, b = {b:?}");
                check!(format!("map(x * 2), {desc}"), mine(a.clone()).map(|x| x * 2), mine(a.clone().map(|x| x * 2)));
                check!(format!("map_err(push '!'), {desc}"), mine(a.clone()).map_err(|e| e + "!"), mine(a.clone().map_err(|e| e + "!")));
                check!(format!("and_then(positive), {desc}"), mine(a.clone()).and_then(|x| if x > 0 { MyResult::Ok(x) } else { MyResult::Err("neg".to_string()) }), mine(a.clone().and_then(|x| if x > 0 { Ok(x) } else { Err("neg".to_string()) })));
                check!(format!("try_my!(a) + try_my!(b), {desc}"), add_mine(mine(a.clone()), mine(b.clone())), mine(add_std(a, b)));
            }
        }
        """,
    ],
    wrong=dict(
        try_panics_on_err=MY_RESULT.replace("$crate::MyResult::Err(e) => return $crate::MyResult::Err(::core::convert::From::from(e)),", "$crate::MyResult::Err(_) => panic!(\"try_my! on an Err\"),"),
    ),
    hints=[("approach", "`?` on `Err(e)` returns `Err(From::from(e))` from the whole function."),
           ("rust", "Inside `macro_rules!`, `return` returns from the function the macro is used in. Name the enum as `$crate::MyResult` so it resolves anywhere.")],
    notes=("The `From::from` call is what lets `?` convert a library error into your application's error type.", "O(1)", "O(1)"),
    follow_up="What trait does real `?` use, and why isn't it stable to implement yourself?",
    related=["L8", "L10"],
))

STAGES = [("use-it", "Use it", "easy"), ("understand-it", "Understand it", "medium"), ("build-it", "Build it", "hard")]

if __name__ == "__main__":
    n = write_track("s1-option-result", "S1", "Option & Result", "S", "core", 1,
                    "The two types every Rust API returns: combinators, `?`, conversions, and building them yourself.",
                    STAGES, P)
    print("S1", n)
