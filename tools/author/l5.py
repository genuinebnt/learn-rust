from author import T, write_track

P = []


def fix(slug, title, level, stage, tags, statement, starter, solution, visible, hidden, hints, notes, follow_up, teaches, rules=None, related=("L5",), wrong=None):
    return dict(slug=slug, title=title, mode="fix", level=level, stage=stage, tags=tags, statement=statement, starter=starter,
                solution=solution, visible=visible, hidden=hidden, hints=hints, notes=notes, follow_up=follow_up,
                teaches=teaches, rules=rules, related=list(related), wrong=wrong)


def write(slug, title, level, stage, tags, statement, starter, solution, visible, hidden, hints, notes, follow_up, teaches, related=("L5",), source=None, examples=(), wrong=None):
    return dict(slug=slug, title=title, level=level, stage=stage, tags=tags, statement=statement, starter=starter,
                solution=solution, visible=visible, hidden=hidden, hints=hints, notes=notes, follow_up=follow_up,
                teaches=teaches, related=list(related), source=source, examples=list(examples), wrong=wrong)


# ---------------------------------------------------------------- generic code (easy)

STACK_SOLUTION = """
pub struct Stack<T> {
    items: Vec<T>,
}

impl<T> Stack<T> {
    pub fn new() -> Self {
        Stack { items: Vec::new() }
    }

    pub fn push(&mut self, item: T) {
        self.items.push(item);
    }

    /// Removes and returns the top item.
    pub fn pop(&mut self) -> Option<T> {
        self.items.pop()
    }

    /// The top item, without removing it.
    pub fn peek(&self) -> Option<&T> {
        self.items.last()
    }

    /// Lets the caller change the top item in place.
    pub fn peek_mut(&mut self) -> Option<&mut T> {
        self.items.last_mut()
    }

    pub fn len(&self) -> usize {
        self.items.len()
    }

    pub fn is_empty(&self) -> bool {
        self.items.is_empty()
    }
}
"""

P.append(write(
    "generic-stack", "Stack<T>", "easy", "generic-code", ["generics", "Option", "impl<T>"],
    """
        Implement a generic `Stack<T>` backed by a `Vec<T>`: `push`, `pop`, `peek`, `peek_mut`, `len` and
        `is_empty`. The last item pushed is the first one popped.

        It must work for any `T`. The tests use types that aren't `Copy`, `Clone`, `Default` or `Debug`, so
        don't add bounds the code doesn't need.
    """,
    """
    pub struct Stack<T> {
        items: Vec<T>,
    }

    impl<T> Stack<T> {
        pub fn new() -> Self {
            todo!()
        }

        pub fn push(&mut self, item: T) {
            todo!()
        }

        /// Removes and returns the top item.
        pub fn pop(&mut self) -> Option<T> {
            todo!()
        }

        /// The top item, without removing it.
        pub fn peek(&self) -> Option<&T> {
            todo!()
        }

        /// Lets the caller change the top item in place.
        pub fn peek_mut(&mut self) -> Option<&mut T> {
            todo!()
        }

        pub fn len(&self) -> usize {
            todo!()
        }

        pub fn is_empty(&self) -> bool {
            todo!()
        }
    }
    """,
    STACK_SOLUTION,
    [T("last_in_first_out", "push 1, 2, 3; pop four times", "(s.pop(), s.pop(), s.pop(), s.pop())", "(Some(3), Some(2), Some(1), None)",
       setup="let mut s = Stack::new();\ns.push(1);\ns.push(2);\ns.push(3);"),
     T("empty", "a new Stack<i32>", "(s.len(), s.is_empty(), s.peek().copied(), s.pop())", "(0, true, None::<i32>, None::<i32>)",
       setup="let mut s: Stack<i32> = Stack::new();"),
     T("peek_keeps_the_item", "push \"a\", \"b\"; peek twice, then len", "(s.peek().map(String::as_str), s.peek().map(String::as_str), s.len())", '(Some("b"), Some("b"), 2)',
       setup='let mut s = Stack::new();\ns.push("a".to_string());\ns.push("b".to_string());'),
     T("peek_mut_edits_the_top", "push 1, 2; add 10 through peek_mut; pop twice", "(s.pop(), s.pop())", "(Some(12), Some(1))",
       setup="let mut s = Stack::new();\ns.push(1);\ns.push(2);\n*s.peek_mut().unwrap() += 10;"),
     T("no_bounds_on_t", "a type with no derives: push Token(1), Token(2); pop", "(s.pop().map(|t| t.0), s.len())", "(Some(2), 1)",
       setup="struct Token(u32);\nlet mut s = Stack::new();\ns.push(Token(1));\ns.push(Token(2));")],
    [T("push_after_emptying", "push 1, pop, pop, push 2, peek", "(a, b, s.peek().copied())", "(Some(1), None, Some(2))",
       setup="let mut s = Stack::new();\ns.push(1);\nlet a = s.pop();\nlet b = s.pop();\ns.push(2);"),
     T("len_counts", "push 5 items, pop 2", "(s.len(), s.is_empty())", "(3, false)",
       setup="let mut s = Stack::new();\nfor i in 0..5 {\n    s.push(i);\n}\ns.pop();\ns.pop();"),
     T("empty_again", "push 1, pop", "(s.len(), s.is_empty(), s.peek().is_none())", "(0, true, true)",
       setup="let mut s = Stack::new();\ns.push(1);\ns.pop();"),
     T("peek_mut_on_empty", "peek_mut on a new stack", "s.peek_mut().is_none()", "true", setup="let mut s: Stack<String> = Stack::new();"),
     T("pop_hands_over_ownership", "push \"hi\"; pop and append \"!\"", "got", '"hi!".to_string()',
       setup='let mut s = Stack::new();\ns.push(String::from("hi"));\nlet mut got = s.pop().unwrap();\ngot.push(\'!\');'),
     T("boxed_closures", "a Stack<Box<dyn Fn(i32) -> i32>>: push +1, then *2; pop and call with 5", "(f(5), g(5))", "(10, 6)",
       setup="let mut s: Stack<Box<dyn Fn(i32) -> i32>> = Stack::new();\ns.push(Box::new(|x| x + 1));\ns.push(Box::new(|x| x * 2));\nlet f = s.pop().unwrap();\nlet g = s.pop().unwrap();"),
     T("zero_sized_items", "push () three times", "(s.len(), s.pop(), s.len())", "(3, Some(()), 2)",
       setup="let mut s = Stack::new();\nfor _ in 0..3 {\n    s.push(());\n}"),
     T("drops_its_items", "push two Rc clones, drop the stack", "std::rc::Rc::strong_count(&rc)", "1",
       setup="let rc = std::rc::Rc::new(5);\nlet mut s = Stack::new();\ns.push(rc.clone());\ns.push(rc.clone());\ndrop(s);"),
     T("peek_mut_then_peek", "push \"a\"; push_str \"b\" through peek_mut; peek", "s.peek().map(String::as_str)", 'Some("ab")',
       setup='let mut s = Stack::new();\ns.push(String::from("a"));\ns.peek_mut().unwrap().push_str("b");'),
     """
     #[test]
     fn random_vs_vec_model() {
         let mut rng = anneal_prelude::Rng::new(4501);
         for _ in 0..300 {
             let mut s = Stack::new();
             let mut model: Vec<i64> = Vec::new();
             let ops = rng.below(20);
             let mut log = Vec::new();
             for _ in 0..ops {
                 match rng.below(4) {
                     0 | 1 => {
                         let x = rng.int(-9, 9);
                         log.push(format!("push {x}"));
                         s.push(x);
                         model.push(x);
                     }
                     2 => {
                         log.push("pop".to_string());
                         check!(format!("{log:?}"), s.pop(), model.pop());
                     }
                     _ => {
                         log.push("peek_mut += 1".to_string());
                         if let Some(t) = s.peek_mut() {
                             *t += 1;
                         }
                         if let Some(t) = model.last_mut() {
                             *t += 1;
                         }
                     }
                 }
                 check!(format!("{log:?}"), (s.len(), s.is_empty(), s.peek().copied()), (model.len(), model.is_empty(), model.last().copied()));
             }
         }
     }

     #[test]
     fn scale_push_pop() {
         let n = 400_000u64;
         let mut s = Stack::new();
         for i in 0..n {
             s.push(i);
         }
         let mut sum = 0u64;
         let mut last = n;
         while let Some(x) = s.pop() {
             assert!(x < last, "popped {x} after {last}");
             last = x;
             sum += x;
         }
         check!("push 0..400000, pop all", sum, n * (n - 1) / 2);
     }
     """],
    [("rust", "Every method is one call on the inner `Vec`: `push`, `pop`, `last`, `last_mut`, `len`, `is_empty`."),
     ("rust", "`Vec::pop` already returns `Option<T>`, so an empty stack needs no special case."),
     ("edge", "`peek` returns `Option<&T>`: a borrow, so it needs no `Clone` bound and doesn't move the item out.")],
    ("A generic type is written once and compiled for each `T` it's used with. `impl<T>` with no bounds means every method must work for any `T`, which is why `peek` lends a reference instead of copying.", "O(1) amortised per operation", "O(n)"),
    "Why does `peek` return `Option<&T>` rather than `Option<T>`? What bound would `Option<T>` need?",
    ["`struct Stack<T>` and `impl<T> Stack<T>`.", "Don't add `Clone`/`Copy`/`Debug` bounds a container doesn't need."],
    source="W1", related=("L5", "S3"),
    wrong=dict(
        queue_order="""
            pub struct Stack<T> {
                items: Vec<T>,
            }

            impl<T> Stack<T> {
                pub fn new() -> Self {
                    Stack { items: Vec::new() }
                }

                pub fn push(&mut self, item: T) {
                    self.items.push(item);
                }

                /// Removes and returns the top item.
                pub fn pop(&mut self) -> Option<T> {
                    if self.items.is_empty() { None } else { Some(self.items.remove(0)) }
                }

                /// The top item, without removing it.
                pub fn peek(&self) -> Option<&T> {
                    self.items.last()
                }

                /// Lets the caller change the top item in place.
                pub fn peek_mut(&mut self) -> Option<&mut T> {
                    self.items.last_mut()
                }

                pub fn len(&self) -> usize {
                    self.items.len()
                }

                pub fn is_empty(&self) -> bool {
                    self.items.is_empty()
                }
            }
        """,
        top_at_the_front="""
            pub struct Stack<T> {
                items: Vec<T>,
            }

            impl<T> Stack<T> {
                pub fn new() -> Self {
                    Stack { items: Vec::new() }
                }

                pub fn push(&mut self, item: T) {
                    self.items.insert(0, item);
                }

                /// Removes and returns the top item.
                pub fn pop(&mut self) -> Option<T> {
                    if self.items.is_empty() { None } else { Some(self.items.remove(0)) }
                }

                /// The top item, without removing it.
                pub fn peek(&self) -> Option<&T> {
                    self.items.first()
                }

                /// Lets the caller change the top item in place.
                pub fn peek_mut(&mut self) -> Option<&mut T> {
                    self.items.first_mut()
                }

                pub fn len(&self) -> usize {
                    self.items.len()
                }

                pub fn is_empty(&self) -> bool {
                    self.items.is_empty()
                }
            }
        """,
        peek_at_the_bottom="""
            pub struct Stack<T> {
                items: Vec<T>,
            }

            impl<T> Stack<T> {
                pub fn new() -> Self {
                    Stack { items: Vec::new() }
                }

                pub fn push(&mut self, item: T) {
                    self.items.push(item);
                }

                /// Removes and returns the top item.
                pub fn pop(&mut self) -> Option<T> {
                    self.items.pop()
                }

                /// The top item, without removing it.
                pub fn peek(&self) -> Option<&T> {
                    self.items.first()
                }

                /// Lets the caller change the top item in place.
                pub fn peek_mut(&mut self) -> Option<&mut T> {
                    self.items.last_mut()
                }

                pub fn len(&self) -> usize {
                    self.items.len()
                }

                pub fn is_empty(&self) -> bool {
                    self.items.is_empty()
                }
            }
        """,
    ),
))

P.append(fix(
    "fix-missing-bound", "Fix: missing bound (E0369)", "easy", "generic-code", ["E0369", "trait bounds", "PartialOrd"],
    "`largest` should return the largest item (the first one on a tie), or `None` for an empty slice. It doesn't compile.",
    """
    /// The largest item; the first one on a tie. None if `items` is empty.
    pub fn largest<T>(items: &[T]) -> Option<&T> {
        let mut best = items.first()?;
        for item in items {
            if item > best {
                best = item;
            }
        }
        Some(best)
    }
    """,
    """
    /// The largest item; the first one on a tie. None if `items` is empty.
    pub fn largest<T: PartialOrd>(items: &[T]) -> Option<&T> {
        let mut best = items.first()?;
        for item in items {
            if item > best {
                best = item;
            }
        }
        Some(best)
    }
    """,
    [T("integers", "[3, 7, 2]", "largest(&[3, 7, 2])", "Some(&7)"),
     T("empty", "[] of i32", "largest::<i32>(&[])", "None"),
     T("floats", "[1.5, -2.0, 0.25]", "largest(&[1.5, -2.0, 0.25])", "Some(&1.5)"),
     T("strs", '["pear", "apple", "zoo"]', 'largest(&["pear", "apple", "zoo"])', 'Some(&"zoo")'),
     T("tie_returns_the_first", "[5, 1, 5]: which 5?", "std::ptr::eq(largest(&v).unwrap(), &v[0])", "true", setup="let v = [5, 1, 5];")],
    [T("single", "[42]", "largest(&[42])", "Some(&42)"),
     T("negatives", "[-3, -1, -2]", "largest(&[-3, -1, -2])", "Some(&-1)"),
     T("extremes", "[i64::MIN, i64::MAX, 0]", "largest(&[i64::MIN, i64::MAX, 0])", "Some(&i64::MAX)"),
     T("uppercase_sorts_first", '["apple", "Zebra"]', 'largest(&["apple", "Zebra"])', 'Some(&"apple")'),
     T("strings", 'Strings ["b", "ab", "ba"]', "largest(&v).map(String::as_str)", 'Some("ba")',
       setup='let v = vec![String::from("b"), String::from("ab"), String::from("ba")];'),
     T("chars", "['q', 'z', 'a']", "largest(&['q', 'z', 'a'])", "Some(&'z')"),
     T("tuples", "[(1, 9), (2, 0), (2, -1)]", "largest(&[(1, 9), (2, 0), (2, -1)])", "Some(&(2, 0))"),
     T("all_equal", "[7, 7, 7]: which 7?", "std::ptr::eq(largest(&v).unwrap(), &v[0])", "true", setup="let v = [7, 7, 7];"),
     T("only_partial_ord", "a PartialOrd-only struct with an f64 field", "largest(&v).map(|w| w.0)", "Some(2.5)",
       setup="#[derive(PartialEq, PartialOrd)]\nstruct Weight(f64);\nlet v = [Weight(1.0), Weight(2.5), Weight(-4.0)];"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(4502);
         for _ in 0..300 {
             let n = rng.below(8);
             let v: Vec<i32> = rng.vec(n, -5, 5);
             let mut want: Option<usize> = None;
             for i in 0..v.len() {
                 if want.map_or(true, |w| v[i] > v[w]) {
                     want = Some(i);
                 }
             }
             check!(format!("items = {v:?}"), largest(&v).map(|r| r as *const i32), want.map(|i| &v[i] as *const i32));
         }
     }
     """],
    [("rust", "`largest` only uses `>` on the items. Which trait provides `>`?"),
     ("rust", "Add the bound in the generic parameter list: `<T: PartialOrd>`. `PartialOrd` rather than `Ord` keeps `f64` working.")],
    ("Inside a generic function the compiler only lets you do what the bounds promise. `>` comes from `PartialOrd`, so the signature has to ask for it.", "O(n)", "O(1)"),
    "Why does `Ord` reject `f64` while `PartialOrd` accepts it? What happens here if the slice holds a NaN?",
    ["A generic function can only use what its bounds promise.", "Comparison operators come from `PartialOrd`; pick the weakest bound that works."],
    rules=dict(lines=1),
    wrong=dict(
        ties_go_last="""
            /// The largest item; the first one on a tie. None if `items` is empty.
            pub fn largest<T: PartialOrd>(items: &[T]) -> Option<&T> {
                let mut best = items.first()?;
                for item in items {
                    if item >= best {
                        best = item;
                    }
                }
                Some(best)
            }
        """,
        smallest="""
            /// The largest item; the first one on a tie. None if `items` is empty.
            pub fn largest<T: PartialOrd>(items: &[T]) -> Option<&T> {
                let mut best = items.first()?;
                for item in items {
                    if item < best {
                        best = item;
                    }
                }
                Some(best)
            }
        """,
    ),
))

PAIR_TAIL = """
impl<T> Pair<T> {
    pub fn new(first: T, second: T) -> Self {
        Pair { first, second }
    }

    /// The same pair with its halves exchanged.
    pub fn swap(self) -> Pair<T> {
        Pair { first: self.second, second: self.first }
    }
}
"""

PAIR_HEAD = """
use std::fmt;

/// Two values of the same type.
#[derive(Debug, PartialEq)]
pub struct Pair<T> {
    pub first: T,
    pub second: T,
}
"""


def pair(impl_line, fmt_line='write!(f, "({}, {})", self.first, self.second)'):
    return PAIR_HEAD + PAIR_TAIL + f"""
/// Prints as `(first, second)`.
{impl_line}
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {{
        {fmt_line}
    }}
}}
"""


P.append(fix(
    "fix-bound-on-the-impl", "Fix: the bound belongs on the impl (E0277)", "easy", "generic-code", ["E0277", "trait bounds", "Display"],
    """
        `Pair<T>` should print as `(first, second)` whenever `T` can be printed, and `new` and `swap` should work for
        any `T`, printable or not. It doesn't compile.
    """,
    pair("impl<T> fmt::Display for Pair<T> {"),
    pair("impl<T: fmt::Display> fmt::Display for Pair<T> {"),
    [T("integers", "Pair::new(1, 2)", "Pair::new(1, 2).to_string()", '"(1, 2)"'),
     T("strs", 'Pair::new("a", "b")', 'Pair::new("a", "b").to_string()', '"(a, b)"'),
     T("swap", "Pair::new(1, 2).swap()", "Pair::new(1, 2).swap()", "Pair { first: 2, second: 1 }"),
     T("swap_works_without_display", "a type that isn't Display: Pair::new(Opaque(1), Opaque(2)).swap()", "Pair::new(Opaque(1), Opaque(2)).swap()",
       "Pair { first: Opaque(2), second: Opaque(1) }", setup="#[derive(Debug, PartialEq)]\nstruct Opaque(u8);"),
     T("nested", "Pair::new(Pair::new(1, 2), Pair::new(3, 4))", "Pair::new(Pair::new(1, 2), Pair::new(3, 4)).to_string()", '"((1, 2), (3, 4))"')],
    [T("strings", 'Pair::new(String::from("x"), String::from("y"))', 'Pair::new(String::from("x"), String::from("y")).to_string()', '"(x, y)"'),
     T("floats", "Pair::new(1.5, -0.25)", "Pair::new(1.5, -0.25).to_string()", '"(1.5, -0.25)"'),
     T("chars", "Pair::new('a', 'é')", "Pair::new('a', 'é').to_string()", '"(a, é)"'),
     T("empty_strs", 'Pair::new("", "")', 'Pair::new("", "").to_string()', '"(, )"'),
     T("swap_then_print", "Pair::new(1, 2).swap()", "Pair::new(1, 2).swap().to_string()", '"(2, 1)"'),
     T("in_format", 'format!("p = {}", Pair::new(3, 4))', 'format!("p = {}", Pair::new(3, 4))', '"p = (3, 4)"'),
     T("new_without_display", "Pair::new(vec![1], vec![2]) (Vec isn't Display)", "Pair::new(vec![1], vec![2]).first", "vec![1]"),
     T("swap_twice", "Pair::new(Opaque(1), Opaque(2)).swap().swap()", "Pair::new(Opaque(1), Opaque(2)).swap().swap()",
       "Pair { first: Opaque(1), second: Opaque(2) }", setup="#[derive(Debug, PartialEq)]\nstruct Opaque(u8);"),
     T("unicode_strings", 'Pair::new("héllo", "wörld")', 'Pair::new("héllo", "wörld").to_string()', '"(héllo, wörld)"'),
     """
     #[test]
     fn random_vs_format() {
         let mut rng = anneal_prelude::Rng::new(4503);
         for _ in 0..200 {
             let (a, b) = (rng.int(-1000, 1000), rng.int(-1000, 1000));
             check!(format!("Pair::new({a}, {b})"), Pair::new(a, b).to_string(), format!("({a}, {b})"));
             check!(format!("Pair::new({a}, {b}).swap()"), Pair::new(a, b).swap(), Pair { first: b, second: a });
         }
     }
     """],
    [("rust", "`{}` needs `T: Display`. Only the `Display` impl formats `T`, so only that impl needs the bound."),
     ("rust", "Putting `T: Display` on the struct itself would make every `Pair` need it, and the `swap` tests would stop compiling.")],
    ("Bounds on an `impl` block apply only to that impl: `Pair<Vec<i32>>` still has `new` and `swap`, it just isn't `Display`. std does the same: `Vec<T>` exists for any `T`, and is `Clone` only when `T: Clone`.", "O(1)", "O(1)"),
    "Why do most std types put bounds on their impls rather than on the struct definition?",
    ["Put a bound on the impl that needs it, not on the type.", "Conditional trait impls: `impl<T: Display> Display for Pair<T>`."],
    rules=dict(lines=1),
    wrong=dict(
        debug_instead="""
            use std::fmt;

            /// Two values of the same type.
            #[derive(Debug, PartialEq)]
            pub struct Pair<T> {
                pub first: T,
                pub second: T,
            }

            impl<T> Pair<T> {
                pub fn new(first: T, second: T) -> Self {
                    Pair { first, second }
                }

                /// The same pair with its halves exchanged.
                pub fn swap(self) -> Pair<T> {
                    Pair { first: self.second, second: self.first }
                }
            }

            /// Prints as `(first, second)`.
            impl<T: fmt::Debug> fmt::Display for Pair<T> {
                fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
                    write!(f, "({:?}, {:?})", self.first, self.second)
                }
            }
        """,
        swap_is_a_copy="""
            use std::fmt;

            /// Two values of the same type.
            #[derive(Debug, PartialEq)]
            pub struct Pair<T> {
                pub first: T,
                pub second: T,
            }

            impl<T> Pair<T> {
                pub fn new(first: T, second: T) -> Self {
                    Pair { first, second }
                }

                /// The same pair with its halves exchanged.
                pub fn swap(self) -> Pair<T> {
                    self
                }
            }

            /// Prints as `(first, second)`.
            impl<T: fmt::Display> fmt::Display for Pair<T> {
                fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
                    write!(f, "({}, {})", self.first, self.second)
                }
            }
        """,
    ),
))


def max_by_key(sig_extra, body):
    return f"""
/// The item with the largest key; the first one on a tie. Calls `key` once per item.
pub fn max_by_key<T, K, F>(items: &[T], mut key: F) -> Option<&T>
where
    F: FnMut(&T) -> K,{sig_extra}
{{
{body}
}}
"""


MAX_BY_KEY_BODY = """    let mut best: Option<(&T, K)> = None;
    for item in items {
        let k = key(item);
        // Strictly greater, so the first of equal keys stays.
        if best.as_ref().map_or(true, |(_, bk)| k > *bk) {
            best = Some((item, k));
        }
    }
    best.map(|(item, _)| item)"""

P.append(write(
    "generic-max-by-key", "Generic max_by_key", "medium", "generic-code", ["generics", "FnMut", "trait bounds"],
    """
        Write `max_by_key`: the item whose `key` is largest, or `None` for an empty slice. On a tie, return the
        **first** such item (`Iterator::max_by_key` returns the last one, so don't just call it).

        Call `key` exactly once per item: it may be expensive. The keys can be any ordered type, including ones
        that aren't `Copy` or `Clone`, like `String`. Add the bounds the body needs.
    """,
    max_by_key("", "    todo!()"),
    max_by_key("\n    K: Ord,", MAX_BY_KEY_BODY),
    [T("longest_word", '["apple", "fig", "banana"], key = len', 'max_by_key(&["apple", "fig", "banana"], |w| w.len())', 'Some(&"banana")'),
     T("empty", "[], key = identity", "max_by_key(&[] as &[i32], |x| *x)", "None"),
     T("tie_returns_the_first", '["ab", "cd", "e"], key = len', 'max_by_key(&["ab", "cd", "e"], |w| w.len())', 'Some(&"ab")'),
     T("key_called_once_per_item", "[4, 9, 2, 9], count the calls", "(best, calls)", "(Some(9), 4)",
       setup="let v = [4, 9, 2, 9];\nlet mut calls = 0;\nlet best = max_by_key(&v, |x| {\n    calls += 1;\n    *x\n}).copied();"),
     T("owned_string_key", "people by name, key = name.to_lowercase()", "max_by_key(&people, |p| p.0.to_lowercase()).map(|p| p.1)", "Some(31)",
       setup='let people = [("ada", 36), ("Zed", 31), ("bob", 25)];')],
    [T("single", "[5], key = identity", "max_by_key(&[5], |x| *x)", "Some(&5)"),
     T("negated_key_finds_min", "[3, -2, 8], key = -x", "max_by_key(&[3, -2, 8], |x: &i32| -x)", "Some(&-2)"),
     T("all_ties_first", "[1, 2, 3], key = constant 0: which item?", "std::ptr::eq(max_by_key(&v, |_| 0).unwrap(), &v[0])", "true", setup="let v = [1, 2, 3];"),
     T("reverse_key_first_min", "[3, 1, 1], key = Reverse(x): which 1?", "std::ptr::eq(max_by_key(&v, |x| std::cmp::Reverse(*x)).unwrap(), &v[1])", "true",
       setup="let v = [3, 1, 1];"),
     T("tuple_key", "(dept, age) key", "max_by_key(&v, |p| (p.1, p.2)).map(|p| p.0)", 'Some("c")',
       setup='let v = [("a", 1, 30), ("b", 2, 20), ("c", 2, 25)];'),
     T("calls_on_empty", "[] counts the calls", "calls", "0",
       setup="let v: [i32; 0] = [];\nlet mut calls = 0;\nlet _ = max_by_key(&v, |x| {\n    calls += 1;\n    *x\n});"),
     T("calls_with_many_ties", "[7; 6], count the calls", "calls", "6",
       setup="let v = [7; 6];\nlet mut calls = 0;\nlet _ = max_by_key(&v, |x| {\n    calls += 1;\n    *x\n});"),
     T("no_clone_items_or_keys", "items and keys that are neither Clone nor Copy", "max_by_key(&v, |x| Key(x.0 * 2)).map(|x| x.0)", "Some(5)",
       setup="#[derive(PartialEq, Eq, PartialOrd, Ord)]\nstruct Key(i32);\nstruct Item(i32);\nlet v = [Item(1), Item(5), Item(-3)];"),
     T("extremes", "[i64::MIN, i64::MAX], key = identity", "max_by_key(&[i64::MIN, i64::MAX], |x| *x)", "Some(&i64::MAX)"),
     T("unicode_len", '["éé", "abc"], key = chars().count()', 'max_by_key(&["éé", "abc"], |w| w.chars().count())', 'Some(&"abc")'),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(4504);
         for _ in 0..300 {
             let n = rng.below(8);
             let words: Vec<String> = (0..n).map(|_| { let len = rng.below(4); rng.string(len, "ab") }).collect();
             let mut want: Option<usize> = None;
             for i in 0..n {
                 if want.map_or(true, |w| words[i].len() > words[w].len()) {
                     want = Some(i);
                 }
             }
             let mut calls = 0;
             let got = max_by_key(&words, |w| {
                 calls += 1;
                 w.len()
             });
             check!(format!("words = {words:?}"), (got.map(|r| r as *const String), calls), (want.map(|i| &words[i] as *const String), n));
         }
     }
     """],
    [("approach", "Walk the items once, keeping the best item together with its key, so the best key is never recomputed."),
     ("rust", "Comparing keys needs `K: Ord`. Store `Option<(&T, K)>`; comparing `k > *bk` borrows the stored key instead of copying it."),
     ("edge", "Use strictly greater (`>`), so an equal key later on doesn't replace the first.")],
    ("The bounds say exactly what the body uses: `F: FnMut(&T) -> K` to call the key (mutably, so it can count or cache), `K: Ord` to compare. No `Clone` or `Copy` is needed because the best key is kept, not re-made.", "O(n) key calls", "O(1)"),
    "Why `FnMut` rather than `Fn` for `key`? What would a caller lose if you asked for `Fn`?",
    ["Choose bounds from what the body does: calling `key` needs `FnMut`, comparing needs `Ord`.", "Keep computed keys instead of calling the closure twice."],
    related=("L5", "S6", "L6"),
    wrong=dict(
        std_ties_go_last=max_by_key("\n    K: Ord,", "    items.iter().max_by_key(|x| key(x))"),
        recomputes_best_key=max_by_key("\n    K: Ord,", """    let mut best: Option<&T> = None;
    for item in items {
        if best.map_or(true, |b| key(item) > key(b)) {
            best = Some(item);
        }
    }
    best"""),
    ),
))

STAGES = [
    ("generic-code", "Generic code", "easy"),
]

# `source` and `examples` are optional; drop empty ones so problem.toml stays tidy.
for p in P:
    if not p.get("source"):
        p.pop("source", None)
    if p.get("rules") is None:
        p.pop("rules", None)
    if p.get("wrong") is None:
        p.pop("wrong", None)

if __name__ == "__main__":
    n = write_track("l5-generics", "L5", "Generics & associated types", "L", "core", 5,
                    "Generic code is written once and compiled per type. Bounds say what a type must do; associated types, const generics and marker types move rules into the type checker.",
                    STAGES, P)
    print("L5", n)
