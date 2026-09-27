from author import T, write_track

P = []


def fix(slug, title, level, stage, tags, statement, starter, solution, visible, hidden, hints, notes, follow_up, teaches, rules=None, related=("L3",)):
    return dict(slug=slug, title=title, mode="fix", level=level, stage=stage, tags=tags, statement=statement, starter=starter,
                solution=solution, visible=visible, hidden=hidden, hints=hints, notes=notes, follow_up=follow_up,
                teaches=teaches, rules=rules, related=list(related))


def write(slug, title, level, stage, tags, statement, starter, solution, visible, hidden, hints, notes, follow_up, teaches, related=("L3",), source=None, examples=()):
    return dict(slug=slug, title=title, level=level, stage=stage, tags=tags, statement=statement, starter=starter,
                solution=solution, visible=visible, hidden=hidden, hints=hints, notes=notes, follow_up=follow_up,
                teaches=teaches, related=list(related), source=source, examples=list(examples))


# ---------------------------------------------------------------- elision (easy)

P.append(write(
    "when-elision-picks-self", "When elision picks &self", "easy", "elision", ["elision", "&self"],
    """
        Fill in `Config`. The signatures are written with elided lifetimes; the tests check what they
        borrow from. In particular, the result of `tag_with_prefix` must stay usable after `prefix` is gone.
    """,
    """
    pub struct Config {
        name: String,
        tags: Vec<String>,
    }

    impl Config {
        pub fn new(name: &str, tags: &[&str]) -> Self {
            todo!()
        }

        pub fn name(&self) -> &str {
            todo!()
        }

        /// The first tag that starts with `prefix`.
        pub fn tag_with_prefix(&self, prefix: &str) -> Option<&str> {
            todo!()
        }
    }
    """,
    """
    pub struct Config {
        name: String,
        tags: Vec<String>,
    }

    impl Config {
        pub fn new(name: &str, tags: &[&str]) -> Self {
            Config { name: name.to_string(), tags: tags.iter().map(|t| t.to_string()).collect() }
        }

        pub fn name(&self) -> &str {
            &self.name
        }

        /// The first tag that starts with `prefix`.
        pub fn tag_with_prefix(&self, prefix: &str) -> Option<&str> {
            self.tags.iter().map(String::as_str).find(|t| t.starts_with(prefix))
        }
    }
    """,
    [T("outlives_prefix", "tags [\"env:prod\", \"team:core\"], prefix \"team:\" dropped before use", "found", 'Some("team:core")',
       setup='let c = Config::new("app", &["env:prod", "team:core"]);\nlet found;\n{\n    let p = String::from("team:");\n    found = c.tag_with_prefix(&p);\n}'),
     T("name", "name \"app\"", 'Config::new("app", &[]).name().to_string()', '"app".to_string()')],
    [T("missing", "prefix \"x\"", 'Config::new("a", &["b"]).tag_with_prefix("x").is_none()', "true"),
     T("first_of_many", "tags [\"k:1\", \"k:2\"]", 'Config::new("a", &["k:1", "k:2"]).tag_with_prefix("k:").map(str::to_string)', 'Some("k:1".to_string())')],
    [("rust", "Elision rule 3: in a method with `&self`, every elided output lifetime is `self`'s. The other inputs get their own lifetimes."),
     ("rust", "`self.tags.iter().map(String::as_str)` gives `&str`s borrowed from `self`.")],
    ("Because the output borrows only from `self`, `prefix` can be a temporary. Writing `<'a>(&'a self, prefix: &'a str)` would tie them together and break the first test.", "O(n)", "O(1)"),
    "Write out the full signature of `tag_with_prefix` with every lifetime explicit.",
    ["Elision rule 3: outputs of `&self` methods borrow from `self`.", "Other reference parameters get independent lifetimes."],
))

P.append(fix(
    "fix-return-ref-to-local", "Fix: returning a reference to a local", "easy", "elision", ["E0515"],
    "`slug` should lowercase the text and join its words with `-`. It doesn't compile.",
    """
    /// Lowercases `text` and joins its words with "-".
    pub fn slug(text: &str) -> &str {
        let s = text.split_whitespace().collect::<Vec<_>>().join("-").to_lowercase();
        &s
    }
    """,
    """
    /// Lowercases `text` and joins its words with "-".
    pub fn slug(text: &str) -> String {
        let s = text.split_whitespace().collect::<Vec<_>>().join("-").to_lowercase();
        s
    }
    """,
    [T("two_words", '"Hello World"', 'slug("Hello World")', '"hello-world".to_string()'),
     T("extra_spaces", '"  Rust  Is Fun "', 'slug("  Rust  Is Fun ")', '"rust-is-fun".to_string()')],
    [T("empty", '""', 'slug("")', "String::new()")],
    [("rust", "`s` is dropped when the function returns. A reference to it would dangle."),
     ("rust", "The text is new, so the function must hand over ownership: return `String`.")],
    ("No lifetime annotation can fix this: the data doesn't exist in any input. When a function creates text, it returns an owned value.", "O(n)", "O(n)"),
    "When could you return `&str` from a function that sometimes creates new text? (See `Cow`.)",
    ["A reference can only point at data that outlives the function.", "New data means an owned return type."],
    rules=dict(lines=2),
))

P.append(fix(
    "longest", "longest(a, b)", "easy", "elision", ["E0106", "lifetime parameters"],
    "`longest` returns the longer of two strings (`a` on a tie). It doesn't compile.",
    """
    /// The longer of `a` and `b`; `a` on a tie.
    pub fn longest(a: &str, b: &str) -> &str {
        if b.len() > a.len() {
            b
        } else {
            a
        }
    }
    """,
    """
    /// The longer of `a` and `b`; `a` on a tie.
    pub fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
        if b.len() > a.len() {
            b
        } else {
            a
        }
    }
    """,
    [T("longer_first", '"apple", "fig"', 'longest("apple", "fig")', '"apple"'),
     T("tie", '"ab", "cd"', 'longest("ab", "cd")', '"ab"')],
    [T("longer_second", '"abc", "abcd"', 'longest("abc", "abcd")', '"abcd"'),
     T("owned_inputs", "two Strings", "longest(&a, &b)", '"xyz!"', setup='let a = String::from("xy");\nlet b = String::from("xyz!");')],
    [("rust", "The result could borrow from either input, and elision can't choose between two."),
     ("rust", "Declare one lifetime `'a` and use it for both inputs and the output: the result lives as long as the shorter of the two.")],
    ("`'a` becomes the overlap of the two borrows, which is exactly as long as the result can safely be used.", "O(1)", "O(1)"),
    "Why can't the compiler infer the output lifetime from the body?",
    ["Two reference inputs and a reference output need an explicit lifetime.", "One shared `'a` means 'valid while both are'."],
    rules=dict(lines=1),
))

P.append(fix(
    "fix-output-borrows-wrong-input", "Fix: the output borrows the wrong input", "easy", "elision", ["over-constrained lifetimes"],
    "`after` compiles, but callers can't use it with a temporary prefix. Fix the signature so the tests compile.",
    """
    /// The part of `line` after `prefix`, if `line` starts with it.
    pub fn after<'a>(line: &'a str, prefix: &'a str) -> Option<&'a str> {
        line.strip_prefix(prefix)
    }
    """,
    """
    /// The part of `line` after `prefix`, if `line` starts with it.
    pub fn after<'a>(line: &'a str, prefix: &str) -> Option<&'a str> {
        line.strip_prefix(prefix)
    }
    """,
    [T("temporary_prefix", "line \"key: value\", prefix dropped before use", "rest", 'Some("value")',
       setup='let line = String::from("key: value");\nlet rest;\n{\n    let p = String::from("key: ");\n    rest = after(&line, &p);\n}'),
     T("no_match", '"abc", "x"', 'after("abc", "x")', "None")],
    [T("whole", '"abc", "abc"', 'after("abc", "abc")', 'Some("")')],
    [("rust", "The result is a slice of `line` only. Which parameter does it need to be tied to?")],
    ("Tying `prefix` to `'a` forces the prefix to live as long as the result. Only list a lifetime on an input when the output really borrows from it.", "O(n)", "O(1)"),
    "What does the signature say to callers, and what does it say to the function body?",
    ["Put a lifetime only on the inputs the output borrows from."],
    rules=dict(lines=1),
))

P.append(fix(
    "fix-impl-trait-hides-borrow", "Fix: impl Trait hides a borrow (E0700)", "medium", "elision", ["E0700", "impl Trait", "+ '_"],
    "`long_words` doesn't compile in edition 2021, even though its items are owned `String`s.",
    """
    /// Words of `text` longer than `min` characters, as owned Strings.
    pub fn long_words(text: &str, min: usize) -> impl Iterator<Item = String> {
        text.split_whitespace().filter(move |w| w.chars().count() > min).map(String::from)
    }
    """,
    """
    /// Words of `text` longer than `min` characters, as owned Strings.
    pub fn long_words(text: &str, min: usize) -> impl Iterator<Item = String> + '_ {
        text.split_whitespace().filter(move |w| w.chars().count() > min).map(String::from)
    }
    """,
    [T("filters", '"a quick brown fox", 3', 'long_words("a quick brown fox", 3).collect::<Vec<_>>()', 'vec!["quick".to_string(), "brown".to_string()]'),
     T("none", '"a b", 5', 'long_words("a b", 5).count()', "0")],
    [T("unicode", '"héllo hi", 4', 'long_words("héllo hi", 4).collect::<Vec<_>>()', 'vec!["héllo".to_string()]')],
    [("rust", "The iterator still reads from `text` while you iterate, but `impl Iterator<Item = String>` doesn't say so."),
     ("rust", "Add `+ '_` to the return type to say the iterator borrows from the input.")],
    ("In edition 2021, `impl Trait` only captures lifetimes that appear in its bounds; `+ '_` adds the input's. Edition 2024 captures all in-scope lifetimes by default, and `use<..>` narrows it.", "O(n)", "O(1)"),
    "When would you want an `impl Trait` return type that does not capture an input lifetime?",
    ["`impl Trait` return types and captured lifetimes.", "`+ '_` as 'borrows from the input'."],
    rules=dict(lines=1),
))

# ---------------------------------------------------------------- structs holding refs (easy)

P.append(write(
    "cursor-over-str", "A parser over &str", "easy", "structs-holding-refs", ["struct lifetimes", "&'a str"],
    """
        `Cursor` walks a borrowed `&'a str`. Each method first skips whitespace, then reads its token.
        On failure it returns `None` and leaves the cursor where it was.

        - `number` reads ASCII digits as a `u64`; `None` if there are none or they overflow.
        - `ident` reads an identifier: ASCII letters, digits and `_`, not starting with a digit.
        - `rest` returns what hasn't been read.

        Tokens must stay usable after the cursor is gone.
    """,
    """
    pub struct Cursor<'a> {
        src: &'a str,
        pos: usize,
    }

    impl<'a> Cursor<'a> {
        pub fn new(src: &'a str) -> Self {
            Cursor { src, pos: 0 }
        }

        pub fn number(&mut self) -> Option<u64> {
            todo!()
        }

        pub fn ident(&mut self) -> Option<&'a str> {
            todo!()
        }

        pub fn rest(&self) -> &'a str {
            todo!()
        }
    }
    """,
    """
    pub struct Cursor<'a> {
        src: &'a str,
        pos: usize,
    }

    impl<'a> Cursor<'a> {
        pub fn new(src: &'a str) -> Self {
            Cursor { src, pos: 0 }
        }

        /// Byte offset of the next non-whitespace character.
        fn skip_ws(&self) -> usize {
            let rest = &self.src[self.pos..];
            self.pos + (rest.len() - rest.trim_start().len())
        }

        pub fn number(&mut self) -> Option<u64> {
            let start = self.skip_ws();
            let rest = &self.src[start..];
            let len = rest.bytes().take_while(u8::is_ascii_digit).count();
            let n = rest[..len].parse().ok()?;
            self.pos = start + len;
            Some(n)
        }

        pub fn ident(&mut self) -> Option<&'a str> {
            let src = self.src;
            let start = self.skip_ws();
            let rest = &src[start..];
            let b = rest.as_bytes();
            if !b.first().is_some_and(|c| c.is_ascii_alphabetic() || *c == b'_') {
                return None;
            }
            let len = b.iter().take_while(|c| c.is_ascii_alphanumeric() || **c == b'_').count();
            self.pos = start + len;
            Some(&rest[..len])
        }

        pub fn rest(&self) -> &'a str {
            let src = self.src;
            &src[self.pos..]
        }
    }
    """,
    [T("tokens", '"  let x = 42": ident, ident, number, rest', "(c.ident(), c.ident(), c.number(), c.rest())", '(Some("let"), Some("x"), None, " = 42")',
       setup='let mut c = Cursor::new("  let x = 42");'),
     T("outlives_cursor", "ident read, then the cursor is dropped", "id", 'Some("alpha")',
       setup='let src = String::from("alpha 7");\nlet id;\n{\n    let mut c = Cursor::new(&src);\n    id = c.ident();\n}')],
    [T("overflow", '"99999999999999999999"', "Cursor::new(\"99999999999999999999\").number()", "None"),
     T("digit_first", '"9abc": ident, then number, then ident', "(c.ident(), c.number(), c.ident())", '(None, Some(9), Some("abc"))', setup='let mut c = Cursor::new("9abc");'),
     T("underscore", '"_x1 rest"', 'Cursor::new("_x1 rest").ident()', 'Some("_x1")'),
     T("unicode_after", '"n é": ident, rest', "(c.ident(), c.rest())", '(Some("n"), " é")', setup='let mut c = Cursor::new("n é");')],
    [("rust", "Return `&'a str`, not a borrow of `self`: copy `self.src` (a `&'a str`, which is `Copy`) into a local and slice that."),
     ("approach", "Compute the new position first, and only store it once the token is known to be valid.")],
    ("The struct holds a borrow, so it can't outlive `src`, but the tokens are tied to `'a`, not to the cursor. `trim_start` measures whitespace without allocating.", "O(n) total", "O(1)"),
    "How would you add `peek` without duplicating the parsing code?",
    ["A struct that borrows its input: `Cursor<'a>`.", "Methods returning `&'a str` instead of `&self`-tied slices."],
))

P.append(fix(
    "fix-struct-outlives-source", "Fix: struct outlives its source (E0597)", "easy", "structs-holding-refs", ["E0597"],
    "`first_lines` collects an `Excerpt` per document, then reads them all. It doesn't compile.",
    """
    pub struct Excerpt<'a> {
        pub text: &'a str,
    }

    /// The first line of each document, after trimming the document.
    pub fn first_lines(docs: &[String]) -> Vec<String> {
        let mut excerpts = Vec::new();
        for d in docs {
            let trimmed = d.trim().to_string();
            excerpts.push(Excerpt { text: trimmed.lines().next().unwrap_or("") });
        }
        excerpts.iter().map(|e| e.text.to_string()).collect()
    }
    """,
    """
    pub struct Excerpt<'a> {
        pub text: &'a str,
    }

    /// The first line of each document, after trimming the document.
    pub fn first_lines(docs: &[String]) -> Vec<String> {
        let mut excerpts = Vec::new();
        for d in docs {
            let trimmed = d.trim();
            excerpts.push(Excerpt { text: trimmed.lines().next().unwrap_or("") });
        }
        excerpts.iter().map(|e| e.text.to_string()).collect()
    }
    """,
    [T("two_docs", '["  hello\\nworld", "x"]', 'first_lines(&["  hello\\nworld".to_string(), "x".to_string()])', 'vec!["hello".to_string(), "x".to_string()]'),
     T("blank_doc", '["\\n"]', 'first_lines(&["\\n".to_string()])', 'vec![String::new()]')],
    [T("none", "[]", "first_lines(&[]).len()", "0")],
    [("rust", "Each `Excerpt` borrows from `trimmed`, which is dropped at the end of each loop iteration, but the excerpts are read after the loop."),
     ("rust", "`d.trim()` is already a `&str` borrowed from `docs`, which lives long enough. No need for a copy.")],
    ("Borrowing from the long-lived input instead of a per-iteration copy fixes the error and removes an allocation.", "O(total length)", "O(n)"),
    "If you really did need to transform each document, how would you keep the excerpts valid?",
    ["A struct's borrow must not outlive what it points at.", "Borrow from the caller's data, not a temporary copy."],
    rules=dict(methods=["clone", "to_owned"], lines=1),
))

P.append(fix(
    "fix-result-borrows-struct", "Fix: the result borrows the struct, not the text", "easy", "structs-holding-refs", ["'a vs '_"],
    "`Document` compiles, but callers can't keep a result after the `Document` is gone. Fix the signatures so the tests compile.",
    """
    pub struct Document<'a> {
        text: &'a str,
    }

    impl<'a> Document<'a> {
        pub fn new(text: &'a str) -> Self {
            Document { text }
        }

        /// The longest line; the first one on a tie.
        pub fn longest_line(&self) -> &str {
            self.text.lines().fold("", |best, l| if l.len() > best.len() { l } else { best })
        }

        /// Every line containing `word`.
        pub fn lines_with(&self, word: &str) -> Vec<&str> {
            self.text.lines().filter(|l| l.contains(word)).collect()
        }
    }
    """,
    """
    pub struct Document<'a> {
        text: &'a str,
    }

    impl<'a> Document<'a> {
        pub fn new(text: &'a str) -> Self {
            Document { text }
        }

        /// The longest line; the first one on a tie.
        pub fn longest_line(&self) -> &'a str {
            self.text.lines().fold("", |best, l| if l.len() > best.len() { l } else { best })
        }

        /// Every line containing `word`.
        pub fn lines_with(&self, word: &str) -> Vec<&'a str> {
            self.text.lines().filter(|l| l.contains(word)).collect()
        }
    }
    """,
    [T("longest_outlives_doc", "text \"a\\nlonger line\\nb\"; drop the Document", "line", '"longer line"',
       setup='let text = String::from("a\\nlonger line\\nb");\nlet line;\n{\n    let doc = Document::new(&text);\n    line = doc.longest_line();\n}'),
     T("lines_outlive_doc", "lines with \"x\"; drop the Document", "found", 'vec!["x1", "2x"]',
       setup='let text = String::from("x1\\nno\\n2x");\nlet found;\n{\n    let doc = Document::new(&text);\n    found = doc.lines_with("x");\n}')],
    [T("tie", '"ab\\ncd"', 'Document::new("ab\\ncd").longest_line()', '"ab"')],
    [("rust", "An elided output in a `&self` method borrows from `self`, the short-lived `Document`. The lines really come from `text`, which lives for `'a`."),
     ("rust", "Say so: return `&'a str` and `Vec<&'a str>`.")],
    ("`&'a str` means 'as long as the text', `&str` from `&self` means 'as long as this Document'. The body compiles either way; only callers see the difference.", "O(n)", "O(k)"),
    "Why is the first version not wrong, just less useful?",
    ["Methods on borrowing structs can return the struct's lifetime.", "Elision picks `self`, which is often too short."],
    rules=dict(lines=2),
))

# ---------------------------------------------------------------- two lifetimes (medium)

P.append(fix(
    "why-a-everywhere-fails", "Why 'a everywhere fails", "medium", "two-lifetimes", ["two lifetime parameters"],
    """
        `Splitter` borrows the text and the separator with one lifetime `'a`. Callers can't keep a piece
        after dropping the separator, though pieces only borrow from the text. Fix it so the tests compile.
        The pieces must stay borrowed: don't copy them into `String`s.
    """,
    """
    pub struct Splitter<'a> {
        text: &'a str,
        sep: &'a str,
    }

    impl<'a> Splitter<'a> {
        pub fn new(text: &'a str, sep: &'a str) -> Self {
            Splitter { text, sep }
        }

        pub fn first(&self) -> &'a str {
            self.text.split(self.sep).next().unwrap_or("")
        }

        pub fn parts(&self) -> Vec<&'a str> {
            self.text.split(self.sep).collect()
        }
    }
    """,
    """
    pub struct Splitter<'t, 's> {
        text: &'t str,
        sep: &'s str,
    }

    impl<'t, 's> Splitter<'t, 's> {
        pub fn new(text: &'t str, sep: &'s str) -> Self {
            Splitter { text, sep }
        }

        pub fn first(&self) -> &'t str {
            self.text.split(self.sep).next().unwrap_or("")
        }

        pub fn parts(&self) -> Vec<&'t str> {
            self.text.split(self.sep).collect()
        }
    }
    """,
    [T("first_outlives_sep", "text \"a,b,c\", separator dropped", "first", '"a"',
       setup='let text = String::from("a,b,c");\nlet first;\n{\n    let sep = String::from(",");\n    first = Splitter::new(&text, &sep).first();\n}'),
     T("parts_outlive_sep", "text \"a--b\", separator dropped", "parts", 'vec!["a", "b"]',
       setup='let text = String::from("a--b");\nlet parts;\n{\n    let sep = String::from("--");\n    parts = Splitter::new(&text, &sep).parts();\n}')],
    [T("no_sep", '"abc", ","', 'Splitter::new("abc", ",").parts()', 'vec!["abc"]')],
    [("rust", "One `'a` for both fields means `'a` can only be as long as the shorter borrow: the separator's."),
     ("rust", "Give the struct two lifetime parameters, and tie the outputs to the text's.")],
    ("With separate `'t` and `'s`, outputs borrow only from the text. Most structs need one lifetime; add a second exactly when outputs come from one field but not another.", "O(n)", "O(k)"),
    "When is one lifetime for several fields the right design?",
    ["A struct with two independent lifetime parameters.", "Outputs tied to one field, not the whole struct."],
    rules=dict(methods=["to_string", "to_owned", "clone", "into", "from"]),
))

P.append(write(
    "zero-copy-tokenizer", "Zero-copy tokenizer", "medium", "two-lifetimes", ["Iterator", "enum with lifetimes"],
    """
        `Tokenizer` yields `Token`s borrowed from the source: identifiers (ASCII letter or `_`, then letters,
        digits, `_`), numbers (ASCII digits) and single punctuation characters (any other non-whitespace
        character). Whitespace separates tokens.

        `longest_ident` returns the longest identifier from any token iterator (the first one on a tie). It
        must work on tokens that outlive the tokenizer.
    """,
    """
    #[derive(Debug, PartialEq, Clone, Copy)]
    pub enum Token<'a> {
        Ident(&'a str),
        Number(&'a str),
        Punct(char),
    }

    pub struct Tokenizer<'a> {
        rest: &'a str,
    }

    impl<'a> Tokenizer<'a> {
        pub fn new(src: &'a str) -> Self {
            Tokenizer { rest: src }
        }
    }

    impl<'a> Iterator for Tokenizer<'a> {
        type Item = Token<'a>;

        fn next(&mut self) -> Option<Token<'a>> {
            todo!()
        }
    }

    pub fn longest_ident<'a, I: IntoIterator<Item = Token<'a>>>(tokens: I) -> Option<&'a str> {
        todo!()
    }
    """,
    """
    #[derive(Debug, PartialEq, Clone, Copy)]
    pub enum Token<'a> {
        Ident(&'a str),
        Number(&'a str),
        Punct(char),
    }

    pub struct Tokenizer<'a> {
        rest: &'a str,
    }

    impl<'a> Tokenizer<'a> {
        pub fn new(src: &'a str) -> Self {
            Tokenizer { rest: src }
        }
    }

    fn is_ident_start(c: char) -> bool {
        c.is_ascii_alphabetic() || c == '_'
    }

    impl<'a> Iterator for Tokenizer<'a> {
        type Item = Token<'a>;

        fn next(&mut self) -> Option<Token<'a>> {
            let s = self.rest.trim_start();
            let c = s.chars().next()?;
            let len = if is_ident_start(c) {
                s.find(|c: char| !(c.is_ascii_alphanumeric() || c == '_')).unwrap_or(s.len())
            } else if c.is_ascii_digit() {
                s.find(|c: char| !c.is_ascii_digit()).unwrap_or(s.len())
            } else {
                c.len_utf8()
            };
            let (text, rest) = s.split_at(len);
            self.rest = rest;
            Some(if is_ident_start(c) {
                Token::Ident(text)
            } else if c.is_ascii_digit() {
                Token::Number(text)
            } else {
                Token::Punct(c)
            })
        }
    }

    pub fn longest_ident<'a, I: IntoIterator<Item = Token<'a>>>(tokens: I) -> Option<&'a str> {
        tokens
            .into_iter()
            .filter_map(|t| match t {
                Token::Ident(s) => Some(s),
                _ => None,
            })
            .reduce(|best, s| if s.len() > best.len() { s } else { best })
    }
    """,
    [T("mixed", '"let x1 = 42+y;"', 'Tokenizer::new("let x1 = 42+y;").collect::<Vec<_>>()',
       "vec![Token::Ident(\"let\"), Token::Ident(\"x1\"), Token::Punct('='), Token::Number(\"42\"), Token::Punct('+'), Token::Ident(\"y\"), Token::Punct(';')]"),
     T("longest_outlives_tokenizer", '"a bb ccc dd"', "best", 'Some("ccc")',
       setup='let src = String::from("a bb ccc dd");\nlet best;\n{\n    let t = Tokenizer::new(&src);\n    best = longest_ident(t);\n}')],
    [T("unicode_punct", '"a→b"', 'Tokenizer::new("a→b").collect::<Vec<_>>()', "vec![Token::Ident(\"a\"), Token::Punct('→'), Token::Ident(\"b\")]"),
     T("blank", '"   "', 'Tokenizer::new("   ").count()', "0"),
     T("tie_first", '"ab cd"', 'longest_ident(Tokenizer::new("ab cd"))', 'Some("ab")'),
     T("numbers_are_not_idents", '"12345 ab"', 'longest_ident(Tokenizer::new("12345 ab"))', 'Some("ab")'),
     T("from_a_vec", "a Vec<Token> built by hand", 'longest_ident(vec![Token::Punct(\'x\'), Token::Ident("q")])', 'Some("q")')],
    [("rust", "`type Item = Token<'a>`: tokens borrow the source, not the tokenizer, so they can outlive it."),
     ("rust", "`s.split_at(len)` gives the token and the rest, both `&'a str`."),
     ("rust", "`longest_ident` only needs `IntoIterator<Item = Token<'a>>`, so it works on a `Tokenizer`, a `Vec`, or anything else.")],
    ("No token allocates. The iterator and the tokens are separate borrows of the source, which is why `longest_ident` can return data after the tokenizer is dropped.", "O(n)", "O(1)"),
    "Add byte offsets to each token for error messages. How does the type change?",
    ["Iterator items that borrow the input: `type Item = Token<'a>`.", "Generic functions over `IntoIterator<Item = Token<'a>>`."],
    source="W36", related=("L3", "S2"),
))

P.append(write(
    "binary-frame-parser", "Zero-copy binary frame parser", "medium", "two-lifetimes", ["&[u8]", "split_first_chunk", "big-endian"],
    """
        A frame is: magic `b"AN"` (2 bytes), a kind byte, a big-endian `u16` length, then that many payload
        bytes.

        - `parse_frame` returns the frame and the bytes after it, or `None` for a bad or truncated frame.
          The payload must borrow from `buf`.
        - `parse_all` parses back-to-back frames until the buffer is empty; `None` if anything is left that
          isn't a whole frame.
    """,
    """
    #[derive(Debug, PartialEq)]
    pub struct Frame<'a> {
        pub kind: u8,
        pub payload: &'a [u8],
    }

    pub const MAGIC: &[u8; 2] = b"AN";

    pub fn parse_frame(buf: &[u8]) -> Option<(Frame<'_>, &[u8])> {
        todo!()
    }

    pub fn parse_all(buf: &[u8]) -> Option<Vec<Frame<'_>>> {
        todo!()
    }
    """,
    """
    #[derive(Debug, PartialEq)]
    pub struct Frame<'a> {
        pub kind: u8,
        pub payload: &'a [u8],
    }

    pub const MAGIC: &[u8; 2] = b"AN";

    pub fn parse_frame(buf: &[u8]) -> Option<(Frame<'_>, &[u8])> {
        let rest = buf.strip_prefix(MAGIC)?;
        let (&kind, rest) = rest.split_first()?;
        let (len, rest) = rest.split_first_chunk::<2>()?;
        let len = usize::from(u16::from_be_bytes(*len));
        if rest.len() < len {
            return None;
        }
        let (payload, rest) = rest.split_at(len);
        Some((Frame { kind, payload }, rest))
    }

    pub fn parse_all(mut buf: &[u8]) -> Option<Vec<Frame<'_>>> {
        let mut frames = Vec::new();
        while !buf.is_empty() {
            let (frame, rest) = parse_frame(buf)?;
            frames.push(frame);
            buf = rest;
        }
        Some(frames)
    }
    """,
    [T("one_frame", 'AN, kind 1, len 5, "hello", then "tail"', "parse_frame(&buf)", 'Some((Frame { kind: 1, payload: &b"hello"[..] }, &b"tail"[..]))',
       setup='let mut buf = b"AN\\x01".to_vec();\nbuf.extend_from_slice(&5u16.to_be_bytes());\nbuf.extend_from_slice(b"hellotail");'),
     T("bad_magic", 'b"XX\\x01\\x00\\x00"', 'parse_frame(b"XX\\x01\\x00\\x00")', "None")],
    [T("truncated_payload", "length 5, only 3 bytes", 'parse_frame(b"AN\\x01\\x00\\x05abc")', "None"),
     T("short_header", 'b"AN\\x01\\x00"', 'parse_frame(b"AN\\x01\\x00")', "None"),
     T("empty_payload", "length 0", 'parse_frame(b"AN\\x07\\x00\\x00")', 'Some((Frame { kind: 7, payload: &[][..] }, &[][..]))'),
     T("zero_copy", "payload points into buf", "same", "true",
       setup='let buf = b"AN\\x01\\x00\\x02hi".to_vec();\nlet (f, _) = parse_frame(&buf).unwrap();\nlet same = std::ptr::eq(f.payload.as_ptr(), buf[5..].as_ptr());'),
     T("two_frames", "two frames back to back", 'parse_all(b"AN\\x01\\x00\\x01aAN\\x02\\x00\\x00").map(|v| v.iter().map(|f| f.kind).collect::<Vec<_>>())', "Some(vec![1, 2])"),
     T("trailing_junk", "one frame then 1 junk byte", 'parse_all(b"AN\\x01\\x00\\x00!")', "None"),
     T("large_length", "length 0xFFFF with 3 bytes", 'parse_frame(b"AN\\x01\\xff\\xffabc")', "None")],
    [("rust", "`strip_prefix`, `split_first` and `split_first_chunk::<2>()` each return `Option`, so every bounds check is a `?`."),
     ("rust", "`u16::from_be_bytes(*len)` reads the network-order length from a `&[u8; 2]`."),
     ("edge case", "Never trust the length field: check that the buffer really has that many bytes.")],
    ("Every step slices the input, so nothing is copied and nothing can index out of bounds. Returning the rest makes `parse_all` a simple loop.", "O(1) per frame", "O(frames)"),
    "How would you parse frames from a socket, where a frame can arrive split across reads?",
    ["Zero-copy parsing: return slices of the input.", "Bounds checks as `Option` combinators instead of indexing."],
    source="W40", related=("L3", "S3"),
))

P.append(fix(
    "fix-a-mut-self-borrows-forever", "Fix: &'a mut self borrows forever", "medium", "two-lifetimes", ["&'a mut self", "E0499"],
    "`Reader::take` compiles, but a caller can't call it twice. Fix it so the tests compile.",
    """
    pub struct Reader<'a> {
        data: &'a [u8],
        pos: usize,
    }

    impl<'a> Reader<'a> {
        pub fn new(data: &'a [u8]) -> Self {
            Reader { data, pos: 0 }
        }

        /// The next `n` bytes, or None if fewer remain.
        pub fn take(&'a mut self, n: usize) -> Option<&'a [u8]> {
            let chunk = self.data.get(self.pos..self.pos + n)?;
            self.pos += n;
            Some(chunk)
        }

        pub fn remaining(&self) -> usize {
            self.data.len() - self.pos
        }
    }
    """,
    """
    pub struct Reader<'a> {
        data: &'a [u8],
        pos: usize,
    }

    impl<'a> Reader<'a> {
        pub fn new(data: &'a [u8]) -> Self {
            Reader { data, pos: 0 }
        }

        /// The next `n` bytes, or None if fewer remain.
        pub fn take(&mut self, n: usize) -> Option<&'a [u8]> {
            let chunk = self.data.get(self.pos..self.pos + n)?;
            self.pos += n;
            Some(chunk)
        }

        pub fn remaining(&self) -> usize {
            self.data.len() - self.pos
        }
    }
    """,
    [T("twice", "data [1, 2, 3, 4, 5]; take 2, take 3, remaining", "(a, b, r.remaining())", "(Some(&[1u8, 2][..]), Some(&[3u8, 4, 5][..]), 0)",
       setup="let data = [1u8, 2, 3, 4, 5];\nlet mut r = Reader::new(&data);\nlet a = r.take(2);\nlet b = r.take(3);"),
     T("too_many", "data [1]; take 9, then take 1", "(x, y)", "(None, Some(&[1u8][..]))",
       setup="let data = [1u8];\nlet mut r = Reader::new(&data);\nlet x = r.take(9);\nlet y = r.take(1);")],
    [T("zero", "take 0 from empty", "Reader::new(&[]).take(0)", "Some(&[][..])")],
    [("rust", "`&'a mut self` borrows the Reader mutably for all of `'a`, the lifetime of the data, so the first call locks it for good."),
     ("rust", "The chunk comes from `data: &'a [u8]`, not from `self`. The `&mut self` borrow can be short.")],
    ("Tying `&mut self` to the struct's own lifetime parameter is a classic trap: it compiles, and the struct becomes unusable after one call. The output lifetime `'a` alone says where the bytes come from.", "O(1)", "O(1)"),
    "Why does `&'a self` (shared) cause much less trouble than `&'a mut self`?",
    ["Never write `&'a mut self` with the struct's own `'a`.", "Outputs can use `'a` while `self` is borrowed briefly."],
    rules=dict(lines=1),
))

# ---------------------------------------------------------------- 'static and T: 'a (medium)

P.append(write(
    "static-bound-vs-static-ref", "'static bound vs &'static", "medium", "static-bounds", ["T: 'static", "Any"],
    """
        `Stash` stores values of any type and gets them back by type. `Box<dyn Any>` needs `T: 'static`,
        which means the value owns its data (or borrows only `'static` data). It does not mean it lives
        forever: a `String` built at runtime qualifies.
    """,
    """
    use std::any::Any;

    #[derive(Default)]
    pub struct Stash {
        items: Vec<Box<dyn Any>>,
    }

    impl Stash {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn put<T: Any>(&mut self, value: T) {
            todo!()
        }

        /// Every stored value of type `T`, in insertion order.
        pub fn all<T: Any>(&self) -> Vec<&T> {
            todo!()
        }
    }
    """,
    """
    use std::any::Any;

    #[derive(Default)]
    pub struct Stash {
        items: Vec<Box<dyn Any>>,
    }

    impl Stash {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn put<T: Any>(&mut self, value: T) {
            self.items.push(Box::new(value));
        }

        /// Every stored value of type `T`, in insertion order.
        pub fn all<T: Any>(&self) -> Vec<&T> {
            self.items.iter().filter_map(|b| b.downcast_ref::<T>()).collect()
        }
    }
    """,
    [T("by_type", "put String, 5u32, \"lit\", 7u32; all::<u32>()", "s.all::<u32>()", "vec![&5, &7]",
       setup='let mut s = Stash::new();\ns.put(format!("user-{}", 42));\ns.put(5u32);\ns.put("lit");\ns.put(7u32);'),
     T("runtime_string_is_static", "the String built with format!", "(s.all::<String>()[0].as_str(), s.all::<&str>())", '("user-42", vec![&"lit"])',
       setup='let mut s = Stash::new();\ns.put(format!("user-{}", 42));\ns.put("lit");')],
    [T("empty", "nothing stored", "Stash::new().all::<i64>().len()", "0"),
     T("types_are_exact", "put 1u64; all::<u32>()", "s.all::<u32>().len()", "0", setup="let mut s = Stash::new();\ns.put(1u64);")],
    [("rust", "`Any` is implemented for every `T: 'static`, so `T: Any` already implies the bound."),
     ("rust", "`Box<dyn Any>::downcast_ref::<T>()` returns `Some(&T)` only if the value is exactly a `T`.")],
    ("`T: 'static` rules out types holding short-lived borrows, because `Any` can't track lifetimes. Owned data like `String` and `Vec` always qualifies.", "O(n) for all", "O(n)"),
    "Why can't `Any` support types with non-'static lifetimes?",
    ["`T: 'static` means 'no short borrows inside', not 'lives forever'.", "`Any` and `downcast_ref`."],
    related=("L3", "L4"),
))

P.append(write(
    "box-dyn-error-downcast", "Box<dyn Error + 'static> and downcasting", "medium", "static-bounds", ["Box<dyn Error>", "downcast_ref", "?"],
    """
        `sum_config` sums the values of `key=value` lines, skipping blank lines. A line without `=` is a
        `ConfigError` with its 1-based line number; a bad number is the `ParseIntError`. Both come back as
        `Box<dyn Error>`.

        `bad_line` recovers the line number when the error is a `ConfigError`.
    """,
    """
    use std::error::Error;
    use std::fmt;

    #[derive(Debug)]
    pub struct ConfigError {
        pub line: usize,
    }

    impl fmt::Display for ConfigError {
        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
            write!(f, "line {}: expected key=value", self.line)
        }
    }

    impl Error for ConfigError {}

    pub fn sum_config(text: &str) -> Result<i64, Box<dyn Error>> {
        todo!()
    }

    pub fn bad_line(err: &(dyn Error + 'static)) -> Option<usize> {
        todo!()
    }
    """,
    """
    use std::error::Error;
    use std::fmt;

    #[derive(Debug)]
    pub struct ConfigError {
        pub line: usize,
    }

    impl fmt::Display for ConfigError {
        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
            write!(f, "line {}: expected key=value", self.line)
        }
    }

    impl Error for ConfigError {}

    pub fn sum_config(text: &str) -> Result<i64, Box<dyn Error>> {
        let mut total = 0;
        for (i, line) in text.lines().enumerate() {
            if line.trim().is_empty() {
                continue;
            }
            let (_, value) = line.split_once('=').ok_or(ConfigError { line: i + 1 })?;
            total += value.trim().parse::<i64>()?;
        }
        Ok(total)
    }

    pub fn bad_line(err: &(dyn Error + 'static)) -> Option<usize> {
        err.downcast_ref::<ConfigError>().map(|e| e.line)
    }
    """,
    [T("sums", '"a=1\\nb = 2"', 'sum_config("a=1\\nb = 2").ok()', "Some(3)"),
     T("config_error_line", '"a=1\\nb"', 'bad_line(&*sum_config("a=1\\nb").unwrap_err())', "Some(2)")],
    [T("parse_error_kept", '"a=x"', 'sum_config("a=x").unwrap_err().is::<std::num::ParseIntError>()', "true"),
     T("parse_error_has_no_line", '"a=x"', 'bad_line(&*sum_config("a=x").unwrap_err())', "None"),
     T("blank_lines", '"a=1\\n\\n b=2 "', 'sum_config("a=1\\n\\n b=2 ").ok()', "Some(3)"),
     T("line_numbers_count_blanks", '"\\n\\nx"', 'bad_line(&*sum_config("\\n\\nx").unwrap_err())', "Some(3)"),
     T("message", '"x"', 'sum_config("x").unwrap_err().to_string()', '"line 1: expected key=value".to_string()')],
    [("rust", "`?` converts any `E: Error + 'static` into `Box<dyn Error>` through `From`, so both error types can use it."),
     ("rust", "`Box<dyn Error>` means `Box<dyn Error + 'static>`. That `'static` is what makes `downcast_ref` possible."),
     ("rust", "`&*boxed_err` turns a `Box<dyn Error>` into `&(dyn Error + 'static)`.")],
    ("Trait objects carry a lifetime bound, defaulting to `'static` in a `Box`. Downcasting relies on `TypeId`, which only exists for `'static` types; that's why `bad_line` takes `dyn Error + 'static`.", "O(n)", "O(1)"),
    "When would you define an error enum instead of returning `Box<dyn Error>`?",
    ["The default `'static` bound on `Box<dyn Trait>`.", "Downcasting errors with `downcast_ref` and `is`."],
    related=("L3", "S1", "C4"),
))

P.append(fix(
    "fix-thread-spawn-static", "Fix: thread::spawn needs 'static", "medium", "static-bounds", ["E0521", "thread::scope"],
    """
        `parallel_sum` sums chunks of a borrowed slice on separate threads. It doesn't compile. Fix it without
        copying the data.
    """,
    """
    use std::thread;

    /// Sums `data` using up to `chunks` threads.
    pub fn parallel_sum(data: &[u64], chunks: usize) -> u64 {
        let size = data.len().div_ceil(chunks.max(1)).max(1);
        let handles: Vec<_> = data
            .chunks(size)
            .map(|chunk| thread::spawn(move || chunk.iter().sum::<u64>()))
            .collect();
        handles.into_iter().map(|h| h.join().expect("worker panicked")).sum()
    }
    """,
    """
    use std::thread;

    /// Sums `data` using up to `chunks` threads.
    pub fn parallel_sum(data: &[u64], chunks: usize) -> u64 {
        let size = data.len().div_ceil(chunks.max(1)).max(1);
        thread::scope(|s| {
            let handles: Vec<_> = data
                .chunks(size)
                .map(|chunk| s.spawn(move || chunk.iter().sum::<u64>()))
                .collect();
            handles.into_iter().map(|h| h.join().expect("worker panicked")).sum()
        })
    }
    """,
    [T("hundred", "1..=100, 4 threads", "parallel_sum(&data, 4)", "5050", setup="let data: Vec<u64> = (1..=100).collect();"),
     T("empty", "[], 3 threads", "parallel_sum(&[], 3)", "0")],
    [T("zero_chunks", "[1, 2, 3], 0 threads", "parallel_sum(&[1, 2, 3], 0)", "6"),
     T("more_threads_than_items", "[1, 2, 3], 10 threads", "parallel_sum(&[1, 2, 3], 10)", "6"),
     T("big", "10⁶ ones, 8 threads", "parallel_sum(&data, 8)", "1_000_000", setup="let data = vec![1u64; 1_000_000];")],
    [("rust", "`thread::spawn` requires `F: 'static`: the thread might outlive this function, and `data` with it."),
     ("rust", "`thread::scope` guarantees every thread spawned in it is joined before it returns, so the closures may borrow `data`.")],
    ("Scoped threads prove to the compiler that the borrow outlives the threads. The usual alternatives, `Arc<Vec<_>>` or `to_vec`, copy or reshape the data.", "O(n / threads) wall time", "O(threads)"),
    "When would you still choose `thread::spawn` with `Arc` over scoped threads?",
    ["Why `thread::spawn` needs `'static`.", "`thread::scope` for borrowing across threads."],
    rules=dict(methods=["to_vec", "to_owned", "clone", "leak", "into_boxed_slice"], types=["Arc", "Rc"]),
    related=("L3", "C1"),
))

# ---------------------------------------------------------------- variance & HRTBs (hard)

P.append(fix(
    "fix-mut-invariance", "Fix: &mut T is invariant", "hard", "variance-hrtbs", ["variance", "&mut T"],
    "`all_names` collects borrowed names, then adds two defaults. It doesn't compile, even though the defaults are string literals.",
    """
    fn add_defaults(names: &mut Vec<&'static str>) {
        names.push("root");
        names.push("admin");
    }

    /// The names in `input` (one per line), then the defaults.
    pub fn all_names(input: &str) -> Vec<&str> {
        let mut names: Vec<&str> = input.lines().collect();
        add_defaults(&mut names);
        names
    }
    """,
    """
    fn add_defaults<'a>(names: &mut Vec<&'a str>) {
        names.push("root");
        names.push("admin");
    }

    /// The names in `input` (one per line), then the defaults.
    pub fn all_names(input: &str) -> Vec<&str> {
        let mut names: Vec<&str> = input.lines().collect();
        add_defaults(&mut names);
        names
    }
    """,
    [T("owned_input", 'input "alice\\nbob" from a String', "all_names(&input)", 'vec!["alice", "bob", "root", "admin"]', setup='let input = String::from("alice\\nbob");'),
     T("empty", '""', 'all_names("")', 'vec!["root", "admin"]')],
    [T("one", 'input "x" from a String', "all_names(&input).len()", "3", setup='let input = String::from("x");')],
    [("rust", "`&'static str` coerces to `&'a str`, so why not `Vec<&'a str>` to `Vec<&'static str>` behind a `&mut`?"),
     ("rust", "Through `&mut`, the function could also read the Vec as `&'static str`s, or store longer-lived references into it, so the element type must match exactly: `&mut T` is invariant in `T`."),
     ("rust", "Make `add_defaults` generic over the element lifetime. Pushing a `&'static str` into a `Vec<&'a str>` is fine.")],
    ("Covariance lets `&'static str` shrink to `&'a str`. Behind `&mut`, the type can't change at all, because the callee could write a short-lived value where a long-lived one is expected, or vice versa. The generic version asks for exactly what it needs.", "O(n)", "O(n)"),
    "Show the unsound program the compiler would accept if `&mut T` were covariant.",
    ["`&mut T` is invariant in `T`.", "Generalise the callee instead of the caller."],
    rules=dict(lines=1),
))

P.append(write(
    "hrtb-borrowed-iteration", "for<'a>: iterate a collection you own", "hard", "variance-hrtbs", ["HRTB", "for<'a>", "IntoIterator"],
    """
        `Stats<C>` owns any collection of `u32` that can be iterated by reference: `Vec`, arrays,
        `VecDeque`, `BTreeSet`… Add the bound that makes this work, then implement the methods. None of
        them may consume or copy the collection.
    """,
    """
    pub struct Stats<C> {
        data: C,
    }

    impl<C> Stats<C> {
        pub fn new(data: C) -> Self {
            Stats { data }
        }

        /// The mean, or None if empty.
        pub fn mean(&self) -> Option<f64> {
            todo!()
        }

        /// Largest minus smallest, or None if empty.
        pub fn spread(&self) -> Option<u32> {
            todo!()
        }

        pub fn count_above(&self, threshold: u32) -> usize {
            todo!()
        }
    }
    """,
    """
    pub struct Stats<C> {
        data: C,
    }

    impl<C> Stats<C>
    where
        for<'a> &'a C: IntoIterator<Item = &'a u32>,
    {
        pub fn new(data: C) -> Self {
            Stats { data }
        }

        /// The mean, or None if empty.
        pub fn mean(&self) -> Option<f64> {
            let (sum, n) = self.data.into_iter().fold((0u64, 0u64), |(s, n), &x| (s + u64::from(x), n + 1));
            (n > 0).then(|| sum as f64 / n as f64)
        }

        /// Largest minus smallest, or None if empty.
        pub fn spread(&self) -> Option<u32> {
            let max = self.data.into_iter().max()?;
            let min = self.data.into_iter().min()?;
            Some(max - min)
        }

        pub fn count_above(&self, threshold: u32) -> usize {
            self.data.into_iter().filter(|&&x| x > threshold).count()
        }
    }
    """,
    [T("vec_mean", "Vec [1, 2, 3]", "Stats::new(vec![1u32, 2, 3]).mean()", "Some(2.0)"),
     T("deque_spread", "VecDeque [5, 1]", "Stats::new(std::collections::VecDeque::from([5u32, 1])).spread()", "Some(4)")],
    [T("array", "[4, 4, 4]", "Stats::new([4u32, 4, 4]).spread()", "Some(0)"),
     T("btreeset", "BTreeSet {1, 10}", "Stats::new(std::collections::BTreeSet::from([1u32, 10])).mean()", "Some(5.5)"),
     T("empty", "empty Vec", "Stats::new(Vec::<u32>::new()).mean()", "None"),
     T("count", "[1, 5, 9], above 4", "Stats::new(vec![1u32, 5, 9]).count_above(4)", "2"),
     T("reuse", "call three methods on the same Stats", "(s.mean(), s.spread(), s.count_above(0))", "(Some(2.0), Some(2), 3)", setup="let s = Stats::new(vec![1u32, 2, 3]);")],
    [("rust", "Inside `mean(&self)` you borrow `self.data` for a lifetime that only exists inside the call. The bound must hold for every such lifetime."),
     ("rust", "`where for<'a> &'a C: IntoIterator<Item = &'a u32>` says: any borrow of `C` can be iterated, yielding borrows of the same length."),
     ("rust", "`&C` is `Copy`, so `self.data.into_iter()` can be called as many times as you like.")],
    ("A higher-ranked bound quantifies over lifetimes the caller can't name. `Fn(&str) -> &str` uses the same mechanism behind its sugar; here it has to be written out because the trait is applied to a reference type.", "O(n) per call", "O(1)"),
    "Rewrite the bound as a per-method `where &'s C: ...` with the method's own lifetime. Which do you prefer, and why?",
    ["Higher-ranked trait bounds: `for<'a>`.", "Bounds on `&C` rather than on `C`."],
    related=("L3", "L4"),
))

P.append(write(
    "self-referential-parser", "The self-referential struct trap", "hard", "variance-hrtbs", ["self-referential", "PhantomData", "design"],
    """
        The tempting design is `struct Parser { source: String, current: Option<&str> }`, where `current` points
        into `source`. It can't be written in safe Rust: moving the struct would move the `String` value while
        the reference still points at its buffer, and there's no lifetime to name for "my own field".

        Instead, let the caller own the text. Implement `Parser<'a, T>` over a borrowed `&'a str`, generic over
        a `Tokenize` strategy, and the two strategies:

        - `Whitespace` splits on whitespace.
        - `Comma` splits on `,`, trims each token, and skips empty ones.

        `current` is the token most recently returned by `advance`: `None` before the first call and after
        the end. Tokens must outlive the parser.
    """,
    """
    use std::marker::PhantomData;

    pub trait Tokenize {
        /// Splits the next token off `input`, returning (token, remainder).
        fn next_token(input: &str) -> Option<(&str, &str)>;
    }

    pub struct Whitespace;

    pub struct Comma;

    impl Tokenize for Whitespace {
        fn next_token(input: &str) -> Option<(&str, &str)> {
            todo!()
        }
    }

    impl Tokenize for Comma {
        fn next_token(input: &str) -> Option<(&str, &str)> {
            todo!()
        }
    }

    pub struct Parser<'a, T> {
        // Replace this with the fields you need. The source text is owned by the caller.
        _todo: PhantomData<(&'a str, T)>,
    }

    impl<'a, T: Tokenize> Parser<'a, T> {
        pub fn new(source: &'a str) -> Self {
            todo!()
        }

        pub fn advance(&mut self) -> Option<&'a str> {
            todo!()
        }

        pub fn current(&self) -> Option<&'a str> {
            todo!()
        }
    }
    """,
    """
    use std::marker::PhantomData;

    pub trait Tokenize {
        /// Splits the next token off `input`, returning (token, remainder).
        fn next_token(input: &str) -> Option<(&str, &str)>;
    }

    pub struct Whitespace;

    pub struct Comma;

    impl Tokenize for Whitespace {
        fn next_token(input: &str) -> Option<(&str, &str)> {
            let input = input.trim_start();
            if input.is_empty() {
                return None;
            }
            let end = input.find(char::is_whitespace).unwrap_or(input.len());
            Some(input.split_at(end))
        }
    }

    impl Tokenize for Comma {
        fn next_token(input: &str) -> Option<(&str, &str)> {
            let input = input.trim_start_matches(|c: char| c == ',' || c.is_whitespace());
            if input.is_empty() {
                return None;
            }
            let end = input.find(',').unwrap_or(input.len());
            let (token, rest) = input.split_at(end);
            Some((token.trim_end(), rest))
        }
    }

    pub struct Parser<'a, T> {
        remaining: &'a str,
        current: Option<&'a str>,
        // T only picks the tokenizer; PhantomData records it without storing one.
        _tokenizer: PhantomData<T>,
    }

    impl<'a, T: Tokenize> Parser<'a, T> {
        pub fn new(source: &'a str) -> Self {
            Parser { remaining: source, current: None, _tokenizer: PhantomData }
        }

        pub fn advance(&mut self) -> Option<&'a str> {
            self.current = match T::next_token(self.remaining) {
                Some((token, rest)) => {
                    self.remaining = rest;
                    Some(token)
                }
                None => None,
            };
            self.current
        }

        pub fn current(&self) -> Option<&'a str> {
            self.current
        }
    }
    """,
    [T("walks", '"parse me please" with Whitespace', "(p.advance(), p.advance(), p.current(), p.advance(), p.advance(), p.current())",
       '(Some("parse"), Some("me"), Some("me"), Some("please"), None, None)',
       setup='let source = String::from("parse me please");\nlet mut p = Parser::<Whitespace>::new(&source);'),
     T("tokens_outlive_parser", '"a b"; drop the parser after one advance', "first", 'Some("a")',
       setup='let source = String::from("a b");\nlet first;\n{\n    let mut p = Parser::<Whitespace>::new(&source);\n    first = p.advance();\n}')],
    [T("comma", '"a, b,,c , " with Comma', "tokens", 'vec!["a", "b", "c"]',
       setup='let mut p = Parser::<Comma>::new("a, b,,c , ");\nlet tokens: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();'),
     T("before_first", "current() before advance", 'Parser::<Whitespace>::new("x").current()', "None"),
     T("empty", '"   " with Whitespace', 'Parser::<Whitespace>::new("   ").advance()', "None"),
     T("comma_keeps_inner_spaces", '" new york , la" with Comma', "tokens", 'vec!["new york", "la"]',
       setup='let mut p = Parser::<Comma>::new(" new york , la");\nlet tokens: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();')],
    [("approach", "Store the unread part of the source (`&'a str`) and the current token (`Option<&'a str>`). No `String` inside the parser."),
     ("rust", "`T` never appears in a field, so the compiler rejects it as unused. `PhantomData<T>` records it at zero size."),
     ("rust", "`next_token(input: &str) -> Option<(&str, &str)>` elides to one lifetime: both halves borrow `input`.")],
    ("Moving the owner out of the struct removes the self-reference: the parser is just two slices of someone else's text. If you truly need owner and view together, reach for a crate (`ouroboros`, `self_cell`) or store offsets instead of references.", "O(n) total", "O(1)"),
    "Rewrite `Parser` to own its `String` by storing byte offsets instead of references. What do you give up?",
    ["Why self-referential structs can't be written safely.", "`PhantomData` for type parameters that pick behaviour."],
    source="W38", related=("L3", "L4"),
))

P.append(fix(
    "fix-closure-returns-its-argument", "Fix: a closure that returns its argument", "hard", "variance-hrtbs", ["closure lifetimes", "fn items"],
    "`trimmed_lines` doesn't compile, although `str::trim` itself is fine.",
    """
    /// Every line of `text`, trimmed, skipping blank ones.
    pub fn trimmed_lines(text: &str) -> Vec<&str> {
        let trim = |s: &str| s.trim();
        text.lines().map(trim).filter(|l| !l.is_empty()).collect()
    }
    """,
    """
    /// Every line of `text`, trimmed, skipping blank ones.
    pub fn trimmed_lines(text: &str) -> Vec<&str> {
        fn trim(s: &str) -> &str {
            s.trim()
        }
        text.lines().map(trim).filter(|l| !l.is_empty()).collect()
    }
    """,
    [T("trims", '"  a \\n\\n b\\n"', 'trimmed_lines("  a \\n\\n b\\n")', 'vec!["a", "b"]'),
     T("owned_input", 'input from a String: "x\\n  y  "', "trimmed_lines(&input)", 'vec!["x", "y"]', setup='let input = String::from("x\\n  y  ");')],
    [T("all_blank", '" \\n\\t\\n"', 'trimmed_lines(" \\n\\t\\n").len()', "0")],
    [("rust", "An annotated `|s: &str|` closure takes any lifetime, but its return type gets one fixed lifetime, so the compiler can't connect the output to the input."),
     ("rust", "A `fn` item gets the full elision rules: `fn trim(s: &str) -> &str` means 'returns a borrow of `s`'. `.map(str::trim)` works too.")],
    ("Closure signatures are inferred, and inference doesn't apply the elision rule that links an output to an input. Named functions (or `str::trim` directly) state the relationship.", "O(n)", "O(k)"),
    "How could a closure be made to work here without turning it into a fn?",
    ["Closures don't get lifetime elision for their return type.", "Prefer `fn` items or method paths when a callback returns a borrow."],
    rules=dict(lines=3),
))

P.append(fix(
    "fix-box-dyn-fn-borrows", "Fix: Box<dyn Fn> that borrows", "hard", "variance-hrtbs", ["trait object lifetimes", "Box<dyn Fn + 'a>"],
    "`make_filter` builds a predicate from a borrowed allow-list. It doesn't compile.",
    """
    /// A predicate that accepts exactly the words in `allowed`.
    pub fn make_filter(allowed: &[&str]) -> Box<dyn Fn(&str) -> bool> {
        Box::new(move |w| allowed.iter().any(|&a| a == w))
    }
    """,
    """
    /// A predicate that accepts exactly the words in `allowed`.
    pub fn make_filter<'a>(allowed: &'a [&str]) -> Box<dyn Fn(&str) -> bool + 'a> {
        Box::new(move |w| allowed.iter().any(|&a| a == w))
    }
    """,
    [T("filters", 'allowed ["red", "blue"] built from Strings', "(f(\"red\"), f(\"green\"))", "(true, false)",
       setup='let owned = vec![String::from("red"), String::from("blue")];\nlet allowed: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();\nlet f = make_filter(&allowed);'),
     T("empty", "allowed []", 'make_filter(&[])("x")', "false")],
    [T("many_calls", 'allowed ["a"]', 'words.iter().filter(|w| f(w)).count()', "2",
       setup='let allowed = vec!["a"];\nlet f = make_filter(&allowed);\nlet words = ["a", "b", "a"];')],
    [("rust", "`Box<dyn Trait>` with no lifetime means `Box<dyn Trait + 'static>`: the closure may not borrow anything short-lived."),
     ("rust", "Add a lifetime bound to the trait object: `+ 'a`. `+ '_` won't do here, because `&[&str]` has two elided lifetimes."),
     ("rust", "`&'a [&str]` implies the inner strings outlive `'a`, so naming just the outer one is enough.")],
    ("Trait objects carry a lifetime bound, just like references. The default in a `Box` is `'static`; a closure capturing `allowed` lives only as long as `allowed`, so the box has to say so.", "O(k) per call", "O(1)"),
    "When would you return `impl Fn(&str) -> bool + 'a` instead of a Box?",
    ["Default `'static` bounds on boxed trait objects.", "`+ 'a` for trait objects that borrow."],
    rules=dict(lines=1),
))

STAGES = [
    ("elision", "Elision", "easy"),
    ("structs-holding-refs", "Structs holding refs", "easy"),
    ("two-lifetimes", "Two lifetimes", "medium"),
    ("static-bounds", "'static and T: 'a", "medium"),
    ("variance-hrtbs", "Variance & HRTBs", "hard"),
]

# `source` and `examples` are optional; drop empty ones so problem.toml stays tidy.
for p in P:
    if not p.get("source"):
        p.pop("source", None)
    if p.get("rules") is None:
        p.pop("rules", None)

if __name__ == "__main__":
    n = write_track("l3-lifetimes", "L3", "Lifetimes", "L", "core", 3,
                    "Lifetimes say what a reference borrows from. Most of the work is choosing which input an output is tied to.",
                    STAGES, P)
    print("L3", n)
