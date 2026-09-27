from author import T, write_track

P = []

P.append(dict(
    slug="fix-use-after-move", title="Fix: use after move", mode="fix", level="easy", stage="moves-and-copy", tags=["E0382", "move"],
    teaches=["Passing a `Vec` by value moves it; the caller can't use it afterwards.", "Read what you need before handing a value away."],
    statement="`summarize` should return the word count and the longest word. It doesn't compile.",
    examples=[("text = \"the quick fox\"", "(3, \"quick\")")],
    starter="""
        /// The number of words and the longest word, e.g. "the quick fox" → (3, "quick").
        pub fn summarize(text: &str) -> (usize, String) {
            let words: Vec<String> = text.split_whitespace().map(String::from).collect();
            let longest = longest_word(words);
            (words.len(), longest)
        }

        fn longest_word(words: Vec<String>) -> String {
            words.into_iter().fold(String::new(), |best, w| if w.len() > best.len() { w } else { best })
        }
    """,
    solution="""
        /// The number of words and the longest word, e.g. "the quick fox" → (3, "quick").
        pub fn summarize(text: &str) -> (usize, String) {
            let words: Vec<String> = text.split_whitespace().map(String::from).collect();
            let count = words.len();
            let longest = longest_word(words);
            (count, longest)
        }

        fn longest_word(words: Vec<String>) -> String {
            words.into_iter().fold(String::new(), |best, w| if w.len() > best.len() { w } else { best })
        }
    """,
    rules=dict(methods=["clone"], lines=2),
    visible=[
        T("three_words", "text = \"the quick fox\"", 'summarize("the quick fox")', '(3, "quick".to_string())'),
        T("empty", "text = \"\"", 'summarize("")', '(0, String::new())'),
    ],
    hidden=[
        T("tie_keeps_first", "text = \"ab cd\"", 'summarize("ab cd")', '(2, "ab".to_string())'),
    ],
    hints=[("rust", "After `longest_word(words)`, `words` belongs to `longest_word`. What do you still need from it?")],
    notes=("Reading `len()` before the move is the whole fix. Changing `longest_word` to borrow `&[String]` also works, but then it has to clone the result.", "O(n)", "O(n)"),
    follow_up="When should a function take `Vec<T>` rather than `&[T]`?",
    related=["L2"],
))

P.append(dict(
    slug="fix-small-struct-copy", title="Fix: a small struct that should be Copy", mode="fix", level="easy", stage="moves-and-copy", tags=["Copy", "derive", "E0382"],
    teaches=["Types are moved by default; `Copy` types are duplicated bit for bit.", "When a type can and should be `Copy`."],
    statement="`two_midpoints` uses `a` twice and doesn't compile. `Point` is two integers; make it behave like one.",
    starter="""
        #[derive(Debug, PartialEq)]
        pub struct Point {
            pub x: i32,
            pub y: i32,
        }

        pub fn midpoint(a: Point, b: Point) -> Point {
            Point { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 }
        }

        /// The midpoints of a→b and a→c.
        pub fn two_midpoints(a: Point, b: Point, c: Point) -> (Point, Point) {
            (midpoint(a, b), midpoint(a, c))
        }
    """,
    solution="""
        #[derive(Debug, PartialEq, Clone, Copy)]
        pub struct Point {
            pub x: i32,
            pub y: i32,
        }

        pub fn midpoint(a: Point, b: Point) -> Point {
            Point { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 }
        }

        /// The midpoints of a→b and a→c.
        pub fn two_midpoints(a: Point, b: Point, c: Point) -> (Point, Point) {
            (midpoint(a, b), midpoint(a, c))
        }
    """,
    rules=dict(methods=["clone"], lines=1),
    visible=[
        T("midpoints", "a = (0,0), b = (2,2), c = (4,0)", "two_midpoints(Point { x: 0, y: 0 }, Point { x: 2, y: 2 }, Point { x: 4, y: 0 })", "(Point { x: 1, y: 1 }, Point { x: 2, y: 0 })"),
        T("reuse_after_call", "a = (1, 1) used after passing by value", "{ let a = Point { x: 1, y: 1 }; let _ = midpoint(a, a); a }", "Point { x: 1, y: 1 }"),
    ],
    hidden=[
        T("negative", "a = (-2,-2), b = (2,2), c = (-2,2)", "two_midpoints(Point { x: -2, y: -2 }, Point { x: 2, y: 2 }, Point { x: -2, y: 2 })", "(Point { x: 0, y: 0 }, Point { x: -2, y: 0 })"),
    ],
    hints=[("rust", "Which derive lets a value be used again after it's passed by value? It needs a second derive alongside it.")],
    notes=("`Copy` needs `Clone` too, and every field must be `Copy`. Small plain-data types like points should be `Copy`; anything owning heap memory can't be.", "O(1)", "O(1)"),
    follow_up="Why can't a struct containing a `String` be `Copy`, and why is that a good thing?",
    related=["S8"],
))

P.append(dict(
    slug="fix-moved-in-loop", title="Fix: value moved in a loop", mode="fix", level="easy", stage="moves-and-copy", tags=["E0382", "&str"],
    teaches=["A value moved in the first iteration isn't there for the second.", "Borrow in helpers that only read."],
    statement="`greet_thrice` should push the same greeting three times. It doesn't compile.",
    starter="""
        /// Pushes "hello, <name>" into `out` three times.
        pub fn greet_thrice(name: String, out: &mut Vec<String>) {
            for _ in 0..3 {
                out.push(greeting(name));
            }
        }

        fn greeting(name: String) -> String {
            format!("hello, {name}")
        }
    """,
    solution="""
        /// Pushes "hello, <name>" into `out` three times.
        pub fn greet_thrice(name: String, out: &mut Vec<String>) {
            for _ in 0..3 {
                out.push(greeting(&name));
            }
        }

        fn greeting(name: &str) -> String {
            format!("hello, {name}")
        }
    """,
    rules=dict(methods=["clone"], lines=2),
    visible=[
        T("three", "name = \"ann\"", '{ let mut out = vec![]; greet_thrice("ann".into(), &mut out); out }', 'vec!["hello, ann"; 3]'),
        T("appends", "out already holds one line", '{ let mut out = vec!["hi".to_string()]; greet_thrice("bo".into(), &mut out); out.len() }', "4"),
    ],
    hidden=[
        T("empty_name", "name = \"\"", '{ let mut out = vec![]; greet_thrice(String::new(), &mut out); out[2].clone() }', '"hello, ".to_string()'),
    ],
    hints=[("rust", "`greeting` only reads the name. Does it need to own it?")],
    notes=("`greeting` only formats, so borrowing `&str` is the right signature; `&name` derefs from `&String`.", "O(n)", "O(n)"),
    follow_up="Why is `&str` a better parameter type than `&String`?",
    related=["L2", "S2"],
))

P.append(dict(
    slug="ownership-round-trip", title="Take ownership, give it back", level="easy", stage="moves-and-copy", tags=["ownership", "return values"],
    teaches=["A function can take a value, change it, and hand it back.", "Moving a `Vec` or `String` never copies the heap data."],
    statement="""
        Write `push_sum`, which appends the sum of `v` to it and returns it, and `swap_owned`, which
        returns its two strings in the other order. Neither may clone.
    """,
    starter="""
        pub fn push_sum(v: Vec<i64>) -> Vec<i64> {
            todo!()
        }

        pub fn swap_owned(a: String, b: String) -> (String, String) {
            todo!()
        }
    """,
    solution="""
        pub fn push_sum(mut v: Vec<i64>) -> Vec<i64> {
            let sum = v.iter().sum();
            v.push(sum);
            v
        }

        pub fn swap_owned(a: String, b: String) -> (String, String) {
            (b, a)
        }
    """,
    visible=[
        T("sum", "v = [1, 2, 3]", "push_sum(vec![1, 2, 3])", "vec![1, 2, 3, 6]"),
        T("swap", "a = \"x\", b = \"y\"", 'swap_owned("x".into(), "y".into())', '("y".to_string(), "x".to_string())'),
    ],
    hidden=[
        T("empty", "v = []", "push_sum(vec![])", "vec![0]"),
        T("same_buffer", "v with capacity 10", "{ let mut v = Vec::with_capacity(10); v.push(5); let p = v.as_ptr(); let out = push_sum(v); out.as_ptr() == p }", "true"),
    ],
    hints=[("rust", "Parameters can be declared `mut v: Vec<i64>` when you own them.")],
    notes=("The hidden test checks the buffer pointer: moving a `Vec` in and out keeps the same heap allocation.", "O(n)", "O(1) extra"),
    follow_up="When would you take `&mut Vec<i64>` instead of taking and returning it?",
    related=["S3"],
))

P.append(dict(
    slug="fix-parameter-types", title="Fix: by value, & or &mut", mode="fix", level="easy", stage="passing-values", tags=["&T", "&mut T", "API design"],
    teaches=["Take `&[T]` to read, `&mut [T]` to change in place, and `Vec<T>` to consume.", "The signature tells the caller what happens to their value."],
    statement="""
        The tests call `count_long`, then `shout_all`, then `into_sentence` on the same `words`. It doesn't
        compile, because every function takes `Vec<String>` by value. Give each the parameter type that fits what it does.
    """,
    starter="""
        /// How many words are at least `min` bytes long.
        pub fn count_long(words: Vec<String>, min: usize) -> usize {
            words.iter().filter(|w| w.len() >= min).count()
        }

        /// Uppercases every word in place.
        pub fn shout_all(mut words: Vec<String>) {
            for w in words.iter_mut() {
                w.make_ascii_uppercase();
            }
        }

        /// Joins the words with spaces.
        pub fn into_sentence(words: Vec<String>) -> String {
            words.join(" ")
        }
    """,
    solution="""
        /// How many words are at least `min` bytes long.
        pub fn count_long(words: &[String], min: usize) -> usize {
            words.iter().filter(|w| w.len() >= min).count()
        }

        /// Uppercases every word in place.
        pub fn shout_all(words: &mut [String]) {
            for w in words.iter_mut() {
                w.make_ascii_uppercase();
            }
        }

        /// Joins the words with spaces.
        pub fn into_sentence(words: Vec<String>) -> String {
            words.join(" ")
        }
    """,
    rules=dict(methods=["clone", "to_vec", "to_owned"]),
    visible=[
        """
        #[test]
        fn read_then_change_then_consume() {
            let mut words = vec!["hi".to_string(), "there".to_string()];
            let long = count_long(&words, 3);
            shout_all(&mut words);
            let sentence = into_sentence(words);
            check!("[\\"hi\\", \\"there\\"]", (long, sentence), (1, "HI THERE".to_string()));
        }
        """,
        T("count_only", "[\"a\", \"bbb\"], min = 2", '{ let w = vec!["a".to_string(), "bbb".to_string()]; count_long(&w, 2) }', "1"),
    ],
    hidden=[
        T("empty", "[]", "{ let mut w: Vec<String> = vec![]; shout_all(&mut w); into_sentence(w) }", "String::new()"),
    ],
    hints=[("approach", "Which of these only reads, which changes in place, and which consumes the words?")],
    notes=("`shout_all` taking the Vec by value uppercased a copy that was then dropped, a silent bug the new signature makes impossible.", "O(n)", "O(1)"),
    follow_up="Why `&mut [String]` instead of `&mut Vec<String>` for `shout_all`?",
    related=["L2", "S3"],
))

P.append(dict(
    slug="fix-borrowed-where-owned", title="Fix: borrowed where owned was needed", mode="fix", level="easy", stage="passing-values", tags=["E0308", "&str to String"],
    teaches=["A struct that owns its data needs a `String`, not a `&str`.", "`to_string`, `to_owned`, `String::from` and `into` all make the copy."],
    statement="`Tag::new` doesn't compile.",
    starter="""
        #[derive(Debug, PartialEq)]
        pub struct Tag {
            pub name: String,
        }

        impl Tag {
            pub fn new(name: &str) -> Tag {
                Tag { name }
            }
        }
    """,
    solution="""
        #[derive(Debug, PartialEq)]
        pub struct Tag {
            pub name: String,
        }

        impl Tag {
            pub fn new(name: &str) -> Tag {
                Tag { name: name.to_string() }
            }
        }
    """,
    rules=dict(lines=1),
    visible=[
        T("builds", "name = \"rust\"", 'Tag::new("rust")', 'Tag { name: "rust".to_string() }'),
        T("from_string", "name from a String", '{ let s = String::from("go"); Tag::new(&s).name }', '"go".to_string()'),
    ],
    hidden=[
        T("outlives_input", "tag kept after its input is dropped", '{ let t = { let s = String::from("tmp"); Tag::new(&s) }; t.name }', '"tmp".to_string()'),
    ],
    hints=[("rust", "The field is a `String`, the parameter a `&str`. Something has to make the owned copy.")],
    notes=("If the struct stored `&str` instead, it would need a lifetime and couldn't outlive its input, which the hidden test relies on.", "O(n)", "O(n)"),
    follow_up="When would you make the constructor take `impl Into<String>`?",
    related=["S2", "L3"],
))

P.append(dict(
    slug="str-parameters", title="&str parameters take both", level="easy", stage="passing-values", tags=["&str", "deref coercion"],
    teaches=["`&str` accepts literals and `&String` through deref coercion.", "Iterating words and taking the first char of each."],
    statement="Return the uppercase initials of `full_name`, e.g. `\"Ada Lovelace\"` → `\"AL\"`.",
    starter="""
        pub fn initials(full_name: &str) -> String {
            todo!()
        }
    """,
    solution="""
        pub fn initials(full_name: &str) -> String {
            full_name
                .split_whitespace()
                .filter_map(|w| w.chars().next())
                .flat_map(char::to_uppercase)
                .collect()
        }
    """,
    visible=[
        T("literal", "\"Ada Lovelace\"", 'initials("Ada Lovelace")', '"AL"'),
        T("from_string", "&String \"grace brewster hopper\"", '{ let s = String::from("grace brewster hopper"); initials(&s) }', '"GBH"'),
    ],
    hidden=[
        T("empty", "\"\"", 'initials("")', '""'),
        T("unicode", "\"élodie ünal\"", 'initials("élodie ünal")', '"ÉÜ"'),
    ],
    hints=[("rust", "`split_whitespace`, then the first `char` of each word, then uppercase."), ("rust", "`char::to_uppercase` returns an iterator, since some characters uppercase to more than one.")],
    notes=("Taking `&str` means callers never allocate to call you. `flat_map(char::to_uppercase)` handles characters whose uppercase form is longer.", "O(n)", "O(k)"),
    follow_up="When is `impl AsRef<str>` a better parameter than `&str`?",
    related=["S2"],
))

P.append(dict(
    slug="fix-needless-clones", title="Fix: remove every clone", mode="fix", level="medium", stage="clones-and-drops", tags=["borrowing", "clone", "lifetimes"],
    teaches=["Return borrowed data (`&str`, `Vec<&str>`) instead of cloning.", "Iterate by reference instead of cloning a collection to iterate it."],
    statement="""
        `Library` works, but clones its whole book list on every call. Remove every clone:
        `search` should return `Vec<&str>` and `longest` should return `Option<&str>`.
    """,
    starter="""
        pub struct Library {
            books: Vec<String>,
        }

        impl Library {
            pub fn new(books: Vec<String>) -> Self {
                Library { books }
            }

            /// Titles containing `needle`.
            pub fn search(&self, needle: &str) -> Vec<String> {
                self.books.clone().into_iter().filter(|b| b.contains(needle)).collect()
            }

            /// The longest title; the last one on a tie.
            pub fn longest(&self) -> Option<String> {
                let mut books = self.books.clone();
                books.sort_by_key(|b| b.len());
                books.last().cloned()
            }

            pub fn count_with(&self, needle: &str) -> usize {
                self.search(&needle.to_string()).len()
            }
        }
    """,
    solution="""
        pub struct Library {
            books: Vec<String>,
        }

        impl Library {
            pub fn new(books: Vec<String>) -> Self {
                Library { books }
            }

            /// Titles containing `needle`.
            pub fn search(&self, needle: &str) -> Vec<&str> {
                self.books.iter().filter(|b| b.contains(needle)).map(String::as_str).collect()
            }

            /// The longest title; the last one on a tie.
            pub fn longest(&self) -> Option<&str> {
                self.books.iter().max_by_key(|b| b.len()).map(String::as_str)
            }

            pub fn count_with(&self, needle: &str) -> usize {
                self.books.iter().filter(|b| b.contains(needle)).count()
            }
        }
    """,
    rules=dict(methods=["clone", "cloned", "to_string", "to_owned"]),
    visible=[
        T("search", "books = [\"Dune\", \"Dune Messiah\", \"Emma\"], needle = \"Dune\"", 'lib.search("Dune")', 'vec!["Dune", "Dune Messiah"]', setup='let lib = Library::new(vec!["Dune".into(), "Dune Messiah".into(), "Emma".into()]);'),
        T("longest", "books = [\"Dune\", \"Dune Messiah\", \"Emma\"]", "lib.longest()", 'Some("Dune Messiah")', setup='let lib = Library::new(vec!["Dune".into(), "Dune Messiah".into(), "Emma".into()]);'),
    ],
    hidden=[
        T("longest_tie_last", "books = [\"ab\", \"cd\"]", "lib.longest()", 'Some("cd")', setup='let lib = Library::new(vec!["ab".into(), "cd".into()]);'),
        T("count", "needle = \"e\"", 'Library::new(vec!["Dune".into(), "Emma".into(), "Tess".into()]).count_with("e")', "2"),
        T("empty", "no books", "lib.longest()", "None", setup="let lib = Library::new(vec![]);"),
    ],
    hints=[("approach", "Each method only reads the books. Can it return references into `self.books`?"),
           ("rust", "`iter().max_by_key(|b| b.len())` returns the last maximum, like sort-then-last.")],
    notes=("The returned `&str`s borrow `self`, so elision ties them to `&self`. No method allocates now except `search`'s result Vec.", "O(n)", "O(k)"),
    follow_up="When is returning owned data the right call even though it costs a clone?",
    related=["L3", "S1"],
))

P.append(dict(
    slug="cow-normalizer", title="Allocate only when you must: Cow", level="medium", stage="clones-and-drops", tags=["Cow", "borrow or own"],
    source="W39",
    teaches=["`Cow<'_, str>` returns the input borrowed when nothing changed, owned when it did.", "Checking before allocating."],
    statement="Replace each tab in `s` with four spaces. When `s` has no tabs, return it without allocating.",
    starter="""
        use std::borrow::Cow;

        pub fn normalize(s: &str) -> Cow<'_, str> {
            todo!()
        }
    """,
    solution="""
        use std::borrow::Cow;

        pub fn normalize(s: &str) -> Cow<'_, str> {
            if s.contains('\\t') {
                Cow::Owned(s.replace('\\t', "    "))
            } else {
                Cow::Borrowed(s)
            }
        }
    """,
    visible=[
        T("tabs", "\"a\\tb\"", 'normalize("a\\tb")', '"a    b"'),
        T("no_tabs_borrowed", "\"plain\"", 'matches!(normalize("plain"), std::borrow::Cow::Borrowed("plain"))', "true"),
    ],
    hidden=[
        T("tabs_owned", "\"\\t\"", 'matches!(normalize("\\t"), std::borrow::Cow::Owned(_))', "true"),
        T("empty", "\"\"", 'normalize("")', '""'),
    ],
    hints=[("rust", "`Cow::Borrowed(s)` costs nothing; `Cow::Owned(String)` when you had to change it.")],
    notes=("Most inputs have no tabs, so most calls allocate nothing. `Cow<str>` derefs to `&str`, so callers barely notice the difference.", "O(n)", "O(n) only when changed"),
    follow_up="Where does std itself return `Cow`?",
    related=["S2", "S7"],
))

P.append(dict(
    slug="predict-drop-order", title="Predict the drop order", level="medium", stage="clones-and-drops", tags=["Drop", "scopes"],
    teaches=["Locals drop in reverse order of declaration; struct fields in declaration order.", "`let _ = expr;` drops a temporary immediately, and `let _ = x;` doesn't move `x`."],
    statement="""
        Read `scene` without running it. Fill `PREDICTED` with the names in the order they're dropped.
        Don't change `scene`.
    """,
    starter="""
        use std::cell::RefCell;

        pub struct Noisy<'a> {
            pub name: &'static str,
            pub log: &'a RefCell<Vec<&'static str>>,
        }

        impl Drop for Noisy<'_> {
            fn drop(&mut self) {
                self.log.borrow_mut().push(self.name);
            }
        }

        pub struct Pair<'a> {
            pub first: Noisy<'a>,
            pub second: Noisy<'a>,
        }

        /// Don't change this function.
        pub fn scene(log: &RefCell<Vec<&'static str>>) {
            let a = Noisy { name: "a", log };
            let _pair = Pair { first: Noisy { name: "first", log }, second: Noisy { name: "second", log } };
            let _ = Noisy { name: "ignored", log };
            let b = Noisy { name: "b", log };
            drop(a);
            let _c = Noisy { name: "c", log };
            let _ = b;
        }

        /// The names in the order `scene` drops them.
        pub const PREDICTED: [&str; 6] = ["?", "?", "?", "?", "?", "?"];
    """,
    solution="""
        use std::cell::RefCell;

        pub struct Noisy<'a> {
            pub name: &'static str,
            pub log: &'a RefCell<Vec<&'static str>>,
        }

        impl Drop for Noisy<'_> {
            fn drop(&mut self) {
                self.log.borrow_mut().push(self.name);
            }
        }

        pub struct Pair<'a> {
            pub first: Noisy<'a>,
            pub second: Noisy<'a>,
        }

        /// Don't change this function.
        pub fn scene(log: &RefCell<Vec<&'static str>>) {
            let a = Noisy { name: "a", log };
            let _pair = Pair { first: Noisy { name: "first", log }, second: Noisy { name: "second", log } };
            let _ = Noisy { name: "ignored", log };
            let b = Noisy { name: "b", log };
            drop(a);
            let _c = Noisy { name: "c", log };
            let _ = b;
        }

        /// The names in the order `scene` drops them.
        /// `let _ = Noisy {..}` drops at once; `drop(a)` next; then locals in reverse:
        /// `_c`, `b` (`let _ = b` didn't move it), then `_pair`, whose fields drop in order.
        pub const PREDICTED: [&str; 6] = ["ignored", "a", "c", "b", "first", "second"];
    """,
    visible=[
        """
        use std::cell::RefCell;

        #[test]
        fn prediction_matches_the_run() {
            let log = RefCell::new(Vec::new());
            scene(&log);
            check!("scene()", PREDICTED.to_vec(), log.into_inner());
        }
        """,
        T("six_names", "PREDICTED", "PREDICTED.iter().filter(|n| **n != \"?\").count()", "6"),
    ],
    hidden=[
        """
        use std::cell::RefCell;

        #[test]
        fn ignored_drops_first() {
            let log = RefCell::new(Vec::new());
            scene(&log);
            check!("first drop in scene()", PREDICTED[0], log.borrow()[0]);
        }
        """,
    ],
    hints=[("rust", "`let _ = value;` binds nothing. What happens to a temporary nobody owns?"),
           ("rust", "`let _ = b;` doesn't move `b`: `_` isn't a binding."),
           ("rust", "Local variables drop in reverse order of declaration; a struct's fields drop in the order they're declared.")],
    notes=("The two `let _` lines are the usual traps: the first drops a temporary immediately, the second does nothing at all.", "—", "—"),
    follow_up="Why does `let _guard = mutex.lock()` hold the lock while `let _ = mutex.lock()` releases it at once?",
    related=["S8", "C1"],
))

P.append(dict(
    slug="raii-span-guard", title="An RAII span guard", level="medium", stage="clones-and-drops", tags=["Drop", "RAII", "unwinding"],
    teaches=["RAII: acquire in a constructor, release in `Drop`.", "`Drop` runs on early return and during a panic too."],
    statement="""
        `Span::enter(name, log)` records `"enter <name>"`, and dropping the span records `"exit <name>"`.
        Exits must happen on every path: normal end of scope, early return, and panic.
    """,
    starter="""
        use std::cell::RefCell;

        pub struct Span<'a> {
            name: &'static str,
            log: &'a RefCell<Vec<String>>,
        }

        impl<'a> Span<'a> {
            pub fn enter(name: &'static str, log: &'a RefCell<Vec<String>>) -> Self {
                todo!()
            }
        }

        impl Drop for Span<'_> {
            fn drop(&mut self) {
                // TODO: record the exit.
                // (Left empty rather than todo!(): a panic in drop during a failing test aborts every test.)
            }
        }
    """,
    solution="""
        use std::cell::RefCell;

        pub struct Span<'a> {
            name: &'static str,
            log: &'a RefCell<Vec<String>>,
        }

        impl<'a> Span<'a> {
            pub fn enter(name: &'static str, log: &'a RefCell<Vec<String>>) -> Self {
                log.borrow_mut().push(format!("enter {name}"));
                Span { name, log }
            }
        }

        impl Drop for Span<'_> {
            fn drop(&mut self) {
                self.log.borrow_mut().push(format!("exit {}", self.name));
            }
        }
    """,
    visible=[
        """
        use std::cell::RefCell;

        #[test]
        fn nested_spans_exit_in_reverse() {
            let log = RefCell::new(Vec::new());
            {
                let _outer = Span::enter("outer", &log);
                let _inner = Span::enter("inner", &log);
            }
            check!("outer, then inner", log.into_inner(), vec!["enter outer", "enter inner", "exit inner", "exit outer"]);
        }

        fn early(log: &RefCell<Vec<String>>, bail: bool) -> u8 {
            let _s = Span::enter("work", log);
            if bail {
                return 0;
            }
            1
        }

        #[test]
        fn early_return_still_exits() {
            let log = RefCell::new(Vec::new());
            early(&log, true);
            check!("return before the end of the function", log.into_inner(), vec!["enter work", "exit work"]);
        }
        """,
    ],
    hidden=[
        """
        use std::cell::RefCell;
        use std::panic::{AssertUnwindSafe, catch_unwind};

        #[test]
        fn panic_still_exits() {
            let log = RefCell::new(Vec::new());
            let _ = catch_unwind(AssertUnwindSafe(|| {
                let _s = Span::enter("risky", &log);
                panic!("boom");
            }));
            check!("a panic inside the span", log.into_inner(), vec!["enter risky", "exit risky"]);
        }
        """,
    ],
    hints=[("rust", "Record the enter in `enter` and the exit in `drop`; the compiler inserts the drop on every exit path.")],
    notes=("Unwinding runs destructors, so the exit is recorded even when the code inside panics. This is how `MutexGuard`, `File` and tracing spans work.", "O(1)", "O(1)"),
    follow_up="What happens to your guard if someone calls `std::mem::forget` on it?",
    related=["C1", "B6"],
))

P.append(dict(
    slug="fix-closure-may-outlive", title="Fix: closure may outlive the function", mode="fix", level="medium", stage="closures-take-ownership", tags=["E0373", "move"],
    teaches=["A returned closure can't borrow a local: the local dies with the function.", "`move` makes the closure own what it captures."],
    statement="`counter(start)` should return a closure that counts up from `start`. It doesn't compile.",
    starter="""
        /// Each call returns the next number after `start`.
        pub fn counter(start: u32) -> impl FnMut() -> u32 {
            let mut n = start;
            || {
                n += 1;
                n
            }
        }
    """,
    solution="""
        /// Each call returns the next number after `start`.
        pub fn counter(start: u32) -> impl FnMut() -> u32 {
            let mut n = start;
            move || {
                n += 1;
                n
            }
        }
    """,
    rules=dict(lines=1),
    visible=[
        T("counts", "start = 10", "{ let mut c = counter(10); (c(), c(), c()) }", "(11, 12, 13)"),
        T("independent", "two counters from 0", "{ let mut a = counter(0); let mut b = counter(0); a(); a(); b() }", "1"),
    ],
    hidden=[
        T("hundred_calls", "start = 0, 100 calls", "{ let mut c = counter(0); (0..100).map(|_| c()).last() }", "Some(100)"),
    ],
    hints=[("rust", "`n` lives on `counter`'s stack. The closure outlives that frame. How does it keep `n`?")],
    notes=("`move` copies `n` into the closure, which then owns its own counter. Each call mutates that copy, hence `FnMut`.", "O(1)", "O(1)"),
    follow_up="Why is this closure `FnMut` and not `Fn`?",
    related=["L6"],
))

P.append(dict(
    slug="move-into-threads", title="Move data into threads", level="medium", stage="closures-take-ownership", tags=["thread::spawn", "move", "'static"],
    teaches=["`thread::spawn` needs a `'static` closure: move the data in.", "`JoinHandle::join` returns the thread's result."],
    statement="Sum each chunk on its own thread and return the total.",
    starter="""
        pub fn parallel_sum(chunks: Vec<Vec<u64>>) -> u64 {
            todo!()
        }
    """,
    solution="""
        use std::thread;

        pub fn parallel_sum(chunks: Vec<Vec<u64>>) -> u64 {
            let handles: Vec<_> = chunks
                .into_iter()
                .map(|chunk| thread::spawn(move || chunk.iter().sum::<u64>()))
                .collect();
            handles.into_iter().map(|h| h.join().expect("worker panicked")).sum()
        }
    """,
    visible=[
        T("three_chunks", "[[1, 2], [3], [4, 5, 6]]", "parallel_sum(vec![vec![1, 2], vec![3], vec![4, 5, 6]])", "21"),
        T("empty", "[]", "parallel_sum(vec![])", "0"),
    ],
    hidden=[
        T("many", "8 chunks of 0..1000", "parallel_sum((0..8).map(|_| (0..1000).collect()).collect())", "8 * 499_500"),
    ],
    hints=[("rust", "`move ||` moves each chunk into its thread; collect the handles before joining so the threads run concurrently.")],
    notes=("Collecting the handles first matters: joining inside the same `map` would run the threads one after another.", "O(n) work", "O(k) threads"),
    follow_up="How would `std::thread::scope` let the threads borrow the chunks instead?",
    related=["C1"],
))

P.append(dict(
    slug="fix-moved-into-closure-in-loop", title="Fix: moved into a closure in a loop", mode="fix", level="medium", stage="closures-take-ownership", tags=["E0382", "Arc", "move"],
    teaches=["A `move` closure in a loop moves the value on the first iteration.", "Share read-only data across threads with `Arc` and `Arc::clone`."],
    statement="Every thread should sum the same data. It doesn't compile. Don't copy the data per thread.",
    starter="""
        use std::thread;

        /// `n` threads each sum `data`; returns every thread's result.
        pub fn sum_everywhere(data: Vec<u64>, n: usize) -> Vec<u64> {
            let mut handles = Vec::new();
            for _ in 0..n {
                handles.push(thread::spawn(move || data.iter().sum::<u64>()));
            }
            handles.into_iter().map(|h| h.join().expect("worker panicked")).collect()
        }
    """,
    solution="""
        use std::sync::Arc;
        use std::thread;

        /// `n` threads each sum `data`; returns every thread's result.
        pub fn sum_everywhere(data: Vec<u64>, n: usize) -> Vec<u64> {
            let data = Arc::new(data);
            let mut handles = Vec::new();
            for _ in 0..n {
                let data = Arc::clone(&data);
                handles.push(thread::spawn(move || data.iter().sum::<u64>()));
            }
            handles.into_iter().map(|h| h.join().expect("worker panicked")).collect()
        }
    """,
    rules=dict(methods=["clone", "to_vec", "to_owned"]),
    visible=[
        T("three_threads", "data = [1, 2, 3], n = 3", "sum_everywhere(vec![1, 2, 3], 3)", "vec![6, 6, 6]"),
        T("no_threads", "n = 0", "sum_everywhere(vec![1], 0)", "Vec::<u64>::new()"),
    ],
    hidden=[
        T("big", "data = 0..10000, n = 4", "sum_everywhere((0..10_000).collect(), 4)", "vec![49_995_000; 4]"),
    ],
    hints=[("rust", "The first iteration's `move` takes `data`. What can each thread own that still points at one shared Vec?"),
           ("rust", "`Arc::clone(&data)` copies a pointer and bumps a count; the Vec itself isn't copied.")],
    notes=("`Arc::clone` is written as a path call on purpose: it reads as \"another handle\", not \"another copy of the data\".", "O(n · threads)", "O(n) once"),
    follow_up="When would you use `thread::scope` instead of `Arc` here?",
    related=["S7", "C1"],
))

P.append(dict(
    slug="fix-move-out-of-index", title="Fix: move out of an index", mode="fix", level="hard", stage="partial-moves-and-mem", tags=["E0507", "mem::take"],
    teaches=["You can't move a value out of a `Vec` by indexing: it would leave a hole.", "`mem::take` swaps in `Default` and hands you the value."],
    statement="`take_first` should move the first name out and leave an empty string in its place. It doesn't compile. `names` is never empty.",
    starter="""
        /// Moves the first name out, leaving "" in its place.
        pub fn take_first(names: &mut Vec<String>) -> String {
            let first = names[0];
            first
        }
    """,
    solution="""
        /// Moves the first name out, leaving "" in its place.
        pub fn take_first(names: &mut Vec<String>) -> String {
            std::mem::take(&mut names[0])
        }
    """,
    rules=dict(methods=["clone", "to_string", "to_owned"], lines=2),
    visible=[
        T("takes", "names = [\"ann\", \"bo\"]", '{ let mut v = vec!["ann".to_string(), "bo".to_string()]; let f = take_first(&mut v); (f, v) }', '("ann".to_string(), vec![String::new(), "bo".to_string()])'),
        T("single", "names = [\"x\"]", '{ let mut v = vec!["x".to_string()]; take_first(&mut v) }', '"x".to_string()'),
    ],
    hidden=[
        T("keeps_length", "names = [\"a\", \"b\", \"c\"]", '{ let mut v = vec!["a".to_string(), "b".to_string(), "c".to_string()]; take_first(&mut v); v.len() }', "3"),
    ],
    hints=[("rust", "Moving out of `names[0]` would leave the Vec with an invalid slot. What could you swap in?"),
           ("rust", "`String` has a cheap `Default`: the empty string, with no allocation.")],
    notes=("`mem::take(&mut x)` is `mem::replace(&mut x, Default::default())`. The Vec stays valid throughout.", "O(1)", "O(1)"),
    follow_up="When would you use `swap_remove` or `remove` instead?",
    related=["S11", "S3"],
))

P.append(dict(
    slug="mem-replace-state", title="State transitions with mem::replace", level="hard", stage="partial-moves-and-mem", tags=["mem::replace", "enum"],
    teaches=["Moving data out of `&mut self` enum variants with `mem::replace`.", "A placeholder that costs nothing, like `String::new()`."],
    statement="""
        Advance a job one step: `Queued(name)` → `Running(name)` → `Done(name)`. `Done` stays `Done`.
        Keep the name without cloning it.
    """,
    starter="""
        #[derive(Debug, PartialEq)]
        pub enum Job {
            Queued(String),
            Running(String),
            Done(String),
        }

        pub fn advance(job: &mut Job) {
            todo!()
        }
    """,
    solution="""
        #[derive(Debug, PartialEq)]
        pub enum Job {
            Queued(String),
            Running(String),
            Done(String),
        }

        pub fn advance(job: &mut Job) {
            // Take the job out, leaving a placeholder that doesn't allocate, then write the next state.
            *job = match std::mem::replace(job, Job::Done(String::new())) {
                Job::Queued(name) => Job::Running(name),
                Job::Running(name) => Job::Done(name),
                done => done,
            };
        }
    """,
    visible=[
        T("queued_to_running", "Queued(\"build\")", '{ let mut j = Job::Queued("build".into()); advance(&mut j); j }', 'Job::Running("build".into())'),
        T("running_to_done", "Running(\"build\")", '{ let mut j = Job::Running("build".into()); advance(&mut j); j }', 'Job::Done("build".into())'),
    ],
    hidden=[
        T("done_stays", "Done(\"x\")", '{ let mut j = Job::Done("x".into()); advance(&mut j); j }', 'Job::Done("x".into())'),
        T("same_buffer", "name's heap buffer kept", '{ let mut j = Job::Queued(String::from("keep")); let p = match &j { Job::Queued(s) => s.as_ptr(), _ => unreachable!() }; advance(&mut j); match &j { Job::Running(s) => s.as_ptr() == p, _ => false } }', "true"),
    ],
    hints=[("rust", "You can't move `name` out of `*job` through a `&mut`. Replace the whole value first, then match on what you got back.")],
    notes=("The hidden test checks the String's buffer pointer: the name moves between variants without being copied.", "O(1)", "O(1)"),
    follow_up="How would you model this as a typestate (`Job<Queued>`, `Job<Running>`) instead?",
    related=["L7", "L5"],
))

P.append(dict(
    slug="option-take-batcher", title="A batcher with Option::take", level="hard", stage="partial-moves-and-mem", tags=["Option::take", "get_or_insert_with"],
    teaches=["`Option::take` moves the value out and leaves `None`.", "`get_or_insert_with` creates the value lazily."],
    statement="""
        `Batcher::new(size)` groups pushed values into batches. `push` returns a full batch when one
        completes; `flush` returns whatever is left, or `None` if nothing is.
    """,
    starter="""
        pub struct Batcher {
            current: Option<Vec<u32>>,
            size: usize,
        }

        impl Batcher {
            pub fn new(size: usize) -> Self {
                todo!()
            }

            pub fn push(&mut self, value: u32) -> Option<Vec<u32>> {
                todo!()
            }

            pub fn flush(&mut self) -> Option<Vec<u32>> {
                todo!()
            }
        }
    """,
    solution="""
        pub struct Batcher {
            current: Option<Vec<u32>>,
            size: usize,
        }

        impl Batcher {
            pub fn new(size: usize) -> Self {
                assert!(size > 0, "batch size must be at least 1");
                Batcher { current: None, size }
            }

            pub fn push(&mut self, value: u32) -> Option<Vec<u32>> {
                let batch = self.current.get_or_insert_with(|| Vec::with_capacity(self.size));
                batch.push(value);
                if batch.len() == self.size {
                    self.current.take()
                } else {
                    None
                }
            }

            pub fn flush(&mut self) -> Option<Vec<u32>> {
                self.current.take()
            }
        }
    """,
    visible=[
        T("fills", "size 2, push 1, 2, 3", "{ let mut b = Batcher::new(2); (b.push(1), b.push(2), b.push(3)) }", "(None, Some(vec![1, 2]), None)"),
        T("flush_rest", "size 3, push 7, flush twice", "{ let mut b = Batcher::new(3); b.push(7); (b.flush(), b.flush()) }", "(Some(vec![7]), None)"),
    ],
    hidden=[
        T("size_one", "size 1", "{ let mut b = Batcher::new(1); (b.push(5), b.flush()) }", "(Some(vec![5]), None)"),
        T("flush_empty", "nothing pushed", "Batcher::new(4).flush()", "None"),
    ],
    hints=[("rust", "`get_or_insert_with` gives you `&mut Vec<u32>`, creating it on first use."), ("rust", "When the batch is full, `take()` hands it back and resets `current` to `None`.")],
    notes=("`self.size` is read inside the closure while `self.current` is borrowed mutably; that works because the closure borrows a different field (disjoint captures in edition 2021).", "O(1) amortised", "O(size)"),
    follow_up="How would you add a time-based flush, and what would it need from the caller?",
    related=["S1", "C2"],
))

P.append(dict(
    slug="rollback-guard", title="Roll back on panic with a guard", level="hard", stage="partial-moves-and-mem", tags=["Drop", "panic safety", "guards"],
    teaches=["A guard armed before the risky work and disarmed after it.", "Panic safety: leave data in a valid state however a function exits."],
    statement="""
        `with_rollback(v, f)` lets `f` push to `v`. If `f` panics, `v` must be truncated back to its
        original length before the panic continues; if `f` returns normally, its pushes stay.
    """,
    starter="""
        pub fn with_rollback(v: &mut Vec<i32>, f: impl FnOnce(&mut Vec<i32>)) {
            todo!()
        }
    """,
    solution="""
        pub fn with_rollback(v: &mut Vec<i32>, f: impl FnOnce(&mut Vec<i32>)) {
            struct Guard<'a> {
                v: &'a mut Vec<i32>,
                len: usize,
                armed: bool,
            }

            impl Drop for Guard<'_> {
                fn drop(&mut self) {
                    if self.armed {
                        self.v.truncate(self.len);
                    }
                }
            }

            let len = v.len();
            let mut guard = Guard { v, len, armed: true };
            f(guard.v);
            // Reached only if `f` returned: keep its pushes.
            guard.armed = false;
        }
    """,
    visible=[
        """
        use std::panic::{AssertUnwindSafe, catch_unwind};

        #[test]
        fn panic_rolls_back() {
            let mut v = vec![1];
            let r = catch_unwind(AssertUnwindSafe(|| {
                with_rollback(&mut v, |v| {
                    v.push(2);
                    v.push(3);
                    panic!("boom");
                })
            }));
            check!("f pushes 2 and 3, then panics", (r.is_err(), v), (true, vec![1]));
        }

        #[test]
        fn success_keeps_pushes() {
            let mut v = vec![1];
            with_rollback(&mut v, |v| v.push(2));
            check!("f pushes 2 and returns", v, vec![1, 2]);
        }
        """,
    ],
    hidden=[
        """
        use std::panic::{AssertUnwindSafe, catch_unwind};

        #[test]
        fn nested_rollbacks() {
            let mut v = vec![];
            with_rollback(&mut v, |v| {
                v.push(1);
                let _ = catch_unwind(AssertUnwindSafe(|| with_rollback(v, |v| {
                    v.push(2);
                    panic!("inner");
                })));
                v.push(3);
            });
            check!("outer keeps 1 and 3; inner rolls back 2", v, vec![1, 3]);
        }
        """,
    ],
    hints=[("approach", "Remember the length. What runs whether `f` returns or panics?"),
           ("rust", "A local struct with a `Drop` impl and an `armed` flag: disarm it only after `f` returns.")],
    notes=("Unwinding drops `guard`, which truncates. On success the flag is cleared first, so the drop does nothing. std uses the same pattern inside `Vec::retain` and sort.", "O(1) plus the truncate", "O(1)"),
    follow_up="Why would `mem::forget` on this guard be harmless, but on some other guards be a soundness bug?",
    related=["S3", "Y2"],
))

STAGES = [
    ("moves-and-copy", "Moves & Copy", "easy"),
    ("passing-values", "Passing values", "easy"),
    ("clones-and-drops", "Clones & drops", "medium"),
    ("closures-take-ownership", "Closures take ownership", "medium"),
    ("partial-moves-and-mem", "Partial moves & mem", "hard"),
]

if __name__ == "__main__":
    n = write_track("l1-ownership-moves", "L1", "Ownership & moves", "L", "core", 1,
                    "Every value has one owner. Moves, copies, clones, drops and the `mem` functions that move data out of places you only borrow.",
                    STAGES, P)
    print("L1", n)
