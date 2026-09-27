from author import T, write_track

P = []


def rs(s: str) -> str:
    """A Rust string literal for `s` (ASCII only)."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '".to_string()'


def receipt(item, qty, price):
    return f"{item:<10.10}{qty:>3} {price:>8.2f}"


# ---------------------------------------------------------------- use (easy)

P.append(dict(
    slug="string-vs-str", title="String vs &str", level="easy", stage="use",
    tags=["&str", "String", "deref"],
    teaches=["Take `&str`, return `String` when you build something new.", "A `&String` coerces to `&str`, so `&str` parameters accept both."],
    statement="""
        - `greet` returns `"Hello, <name>!"`.
        - `exclaim` appends `!` to a `String` in place.
        - `first_word` returns the text before the first space, borrowed from the input.
    """,
    examples=[('greet("Ada")', '"Hello, Ada!"'), ('first_word("hello world")', '"hello"')],
    starter="""
        pub fn greet(name: &str) -> String {
            todo!()
        }

        pub fn exclaim(s: &mut String) {
            todo!()
        }

        pub fn first_word(s: &str) -> &str {
            todo!()
        }
    """,
    solution="""
        pub fn greet(name: &str) -> String {
            format!("Hello, {name}!")
        }

        pub fn exclaim(s: &mut String) {
            s.push('!');
        }

        pub fn first_word(s: &str) -> &str {
            s.split(' ').next().unwrap_or(s)
        }
    """,
    visible=[
        T("greets_literal_and_owned", 'greet("Ada") and greet(&String::from("Bo"))', '(greet("Ada"), greet(&name))', '("Hello, Ada!".to_string(), "Hello, Bo!".to_string())',
          setup='let name = String::from("Bo");'),
        T("first", '"hello world"', 'first_word("hello world")', '"hello"'),
    ],
    hidden=[
        T("in_place", 'exclaim twice on "wow"', "s", '"wow!!".to_string()', setup='let mut s = String::from("wow");\nexclaim(&mut s);\nexclaim(&mut s);'),
        T("no_space", '"single"', 'first_word("single")', '"single"'),
        T("leading_space", '" x"', 'first_word(" x")', '""'),
    ],
    hints=[("rust", "A `&str` parameter accepts string literals and `&String` alike, thanks to deref coercion."),
           ("rust", "`first_word` can return a slice of its input; no allocation needed.")],
    notes=("`String` owns a growable buffer; `&str` borrows some UTF-8 text from anywhere. Taking `&str` is the most flexible parameter; returning `String` is right when you build new text.", "O(n)", "O(n) for greet"),
    follow_up="When would you take `impl Into<String>` instead of `&str`?",
    related=["L1"],
))

P.append(dict(
    slug="split-trim-parse", title="split, trim, parse", level="easy", stage="use",
    tags=["split", "parse", "Result"],
    teaches=["`split(',').map(str::trim)` pipelines.", "Summing an iterator of `Result`s into a `Result`."],
    statement="""
        Sum a comma-separated list of integers. Spaces around numbers don't matter and empty fields are
        skipped. Return the parse error if any field isn't an integer.
    """,
    examples=[('"1, 2 ,3"', "Ok(6)"), ('"1,x"', "Err(..)")],
    starter="""
        use std::num::ParseIntError;

        pub fn sum_csv(line: &str) -> Result<i64, ParseIntError> {
            todo!()
        }
    """,
    solution="""
        use std::num::ParseIntError;

        pub fn sum_csv(line: &str) -> Result<i64, ParseIntError> {
            line.split(',')
                .map(str::trim)
                .filter(|f| !f.is_empty())
                .map(str::parse::<i64>)
                .sum()
        }
    """,
    visible=[
        T("spaces", '"1, 2 ,3"', 'sum_csv("1, 2 ,3")', "Ok(6)"),
        T("bad_field", '"1,x"', 'sum_csv("1,x").is_err()', "true"),
    ],
    hidden=[
        T("empty", '""', 'sum_csv("")', "Ok(0)"),
        T("empty_fields_and_negatives", '" -4 ,, 10"', 'sum_csv(" -4 ,, 10")', "Ok(6)"),
        T("float_is_not_int", '"1.5"', 'sum_csv("1.5").is_err()', "true"),
    ],
    hints=[("rust", "`str::trim` and `str::parse::<i64>` can be passed to `map` directly."),
           ("rust", "`Sum` is implemented for `Result<T, E>`: summing `Result`s stops at the first `Err`.")],
    notes=("The whole function is one pipeline. Summing into `Result` short-circuits on the first bad field, so no manual loop or early return is needed.", "O(n)", "O(1)"),
    follow_up="How would you report which field failed, and at what position?",
    related=["S1"],
))

P.append(dict(
    slug="fix-string-plus-string", title="Fix: + with two Strings", mode="fix", level="easy", stage="use",
    tags=["E0308", "E0369", "Add"],
    teaches=["`String + &str` consumes the left side and borrows the right.", "`&str + ...` doesn't exist; use `format!`."],
    statement="Both functions should build a new string. Neither compiles.",
    starter="""
        /// "last, first"
        pub fn full_name(first: String, last: String) -> String {
            last + ", " + first
        }

        /// "name#id"
        pub fn tag(name: &str, id: u32) -> String {
            name + "#" + id
        }
    """,
    solution="""
        /// "last, first"
        pub fn full_name(first: String, last: String) -> String {
            last + ", " + &first
        }

        /// "name#id"
        pub fn tag(name: &str, id: u32) -> String {
            format!("{name}#{id}")
        }
    """,
    visible=[
        T("name", '"Ada", "Lovelace"', 'full_name("Ada".into(), "Lovelace".into())', rs("Lovelace, Ada")),
        T("tagged", '"ferris", 7', 'tag("ferris", 7)', rs("ferris#7")),
    ],
    hidden=[
        T("empty_first", '"", "X"', 'full_name(String::new(), "X".into())', rs("X, ")),
        T("zero", '"a", 0', 'tag("a", 0)', rs("a#0")),
    ],
    hints=[("rust", "`impl Add<&str> for String` is the only `+` for strings: left side owned `String`, right side `&str`."),
           ("rust", "A `&str` on the left can't grow, and a number isn't a `&str`. `format!` handles both.")],
    notes=("`+` reuses the left `String`'s buffer, which is why it takes it by value. `&first` derefs `&String` to `&str`. For anything mixed, `format!` is clearer.", "O(n)", "O(n)"),
    follow_up="Why is `a + &b` often faster than `format!(\"{a}{b}\")`?",
    rules=dict(lines=2),
))

P.append(dict(
    slug="compare-ignoring-case", title="Compare ignoring case without allocating", level="easy", stage="use",
    tags=["eq_ignore_ascii_case", "zero allocation"],
    teaches=["`eq_ignore_ascii_case` compares without building lowercase copies."],
    statement="""
        - `is_command`: does `input`, with surrounding whitespace ignored, name `command`, ignoring ASCII case?
        - `count_word`: how many whitespace-separated words of `text` equal `word`, ignoring ASCII case?

        Don't allocate: no `to_lowercase` or `to_uppercase`.
    """,
    starter="""
        pub fn is_command(input: &str, command: &str) -> bool {
            todo!()
        }

        pub fn count_word(text: &str, word: &str) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn is_command(input: &str, command: &str) -> bool {
            input.trim().eq_ignore_ascii_case(command)
        }

        pub fn count_word(text: &str, word: &str) -> usize {
            text.split_whitespace().filter(|w| w.eq_ignore_ascii_case(word)).count()
        }
    """,
    visible=[
        T("command", '"  QUIT \\n", "quit"', 'is_command("  QUIT \\n", "quit")', "true"),
        T("count", '"The cat saw the THE", "the"', 'count_word("The cat saw the THE", "the")', "3"),
    ],
    hidden=[
        T("prefix_is_not_equal", '"quitter", "quit"', 'is_command("quitter", "quit")', "false"),
        T("none", '"", "a"', 'count_word("", "a")', "0"),
    ],
    hints=[("rust", "`str::eq_ignore_ascii_case` compares byte by byte, folding ASCII letters, with no allocation.")],
    notes=("Lowercasing both sides allocates two Strings per comparison; `eq_ignore_ascii_case` allocates nothing. It only folds ASCII, which is right for commands and keywords.", "O(n)", "O(1)"),
    follow_up="What would you use for case-insensitive comparison of arbitrary Unicode text?",
    rules=dict(methods=["to_lowercase", "to_uppercase", "to_ascii_lowercase", "to_ascii_uppercase"]),
))

P.append(dict(
    slug="format-width-precision", title="format! width & precision", level="easy", stage="use",
    tags=["format!", "alignment", "{:#x}"],
    teaches=["`{:<10}` / `{:>8.2}`: alignment, width, precision.", "Precision on a string truncates it; `#` adds `0x`, and the width includes it."],
    statement="""
        - `receipt_line`: the item left-aligned in 10 columns (cut to 10 if longer), the quantity
          right-aligned in 3, a space, then the price right-aligned in 8 with two decimals.
        - `hex_id`: the id as `0x` plus 8 zero-padded lowercase hex digits.

        Use format specifiers, not manual padding.
    """,
    examples=[('receipt_line("Coffee", 2, 3.5)', repr(receipt("Coffee", 2, 3.5)).replace("'", '"')), ("hex_id(255)", '"0x000000ff"')],
    starter="""
        pub fn receipt_line(item: &str, qty: u32, price: f64) -> String {
            todo!()
        }

        pub fn hex_id(id: u32) -> String {
            todo!()
        }
    """,
    solution="""
        pub fn receipt_line(item: &str, qty: u32, price: f64) -> String {
            format!("{item:<10.10}{qty:>3} {price:>8.2}")
        }

        pub fn hex_id(id: u32) -> String {
            format!("{id:#010x}")
        }
    """,
    visible=[
        T("coffee", '"Coffee", 2, 3.5', 'receipt_line("Coffee", 2, 3.5)', rs(receipt("Coffee", 2, 3.5))),
        T("hex", "255", "hex_id(255)", rs("0x000000ff")),
    ],
    hidden=[
        T("long_item_cut", '"Cappuccino grande", 1, 4.25', 'receipt_line("Cappuccino grande", 1, 4.25)', rs(receipt("Cappuccino grande", 1, 4.25))),
        T("big_price", '"Tea", 120, 1234.5', 'receipt_line("Tea", 120, 1234.5)', rs(receipt("Tea", 120, 1234.5))),
        T("max_id", "u32::MAX", "hex_id(u32::MAX)", rs("0xffffffff")),
    ],
    hints=[("rust", "`{:<10}` pads to 10 on the right; `{:.10}` on a string keeps at most 10 characters. Combine as `{item:<10.10}`."),
           ("rust", "`{:#010x}`: `#` adds `0x`, `0` pads with zeros, and the width 10 includes the `0x`.")],
    notes=("One `format!` call does all the layout. The same specifiers work in `write!`, `println!` and `Display` impls that call `f.pad`.", "O(1)", "O(1)"),
    follow_up="How would you make the column widths configurable at runtime (`{:>width$}`)?",
    rules=dict(methods=["repeat"]),
))

P.append(dict(
    slug="join-without-join", title="Build a String in one allocation", level="easy", stage="use",
    tags=["with_capacity", "push_str"],
    teaches=["`String::with_capacity` when you know the final size.", "`push_str` into one buffer instead of repeated `+`."],
    statement="""
        Join `words` with `sep` between them, without `join` or `concat`. Compute the final length first and
        allocate once.
    """,
    examples=[('words = ["a", "bc", "d"], sep = ", "', '"a, bc, d"')],
    starter="""
        pub fn join_words(words: &[&str], sep: &str) -> String {
            todo!()
        }
    """,
    solution="""
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
    """,
    visible=[
        T("three", 'words = ["a", "bc", "d"], sep = ", "', 'join_words(&["a", "bc", "d"], ", ")', rs("a, bc, d")),
        T("one", 'words = ["solo"], sep = "-"', 'join_words(&["solo"], "-")', rs("solo")),
    ],
    hidden=[
        T("none", "words = [], sep = \"-\"", 'join_words(&[], "-")', "String::new()"),
        T("empty_sep", 'words = ["a", "b"], sep = ""', 'join_words(&["a", "b"], "")', rs("ab")),
        T("unicode_sep", 'words = ["x", "y"], sep = " → "', 'join_words(&["x", "y"], " → ")', '"x → y".to_string()'),
    ],
    hints=[("approach", "Total length is the sum of the word lengths plus one separator between each pair."),
           ("rust", "`saturating_sub(1)` keeps the separator count at 0 for an empty slice.")],
    notes=("Lengths are in bytes, which is what `String` capacity counts, so Unicode separators need no special case. One allocation, then only copies.", "O(total length)", "O(total length)"),
    follow_up="How does `[&str]::join` compute its capacity internally?",
    rules=dict(methods=["join", "concat", "collect", "fold"]),
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
    ],
    hidden=[
        T("invalid_utf8", 'b"ok \\xff"', 'word_frequencies(&b"ok \\xff"[..]).is_err()', "true"),
        T("punctuation_only", '"-- !! ..."', 'word_frequencies("-- !! ...".as_bytes()).unwrap().len()', "0"),
        T("inner_punctuation_kept", '"don\'t Don\'t"', 'word_frequencies("don\'t Don\'t".as_bytes()).unwrap()', 'vec![("don\'t".to_string(), 2)]'),
    ],
    hints=[("rust", "`BufRead::lines()` yields `io::Result<String>`; `let line = line?;` propagates a read or UTF-8 error."),
           ("rust", "`raw.trim_matches(|c: char| !c.is_alphanumeric())` strips punctuation from both ends only."),
           ("rust", "Sort with `b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0))` for count-descending, then alphabetical.")],
    notes=("Taking `R: BufRead` means the same code reads a file, stdin or a byte slice in tests. Memory grows with the number of distinct words, not the input size.", "O(n + k log k)", "O(k)"),
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
    ],
    hidden=[
        T("emoji", '"🦀!"', 'sizes("🦀!")', "(5, 2)"),
        T("nth", '"héllo", 1 and 9', '(nth_char("héllo", 1), nth_char("héllo", 9))', "(Some('é'), None)"),
        T("offsets_slice_cleanly", "every offset from positions(\"x→y→z\", '→') is a char boundary", "ok", "true",
          setup="let s = \"x→y→z\";\nlet ok = positions(s, '→').iter().all(|&i| s.is_char_boundary(i) && s[i..].starts_with('→'));"),
    ],
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
    ],
    hidden=[
        T("emoji", '"🦀🦀🦀", 2', 'prefix("🦀🦀🦀", 2)', '"🦀🦀"'),
        T("zero", '"abc", 0', 'prefix("abc", 0)', '""'),
        T("shorter_in_chars_than_bytes", '"日本", 3', 'prefix("日本", 3)', '"日本"'),
    ],
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
    ],
    hidden=[
        T("odd", "\"abc\", 6, '-'", "center(\"abc\", 6, '-')", rs("-abc--")),
        T("too_wide", "\"日本語\", 3, ' '", "center(\"日本語\", 3, ' ')", '"日本語".to_string()'),
        T("multibyte_fill", "\"x\", 3, '·'", "center(\"x\", 3, '·')", '"·x·".to_string()'),
    ],
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
    ],
    hidden=[
        T("emoji", '"🦀x"', 'reverse_each_word("🦀x")', '"x🦀".to_string()'),
        T("extra_spaces", '"  a   bc "', 'reverse_each_word("  a   bc ")', rs("a cb")),
        T("empty", '""', 'reverse_each_word("")', "String::new()"),
    ],
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
    ],
    hidden=[
        T("all_five", "\"&<>\\\"'\"", "escape_html(\"&<>\\\"'\").into_owned()", rs("&amp;&lt;&gt;&quot;&#39;")),
        T("owned_when_changed", '"x&y"', 'matches!(escape_html("x&y"), std::borrow::Cow::Owned(_))', "true"),
        T("unicode", '"é<é"', 'escape_html("é<é").into_owned()', '"é&lt;é".to_string()'),
        T("empty", '""', 'matches!(escape_html(""), std::borrow::Cow::Borrowed(""))', "true"),
    ],
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
    ],
    hidden=[
        T("width", "{:>12} then |", 'format!("{:>12}|", Money { cents: 1234, currency: "USD" })', rs("   12.34 USD|")),
        T("left", "{:<10} then |", 'format!("{:<10}|", Money { cents: 7, currency: "GBP" })', rs("0.07 GBP  |")),
        T("debug_unchanged", "{:?}", 'format!("{:?}", Money { cents: 1, currency: "USD" })', r'"Money { cents: 1, currency: \"USD\" }".to_string()'),
        T("min_value", "i64::MIN cents", 'format!("{}", Money { cents: i64::MIN, currency: "X" })', rs("-92233720368547758.08 X")),
    ],
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
    ],
    hidden=[
        T("empty_key", '" = 3"', '" = 3".parse::<Setting>()', "Err(SettingError::EmptyKey)"),
        T("bad_value", '"a = x "', '"a = x ".parse::<Setting>()', 'Err(SettingError::BadValue("x".to_string()))'),
        T("second_equals_is_value", '"a=b=c"', '"a=b=c".parse::<Setting>()', 'Err(SettingError::BadValue("b=c".to_string()))'),
        T("negative", '"offset=-7"', '"offset=-7".parse::<Setting>()', 'Ok(Setting { key: "offset".to_string(), value: -7 })'),
    ],
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
    ],
    hidden=[
        T("mid_char", '"héllo", 5', 'truncate("héllo", 5)', '"h…".to_string()'),
        T("cjk", '"日本語テキスト", 10', 'truncate("日本語テキスト", 10)', '"日本…".to_string()'),
        T("no_room", '"abc", 2', 'truncate("abc", 2)', "String::new()"),
        T("exact_fit", '"abcd", 4', 'truncate("abcd", 4)', rs("abcd")),
    ],
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
    ],
    hidden=[
        T("empty_host", '"ftp://:21/"', 'parse_url("ftp://:21/")', "None"),
        T("port_too_big", '"http://h:99999/"', 'parse_url("http://h:99999/")', "None"),
        T("no_scheme", '"example.com/x"', 'parse_url("example.com/x")', "None"),
        T("flag_query", '"http://h?flag&&a="', 'parse_url("http://h?flag&&a=").map(|u| (u.path, u.query))', 'Some(("/", vec![("flag", ""), ("a", "")]))'),
        T("borrows_input", "host points into the input", "same", "true",
          setup='let s = String::from("http://host/p");\nlet u = parse_url(&s).unwrap();\nlet same = std::ptr::eq(u.host.as_ptr(), s[7..].as_ptr());'),
    ],
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
    ],
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
    ],
    hidden=[
        T("unknown", '"{missing}"', 'render("{missing}", &vars)', 'Err(TemplateError::Unknown("missing".to_string()))', setup='let vars = std::collections::HashMap::from([("name", "Ada")]);'),
        T("unclosed", '"oops {name"', 'render("oops {name", &vars)', "Err(TemplateError::Unclosed(5))", setup='let vars = std::collections::HashMap::from([("name", "Ada")]);'),
        T("stray", '"a } b"', 'render("a } b", &vars)', "Err(TemplateError::StrayBrace(2))", setup="let vars = std::collections::HashMap::new();"),
        T("unicode_offsets", '"é}"', 'render("é}", &vars)', "Err(TemplateError::StrayBrace(2))", setup="let vars = std::collections::HashMap::new();"),
        T("adjacent", '"{a}{b}{{"', 'render("{a}{b}{{", &vars)', 'Ok("12{".to_string())', setup='let vars = std::collections::HashMap::from([("a", "1"), ("b", "2")]);'),
        T("empty_name", '"{}"', 'render("{}", &vars)', 'Err(TemplateError::Unknown(String::new()))', setup="let vars = std::collections::HashMap::new();"),
    ],
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
