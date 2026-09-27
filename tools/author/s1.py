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
    ],
    hidden=[
        T("out_of_range", "port = \"70000\"", 'port(&std::collections::HashMap::from([("port".to_string(), "70000".to_string())]))', 'Err("invalid port: 70000".to_string())'),
    ],
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
    ],
    hidden=[
        T("extra_spaces", "s = \"  a  bb   ccc \"", 'third_word_len("  a  bb   ccc ")', "Some(3)"),
        T("empty", "s = \"\"", 'third_word_len("")', "None"),
    ],
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
    ],
    hidden=[
        T("empty", "v = [], x = 1", "find(&[], 1)", "None"),
        T("first", "v = [-1, -1], x = -1", "find(&[-1, -1], -1)", "Some(0)"),
    ],
    hints=[("rust", "A negative `i32` can't become a `usize`. Which conversion reports that?")],
    notes=("`try_from` fails exactly on the sentinel, so there's no magic number in the new code.", "O(n)", "O(1)"),
    follow_up="Where else do sentinels hide in std or C APIs, and how do their Rust wrappers expose them?",
    related=["S8", "Y3"],
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
    ],
    hidden=[
        T("shout_none", "no nickname", '{ let mut u = User { name: "Ada".into(), nickname: None }; shout_nickname(&mut u); (u.nickname, u.name) }', '(None, "Ada".to_string())'),
    ],
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
    ],
    hidden=[
        T("default_unused", "labels = {2: \"two\"}, id = 2", 'label_or(&m, 2, "?")', '"two"', setup='let m = std::collections::HashMap::from([(2, "two".to_string())]);'),
    ],
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
    ],
    hidden=[
        T("negative", "s = Some(\"-7\")", 'parse_optional(Some("-7"))', "Ok(Some(-7))"),
        T("empty_string", "s = Some(\"\")", 'parse_optional(Some("")).is_err()', "true"),
    ],
    hints=[("rust", "`s.map(str::parse)` has type `Option<Result<i32, _>>`. Which way round do you need it?")],
    notes=("`transpose` exists for exactly this: the caller can then use `?` on the result.", "O(n)", "O(1)"),
    follow_up="Where do you hit `Option<Result<..>>` in real code?",
    related=["L8"],
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
    ],
    hidden=[
        T("empty", "[]", "parse_all(&[])", "Ok(vec![])"),
        T("overflow", "[\"99999999999\"]", 'parse_all(&["99999999999"])', 'Err("bad number: 99999999999".to_string())'),
    ],
    hints=[("rust", "`Result<Vec<T>, E>` implements `FromIterator<Result<T, E>>`.")],
    notes=("`collect` short-circuits on the first `Err`, so later items aren't parsed.", "O(n)", "O(n)"),
    follow_up="How would you collect every error instead of just the first?",
    related=["S6", "L8"],
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
    ],
    hidden=[
        T("whitespace_only", "\"   \"", 'average("   ")', 'Err("no numbers".to_string())'),
        T("trailing_comma", "\"4,\"", 'average("4,")', 'Err("not a number: ".to_string())'),
    ],
    hints=[("rust", "Turn each parse into a `Result` with a message, then collect into `Result<Vec<_>, _>` and use `?`."),
           ("edge case", "Blank input would otherwise divide by zero or fail on the empty item.")],
    notes=("Every failure path now returns a message instead of panicking. The blank check has to come first, or `\"\"` reports `not a number: `.", "O(n)", "O(n)"),
    follow_up="Which unwraps in a codebase are fine, and how would you document them?",
    related=["L8"],
))

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
    solution="""
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
    """,
    visible=[
        T("is_some_none", "Some(1), None", "(MyOption::Some(1).is_some(), MyOption::<i32>::None.is_none())", "(true, true)"),
        T("map_and_then", "Some(2)", "MyOption::Some(2).map(|x| x * 10).and_then(|x| if x > 5 { MyOption::Some(x + 1) } else { MyOption::None })", "MyOption::Some(21)"),
        T("unwrap_or", "None", "MyOption::None.unwrap_or(7)", "7"),
        T("take", "Some(\"a\")", '{ let mut o = MyOption::Some("a"); let t = o.take(); (t, o) }', '(MyOption::Some("a"), MyOption::None)'),
    ],
    hidden=[
        T("or", "None or Some(3)", "MyOption::None.or(MyOption::Some(3))", "MyOption::Some(3)"),
        T("ok_or", "None", 'MyOption::<u8>::None.ok_or("missing")', 'Err("missing")'),
        T("filter", "Some(4), Some(5)", "(MyOption::Some(4).filter(|x| x % 2 == 0), MyOption::Some(5).filter(|x| x % 2 == 0))", "(MyOption::Some(4), MyOption::None)"),
        T("unwrap_or_else_lazy", "Some(1)", "MyOption::Some(1).unwrap_or_else(|| panic!(\"should not run\"))", "1"),
    ],
    hints=[("approach", "Each method is one `match` on `Some(v)` / `None`."),
           ("rust", "`take` has `&mut self` and must return the old value. `std::mem::replace` swaps in `None`.")],
    notes=("`filter` uses a match guard to keep ownership of `v`. `unwrap_or_else` only calls `f` on `None`, which is the point of the `_else` variants.", "O(1) each", "O(1)"),
    follow_up="Why does `Option<&T>` have the same size as `&T`?",
    related=["L7", "L6", "Y1"],
))

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
    solution="""
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
    """,
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
    ],
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
