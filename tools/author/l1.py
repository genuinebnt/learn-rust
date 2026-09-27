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
        T("single_word", "text = \"rust\"", 'summarize("rust")', '(1, "rust".to_string())'),
        T("tie_first_wins", "text = \"cat dog\"", 'summarize("cat dog")', '(2, "cat".to_string())'),
        T("extra_spaces", "text = \"  a  bb \"", 'summarize("  a  bb ")', '(2, "bb".to_string())'),
    ],
    hidden=[
        T("tie_keeps_first", "text = \"ab cd\"", 'summarize("ab cd")', '(2, "ab".to_string())'),
        T("three_way_tie", "text = \"aa bb cc\"", 'summarize("aa bb cc")', '(3, "aa".to_string())'),
        T("longest_last", "text = \"a bb ccc\"", 'summarize("a bb ccc")', '(3, "ccc".to_string())'),
        T("runs_of_spaces", "text = \"a   bb  c\"", 'summarize("a   bb  c")', '(3, "bb".to_string())'),
        T("leading_trailing", "text = \"  hi  \"", 'summarize("  hi  ")', '(1, "hi".to_string())'),
        T("tabs_and_newlines", "text = \"one\\ttwo\\nthree\"", 'summarize("one\\ttwo\\nthree")', '(3, "three".to_string())'),
        T("only_whitespace", "text = \"   \"", 'summarize("   ")', '(0, String::new())'),
        T("unicode_bytes", "text = \"ab ünï\" (\"ünï\" is 5 bytes)", 'summarize("ab ünï")', '(2, "ünï".to_string())'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1101);
            for _ in 0..300 {
                let n = rng.below(24);
                let text = rng.string(n, "ab  \\t\\n");
                let words: Vec<&str> = text.split_whitespace().collect();
                let mut best = "";
                for w in &words {
                    if w.len() > best.len() {
                        best = w;
                    }
                }
                check!(format!("text = {text:?}"), summarize(&text), (words.len(), best.to_string()));
            }
        }

        #[test]
        fn many_words() {
            let text = "ab ".repeat(100_000) + "abc";
            check!("text = \\"ab ab … ab abc\\" (100001 words)", summarize(&text), (100_001, "abc".to_string()));
        }
        """,
    ],
    wrong=dict(
        split_on_space="""
            /// The number of words and the longest word, e.g. "the quick fox" → (3, "quick").
            pub fn summarize(text: &str) -> (usize, String) {
                let words: Vec<String> = text.split_whitespace().map(String::from).collect();
                let count = text.split(' ').count();
                let longest = longest_word(words);
                (count, longest)
            }

            fn longest_word(words: Vec<String>) -> String {
                words.into_iter().fold(String::new(), |best, w| if w.len() > best.len() { w } else { best })
            }
        """,
        spaces_plus_one="""
            /// The number of words and the longest word, e.g. "the quick fox" → (3, "quick").
            pub fn summarize(text: &str) -> (usize, String) {
                let words: Vec<String> = text.split_whitespace().map(String::from).collect();
                let count = text.matches(' ').count() + 1;
                let longest = longest_word(words);
                (count, longest)
            }

            fn longest_word(words: Vec<String>) -> String {
                words.into_iter().fold(String::new(), |best, w| if w.len() > best.len() { w } else { best })
            }
        """,
    ),
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
        T("all_same", "a = b = c = (3, 5)", "two_midpoints(Point { x: 3, y: 5 }, Point { x: 3, y: 5 }, Point { x: 3, y: 5 })", "(Point { x: 3, y: 5 }, Point { x: 3, y: 5 })"),
        T("odd_sums_truncate", "a = (0, 0), b = (1, 3), c = (-1, -3)", "two_midpoints(Point { x: 0, y: 0 }, Point { x: 1, y: 3 }, Point { x: -1, y: -3 })", "(Point { x: 0, y: 1 }, Point { x: 0, y: -1 })"),
        T("b_usable_after", "b used again after two_midpoints", "{ let b = Point { x: 2, y: 2 }; let _ = two_midpoints(Point { x: 0, y: 0 }, b, Point { x: 4, y: 4 }); b }", "Point { x: 2, y: 2 }"),
    ],
    hidden=[
        T("negative", "a = (-2,-2), b = (2,2), c = (-2,2)", "two_midpoints(Point { x: -2, y: -2 }, Point { x: 2, y: 2 }, Point { x: -2, y: 2 })", "(Point { x: 0, y: 0 }, Point { x: -2, y: 0 })"),
        T("a_not_at_origin", "a = (4, 6), b = (0, 0), c = (8, 2)", "two_midpoints(Point { x: 4, y: 6 }, Point { x: 0, y: 0 }, Point { x: 8, y: 2 })", "(Point { x: 2, y: 3 }, Point { x: 6, y: 4 })"),
        T("rounds_toward_zero", "a = (-3, -3), b = (0, 0), c = (0, 1)", "two_midpoints(Point { x: -3, y: -3 }, Point { x: 0, y: 0 }, Point { x: 0, y: 1 })", "(Point { x: -1, y: -1 }, Point { x: -1, y: -1 })"),
        T("odd_sums", "a = (1, 1), b = (2, 2), c = (4, 5)", "two_midpoints(Point { x: 1, y: 1 }, Point { x: 2, y: 2 }, Point { x: 4, y: 5 })", "(Point { x: 1, y: 1 }, Point { x: 2, y: 3 })"),
        T("order_of_results", "a = (0, 0), b = (10, 0), c = (0, 10)", "two_midpoints(Point { x: 0, y: 0 }, Point { x: 10, y: 0 }, Point { x: 0, y: 10 })", "(Point { x: 5, y: 0 }, Point { x: 0, y: 5 })"),
        T("big_coordinates", "a = (5·10⁸, -5·10⁸), b = (5·10⁸, 5·10⁸), c = (-5·10⁸, -5·10⁸)", "two_midpoints(Point { x: 500_000_000, y: -500_000_000 }, Point { x: 500_000_000, y: 500_000_000 }, Point { x: -500_000_000, y: -500_000_000 })", "(Point { x: 500_000_000, y: 0 }, Point { x: 0, y: -500_000_000 })"),
        T("all_three_usable_after", "a, b, c used again after two_midpoints", "{ let (a, b, c) = (Point { x: 1, y: 2 }, Point { x: 3, y: 4 }, Point { x: 5, y: 6 }); let _ = two_midpoints(a, b, c); (a, b, c) }", "(Point { x: 1, y: 2 }, Point { x: 3, y: 4 }, Point { x: 5, y: 6 })"),
        """
        fn is_copy<T: Copy>(_: &T) -> bool {
            true
        }

        #[test]
        fn point_is_copy() {
            check!("Point: Copy", is_copy(&Point { x: 0, y: 0 }), true);
        }

        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1102);
            for _ in 0..300 {
                let v: Vec<i32> = rng.vec(6, -1000, 1000);
                let (a, b, c) = (Point { x: v[0], y: v[1] }, Point { x: v[2], y: v[3] }, Point { x: v[4], y: v[5] });
                let want = (Point { x: (v[0] + v[2]) / 2, y: (v[1] + v[3]) / 2 }, Point { x: (v[0] + v[4]) / 2, y: (v[1] + v[5]) / 2 });
                check!(format!("a = {a:?}, b = {b:?}, c = {c:?}"), two_midpoints(a, b, c), want);
            }
        }
        """,
    ],
    wrong=dict(
        # Two changed lines, so it also breaks the line limit; with only one line there's no compiling wrong fix.
        origin_for_a="""
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
                (midpoint(a, b), midpoint(Point { x: 0, y: 0 }, c))
            }
        """,
    ),
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
        T("unicode_name", "name = \"zoë\"", '{ let mut out = vec![]; greet_thrice("zoë".into(), &mut out); out }', 'vec!["hello, zoë"; 3]'),
        T("empty_name_visible", "name = \"\"", '{ let mut out = vec![]; greet_thrice(String::new(), &mut out); out }', 'vec!["hello, "; 3]'),
        T("existing_line_kept", "out = [\"x\"], name = \"kim\"", '{ let mut out = vec!["x".to_string()]; greet_thrice("kim".into(), &mut out); out }', 'vec!["x", "hello, kim", "hello, kim", "hello, kim"]'),
    ],
    hidden=[
        T("empty_name", "name = \"\"", '{ let mut out = vec![]; greet_thrice(String::new(), &mut out); out[2].clone() }', '"hello, ".to_string()'),
        T("empty_name_all_three", "name = \"\"", '{ let mut out = vec![]; greet_thrice(String::new(), &mut out); out }', 'vec!["hello, "; 3]'),
        T("keeps_existing_first", "out = [\"hi\"], name = \"bo\"", '{ let mut out = vec!["hi".to_string()]; greet_thrice("bo".into(), &mut out); out }', 'vec!["hi", "hello, bo", "hello, bo", "hello, bo"]'),
        T("third_is_full", "name = \"ann\", the last push", '{ let mut out = vec![]; greet_thrice("ann".into(), &mut out); out[2].clone() }', '"hello, ann".to_string()'),
        T("name_with_spaces", "name = \"ann lee\"", '{ let mut out = vec![]; greet_thrice("ann lee".into(), &mut out); out }', 'vec!["hello, ann lee"; 3]'),
        T("called_twice", "greet_thrice(\"a\"), then greet_thrice(\"b\")", '{ let mut out = vec![]; greet_thrice("a".into(), &mut out); greet_thrice("b".into(), &mut out); out }', 'vec!["hello, a", "hello, a", "hello, a", "hello, b", "hello, b", "hello, b"]'),
        T("independent_strings", "change out[0] afterwards", '{ let mut out = vec![]; greet_thrice("x".into(), &mut out); out[0].push(\'!\'); out }', 'vec!["hello, x!", "hello, x", "hello, x"]'),
        T("long_name", "name = 10000 × 'n'", '{ let mut out = vec![]; greet_thrice("n".repeat(10_000), &mut out); out.iter().map(|s| s.len()).collect::<Vec<_>>() }', "vec![10_007; 3]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1103);
            for _ in 0..300 {
                let before = rng.below(4);
                let len = rng.below(8);
                let name = rng.string(len, "abé ");
                let mut out: Vec<String> = (0..before).map(|i| format!("old {i}")).collect();
                let mut want = out.clone();
                for _ in 0..3 {
                    want.push(format!("hello, {name}"));
                }
                greet_thrice(name.clone(), &mut out);
                check!(format!("name = {name:?}, out had {before} lines"), out, want);
            }
        }
        """,
    ],
    wrong=dict(
        take_the_name="""
            /// Pushes "hello, <name>" into `out` three times.
            pub fn greet_thrice(mut name: String, out: &mut Vec<String>) {
                for _ in 0..3 {
                    out.push(greeting(std::mem::take(&mut name)));
                }
            }

            fn greeting(name: String) -> String {
                format!("hello, {name}")
            }
        """,
    ),
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
        T("swap_empty", "a = \"\", b = \"z\"", 'swap_owned(String::new(), "z".into())', '("z".to_string(), String::new())'),
        T("sum_of_one", "v = [4]", "push_sum(vec![4])", "vec![4, 4]"),
        T("sum_negative", "v = [-1, -2]", "push_sum(vec![-1, -2])", "vec![-1, -2, -3]"),
    ],
    hidden=[
        T("empty", "v = []", "push_sum(vec![])", "vec![0]"),
        T("same_buffer", "v with capacity 10", "{ let mut v = Vec::with_capacity(10); v.push(5); let p = v.as_ptr(); let out = push_sum(v); out.as_ptr() == p }", "true"),
        T("single", "v = [7]", "push_sum(vec![7])", "vec![7, 7]"),
        T("negatives", "v = [-5, 2]", "push_sum(vec![-5, 2])", "vec![-5, 2, -3]"),
        T("cancels_out", "v = [5, -5]", "push_sum(vec![5, -5])", "vec![5, -5, 0]"),
        T("beyond_i32", "v = [3000000000, 3000000000]", "push_sum(vec![3_000_000_000, 3_000_000_000])", "vec![3_000_000_000, 3_000_000_000, 6_000_000_000]"),
        T("near_i64_max", "v = [i64::MAX / 2, i64::MAX / 2]", "push_sum(vec![i64::MAX / 2, i64::MAX / 2])", "vec![i64::MAX / 2, i64::MAX / 2, i64::MAX - 1]"),
        T("swap_unicode", "a = \"ünï\", b = \"日本\"", 'swap_owned("ünï".into(), "日本".into())', '("日本".to_string(), "ünï".to_string())'),
        T("swap_same_buffers", "a and b keep their heap buffers", '{ let (a, b) = (String::from("left"), String::from("right")); let (pa, pb) = (a.as_ptr(), b.as_ptr()); let (x, y) = swap_owned(a, b); (x.as_ptr() == pb, y.as_ptr() == pa) }', "(true, true)"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1104);
            for _ in 0..300 {
                let n = rng.below(20);
                let v: Vec<i64> = rng.vec(n, -1_000_000_000_000, 1_000_000_000_000);
                let mut want = v.clone();
                want.push(v.iter().sum());
                check!(format!("v = {v:?}"), push_sum(v.clone()), want);
            }
        }

        #[test]
        fn long_vec() {
            let v: Vec<i64> = (1..=200_000).collect();
            let out = push_sum(v);
            check!("v = 1..=200000", (out.len(), out[199_999], out[200_000]), (200_001, 200_000, 20_000_100_000));
        }
        """,
    ],
    wrong=dict(
        narrow_sum="""
            pub fn push_sum(mut v: Vec<i64>) -> Vec<i64> {
                let sum: i32 = v.iter().map(|&x| x as i32).sum();
                v.push(sum as i64);
                v
            }

            pub fn swap_owned(a: String, b: String) -> (String, String) {
                (b, a)
            }
        """,
        sum_at_front="""
            pub fn push_sum(mut v: Vec<i64>) -> Vec<i64> {
                let sum = v.iter().sum();
                v.insert(0, sum);
                v
            }

            pub fn swap_owned(a: String, b: String) -> (String, String) {
                (b, a)
            }
        """,
        copies_the_buffer="""
            pub fn push_sum(v: Vec<i64>) -> Vec<i64> {
                let mut out = Vec::with_capacity(v.len() + 1);
                out.extend_from_slice(&v);
                out.push(v.iter().sum());
                out
            }

            pub fn swap_owned(a: String, b: String) -> (String, String) {
                (b, a)
            }
        """,
    ),
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
        T("shout_in_place", "[\"ab\", \"c\"]", '{ let mut w = vec!["ab".to_string(), "c".to_string()]; shout_all(&mut w); w }', 'vec!["AB", "C"]'),
        T("sentence", "[\"a\", \"b\", \"c\"]", 'into_sentence(vec!["a".to_string(), "b".to_string(), "c".to_string()])', '"a b c".to_string()'),
        T("count_at_least", "[\"ab\", \"abc\", \"a\"], min = 2 (at least, so \"ab\" counts)", '{ let w = vec!["ab".to_string(), "abc".to_string(), "a".to_string()]; count_long(&w, 2) }', "2"),
    ],
    hidden=[
        T("empty", "[]", "{ let mut w: Vec<String> = vec![]; shout_all(&mut w); into_sentence(w) }", "String::new()"),
        T("count_empty", "[], min = 1", "count_long(&[], 1)", "0"),
        T("count_min_zero", "[\"\", \"a\"], min = 0", '{ let w = vec![String::new(), "a".to_string()]; count_long(&w, 0) }', "2"),
        T("count_exact_length", "[\"abc\", \"ab\"], min = 3", '{ let w = vec!["abc".to_string(), "ab".to_string()]; count_long(&w, 3) }', "1"),
        T("count_bytes_not_chars", "[\"é\", \"ab\", \"日\"], min = 3 (é is 2 bytes, 日 is 3)", '{ let w = vec!["é".to_string(), "ab".to_string(), "日".to_string()]; count_long(&w, 3) }', "1"),
        T("shout_mixed", "[\"aB1\", \"x-y\"]", '{ let mut w = vec!["aB1".to_string(), "x-y".to_string()]; shout_all(&mut w); w }', 'vec!["AB1", "X-Y"]'),
        T("shout_twice", "shout_all twice", '{ let mut w = vec!["go".to_string()]; shout_all(&mut w); shout_all(&mut w); w }', 'vec!["GO"]'),
        T("sentence_single", "[\"one\"]", 'into_sentence(vec!["one".to_string()])', '"one".to_string()'),
        T("sentence_empty_words", "[\"\", \"\"]", "into_sentence(vec![String::new(), String::new()])", '" ".to_string()'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1105);
            for _ in 0..300 {
                let n = rng.below(6);
                let mut words = Vec::new();
                for _ in 0..n {
                    let len = rng.below(5);
                    words.push(rng.string(len, "abé日"));
                }
                let min = rng.below(7);
                let input = format!("words = {words:?}, min = {min}");
                let want_count = words.iter().filter(|w| w.len() >= min).count();
                let want_sentence = words.iter().map(|w| w.to_ascii_uppercase()).collect::<Vec<_>>().join(" ");
                let count = count_long(&words, min);
                shout_all(&mut words);
                check!(input, (count, into_sentence(words)), (want_count, want_sentence));
            }
        }
        """,
    ],
    wrong=dict(
        shout_a_copy="""
            /// How many words are at least `min` bytes long.
            pub fn count_long(words: &[String], min: usize) -> usize {
                words.iter().filter(|w| w.len() >= min).count()
            }

            /// Uppercases every word in place.
            pub fn shout_all(words: &mut [String]) {
                for w in words.iter() {
                    let _ = w.to_uppercase();
                }
            }

            /// Joins the words with spaces.
            pub fn into_sentence(words: Vec<String>) -> String {
                words.join(" ")
            }
        """,
        counts_chars="""
            /// How many words are at least `min` bytes long.
            pub fn count_long(words: &[String], min: usize) -> usize {
                words.iter().filter(|w| w.chars().count() >= min).count()
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
    ),
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
        T("empty", "name = \"\"", 'Tag::new("")', "Tag { name: String::new() }"),
        T("with_spaces", "name = \"big data\"", 'Tag::new("big data").name', '"big data".to_string()'),
        T("exact_copy", "name = \"Rust 2021\"", 'Tag::new("Rust 2021") == Tag { name: String::from("Rust 2021") }', "true"),
    ],
    hidden=[
        T("outlives_input", "tag kept after its input is dropped", '{ let t = { let s = String::from("tmp"); Tag::new(&s) }; t.name }', '"tmp".to_string()'),
        T("spaces_kept", "name = \" a b \"", 'Tag::new(" a b ").name', '" a b ".to_string()'),
        T("case_kept", "name = \"RuSt\"", 'Tag::new("RuSt").name', '"RuSt".to_string()'),
        T("unicode", "name = \"日本語\"", 'Tag::new("日本語").name', '"日本語".to_string()'),
        T("emoji", "name = \"🦀 crab\"", 'Tag::new("🦀 crab").name', '"🦀 crab".to_string()'),
        T("source_changed_later", "input String changed after new", '{ let mut s = String::from("old"); let t = Tag::new(&s); s.push_str("er"); (t.name, s) }', '("old".to_string(), "older".to_string())'),
        T("two_tags_one_str", "two tags from the same &str", '{ let s = "same"; let (a, b) = (Tag::new(s), Tag::new(s)); a == b && a.name.as_ptr() != b.name.as_ptr() }', "true"),
        T("long_name", "name = 100000 × 'x'", 'Tag::new(&"x".repeat(100_000)).name.len()', "100_000"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1106);
            for _ in 0..300 {
                let len = rng.below(12);
                let s = rng.string(len, "aZ é日🦀\\t");
                check!(format!("name = {s:?}"), Tag::new(&s).name, s.clone());
            }
        }
        """,
    ],
    wrong=dict(
        with_capacity="""
            #[derive(Debug, PartialEq)]
            pub struct Tag {
                pub name: String,
            }

            impl Tag {
                pub fn new(name: &str) -> Tag {
                    Tag { name: String::with_capacity(name.len()) }
                }
            }
        """,
        trimmed="""
            #[derive(Debug, PartialEq)]
            pub struct Tag {
                pub name: String,
            }

            impl Tag {
                pub fn new(name: &str) -> Tag {
                    Tag { name: name.trim().to_string() }
                }
            }
        """,
    ),
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
        T("single_word", "\"plato\"", 'initials("plato")', '"P"'),
        T("extra_spaces_visible", "\" grace  hopper \"", 'initials(" grace  hopper ")', '"GH"'),
        T("all_lowercase", "\"alan mathison turing\"", 'initials("alan mathison turing")', '"AMT"'),
    ],
    hidden=[
        T("empty", "\"\"", 'initials("")', '""'),
        T("unicode", "\"élodie ünal\"", 'initials("élodie ünal")', '"ÉÜ"'),
        T("only_spaces", "\"   \"", 'initials("   ")', '""'),
        T("extra_spaces", "\"  ada   lovelace  \"", 'initials("  ada   lovelace  ")', '"AL"'),
        T("tabs_and_newlines", "\"ada\\tbyron\\nlovelace\"", 'initials("ada\\tbyron\\nlovelace")', '"ABL"'),
        T("already_upper", "\"ALAN TURING\"", 'initials("ALAN TURING")', '"AT"'),
        T("digits_and_marks", "\"3d printer -x\"", 'initials("3d printer -x")', '"3P-"'),
        T("sharp_s", "\"ßen ob\" (ß uppercases to SS)", 'initials("ßen ob")', '"SSO"'),
        T("one_letter_words", "\"a b c\"", 'initials("a b c")', '"ABC"'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1107);
            for _ in 0..300 {
                let len = rng.below(16);
                let name = rng.string(len, "abéß  \\t");
                let mut want = String::new();
                let mut at_start = true;
                for c in name.chars() {
                    if c.is_whitespace() {
                        at_start = true;
                    } else if at_start {
                        want.extend(c.to_uppercase());
                        at_start = false;
                    }
                }
                check!(format!("full_name = {name:?}"), initials(&name), want);
            }
        }

        #[test]
        fn many_words() {
            let name = "ab ".repeat(200_000);
            check!("\\"ab ab … ab \\" (200000 words)", initials(&name), "A".repeat(200_000));
        }
        """,
    ],
    wrong=dict(
        split_on_space="""
            pub fn initials(full_name: &str) -> String {
                full_name
                    .split(' ')
                    .filter_map(|w| w.chars().next())
                    .flat_map(char::to_uppercase)
                    .collect()
            }
        """,
        ascii_upper="""
            pub fn initials(full_name: &str) -> String {
                full_name
                    .split_whitespace()
                    .filter_map(|w| w.chars().next())
                    .map(|c| c.to_ascii_uppercase())
                    .collect()
            }
        """,
        first_byte="""
            pub fn initials(full_name: &str) -> String {
                full_name
                    .split_whitespace()
                    .map(|w| (w.as_bytes()[0] as char).to_ascii_uppercase())
                    .collect()
            }
        """,
    ),
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
        T("count_with", "books = [\"Dune\", \"Dune Messiah\", \"Emma\"], needle = \"Dune\"", 'lib.count_with("Dune")', "2", setup='let lib = Library::new(vec!["Dune".into(), "Dune Messiah".into(), "Emma".into()]);'),
        T("longest_tie_is_last", "books = [\"ab\", \"cd\", \"e\"]", "lib.longest()", 'Some("cd")', setup='let lib = Library::new(vec!["ab".into(), "cd".into(), "e".into()]);'),
        T("longest_no_books", "books = []", "lib.longest()", "None", setup="let lib = Library::new(vec![]);"),
    ],
    hidden=[
        T("longest_tie_last", "books = [\"ab\", \"cd\"]", "lib.longest()", 'Some("cd")', setup='let lib = Library::new(vec!["ab".into(), "cd".into()]);'),
        T("count", "needle = \"e\"", 'Library::new(vec!["Dune".into(), "Emma".into(), "Tess".into()]).count_with("e")', "2"),
        T("empty", "no books", "lib.longest()", "None", setup="let lib = Library::new(vec![]);"),
        T("search_empty_library", "no books, needle = \"a\"", 'lib.search("a")', "Vec::<&str>::new()", setup="let lib = Library::new(vec![]);"),
        T("search_none_match", "books = [\"Dune\", \"Emma\"], needle = \"x\"", 'lib.search("x")', "Vec::<&str>::new()", setup='let lib = Library::new(vec!["Dune".into(), "Emma".into()]);'),
        T("search_empty_needle", "books = [\"b\", \"a\"], needle = \"\"", 'lib.search("")', 'vec!["b", "a"]', setup='let lib = Library::new(vec!["b".into(), "a".into()]);'),
        T("search_middle_of_title", "books = [\"The Hobbit\", \"Hob\"], needle = \"obb\"", 'lib.search("obb")', 'vec!["The Hobbit"]', setup='let lib = Library::new(vec!["The Hobbit".into(), "Hob".into()]);'),
        T("case_sensitive", "books = [\"dune\", \"Dune\"], needle = \"D\"", '(lib.search("D"), lib.count_with("D"))', '(vec!["Dune"], 1)', setup='let lib = Library::new(vec!["dune".into(), "Dune".into()]);'),
        T("unicode", "books = [\"Café\", \"Cafe\", \"日本\"], needle = \"é\" (日本 is 6 bytes, Café 5)", '(lib.search("é"), lib.longest())', '(vec!["Café"], Some("日本"))', setup='let lib = Library::new(vec!["Café".into(), "Cafe".into(), "日本".into()]);'),
        T("longest_tie_of_three_last", "books = [\"xy\", \"a\", \"zw\", \"uv\"]", "lib.longest()", 'Some("uv")', setup='let lib = Library::new(vec!["xy".into(), "a".into(), "zw".into(), "uv".into()]);'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1108);
            for _ in 0..300 {
                let n = rng.below(7);
                let mut books = Vec::new();
                for _ in 0..n {
                    let len = rng.below(5);
                    books.push(rng.string(len, "abc"));
                }
                let len = rng.below(3);
                let needle = rng.string(len, "abc");
                let lib = Library::new(books.clone());
                let want_search: Vec<&str> = books.iter().filter(|b| b.contains(needle.as_str())).map(|b| b.as_str()).collect();
                let mut want_longest: Option<&str> = None;
                for b in &books {
                    if want_longest.map_or(true, |l| b.len() >= l.len()) {
                        want_longest = Some(b);
                    }
                }
                check!(
                    format!("books = {books:?}, needle = {needle:?}"),
                    (lib.search(&needle), lib.longest(), lib.count_with(&needle)),
                    (want_search.clone(), want_longest, want_search.len())
                );
            }
        }
        """,
    ],
    wrong=dict(
        first_on_tie="""
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
                    let mut best: Option<&str> = None;
                    for b in &self.books {
                        if best.map_or(true, |l| b.len() > l.len()) {
                            best = Some(b);
                        }
                    }
                    best
                }

                pub fn count_with(&self, needle: &str) -> usize {
                    self.books.iter().filter(|b| b.contains(needle)).count()
                }
            }
        """,
        search_prefix="""
            pub struct Library {
                books: Vec<String>,
            }

            impl Library {
                pub fn new(books: Vec<String>) -> Self {
                    Library { books }
                }

                /// Titles containing `needle`.
                pub fn search(&self, needle: &str) -> Vec<&str> {
                    self.books.iter().filter(|b| b.starts_with(needle)).map(String::as_str).collect()
                }

                /// The longest title; the last one on a tie.
                pub fn longest(&self) -> Option<&str> {
                    self.books.iter().max_by_key(|b| b.len()).map(String::as_str)
                }

                pub fn count_with(&self, needle: &str) -> usize {
                    self.search(needle).len()
                }
            }
        """,
    ),
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
        T("two_tabs", "\"\\tx\\t\"", 'normalize("\\tx\\t")', '"    x    "'),
        T("empty_visible", "\"\"", 'normalize("")', '""'),
        T("changed_is_owned", "\"x\\ty\"", 'matches!(normalize("x\\ty"), std::borrow::Cow::Owned(_))', "true"),
    ],
    hidden=[
        T("tabs_owned", "\"\\t\"", 'matches!(normalize("\\t"), std::borrow::Cow::Owned(_))', "true"),
        T("empty", "\"\"", 'normalize("")', '""'),
        T("empty_borrowed", "\"\"", 'matches!(normalize(""), std::borrow::Cow::Borrowed(""))', "true"),
        T("only_tab", "\"\\t\"", 'normalize("\\t")', '"    "'),
        T("consecutive_tabs", "\"a\\t\\tb\"", 'normalize("a\\t\\tb")', '"a        b"'),
        T("not_tab_stops", "\"abc\\td\" (always four spaces, not to the next tab stop)", 'normalize("abc\\td")', '"abc    d"'),
        T("unicode_around_tab", "\"é\\t日\"", 'normalize("é\\t日")', '"é    日"'),
        T("other_whitespace_kept", "\"a\\nb \\r\"", 'matches!(normalize("a\\nb \\r"), std::borrow::Cow::Borrowed("a\\nb \\r"))', "true"),
        T("borrowed_same_pointer", "\"no tabs here\"", '{ let s = String::from("no tabs here"); let out = normalize(&s); out.as_ptr() == s.as_ptr() }', "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1109);
            for _ in 0..300 {
                let len = rng.below(12);
                let s = rng.string(len, "ab é\\t");
                let mut want = String::new();
                for c in s.chars() {
                    if c == '\\t' {
                        want.push_str("    ");
                    } else {
                        want.push(c);
                    }
                }
                let out = normalize(&s);
                let borrowed = matches!(out, std::borrow::Cow::Borrowed(_));
                check!(format!("s = {s:?}"), (out.into_owned(), borrowed), (want, !s.contains('\\t')));
            }
        }

        #[test]
        fn scale_1m_tabs() {
            let s = "\\t".repeat(1_000_000);
            let out = normalize(&s);
            check!("s = 1000000 tabs", (out.len(), out.bytes().all(|b| b == b' ')), (4_000_000, true));
        }
        """,
    ],
    wrong=dict(
        always_owned="""
            use std::borrow::Cow;

            pub fn normalize(s: &str) -> Cow<'_, str> {
                Cow::Owned(s.replace('\\t', "    "))
            }
        """,
        tab_stops="""
            use std::borrow::Cow;

            pub fn normalize(s: &str) -> Cow<'_, str> {
                if !s.contains('\\t') {
                    return Cow::Borrowed(s);
                }
                let mut out = String::new();
                let mut col = 0;
                for c in s.chars() {
                    if c == '\\t' {
                        let pad = 4 - col % 4;
                        out.push_str(&" ".repeat(pad));
                        col += pad;
                    } else {
                        out.push(c);
                        col += 1;
                    }
                }
                Cow::Owned(out)
            }
        """,
        rescan_from_start="""
            use std::borrow::Cow;

            pub fn normalize(s: &str) -> Cow<'_, str> {
                if !s.contains('\\t') {
                    return Cow::Borrowed(s);
                }
                let mut out = s.to_string();
                while let Some(i) = out.find('\\t') {
                    out.replace_range(i..i + 1, "    ");
                }
                Cow::Owned(out)
            }
        """,
    ),
    hints=[("rust", "`Cow::Borrowed(s)` costs nothing; `Cow::Owned(String)` when you had to change it.")],
    notes=("Most inputs have no tabs, so most calls allocate nothing. `Cow<str>` derefs to `&str`, so callers barely notice the difference.", "O(n)", "O(n) only when changed"),
    follow_up="Where does std itself return `Cow`?",
    related=["S2", "S7"],
))

# The scene as given, with a wrong prediction filled in.
WRONG_DROP_ORDER = """
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
    pub const PREDICTED: [&str; 6] = PREDICTED_VALUE;
"""

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
        T("known_names", "PREDICTED", 'PREDICTED.iter().all(|n| ["a", "b", "c", "first", "second", "ignored"].contains(n))', "true"),
        """
        #[test]
        fn first_drop() {
            let log = RefCell::new(Vec::new());
            scene(&log);
            check!("the first name dropped", PREDICTED[0], log.into_inner()[0]);
        }

        #[test]
        fn last_drop() {
            let log = RefCell::new(Vec::new());
            scene(&log);
            check!("the last name dropped", PREDICTED[5], log.into_inner()[5]);
        }
        """,
    ],
    hidden=[
        """
        use std::cell::RefCell;

        fn run() -> Vec<&'static str> {
            let log = RefCell::new(Vec::new());
            scene(&log);
            log.into_inner()
        }

        fn at(names: &[&str], name: &str) -> Option<usize> {
            names.iter().position(|n| *n == name)
        }

        #[test]
        fn ignored_drops_first() {
            let log = RefCell::new(Vec::new());
            scene(&log);
            check!("first drop in scene()", PREDICTED[0], log.borrow()[0]);
        }

        #[test]
        fn each_name_once() {
            let mut names = PREDICTED.to_vec();
            names.sort();
            names.dedup();
            check!("distinct names in PREDICTED", names.len(), 6);
        }

        #[test]
        fn explicit_drop_second() {
            check!("second drop in scene(): drop(a)", PREDICTED[1], run()[1]);
        }

        #[test]
        fn c_before_b() {
            let (p, r) = (PREDICTED, run());
            check!("c and b: `let _ = b;` doesn't move b", (at(&p, "c") < at(&p, "b")), (at(&r, "c") < at(&r, "b")));
        }

        #[test]
        fn fields_in_declaration_order() {
            let (p, r) = (PREDICTED, run());
            check!("Pair's fields first and second", (at(&p, "first") < at(&p, "second")), (at(&r, "first") < at(&r, "second")));
        }

        #[test]
        fn pair_drops_last() {
            let (p, r) = (PREDICTED, run());
            check!("the last two drops (the Pair)", (p[4], p[5]), (r[4], r[5]));
        }

        #[test]
        fn locals_in_reverse() {
            check!("third and fourth drops in scene()", (PREDICTED[2], PREDICTED[3]), (run()[2], run()[3]));
        }

        #[test]
        fn whole_order() {
            check!("scene()", PREDICTED.to_vec(), run());
        }
        """,
    ],
    wrong=dict(
        let_underscore_moves=WRONG_DROP_ORDER.replace("PREDICTED_VALUE", '["ignored", "a", "b", "c", "first", "second"]'),
        fields_in_reverse=WRONG_DROP_ORDER.replace("PREDICTED_VALUE", '["ignored", "a", "c", "b", "second", "first"]'),
        temporary_lives_on=WRONG_DROP_ORDER.replace("PREDICTED_VALUE", '["a", "c", "b", "ignored", "first", "second"]'),
    ),
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

        #[test]
        fn normal_return_exits() {
            let log = RefCell::new(Vec::new());
            early(&log, false);
            check!("return at the end of the function", log.into_inner(), vec!["enter work", "exit work"]);
        }

        #[test]
        fn single_span() {
            let log = RefCell::new(Vec::new());
            {
                let _s = Span::enter("only", &log);
            }
            check!("one span in a block", log.into_inner(), vec!["enter only", "exit only"]);
        }

        #[test]
        fn sequential_spans() {
            let log = RefCell::new(Vec::new());
            {
                let _a = Span::enter("a", &log);
            }
            {
                let _b = Span::enter("b", &log);
            }
            check!("span a, then span b", log.into_inner(), vec!["enter a", "exit a", "enter b", "exit b"]);
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

        #[test]
        fn panic_in_nested_spans() {
            let log = RefCell::new(Vec::new());
            let _ = catch_unwind(AssertUnwindSafe(|| {
                let _outer = Span::enter("outer", &log);
                let _inner = Span::enter("inner", &log);
                panic!("boom");
            }));
            check!("a panic inside two spans", log.into_inner(), vec!["enter outer", "enter inner", "exit inner", "exit outer"]);
        }

        #[test]
        fn nothing_before_the_drop() {
            let log = RefCell::new(Vec::new());
            let s = Span::enter("held", &log);
            let before = log.borrow().clone();
            drop(s);
            check!("the log while the span is alive", before, vec!["enter held"]);
        }

        #[test]
        fn explicit_drop_exits_early() {
            let log = RefCell::new(Vec::new());
            {
                let a = Span::enter("a", &log);
                drop(a);
                let _b = Span::enter("b", &log);
            }
            check!("drop(a), then enter b", log.into_inner(), vec!["enter a", "exit a", "enter b", "exit b"]);
        }

        fn take(_s: Span<'_>) {}

        #[test]
        fn moved_span_exits_where_it_ends() {
            let log = RefCell::new(Vec::new());
            {
                let s = Span::enter("moved", &log);
                take(s);
                let _after = Span::enter("after", &log);
            }
            check!("span moved into a function that drops it", log.into_inner(), vec!["enter moved", "exit moved", "enter after", "exit after"]);
        }

        #[test]
        fn in_a_loop() {
            let log = RefCell::new(Vec::new());
            for name in ["x", "y"] {
                let _s = Span::enter(name, &log);
            }
            check!("a span per loop iteration", log.into_inner(), vec!["enter x", "exit x", "enter y", "exit y"]);
        }

        #[test]
        fn forgotten_span_never_exits() {
            let log = RefCell::new(Vec::new());
            std::mem::forget(Span::enter("lost", &log));
            check!("mem::forget(span)", log.into_inner(), vec!["enter lost"]);
        }

        #[test]
        fn random_vs_model() {
            const NAMES: [&str; 4] = ["p", "q", "r", "s"];
            let mut rng = anneal_prelude::Rng::new(1110);
            for _ in 0..200 {
                let log = RefCell::new(Vec::new());
                let mut want = Vec::new();
                let mut ops = Vec::new();
                {
                    let mut open: Vec<(Span, &str)> = Vec::new();
                    for _ in 0..rng.below(12) {
                        if rng.bool() || open.is_empty() {
                            let name = *rng.pick(&NAMES);
                            want.push(format!("enter {name}"));
                            ops.push(format!("enter {name}"));
                            open.push((Span::enter(name, &log), name));
                        } else {
                            let i = rng.below(open.len());
                            let (span, name) = open.remove(i);
                            want.push(format!("exit {name}"));
                            ops.push(format!("drop {name}"));
                            drop(span);
                        }
                    }
                    while let Some((span, name)) = open.pop() {
                        want.push(format!("exit {name}"));
                        drop(span);
                    }
                }
                check!(format!("{ops:?}, then the rest in reverse"), log.into_inner(), want);
            }
        }
        """,
    ],
    wrong=dict(
        exit_at_enter="""
            use std::cell::RefCell;

            pub struct Span<'a> {
                name: &'static str,
                log: &'a RefCell<Vec<String>>,
            }

            impl<'a> Span<'a> {
                pub fn enter(name: &'static str, log: &'a RefCell<Vec<String>>) -> Self {
                    log.borrow_mut().push(format!("enter {name}"));
                    log.borrow_mut().push(format!("exit {name}"));
                    Span { name, log }
                }
            }

            impl Drop for Span<'_> {
                fn drop(&mut self) {
                    let _ = (self.name, self.log);
                }
            }
        """,
        exit_without_name="""
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
                    self.log.borrow_mut().push("exit".to_string());
                }
            }
        """,
    ),
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
        T("first_call", "start = 0, one call", "{ let mut c = counter(0); c() }", "1"),
        T("five_calls", "start = 1, five calls", "{ let mut c = counter(1); (0..5).map(|_| c()).collect::<Vec<_>>() }", "vec![2, 3, 4, 5, 6]"),
        T("start_not_returned", "start = 42", "{ let mut c = counter(42); c() }", "43"),
    ],
    hidden=[
        T("hundred_calls", "start = 0, 100 calls", "{ let mut c = counter(0); (0..100).map(|_| c()).last() }", "Some(100)"),
        T("near_max", "start = u32::MAX - 2, two calls", "{ let mut c = counter(u32::MAX - 2); (c(), c()) }", "(u32::MAX - 1, u32::MAX)"),
        T("interleaved", "a and b from 5, called a, b, a, b", "{ let mut a = counter(5); let mut b = counter(5); (a(), b(), a(), b()) }", "(6, 6, 7, 7)"),
        T("different_starts", "counter(0) and counter(100)", "{ let mut a = counter(0); let mut b = counter(100); (a(), b(), a()) }", "(1, 101, 2)"),
        T("boxed", "Box<dyn FnMut() -> u32> from counter(3)", "{ let mut c: Box<dyn FnMut() -> u32> = Box::new(counter(3)); (c(), c()) }", "(4, 5)"),
        T("start_variable_dropped", "start comes from a local that goes away", "{ let mut c = { let s = String::from(\"41\"); counter(s.parse().unwrap()) }; c() }", "42"),
        T("many_calls", "start = 0, 100000 calls", "{ let mut c = counter(0); let mut last = 0; for _ in 0..100_000 { last = c(); } last }", "100_000"),
        """
        fn call_twice(mut f: impl FnMut() -> u32) -> (u32, u32) {
            (f(), f())
        }

        #[test]
        fn passed_by_value() {
            check!("call_twice(counter(7))", call_twice(counter(7)), (8, 9));
        }

        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1111);
            for _ in 0..300 {
                let start = rng.int(0, 1_000_000) as u32;
                let calls = rng.below(20) + 1;
                let mut c = counter(start);
                let got: Vec<u32> = (0..calls).map(|_| c()).collect();
                let want: Vec<u32> = (1..=calls as u32).map(|k| start + k).collect();
                check!(format!("start = {start}, {calls} calls"), got, want);
            }
        }
        """,
    ],
    wrong=dict(
        # Needs more than the one changed line, so it breaks the line limit too; with one line there's no compiling wrong fix.
        returns_before_increment="""
            /// Each call returns the next number after `start`.
            pub fn counter(start: u32) -> impl FnMut() -> u32 {
                let mut n = start;
                move || {
                    let current = n;
                    n += 1;
                    current
                }
            }
        """,
    ),
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
        T("single_chunk", "[[10, 20]]", "parallel_sum(vec![vec![10, 20]])", "30"),
        T("one_empty_chunk", "[[]]", "parallel_sum(vec![vec![]])", "0"),
        T("zeros", "[[0, 0], [0]]", "parallel_sum(vec![vec![0, 0], vec![0]])", "0"),
    ],
    hidden=[
        T("many", "8 chunks of 0..1000", "parallel_sum((0..8).map(|_| (0..1000).collect()).collect())", "8 * 499_500"),
        T("empty_chunks_inside", "[[], [1], []]", "parallel_sum(vec![vec![], vec![1], vec![]])", "1"),
        T("only_empty_chunks", "[[], []]", "parallel_sum(vec![vec![], vec![]])", "0"),
        T("beyond_u32", "[[5000000000], [5000000000]]", "parallel_sum(vec![vec![5_000_000_000], vec![5_000_000_000]])", "10_000_000_000"),
        T("near_u64_max", "[[u64::MAX / 2], [u64::MAX / 2]]", "parallel_sum(vec![vec![u64::MAX / 2], vec![u64::MAX / 2]])", "u64::MAX - 1"),
        T("sixty_four_chunks", "64 chunks [i]", "parallel_sum((0..64).map(|i| vec![i]).collect())", "2016"),
        T("one_big_chunk", "[1..=200000]", "parallel_sum(vec![(1..=200_000).collect()])", "20_000_100_000"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1112);
            for _ in 0..100 {
                let k = rng.below(6);
                let mut chunks: Vec<Vec<u64>> = Vec::new();
                for _ in 0..k {
                    let len = rng.below(8);
                    chunks.push(rng.vec(len, 0, 1_000_000_000_000));
                }
                let want: u64 = chunks.iter().flatten().sum();
                check!(format!("chunks = {chunks:?}"), parallel_sum(chunks.clone()), want);
            }
        }
        """,
    ],
    wrong=dict(
        narrow_sum="""
            use std::thread;

            pub fn parallel_sum(chunks: Vec<Vec<u64>>) -> u64 {
                let handles: Vec<_> = chunks
                    .into_iter()
                    .map(|chunk| thread::spawn(move || chunk.iter().map(|&x| x as u32).sum::<u32>()))
                    .collect();
                handles.into_iter().map(|h| h.join().expect("worker panicked") as u64).sum()
            }
        """,
        reduce_panics_on_empty="""
            use std::thread;

            pub fn parallel_sum(chunks: Vec<Vec<u64>>) -> u64 {
                let handles: Vec<_> = chunks
                    .into_iter()
                    .map(|chunk| thread::spawn(move || chunk.into_iter().reduce(|a, b| a + b).unwrap()))
                    .collect();
                handles.into_iter().map(|h| h.join().expect("worker panicked")).sum()
            }
        """,
    ),
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
        T("one_thread", "data = [4, 5], n = 1", "sum_everywhere(vec![4, 5], 1)", "vec![9]"),
        T("empty_data_visible", "data = [], n = 2", "sum_everywhere(vec![], 2)", "vec![0, 0]"),
        T("two_threads", "data = [10, 20], n = 2", "sum_everywhere(vec![10, 20], 2)", "vec![30, 30]"),
    ],
    hidden=[
        T("big", "data = 0..10000, n = 4", "sum_everywhere((0..10_000).collect(), 4)", "vec![49_995_000; 4]"),
        T("empty_data", "data = [], n = 3", "sum_everywhere(vec![], 3)", "vec![0, 0, 0]"),
        T("single_value", "data = [9], n = 2", "sum_everywhere(vec![9], 2)", "vec![9, 9]"),
        T("uneven_split", "data = [1, 2, 3, 4, 5], n = 2", "sum_everywhere(vec![1, 2, 3, 4, 5], 2)", "vec![15, 15]"),
        T("sixteen_threads", "data = [1, 1, 1], n = 16", "sum_everywhere(vec![1, 1, 1], 16)", "vec![3; 16]"),
        T("large_values", "data = [u64::MAX / 4; 2], n = 2", "sum_everywhere(vec![u64::MAX / 4; 2], 2)", "vec![u64::MAX / 4 * 2; 2]"),
        T("empty_no_threads", "data = [], n = 0", "sum_everywhere(vec![], 0)", "Vec::<u64>::new()"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1113);
            for _ in 0..100 {
                let len = rng.below(10);
                let data: Vec<u64> = rng.vec(len, 0, 1_000_000);
                let n = rng.below(5);
                let want = vec![data.iter().sum::<u64>(); n];
                check!(format!("data = {data:?}, n = {n}"), sum_everywhere(data.clone(), n), want);
            }
        }
        """,
    ],
    wrong=dict(
        take_per_thread="""
            use std::thread;

            /// `n` threads each sum `data`; returns every thread's result.
            pub fn sum_everywhere(mut data: Vec<u64>, n: usize) -> Vec<u64> {
                let mut handles = Vec::new();
                for _ in 0..n {
                    let mine = std::mem::take(&mut data);
                    handles.push(thread::spawn(move || mine.iter().sum::<u64>()));
                }
                handles.into_iter().map(|h| h.join().expect("worker panicked")).collect()
            }
        """,
        split_between_threads="""
            use std::sync::Arc;
            use std::thread;

            /// `n` threads each sum `data`; returns every thread's result.
            pub fn sum_everywhere(data: Vec<u64>, n: usize) -> Vec<u64> {
                let data = Arc::new(data);
                let mut handles = Vec::new();
                for i in 0..n {
                    let data = Arc::clone(&data);
                    handles.push(thread::spawn(move || data.iter().skip(i).step_by(n).sum::<u64>()));
                }
                handles.into_iter().map(|h| h.join().expect("worker panicked")).collect()
            }
        """,
    ),
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
        T("leaves_empty_string", "names = [\"x\"]", '{ let mut v = vec!["x".to_string()]; take_first(&mut v); v }', "vec![String::new()]"),
        T("others_untouched", "names = [\"a\", \"b\"]", '{ let mut v = vec!["a".to_string(), "b".to_string()]; take_first(&mut v); v[1].clone() }', '"b".to_string()'),
        T("second_call", "take_first twice on [\"a\"]", '{ let mut v = vec!["a".to_string()]; take_first(&mut v); take_first(&mut v) }', "String::new()"),
    ],
    hidden=[
        T("keeps_length", "names = [\"a\", \"b\", \"c\"]", '{ let mut v = vec!["a".to_string(), "b".to_string(), "c".to_string()]; take_first(&mut v); v.len() }', "3"),
        T("rest_untouched", "names = [\"a\", \"b\", \"c\"]", '{ let mut v = vec!["a".to_string(), "b".to_string(), "c".to_string()]; take_first(&mut v); v }', 'vec!["", "b", "c"]'),
        T("first_already_empty", "names = [\"\", \"b\"]", '{ let mut v = vec![String::new(), "b".to_string()]; (take_first(&mut v), v) }', '(String::new(), vec![String::new(), "b".to_string()])'),
        T("twice", "take_first twice on [\"ann\", \"bo\"]", '{ let mut v = vec!["ann".to_string(), "bo".to_string()]; let a = take_first(&mut v); let b = take_first(&mut v); (a, b) }', '("ann".to_string(), String::new())'),
        T("same_buffer", "the returned String is the one from the Vec", '{ let mut v = vec![String::from("moved")]; let p = v[0].as_ptr(); take_first(&mut v).as_ptr() == p }', "true"),
        T("slot_not_allocated", "capacity left in names[0]", '{ let mut v = vec![String::from("gone")]; take_first(&mut v); v[0].capacity() }', "0"),
        T("unicode", "names = [\"日本\", \"é\"]", '{ let mut v = vec!["日本".to_string(), "é".to_string()]; (take_first(&mut v), v) }', '("日本".to_string(), vec![String::new(), "é".to_string()])'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1114);
            for _ in 0..300 {
                let n = rng.below(6) + 1;
                let mut names = Vec::new();
                for _ in 0..n {
                    let len = rng.below(4);
                    names.push(rng.string(len, "abé"));
                }
                let mut want_rest = names.clone();
                let want_first = std::mem::replace(&mut want_rest[0], String::new());
                let input = format!("names = {names:?}");
                let first = take_first(&mut names);
                check!(input, (first, names), (want_first, want_rest));
            }
        }
        """,
    ],
    wrong=dict(
        remove_first="""
            /// Moves the first name out, leaving "" in its place.
            pub fn take_first(names: &mut Vec<String>) -> String {
                let first = names.remove(0);
                first
            }
        """,
        pop_last="""
            /// Moves the first name out, leaving "" in its place.
            pub fn take_first(names: &mut Vec<String>) -> String {
                let first = names.pop().unwrap_or_default();
                first
            }
        """,
    ),
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
        T("done_stays_done", "Done(\"ship\")", '{ let mut j = Job::Done("ship".into()); advance(&mut j); j }', 'Job::Done("ship".into())'),
        T("two_steps", "Queued(\"test\") advanced twice", '{ let mut j = Job::Queued("test".into()); advance(&mut j); advance(&mut j); j }', 'Job::Done("test".into())'),
        T("three_steps", "Queued(\"lint\") advanced three times", '{ let mut j = Job::Queued("lint".into()); for _ in 0..3 { advance(&mut j); } j }', 'Job::Done("lint".into())'),
    ],
    hidden=[
        T("done_stays", "Done(\"x\")", '{ let mut j = Job::Done("x".into()); advance(&mut j); j }', 'Job::Done("x".into())'),
        T("same_buffer", "name's heap buffer kept", '{ let mut j = Job::Queued(String::from("keep")); let p = match &j { Job::Queued(s) => s.as_ptr(), _ => unreachable!() }; advance(&mut j); match &j { Job::Running(s) => s.as_ptr() == p, _ => false } }', "true"),
        T("same_buffer_to_done", "Running → Done keeps the buffer", '{ let mut j = Job::Running(String::from("keep")); let p = match &j { Job::Running(s) => s.as_ptr(), _ => unreachable!() }; advance(&mut j); match &j { Job::Done(s) => s.as_ptr() == p, _ => false } }', "true"),
        T("done_keeps_buffer", "Done stays Done with the same buffer", '{ let mut j = Job::Done(String::from("keep")); let p = match &j { Job::Done(s) => s.as_ptr(), _ => unreachable!() }; advance(&mut j); match &j { Job::Done(s) => s.as_ptr() == p, _ => false } }', "true"),
        T("done_twice", "Done(\"x\") advanced twice", '{ let mut j = Job::Done("x".into()); advance(&mut j); advance(&mut j); j }', 'Job::Done("x".into())'),
        T("ten_steps", "Queued(\"q\") advanced 10 times", '{ let mut j = Job::Queued("q".into()); for _ in 0..10 { advance(&mut j); } j }', 'Job::Done("q".into())'),
        T("empty_name", "Queued(\"\")", '{ let mut j = Job::Queued(String::new()); advance(&mut j); j }', "Job::Running(String::new())"),
        T("unicode_name", "Running(\"日本 ✓\")", '{ let mut j = Job::Running("日本 ✓".into()); advance(&mut j); j }', 'Job::Done("日本 ✓".into())'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1115);
            for _ in 0..300 {
                let len = rng.below(5);
                let name = rng.string(len, "ab");
                let start = rng.below(3);
                let steps = rng.below(4);
                let make = |stage: usize, name: String| match stage {
                    0 => Job::Queued(name),
                    1 => Job::Running(name),
                    _ => Job::Done(name),
                };
                let mut job = make(start, name.clone());
                let input = format!("{job:?}, advanced {steps} times");
                for _ in 0..steps {
                    advance(&mut job);
                }
                check!(input, job, make((start + steps).min(2), name));
            }
        }
        """,
    ],
    wrong=dict(
        clones_the_name="""
            #[derive(Debug, PartialEq)]
            pub enum Job {
                Queued(String),
                Running(String),
                Done(String),
            }

            pub fn advance(job: &mut Job) {
                *job = match job {
                    Job::Queued(name) => Job::Running(name.clone()),
                    Job::Running(name) => Job::Done(name.clone()),
                    Job::Done(name) => Job::Done(name.clone()),
                };
            }
        """,
        done_starts_over="""
            #[derive(Debug, PartialEq)]
            pub enum Job {
                Queued(String),
                Running(String),
                Done(String),
            }

            pub fn advance(job: &mut Job) {
                *job = match std::mem::replace(job, Job::Done(String::new())) {
                    Job::Queued(name) => Job::Running(name),
                    Job::Running(name) => Job::Done(name),
                    Job::Done(name) => Job::Queued(name),
                };
            }
        """,
        done_loses_name="""
            #[derive(Debug, PartialEq)]
            pub enum Job {
                Queued(String),
                Running(String),
                Done(String),
            }

            pub fn advance(job: &mut Job) {
                let next = match std::mem::replace(job, Job::Done(String::new())) {
                    Job::Queued(name) => Job::Running(name),
                    Job::Running(name) => Job::Done(name),
                    Job::Done(_) => return,
                };
                *job = next;
            }
        """,
    ),
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
        T("exact_multiple", "size 2, push 1, 2, 3, 4", "{ let mut b = Batcher::new(2); (b.push(1), b.push(2), b.push(3), b.push(4)) }", "(None, Some(vec![1, 2]), None, Some(vec![3, 4]))"),
        T("flush_nothing", "size 2, nothing pushed", "Batcher::new(2).flush()", "None"),
        T("flush_after_batch", "size 1, push 5, flush", "{ let mut b = Batcher::new(1); (b.push(5), b.flush()) }", "(Some(vec![5]), None)"),
    ],
    hidden=[
        T("size_one", "size 1", "{ let mut b = Batcher::new(1); (b.push(5), b.flush()) }", "(Some(vec![5]), None)"),
        T("flush_empty", "nothing pushed", "Batcher::new(4).flush()", "None"),
        T("flush_after_full_batch", "size 2, push 1, 2, then flush", "{ let mut b = Batcher::new(2); b.push(1); (b.push(2), b.flush()) }", "(Some(vec![1, 2]), None)"),
        T("push_after_flush", "size 3, push 1, flush, push 2, 3, 4", "{ let mut b = Batcher::new(3); b.push(1); let f = b.flush(); (f, b.push(2), b.push(3), b.push(4)) }", "(Some(vec![1]), None, None, Some(vec![2, 3, 4]))"),
        T("size_one_every_push", "size 1, push 1, 2, 3", "{ let mut b = Batcher::new(1); (b.push(1), b.push(2), b.push(3)) }", "(Some(vec![1]), Some(vec![2]), Some(vec![3]))"),
        T("extreme_values", "size 2, push 0, u32::MAX", "{ let mut b = Batcher::new(2); (b.push(0), b.push(u32::MAX)) }", "(None, Some(vec![0, u32::MAX]))"),
        T("duplicates", "size 3, push 7, 7, 7", "{ let mut b = Batcher::new(3); (b.push(7), b.push(7), b.push(7)) }", "(None, None, Some(vec![7, 7, 7]))"),
        T("big_batches", "size 1000, push 0..2500, then flush", "{ let mut b = Batcher::new(1000); let full: Vec<Vec<u32>> = (0..2500).filter_map(|i| b.push(i)).collect(); (full.len(), full[1][999], b.flush().map(|r| (r.len(), r[0]))) }", "(2, 1999, Some((500, 2000)))"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(1116);
            for _ in 0..300 {
                let size = rng.below(5) + 1;
                let mut b = Batcher::new(size);
                let mut pending: Vec<u32> = Vec::new();
                let mut ops = Vec::new();
                for _ in 0..rng.below(15) {
                    if rng.below(4) == 0 {
                        ops.push("flush".to_string());
                        let want = if pending.is_empty() { None } else { Some(std::mem::take(&mut pending)) };
                        check!(format!("size = {size}, {ops:?}"), b.flush(), want);
                    } else {
                        let v = rng.below(100) as u32;
                        ops.push(format!("push {v}"));
                        pending.push(v);
                        let want = if pending.len() == size { Some(std::mem::take(&mut pending)) } else { None };
                        check!(format!("size = {size}, {ops:?}"), b.push(v), want);
                    }
                }
            }
        }
        """,
    ],
    wrong=dict(
        flush_always_some="""
            pub struct Batcher {
                current: Vec<u32>,
                size: usize,
            }

            impl Batcher {
                pub fn new(size: usize) -> Self {
                    Batcher { current: Vec::new(), size }
                }

                pub fn push(&mut self, value: u32) -> Option<Vec<u32>> {
                    self.current.push(value);
                    if self.current.len() == self.size {
                        Some(std::mem::take(&mut self.current))
                    } else {
                        None
                    }
                }

                pub fn flush(&mut self) -> Option<Vec<u32>> {
                    Some(std::mem::take(&mut self.current))
                }
            }
        """,
        off_by_one="""
            pub struct Batcher {
                current: Option<Vec<u32>>,
                size: usize,
            }

            impl Batcher {
                pub fn new(size: usize) -> Self {
                    Batcher { current: None, size }
                }

                pub fn push(&mut self, value: u32) -> Option<Vec<u32>> {
                    let batch = self.current.get_or_insert_with(Vec::new);
                    if batch.len() == self.size {
                        let full = self.current.replace(vec![value]);
                        return full;
                    }
                    batch.push(value);
                    None
                }

                pub fn flush(&mut self) -> Option<Vec<u32>> {
                    self.current.take()
                }
            }
        """,
        never_resets="""
            pub struct Batcher {
                current: Option<Vec<u32>>,
                size: usize,
            }

            impl Batcher {
                pub fn new(size: usize) -> Self {
                    Batcher { current: None, size }
                }

                pub fn push(&mut self, value: u32) -> Option<Vec<u32>> {
                    let batch = self.current.get_or_insert_with(Vec::new);
                    batch.push(value);
                    if batch.len() % self.size == 0 {
                        Some(batch[batch.len() - self.size..].to_vec())
                    } else {
                        None
                    }
                }

                pub fn flush(&mut self) -> Option<Vec<u32>> {
                    self.current.take()
                }
            }
        """,
    ),
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

        #[test]
        fn panic_without_pushes() {
            let mut v = vec![1, 2];
            let r = catch_unwind(AssertUnwindSafe(|| with_rollback(&mut v, |_| panic!("boom"))));
            check!("f panics at once", (r.is_err(), v), (true, vec![1, 2]));
        }

        #[test]
        fn success_on_empty() {
            let mut v = vec![];
            with_rollback(&mut v, |v| {
                v.push(1);
                v.push(2);
            });
            check!("v = [], f pushes 1 and 2", v, vec![1, 2]);
        }

        #[test]
        fn rollback_keeps_earlier_values() {
            let mut v = vec![7, 8, 9];
            let _ = catch_unwind(AssertUnwindSafe(|| {
                with_rollback(&mut v, |v| {
                    v.push(10);
                    panic!("boom");
                })
            }));
            check!("v = [7, 8, 9], f pushes 10 then panics", v, vec![7, 8, 9]);
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

        #[test]
        fn panic_keeps_propagating() {
            let mut v = vec![1];
            let r = catch_unwind(AssertUnwindSafe(|| with_rollback(&mut v, |_| panic!("boom"))));
            let msg = r.err().and_then(|e| e.downcast_ref::<&str>().map(|s| s.to_string()));
            check!("f panics with \\"boom\\"", msg, Some("boom".to_string()));
        }

        #[test]
        fn outer_panic_undoes_inner_success() {
            let mut v = vec![0];
            let _ = catch_unwind(AssertUnwindSafe(|| {
                with_rollback(&mut v, |v| {
                    with_rollback(v, |v| v.push(1));
                    v.push(2);
                    panic!("outer");
                })
            }));
            check!("inner succeeds, outer panics", v, vec![0]);
        }

        #[test]
        fn empty_and_panic() {
            let mut v = vec![];
            let _ = catch_unwind(AssertUnwindSafe(|| with_rollback(&mut v, |v| {
                v.push(9);
                panic!("boom");
            })));
            check!("v = [], f pushes 9 then panics", v, Vec::<i32>::new());
        }

        #[test]
        fn success_without_pushes() {
            let mut v = vec![4, 5];
            with_rollback(&mut v, |_| {});
            check!("v = [4, 5], f does nothing", v, vec![4, 5]);
        }

        #[test]
        fn success_then_panic() {
            let mut v = vec![];
            with_rollback(&mut v, |v| v.push(1));
            let _ = catch_unwind(AssertUnwindSafe(|| with_rollback(&mut v, |v| {
                v.push(2);
                panic!("boom");
            })));
            with_rollback(&mut v, |v| v.push(3));
            check!("push 1 ok, push 2 panics, push 3 ok", v, vec![1, 3]);
        }

        #[test]
        fn big_rollback() {
            let mut v: Vec<i32> = (0..1000).collect();
            let _ = catch_unwind(AssertUnwindSafe(|| with_rollback(&mut v, |v| {
                v.extend(0..200_000);
                panic!("boom");
            })));
            check!("v = 0..1000, f pushes 200000 then panics", (v.len(), v[999]), (1000, 999));
        }

        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(1117);
            for _ in 0..60 {
                let len = rng.below(5);
                let mut v: Vec<i32> = rng.vec(len, -9, 9);
                let adds = rng.below(5);
                let pushes: Vec<i32> = rng.vec(adds, -9, 9);
                let fails = rng.bool();
                let mut want = v.clone();
                if !fails {
                    want.extend(&pushes);
                }
                let input = format!("v = {v:?}, f pushes {pushes:?}, panics: {fails}");
                let _ = catch_unwind(AssertUnwindSafe(|| with_rollback(&mut v, |v| {
                    v.extend(&pushes);
                    if fails {
                        panic!("random");
                    }
                })));
                check!(input, v, want);
            }
        }
        """,
    ],
    wrong=dict(
        swallows_the_panic="""
            use std::panic::{AssertUnwindSafe, catch_unwind};

            pub fn with_rollback(v: &mut Vec<i32>, f: impl FnOnce(&mut Vec<i32>)) {
                let len = v.len();
                let r = catch_unwind(AssertUnwindSafe(|| f(v)));
                if r.is_err() {
                    v.truncate(len);
                }
            }
        """,
        always_truncates="""
            pub fn with_rollback(v: &mut Vec<i32>, f: impl FnOnce(&mut Vec<i32>)) {
                struct Guard<'a> {
                    v: &'a mut Vec<i32>,
                    len: usize,
                }

                impl Drop for Guard<'_> {
                    fn drop(&mut self) {
                        self.v.truncate(self.len);
                    }
                }

                let len = v.len();
                let guard = Guard { v, len };
                f(guard.v);
            }
        """,
        clears_on_panic="""
            pub fn with_rollback(v: &mut Vec<i32>, f: impl FnOnce(&mut Vec<i32>)) {
                struct Guard<'a> {
                    v: &'a mut Vec<i32>,
                    armed: bool,
                }

                impl Drop for Guard<'_> {
                    fn drop(&mut self) {
                        if self.armed {
                            self.v.clear();
                        }
                    }
                }

                let mut guard = Guard { v, armed: true };
                f(guard.v);
                guard.armed = false;
            }
        """,
    ),
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
