from author import T, write_track

HM = "std::collections::HashMap"
P = []


def fix(slug, title, level, stage, tags, statement, starter, solution, visible, hidden, hints, notes, follow_up, teaches, rules=None, related=("L2",)):
    return dict(slug=slug, title=title, mode="fix", level=level, stage=stage, tags=tags, statement=statement, starter=starter,
                solution=solution, visible=visible, hidden=hidden, hints=hints, notes=notes, follow_up=follow_up,
                teaches=teaches, rules=rules or dict(methods=["clone"]), related=list(related))


def write(slug, title, level, stage, tags, statement, starter, solution, visible, hidden, hints, notes, follow_up, teaches, related=("L2",)):
    return dict(slug=slug, title=title, level=level, stage=stage, tags=tags, statement=statement, starter=starter,
                solution=solution, visible=visible, hidden=hidden, hints=hints, notes=notes, follow_up=follow_up,
                teaches=teaches, related=list(related))


# ---------------------------------------------------------------- shared vs unique (easy)

P.append(fix(
    "fix-push-while-holding-a-reference", "Fix: push while holding a reference", "easy", "shared-vs-unique", ["E0502"],
    "`add_and_max` should push `x` and return the largest value including `x`. It doesn't compile.",
    """
    /// Pushes `x` and returns the largest value, which may be `x`.
    pub fn add_and_max(v: &mut Vec<i32>, x: i32) -> i32 {
        let max = v.iter().max().unwrap_or(&x);
        v.push(x);
        *max.max(&x)
    }
    """,
    """
    /// Pushes `x` and returns the largest value, which may be `x`.
    pub fn add_and_max(v: &mut Vec<i32>, x: i32) -> i32 {
        let max = v.iter().copied().max().unwrap_or(x);
        v.push(x);
        max.max(x)
    }
    """,
    [T("larger_exists", "v = [3, 9], x = 4", "{ let mut v = vec![3, 9]; (add_and_max(&mut v, 4), v) }", "(9, vec![3, 9, 4])"),
     T("x_is_max", "v = [1], x = 5", "{ let mut v = vec![1]; add_and_max(&mut v, 5) }", "5")],
    [T("empty", "v = [], x = -2", "{ let mut v = vec![]; (add_and_max(&mut v, -2), v) }", "(-2, vec![-2])")],
    [("rust", "`max` is a reference into `v`, still in use after `push`. A push can reallocate the Vec and leave it dangling."),
     ("rust", "Copy the number out (`copied()`) so nothing borrows `v` across the push.")],
    ("An `i32` is `Copy`, so holding the value instead of `&i32` ends the borrow before the push.", "O(n)", "O(1)"),
    "Why is holding a reference into a Vec across a push unsound, even if the Vec doesn't reallocate?",
    ["A shared borrow into a Vec forbids mutating the Vec until the borrow's last use.", "Copy small values out instead of holding references."],
    rules=dict(methods=["clone"], lines=2),
))

P.append(write(
    "many-readers-one-writer", "Many readers, one writer", "easy", "shared-vs-unique", ["&T", "&mut T"],
    "Implement `Counter`: `total` and `busiest` only read and take `&self`; `hit` changes a slot and takes `&mut self`.",
    """
    pub struct Counter {
        hits: Vec<u32>,
    }

    impl Counter {
        pub fn new(slots: usize) -> Self {
            todo!()
        }

        pub fn hit(&mut self, slot: usize) {
            todo!()
        }

        pub fn total(&self) -> u32 {
            todo!()
        }

        /// The slot with the most hits; the lowest index on a tie; None if there are no slots.
        pub fn busiest(&self) -> Option<usize> {
            todo!()
        }
    }
    """,
    """
    pub struct Counter {
        hits: Vec<u32>,
    }

    impl Counter {
        pub fn new(slots: usize) -> Self {
            Counter { hits: vec![0; slots] }
        }

        pub fn hit(&mut self, slot: usize) {
            self.hits[slot] += 1;
        }

        pub fn total(&self) -> u32 {
            self.hits.iter().sum()
        }

        /// The slot with the most hits; the lowest index on a tie; None if there are no slots.
        pub fn busiest(&self) -> Option<usize> {
            let max = *self.hits.iter().max()?;
            self.hits.iter().position(|&h| h == max)
        }
    }
    """,
    [T("counts", "3 slots, hits on 1, 1, 2", "{ let mut c = Counter::new(3); c.hit(1); c.hit(1); c.hit(2); let (a, b) = (&c, &c); (a.total(), b.busiest()) }", "(3, Some(1))"),
     T("no_hits", "2 slots, no hits", "Counter::new(2).busiest()", "Some(0)")],
    [T("no_slots", "0 slots", "(Counter::new(0).total(), Counter::new(0).busiest())", "(0, None)")],
    [("rust", "Methods that only read take `&self`, so any number of callers can hold one at once.")],
    ("`busiest` returns an index, not a reference, so callers can keep it while hitting more slots.", "O(n)", "O(1)"),
    "Why does `Vec::iter().max()` return the last maximum but `position` the first?",
    ["`&self` methods can run while other shared borrows are alive.", "`&mut self` requires that no other borrow exists."],
))

P.append(fix(
    "fix-mut-from-shared-self", "Fix: returning &mut from &self", "easy", "shared-vs-unique", ["E0596"],
    "`top_mut` should let the caller edit the top of the stack in place. It doesn't compile.",
    """
    pub struct Stack {
        items: Vec<i32>,
    }

    impl Stack {
        pub fn new() -> Self {
            Stack { items: Vec::new() }
        }

        pub fn push(&mut self, x: i32) {
            self.items.push(x);
        }

        /// The top item, for editing in place.
        pub fn top_mut(&self) -> Option<&mut i32> {
            self.items.last_mut()
        }
    }
    """,
    """
    pub struct Stack {
        items: Vec<i32>,
    }

    impl Stack {
        pub fn new() -> Self {
            Stack { items: Vec::new() }
        }

        pub fn push(&mut self, x: i32) {
            self.items.push(x);
        }

        /// The top item, for editing in place.
        pub fn top_mut(&mut self) -> Option<&mut i32> {
            self.items.last_mut()
        }
    }
    """,
    [T("edit_top", "push 1, 2; add 10 to the top", "{ let mut s = Stack::new(); s.push(1); s.push(2); *s.top_mut().unwrap() += 10; s.top_mut().copied() }", "Some(12)"),
     T("empty", "new stack", "Stack::new().top_mut().is_none()", "true")],
    [T("only_top_changes", "push 5, 6; set top to 0", "{ let mut s = Stack::new(); s.push(5); s.push(6); if let Some(t) = s.top_mut() { *t = 0; } s.items_for_test() }", "vec![5, 0]")],
    [("rust", "You can't get a `&mut` to something through a `&`. What does the method need to take?")],
    ("A `&mut` out needs a `&mut` in: `&self` promises the method changes nothing.", "O(1)", "O(1)"),
    "What's the difference between `&mut self` and `mut self` in a method signature?",
    ["You can only hand out `&mut` to data you have `&mut` access to.", "The receiver type is part of the API contract."],
    rules=dict(lines=1),
))
# The hidden test above reads the items through a helper; add it to both versions.
for key in ("starter", "solution"):
    P[-1][key] = P[-1][key].rstrip() + """

    impl Stack {
        /// For tests.
        pub fn items_for_test(&self) -> Vec<i32> {
            self.items.to_vec()
        }
    }
    """

P.append(write(
    "most-repeated-word", "Count words without cloning", "easy", "shared-vs-unique", ["&str", "HashMap"],
    "Return the most repeated word in `text` (ties: alphabetically first), as a slice of `text`. Don't allocate a `String` per word.",
    """
    pub fn most_repeated(text: &str) -> Option<&str> {
        todo!()
    }
    """,
    """
    use std::collections::HashMap;

    pub fn most_repeated(text: &str) -> Option<&str> {
        let mut counts: HashMap<&str, usize> = HashMap::new();
        for w in text.split_whitespace() {
            *counts.entry(w).or_insert(0) += 1;
        }
        counts.into_iter().max_by(|a, b| a.1.cmp(&b.1).then_with(|| b.0.cmp(a.0))).map(|(w, _)| w)
    }
    """,
    [T("repeated", "\"b a b c a b\"", "most_repeated(&text)", 'Some("b")', setup='let text = String::from("b a b c a b");'),
     T("empty", "\"\"", 'most_repeated("")', "None")],
    [T("tie", "\"x y y x\"", 'most_repeated("x y y x")', 'Some("x")')],
    [("rust", "Keys can be `&str` slices of `text`; the map then borrows `text` instead of owning copies.")],
    ("The result borrows from `text`, so the signature's elided lifetime ties it to the input.", "O(n)", "O(k)"),
    "What stops you from returning a key of the map after the map is dropped?",
    ["Borrowed keys in a `HashMap<&str, usize>`.", "Returning a slice of the input."],
    related=("L2", "S4"),
))

P.append(fix(
    "fix-mutate-through-shared-ref", "Fix: mutate through a shared reference", "easy", "shared-vs-unique", ["E0594"],
    "`deposit_all` should add `amount` to every account. It doesn't compile.",
    """
    pub struct Account {
        pub balance: i64,
    }

    /// Adds `amount` to every account.
    pub fn deposit_all(accounts: &[Account], amount: i64) {
        for a in accounts {
            a.balance += amount;
        }
    }
    """,
    """
    pub struct Account {
        pub balance: i64,
    }

    /// Adds `amount` to every account.
    pub fn deposit_all(accounts: &mut [Account], amount: i64) {
        for a in accounts {
            a.balance += amount;
        }
    }
    """,
    [T("deposits", "balances [1, 2], amount 5", "{ let mut a = [Account { balance: 1 }, Account { balance: 2 }]; deposit_all(&mut a, 5); (a[0].balance, a[1].balance) }", "(6, 7)")],
    [T("empty", "no accounts", "{ let mut a: [Account; 0] = []; deposit_all(&mut a, 5); a.len() }", "0")],
    [("rust", "Iterating a `&[T]` gives `&T`. What do you iterate to get `&mut T`?")],
    ("Iterating `&mut [T]` yields `&mut T`, so the loop body needs no change.", "O(n)", "O(1)"),
    "Why can't `&T` be used to mutate, even when nobody else holds a reference?",
    ["Writing through a reference needs `&mut`.", "`for x in slice` yields `&T` or `&mut T` depending on the slice."],
    rules=dict(lines=1),
))

P.append(write(
    "split-first-mut", "Unique, not mutable: split_first_mut", "easy", "shared-vs-unique", ["split_first_mut", "&mut"],
    "Add the first element to every other element of `v`, in place.",
    """
    pub fn add_head_to_rest(v: &mut [i32]) {
        todo!()
    }
    """,
    """
    pub fn add_head_to_rest(v: &mut [i32]) {
        if let Some((head, rest)) = v.split_first_mut() {
            for x in rest {
                *x += *head;
            }
        }
    }
    """,
    [T("adds", "v = [10, 1, 2]", "{ let mut v = [10, 1, 2]; add_head_to_rest(&mut v); v }", "[10, 11, 12]"),
     T("single", "v = [5]", "{ let mut v = [5]; add_head_to_rest(&mut v); v }", "[5]")],
    [T("empty", "v = []", "{ let mut v: [i32; 0] = []; add_head_to_rest(&mut v); v }", "[]")],
    [("rust", "`&v[0]` and `&mut v[1..]` at once won't compile. `split_first_mut` splits one borrow into two that can't overlap.")],
    ("`&mut` means exclusive access, not merely writable: two parts of a slice need two borrows that provably don't overlap.", "O(n)", "O(1)"),
    "How would you do the same with `split_at_mut(1)`?",
    ["`&mut` is about uniqueness: no other reference may overlap it.", "`split_first_mut` returns the head and the rest as separate borrows."],
))

# ---------------------------------------------------------------- where borrows end (easy)

P.append(fix(
    "fix-borrow-kept-alive", "Fix: a borrow kept alive by a later use", "easy", "where-borrows-end", ["E0499", "NLL"],
    "`shout_first` should uppercase the first name and then append `!` to every name. It doesn't compile.",
    """
    /// Uppercases the first name, then appends "!" to every name.
    pub fn shout_first(names: &mut Vec<String>) {
        let first = &mut names[0];
        for n in names.iter_mut() {
            n.push('!');
        }
        first.make_ascii_uppercase();
    }
    """,
    """
    /// Uppercases the first name, then appends "!" to every name.
    pub fn shout_first(names: &mut Vec<String>) {
        let first = &mut names[0];
        first.make_ascii_uppercase();
        for n in names.iter_mut() {
            n.push('!');
        }
    }
    """,
    [T("two", "names = [\"ann\", \"bo\"]", '{ let mut v = vec!["ann".to_string(), "bo".to_string()]; shout_first(&mut v); v }', 'vec!["ANN!".to_string(), "bo!".to_string()]')],
    [T("one", "names = [\"x\"]", '{ let mut v = vec!["x".to_string()]; shout_first(&mut v); v }', 'vec!["X!".to_string()]')],
    [("rust", "A borrow lasts until its last use. Where is `first` last used?")],
    ("With non-lexical lifetimes, `first`'s borrow ends after `make_ascii_uppercase`, so moving that line up is the fix.", "O(n)", "O(1)"),
    "What did borrows look like before non-lexical lifetimes (Rust 2018)?",
    ["A borrow ends at its last use, not at the end of the block.", "Reordering is often the whole fix."],
    rules=dict(methods=["clone"], lines=2),
))

P.append(write(
    "end-borrow-before-mutating", "End the borrow before you mutate", "easy", "where-borrows-end", ["NLL", "format!"],
    "Append a copy of the longest word, with `!` added, to `words`. Build the new `String` while you're reading, then push.",
    """
    pub fn append_longest(words: &mut Vec<String>) {
        todo!()
    }
    """,
    """
    pub fn append_longest(words: &mut Vec<String>) {
        let shouted = match words.iter().max_by_key(|w| w.len()) {
            Some(longest) => format!("{longest}!"),
            None => return,
        };
        words.push(shouted);
    }
    """,
    [T("appends", "[\"hi\", \"hello\"]", '{ let mut v = vec!["hi".to_string(), "hello".to_string()]; append_longest(&mut v); v }', 'vec!["hi".to_string(), "hello".to_string(), "hello!".to_string()]')],
    [T("empty", "[]", "{ let mut v: Vec<String> = vec![]; append_longest(&mut v); v.len() }", "0")],
    [("rust", "`format!` makes an owned `String` while `longest` is borrowed; after that, nothing borrows `words`.")],
    ("The shared borrow from `max_by_key` ends once `format!` returns, so `push` is allowed on the next line.", "O(n)", "O(len)"),
    "Why does `words.push(format!(\"{}!\", words[0]))` compile?",
    ["Produce an owned value inside the borrow, mutate after it."],
))

P.append(fix(
    "fix-read-after-clear", "Fix: keep the length, not the reference", "easy", "where-borrows-end", ["E0502"],
    "`longest_then_clear` should clear the list and return the length of its longest word. It doesn't compile.",
    """
    /// Clears `words` and returns the length of the longest one (0 if empty).
    pub fn longest_then_clear(words: &mut Vec<String>) -> usize {
        let longest = words.iter().max_by_key(|w| w.len());
        words.clear();
        longest.map_or(0, |w| w.len())
    }
    """,
    """
    /// Clears `words` and returns the length of the longest one (0 if empty).
    pub fn longest_then_clear(words: &mut Vec<String>) -> usize {
        let longest = words.iter().map(|w| w.len()).max();
        words.clear();
        longest.unwrap_or(0)
    }
    """,
    [T("clears", "[\"a\", \"abc\"]", '{ let mut v = vec!["a".to_string(), "abc".to_string()]; let n = longest_then_clear(&mut v); (n, v.len()) }', "(3, 0)")],
    [T("empty", "[]", "{ let mut v: Vec<String> = vec![]; longest_then_clear(&mut v) }", "0")],
    [("rust", "`longest` points at a String that `clear` frees. What do you actually need from it?")],
    ("Keeping a `usize` instead of a `&String` ends the borrow before `clear`.", "O(n)", "O(1)"),
    "What would happen in C++ if you read `longest` after `clear()`?",
    ["Hold the data you need, not a reference to it, across a mutation."],
    rules=dict(methods=["clone"], lines=2),
))

P.append(write(
    "entry-returns-a-borrow", "The entry API returns a borrow", "easy", "where-borrows-end", ["HashMap::entry", "lifetimes"],
    "Return a `&mut Vec<u32>` for `key` in `map`, creating an empty one if needed.",
    """
    use std::collections::HashMap;

    pub fn get_or_create<'m>(map: &'m mut HashMap<String, Vec<u32>>, key: &str) -> &'m mut Vec<u32> {
        todo!()
    }
    """,
    """
    use std::collections::HashMap;

    pub fn get_or_create<'m>(map: &'m mut HashMap<String, Vec<u32>>, key: &str) -> &'m mut Vec<u32> {
        map.entry(key.to_string()).or_default()
    }
    """,
    [T("creates_and_reuses", "push 1 then 2 under \"a\"", '{ let mut m = std::collections::HashMap::new(); get_or_create(&mut m, "a").push(1); get_or_create(&mut m, "a").push(2); m["a"].clone() }', "vec![1, 2]")],
    [T("separate_keys", "\"a\" and \"b\"", '{ let mut m = std::collections::HashMap::new(); get_or_create(&mut m, "a").push(1); get_or_create(&mut m, "b"); m.len() }', "2")],
    [("rust", "`or_default()` returns `&mut V` borrowed from the map for `'m`.")],
    ("One lookup, and the returned `&mut` keeps the map borrowed for as long as the caller uses it.", "O(1)", "O(1)"),
    "Why does `entry` take the key by value?",
    ["The entry API hands back a borrow into the map.", "Lifetimes connect the output to the map, not to the key."],
    related=("L2", "S4"),
))

# ---------------------------------------------------------------- reborrows (medium)

P.append(fix(
    "fix-moved-mut-into-generic", "Fix: a &mut moved into a generic call", "medium", "reborrows", ["E0382", "reborrow"],
    "`write_twice` should write `s` into `out` twice. It doesn't compile.",
    """
    use std::fmt::Write;

    fn put<W: Write>(mut w: W, s: &str) {
        w.write_str(s).expect("writing to a String can't fail");
    }

    /// Writes `s` into `out`, twice.
    pub fn write_twice(out: &mut String, s: &str) {
        put(out, s);
        put(out, s);
    }
    """,
    """
    use std::fmt::Write;

    fn put<W: Write>(mut w: W, s: &str) {
        w.write_str(s).expect("writing to a String can't fail");
    }

    /// Writes `s` into `out`, twice.
    pub fn write_twice(out: &mut String, s: &str) {
        put(&mut *out, s);
        put(out, s);
    }
    """,
    [T("twice", "s = \"ab\"", "{ let mut o = String::new(); write_twice(&mut o, \"ab\"); o }", "\"abab\".to_string()"),
     T("keeps_existing", "out = \"x\", s = \"y\"", "{ let mut o = String::from(\"x\"); write_twice(&mut o, \"y\"); o }", "\"xyy\".to_string()")],
    [T("empty", "s = \"\"", "{ let mut o = String::from(\"z\"); write_twice(&mut o, \"\"); o }", "\"z\".to_string()")],
    [("rust", "When a parameter's type is exactly `&mut T`, Rust reborrows automatically. When it's a generic `W`, the `&mut` itself is moved."),
     ("rust", "`&mut *out` makes a fresh, shorter borrow to pass, leaving `out` usable.")],
    ("A `&mut` isn't `Copy`, so passing it to a generic parameter moves it. `fmt::Write` has `impl Write for &mut W`, so a reborrow fits the generic and keeps the original.", "O(n)", "O(1)"),
    "Why does calling `out.push_str(s)` twice not have this problem?",
    ["Implicit reborrows happen only when the target type is known to be `&mut`.", "`&mut *r` is an explicit reborrow."],
    rules=dict(methods=["clone"], lines=1),
))

P.append(write(
    "helpers-take-mut", "Pass &mut to a helper, twice", "medium", "reborrows", ["&mut", "implicit reborrow"],
    "Write `normalize`, which trims and lowercases a string in place, and `same_after_normalizing`, which normalizes both and compares them.",
    """
    pub fn normalize(s: &mut String) {
        todo!()
    }

    pub fn same_after_normalizing(a: &mut String, b: &mut String) -> bool {
        todo!()
    }
    """,
    """
    pub fn normalize(s: &mut String) {
        let trimmed = s.trim().to_lowercase();
        *s = trimmed;
    }

    pub fn same_after_normalizing(a: &mut String, b: &mut String) -> bool {
        normalize(a);
        normalize(b);
        a == b
    }
    """,
    [T("equal", "\"  Rust \", \"rust\"", '{ let (mut a, mut b) = ("  Rust ".to_string(), "rust".to_string()); (same_after_normalizing(&mut a, &mut b), a) }', '(true, "rust".to_string())')],
    [T("different", "\"a\", \"b\"", '{ let (mut a, mut b) = ("a".to_string(), "b".to_string()); same_after_normalizing(&mut a, &mut b) }', "false")],
    [("rust", "Passing `a` (a `&mut String`) to `normalize(s: &mut String)` reborrows it, so `a` is usable afterwards.")],
    ("Each call reborrows `a` for just the call, which is why `a == b` still works.", "O(n)", "O(n)"),
    "Could `normalize` avoid allocating a new String?",
    ["Implicit reborrowing when passing `&mut` to a `&mut` parameter."],
))

P.append(write(
    "two-phase-borrows", "vec.push(vec.len()) and two-phase borrows", "medium", "reborrows", ["two-phase borrows"],
    "Push `v.len()` onto `v`, `n` times. Write it as `v.push(v.len())`.",
    """
    pub fn push_lengths(v: &mut Vec<usize>, n: usize) {
        todo!()
    }
    """,
    """
    pub fn push_lengths(v: &mut Vec<usize>, n: usize) {
        for _ in 0..n {
            // Two-phase borrow: `&mut v` is reserved, `v.len()` reads, then the push activates.
            v.push(v.len());
        }
    }
    """,
    [T("three", "v = [], n = 3", "{ let mut v = vec![]; push_lengths(&mut v, 3); v }", "vec![0, 1, 2]")],
    [T("existing", "v = [9], n = 2", "{ let mut v = vec![9]; push_lengths(&mut v, 2); v }", "vec![9, 1, 2]")],
    [("rust", "It looks like a shared and a mutable borrow at once. It compiles because the mutable borrow of an autoref'd method receiver isn't active until the arguments are evaluated.")],
    ("Two-phase borrows exist precisely so `v.push(v.len())` compiles. They only apply to autoref'd method calls and compound assignment.", "O(n)", "O(1) amortised"),
    "Why doesn't `let r = &mut v; r.push(v.len());` compile?",
    ["Two-phase borrows: reserve, evaluate arguments, then activate."],
))

P.append(fix(
    "fix-two-mut-into-players", "Fix: two &mut into one Vec", "medium", "reborrows", ["E0499"],
    "`transfer` should move points from one player to another. It doesn't compile.",
    """
    pub struct Player {
        pub score: u32,
    }

    /// Moves `points` from player `from` to player `to`.
    pub fn transfer(players: &mut [Player], from: usize, to: usize, points: u32) {
        let a = &mut players[from];
        let b = &mut players[to];
        a.score -= points;
        b.score += points;
    }
    """,
    """
    pub struct Player {
        pub score: u32,
    }

    /// Moves `points` from player `from` to player `to`.
    pub fn transfer(players: &mut [Player], from: usize, to: usize, points: u32) {
        players[from].score -= points;
        players[to].score += points;
    }
    """,
    [T("moves", "scores [10, 0], move 4 from 0 to 1", "{ let mut p = [Player { score: 10 }, Player { score: 0 }]; transfer(&mut p, 0, 1, 4); (p[0].score, p[1].score) }", "(6, 4)")],
    [T("same_player", "scores [5], move 3 from 0 to 0", "{ let mut p = [Player { score: 5 }]; transfer(&mut p, 0, 0, 3); p[0].score }", "5")],
    [("rust", "Two `&mut` into the same slice can't be alive at once, even for different indices: the compiler can't prove `from != to`."),
     ("approach", "Do you need both references at the same time?")],
    ("Each statement borrows the slice for one line, so the borrows never overlap. It also handles `from == to` correctly, which two live `&mut`s couldn't.", "O(1)", "O(1)"),
    "What if you really need both `&mut` at once?",
    ["The borrow checker reasons about the whole slice, not individual indices."],
))

P.append(write(
    "explicit-reborrow-generic-sink", "Explicit reborrow with &mut *r", "medium", "reborrows", ["reborrow", "generics"],
    "Using `emit_all` (don't change it), write `emit_twice`, which emits `xs` into `sink` twice.",
    """
    pub trait Sink {
        fn put(&mut self, x: i32);
    }

    impl Sink for Vec<i32> {
        fn put(&mut self, x: i32) {
            self.push(x);
        }
    }

    impl<S: Sink + ?Sized> Sink for &mut S {
        fn put(&mut self, x: i32) {
            (**self).put(x);
        }
    }

    /// Don't change this.
    pub fn emit_all<S: Sink>(mut sink: S, xs: &[i32]) {
        for &x in xs {
            sink.put(x);
        }
    }

    pub fn emit_twice(sink: &mut Vec<i32>, xs: &[i32]) {
        todo!()
    }
    """,
    """
    pub trait Sink {
        fn put(&mut self, x: i32);
    }

    impl Sink for Vec<i32> {
        fn put(&mut self, x: i32) {
            self.push(x);
        }
    }

    impl<S: Sink + ?Sized> Sink for &mut S {
        fn put(&mut self, x: i32) {
            (**self).put(x);
        }
    }

    /// Don't change this.
    pub fn emit_all<S: Sink>(mut sink: S, xs: &[i32]) {
        for &x in xs {
            sink.put(x);
        }
    }

    pub fn emit_twice(sink: &mut Vec<i32>, xs: &[i32]) {
        emit_all(&mut *sink, xs);
        emit_all(sink, xs);
    }
    """,
    [T("twice", "xs = [7, 8]", "{ let mut v = vec![]; emit_twice(&mut v, &[7, 8]); v }", "vec![7, 8, 7, 8]")],
    [T("empty", "xs = []", "{ let mut v = vec![1]; emit_twice(&mut v, &[]); v }", "vec![1]")],
    [("rust", "`emit_all` takes `S` by value. Passing `sink` moves the `&mut Vec`; `&mut *sink` passes a new, shorter borrow.")],
    ("The blanket `impl Sink for &mut S` is what makes passing a `&mut` possible at all; the explicit reborrow keeps `sink` usable.", "O(n)", "O(1)"),
    "Why do std's `io::Write` and `Iterator` have the same `impl for &mut T` pattern?",
    ["`&mut *r` reborrows explicitly.", "Blanket impls for `&mut S` let callers lend a sink instead of giving it away."],
    related=("L2", "L4"),
))

# ---------------------------------------------------------------- iterator invalidation (medium)

P.append(fix(
    "fix-remove-while-iterating", "Fix: remove while iterating", "medium", "iterator-invalidation", ["E0502", "retain"],
    "`remove_prefixed` should drop every name starting with `prefix`. It doesn't compile.",
    """
    /// Removes every name starting with `prefix`.
    pub fn remove_prefixed(names: &mut Vec<String>, prefix: &str) {
        for (i, n) in names.iter().enumerate() {
            if n.starts_with(prefix) {
                names.remove(i);
            }
        }
    }
    """,
    """
    /// Removes every name starting with `prefix`.
    pub fn remove_prefixed(names: &mut Vec<String>, prefix: &str) {
        names.retain(|n| !n.starts_with(prefix));
    }
    """,
    [T("removes", "[\"tmp_a\", \"keep\", \"tmp_b\"], prefix \"tmp\"", '{ let mut v: Vec<String> = ["tmp_a", "keep", "tmp_b"].map(String::from).to_vec(); remove_prefixed(&mut v, "tmp"); v }', 'vec!["keep".to_string()]')],
    [T("adjacent", "[\"x1\", \"x2\", \"y\"], prefix \"x\"", '{ let mut v: Vec<String> = ["x1", "x2", "y"].map(String::from).to_vec(); remove_prefixed(&mut v, "x"); v }', 'vec!["y".to_string()]')],
    [("rust", "Even if it compiled, removing inside the loop would skip the element after each removal. Which method filters a Vec in place?")],
    ("`retain` keeps order, visits each element once and shifts the survivors once. The hidden test's adjacent matches are what an index loop gets wrong.", "O(n)", "O(1)"),
    "How would you do this in C++ safely (erase-remove)?",
    ["Mutating a Vec invalidates iterators over it; the borrow checker stops it at compile time.", "`retain` is the in-place filter."],
))

P.append(write(
    "retain-mut", "retain_mut instead of an index loop", "medium", "iterator-invalidation", ["retain_mut"],
    "In one pass, remove the zeros from `v` and halve every value that stays.",
    """
    pub fn drop_zeros_and_halve(v: &mut Vec<i32>) {
        todo!()
    }
    """,
    """
    pub fn drop_zeros_and_halve(v: &mut Vec<i32>) {
        v.retain_mut(|x| {
            if *x == 0 {
                return false;
            }
            *x /= 2;
            true
        });
    }
    """,
    [T("mixed", "[4, 0, 6, 0]", "{ let mut v = vec![4, 0, 6, 0]; drop_zeros_and_halve(&mut v); v }", "vec![2, 3]")],
    [T("halves_to_zero", "[1, 2]", "{ let mut v = vec![1, 2]; drop_zeros_and_halve(&mut v); v }", "vec![0, 1]")],
    [("rust", "`retain_mut` gives the predicate `&mut T`, so it can change the element it keeps.")],
    ("One pass, no index arithmetic. Note that 1 halves to 0 but stays, because the check happens before the change.", "O(n)", "O(1)"),
    "Why did std add `retain_mut` instead of changing `retain`?",
    ["`retain_mut` filters and edits in one pass."],
))

P.append(fix(
    "fix-push-while-iterating", "Fix: push to the Vec you iterate", "medium", "iterator-invalidation", ["E0502"],
    "`expand` should add two subtasks for every task ending in `*`. It doesn't compile. Only the original tasks are expanded.",
    """
    /// For each task ending in '*', appends "<task>.1" and "<task>.2".
    pub fn expand(tasks: &mut Vec<String>) {
        for t in tasks.iter() {
            if t.ends_with('*') {
                tasks.push(format!("{t}.1"));
                tasks.push(format!("{t}.2"));
            }
        }
    }
    """,
    """
    /// For each task ending in '*', appends "<task>.1" and "<task>.2".
    pub fn expand(tasks: &mut Vec<String>) {
        let extra: Vec<String> = tasks
            .iter()
            .filter(|t| t.ends_with('*'))
            .flat_map(|t| [format!("{t}.1"), format!("{t}.2")])
            .collect();
        tasks.extend(extra);
    }
    """,
    [T("expands", "[\"a*\", \"b\"]", '{ let mut v: Vec<String> = ["a*", "b"].map(String::from).to_vec(); expand(&mut v); v }', 'vec!["a*", "b", "a*.1", "a*.2"]')],
    [T("none", "[\"x\"]", '{ let mut v = vec!["x".to_string()]; expand(&mut v); v.len() }', "1")],
    [("approach", "Work out what to add while reading, then add it after the loop.")],
    ("Collecting first means the new tasks aren't themselves expanded, and the Vec is only mutated once nothing borrows it.", "O(n)", "O(k)"),
    "What's the equivalent bug in Python, and why doesn't it crash there?",
    ["Collect, then mutate."],
))

P.append(write(
    "collect-then-mutate", "Two passes: read, then write", "medium", "iterator-invalidation", ["two passes"],
    "Add 10 to every score below the average (integer average, rounded down).",
    """
    pub fn bump_below_average(scores: &mut [u32]) {
        todo!()
    }
    """,
    """
    pub fn bump_below_average(scores: &mut [u32]) {
        if scores.is_empty() {
            return;
        }
        let avg = scores.iter().map(|&s| s as u64).sum::<u64>() / scores.len() as u64;
        for s in scores.iter_mut().filter(|s| (**s as u64) < avg) {
            *s += 10;
        }
    }
    """,
    [T("bumps", "[10, 20, 30]", "{ let mut v = [10, 20, 30]; bump_below_average(&mut v); v }", "[20, 20, 30]")],
    [T("empty", "[]", "{ let mut v: [u32; 0] = []; bump_below_average(&mut v); v }", "[]"),
     T("all_equal", "[5, 5]", "{ let mut v = [5, 5]; bump_below_average(&mut v); v }", "[5, 5]")],
    [("approach", "The average depends on every value, so compute it in a first pass before changing anything.")],
    ("The first pass's shared borrow ends before `iter_mut` starts. Summing in `u64` avoids overflow.", "O(n)", "O(1)"),
    "Could you do this in one pass?",
    ["Separate reading and writing into two passes."],
))

P.append(write(
    "extract-if", "Partition with extract_if", "medium", "iterator-invalidation", ["extract_if"],
    "Remove every job whose deadline is before `now` from `jobs` and return them, both in their original order.",
    """
    #[derive(Debug, PartialEq)]
    pub struct Job {
        pub name: &'static str,
        pub deadline: u64,
    }

    pub fn take_expired(jobs: &mut Vec<Job>, now: u64) -> Vec<Job> {
        todo!()
    }
    """,
    """
    #[derive(Debug, PartialEq)]
    pub struct Job {
        pub name: &'static str,
        pub deadline: u64,
    }

    pub fn take_expired(jobs: &mut Vec<Job>, now: u64) -> Vec<Job> {
        jobs.extract_if(.., |j| j.deadline < now).collect()
    }
    """,
    [T("splits", "deadlines 5, 20, 7; now 10", '{ let mut v = vec![Job { name: "a", deadline: 5 }, Job { name: "b", deadline: 20 }, Job { name: "c", deadline: 7 }]; let gone = take_expired(&mut v, 10); (gone.iter().map(|j| j.name).collect::<Vec<_>>(), v.iter().map(|j| j.name).collect::<Vec<_>>()) }', '(vec!["a", "c"], vec!["b"])')],
    [T("none", "deadline 50; now 10", '{ let mut v = vec![Job { name: "a", deadline: 50 }]; take_expired(&mut v, 10).len() }', "0")],
    [("rust", "`Vec::extract_if(range, pred)` removes matching elements and yields them, by value, in order.")],
    ("One pass, both halves keep their order, and removed jobs are moved out, not cloned.", "O(n)", "O(k)"),
    "What happens to the Vec if you drop the `ExtractIf` iterator halfway?",
    ["`extract_if` moves matching elements out while iterating."],
))

P.append(fix(
    "fix-map-mutation-during-iteration", "Fix: HashMap mutation during iteration", "medium", "iterator-invalidation", ["E0502", "HashMap::retain"],
    "`drop_zero` should remove every entry whose value is 0. It doesn't compile.",
    """
    use std::collections::HashMap;

    /// Removes every entry whose count is zero.
    pub fn drop_zero(counts: &mut HashMap<String, u32>) {
        for (k, v) in counts.iter() {
            if *v == 0 {
                counts.remove(k);
            }
        }
    }
    """,
    """
    use std::collections::HashMap;

    /// Removes every entry whose count is zero.
    pub fn drop_zero(counts: &mut HashMap<String, u32>) {
        counts.retain(|_, v| *v != 0);
    }
    """,
    [T("drops", "{a: 0, b: 2}", '{ let mut m = std::collections::HashMap::from([("a".to_string(), 0), ("b".to_string(), 2)]); drop_zero(&mut m); m }', f'{HM}::from([("b".to_string(), 2)])')],
    [T("all_zero", "{a: 0, b: 0}", '{ let mut m = std::collections::HashMap::from([("a".to_string(), 0), ("b".to_string(), 0)]); drop_zero(&mut m); m.len() }', "0")],
    [("rust", "Maps have the same in-place filter as Vec.")],
    ("Removing from a hash table can move other entries, so an iterator over it can't survive a removal.", "O(n)", "O(1)"),
    "How would you remove the entries and also collect their keys?",
    ["`HashMap::retain` filters in place."],
    related=("L2", "S4"),
))

# ---------------------------------------------------------------- split borrows (medium)

P.append(dict(slug="two-mutable-borrows-of-self"))  # written by hand; keeps its position

P.append(fix(
    "fix-field-borrow-and-mut-method", "Fix: borrow a field while calling a &mut method", "medium", "split-borrows", ["E0502"],
    "`append` should save the current text to history, then append `more`. It doesn't compile.",
    """
    pub struct Editor {
        pub text: String,
        pub history: Vec<String>,
    }

    impl Editor {
        fn save_snapshot(&mut self, s: &str) {
            self.history.push(s.to_string());
        }

        /// Saves the current text, then appends `more`.
        pub fn append(&mut self, more: &str) {
            let before = &self.text;
            self.save_snapshot(before);
            self.text.push_str(more);
        }
    }
    """,
    """
    pub struct Editor {
        pub text: String,
        pub history: Vec<String>,
    }

    impl Editor {
        /// Saves the current text, then appends `more`.
        pub fn append(&mut self, more: &str) {
            self.history.push(self.text.to_string());
            self.text.push_str(more);
        }
    }
    """,
    [T("saves", "text \"ab\", append \"c\"", '{ let mut e = Editor { text: "ab".into(), history: vec![] }; e.append("c"); (e.text, e.history) }', '("abc".to_string(), vec!["ab".to_string()])')],
    [T("twice", "append \"x\" then \"y\"", '{ let mut e = Editor { text: String::new(), history: vec![] }; e.append("x"); e.append("y"); e.history }', 'vec![String::new(), "x".to_string()]')],
    [("rust", "`save_snapshot(&mut self, ..)` needs all of `self` while `before` borrows `self.text`."),
     ("rust", "Touch the fields directly: `self.history` and `self.text` are disjoint.")],
    ("Field paths borrow one field each, so reading `self.text` while pushing to `self.history` is fine inside one function.", "O(n)", "O(n)"),
    "How else could `save_snapshot` be written so it doesn't need all of `self`?",
    ["A `&mut self` method borrows the whole struct; field paths borrow one field."],
))

P.append(write(
    "pair-mut", "Two &mut into one slice", "medium", "split-borrows", ["split_at_mut"],
    "Return mutable references to `v[i]` and `v[j]` at once, or `None` if they're the same index or out of bounds.",
    """
    pub fn pair_mut<T>(v: &mut [T], i: usize, j: usize) -> Option<(&mut T, &mut T)> {
        todo!()
    }
    """,
    """
    pub fn pair_mut<T>(v: &mut [T], i: usize, j: usize) -> Option<(&mut T, &mut T)> {
        if i == j || i >= v.len() || j >= v.len() {
            return None;
        }
        let (lo, hi) = (i.min(j), i.max(j));
        let (left, right) = v.split_at_mut(hi);
        let (a, b) = (&mut left[lo], &mut right[0]);
        Some(if i < j { (a, b) } else { (b, a) })
    }
    """,
    [T("both", "v = [1, 2, 3], i = 0, j = 2", "{ let mut v = [1, 2, 3]; if let Some((a, b)) = pair_mut(&mut v, 0, 2) { std::mem::swap(a, b); } v }", "[3, 2, 1]"),
     T("same_index", "i = j = 1", "pair_mut(&mut [1, 2], 1, 1).is_none()", "true")],
    [T("order_kept", "i = 2, j = 0", "{ let mut v = [10, 20, 30]; let (a, b) = pair_mut(&mut v, 2, 0).unwrap(); (*a, *b) }", "(30, 10)"),
     T("out_of_bounds", "j = 5", "pair_mut(&mut [1, 2], 0, 5).is_none()", "true")],
    [("rust", "Split at the larger index: the smaller one is in the left half, the larger is the first element of the right half.")],
    ("`split_at_mut` gives two borrows that can't overlap; returning them in the caller's order is the last detail.", "O(1)", "O(1)"),
    "std has `get_disjoint_mut`. What does it check that this doesn't?",
    ["Two `&mut` into one slice via `split_at_mut`."],
    related=("L2", "S3"),
))

P.append(write(
    "destructure-self", "Destructure self into field borrows", "medium", "split-borrows", ["patterns", "split borrows"],
    "Record each value: push it to `values`, add it to `total`, and raise `max`. Use the helper `update`, which needs three `&mut` at once.",
    """
    pub struct Stats {
        pub values: Vec<f64>,
        pub total: f64,
        pub max: f64,
    }

    fn update(values: &mut Vec<f64>, total: &mut f64, max: &mut f64, x: f64) {
        values.push(x);
        *total += x;
        *max = max.max(x);
    }

    impl Stats {
        pub fn record_all(&mut self, xs: &[f64]) {
            todo!()
        }
    }
    """,
    """
    pub struct Stats {
        pub values: Vec<f64>,
        pub total: f64,
        pub max: f64,
    }

    fn update(values: &mut Vec<f64>, total: &mut f64, max: &mut f64, x: f64) {
        values.push(x);
        *total += x;
        *max = max.max(x);
    }

    impl Stats {
        pub fn record_all(&mut self, xs: &[f64]) {
            let Stats { values, total, max } = self;
            for &x in xs {
                update(values, total, max, x);
            }
        }
    }
    """,
    [T("records", "xs = [1.5, 4.0, 2.5]", "{ let mut s = Stats { values: vec![], total: 0.0, max: f64::MIN }; s.record_all(&[1.5, 4.0, 2.5]); (s.values.len(), s.total, s.max) }", "(3, 8.0, 4.0)")],
    [T("empty", "xs = []", "{ let mut s = Stats { values: vec![], total: 1.0, max: 0.0 }; s.record_all(&[]); (s.values.len(), s.total) }", "(0, 1.0)")],
    [("rust", "`let Stats { values, total, max } = self;` gives three separate `&mut` borrows, one per field.")],
    ("Destructuring a `&mut Stats` binds each field by `&mut` (default binding modes), which is how you hand several fields to one call.", "O(n)", "O(1)"),
    "Why can't you write `update(&mut self.values, &mut self.total, &mut self.max, x)` through a getter?",
    ["Destructuring `&mut self` splits it into field borrows."],
))

P.append(fix(
    "fix-swap-without-swap", "Fix: swap two Vec elements", "medium", "split-borrows", ["E0499", "mem::take"],
    "`swap_items` should exchange two elements. It doesn't compile. Fix it without `slice::swap` or `mem::swap`.",
    """
    /// Swaps the elements at `i` and `j`.
    pub fn swap_items(v: &mut [String], i: usize, j: usize) {
        let a = &mut v[i];
        let b = &mut v[j];
        let tmp = std::mem::take(a);
        *a = std::mem::take(b);
        *b = tmp;
    }
    """,
    """
    /// Swaps the elements at `i` and `j`.
    pub fn swap_items(v: &mut [String], i: usize, j: usize) {
        if i == j {
            return;
        }
        let (lo, hi) = (i.min(j), i.max(j));
        let (left, right) = v.split_at_mut(hi);
        let (a, b) = (&mut left[lo], &mut right[0]);
        let tmp = std::mem::take(a);
        *a = std::mem::take(b);
        *b = tmp;
    }
    """,
    [T("swaps", "[\"a\", \"b\", \"c\"], 0 ↔ 2", '{ let mut v = ["a", "b", "c"].map(String::from); swap_items(&mut v, 0, 2); v }', '["c", "b", "a"].map(String::from)')],
    [T("same_index", "1 ↔ 1", '{ let mut v = ["a", "b"].map(String::from); swap_items(&mut v, 1, 1); v }', '["a", "b"].map(String::from)'),
     T("reversed", "2 ↔ 0", '{ let mut v = ["a", "b", "c"].map(String::from); swap_items(&mut v, 2, 0); v }', '["c", "b", "a"].map(String::from)')],
    [("rust", "Two live `&mut v[..]` won't compile. Split the slice so each index is in its own half."),
     ("edge case", "`i == j` must be handled before splitting.")],
    ("`slice::swap` does exactly this with raw pointers inside std. Splitting the slice is the safe equivalent.", "O(1)", "O(1)"),
    "How does `slice::swap` implement this internally?",
    ["`split_at_mut` for two disjoint `&mut`."],
    rules=dict(methods=["swap", "clone"]),
))

P.append(write(
    "view-struct", "A view struct over two fields", "medium", "split-borrows", ["lifetimes", "view structs"],
    "`Document::header()` returns a `Header` holding `&mut` to the title and tags at once. `Header::retitle` sets the title and adds an `\"edited\"` tag.",
    """
    pub struct Document {
        pub title: String,
        pub body: String,
        pub tags: Vec<String>,
    }

    pub struct Header<'a> {
        pub title: &'a mut String,
        pub tags: &'a mut Vec<String>,
    }

    impl Document {
        pub fn header(&mut self) -> Header<'_> {
            todo!()
        }
    }

    impl Header<'_> {
        pub fn retitle(&mut self, new_title: &str) {
            todo!()
        }
    }
    """,
    """
    pub struct Document {
        pub title: String,
        pub body: String,
        pub tags: Vec<String>,
    }

    pub struct Header<'a> {
        pub title: &'a mut String,
        pub tags: &'a mut Vec<String>,
    }

    impl Document {
        pub fn header(&mut self) -> Header<'_> {
            Header { title: &mut self.title, tags: &mut self.tags }
        }
    }

    impl Header<'_> {
        pub fn retitle(&mut self, new_title: &str) {
            self.title.clear();
            self.title.push_str(new_title);
            self.tags.push("edited".to_string());
        }
    }
    """,
    [T("retitles", "title \"old\"", '{ let mut d = Document { title: "old".into(), body: "text".into(), tags: vec![] }; d.header().retitle("new"); (d.title, d.tags, d.body) }', '("new".to_string(), vec!["edited".to_string()], "text".to_string())')],
    [T("twice", "retitle twice", '{ let mut d = Document { title: String::new(), body: String::new(), tags: vec![] }; let mut h = d.header(); h.retitle("a"); h.retitle("b"); d.tags.len() }', "2")],
    [("rust", "A struct of `&mut` field references carries the split borrow around as one value.")],
    ("`body` stays untouched and unborrowed by the view, which is the point of a view struct.", "O(n)", "O(1)"),
    "When does a view struct beat passing several `&mut` parameters?",
    ["View structs: a named bundle of disjoint field borrows."],
    related=("L2", "L3"),
))

P.append(fix(
    "fix-borrow-through-getter", "Fix: borrow through a getter", "medium", "split-borrows", ["E0502", "getters"],
    "`log_expensive` should log every price above `limit`. It doesn't compile.",
    """
    pub struct Shop {
        items: Vec<u32>,
        log: Vec<String>,
    }

    impl Shop {
        pub fn new(items: Vec<u32>) -> Self {
            Shop { items, log: Vec::new() }
        }

        fn items(&self) -> &[u32] {
            &self.items
        }

        /// Logs every price above `limit`.
        pub fn log_expensive(&mut self, limit: u32) {
            for p in self.items() {
                if *p > limit {
                    self.log.push(format!("expensive: {p}"));
                }
            }
        }

        pub fn log(&self) -> &[String] {
            &self.log
        }
    }
    """,
    """
    pub struct Shop {
        items: Vec<u32>,
        log: Vec<String>,
    }

    impl Shop {
        pub fn new(items: Vec<u32>) -> Self {
            Shop { items, log: Vec::new() }
        }

        /// Logs every price above `limit`.
        pub fn log_expensive(&mut self, limit: u32) {
            for p in &self.items {
                if *p > limit {
                    self.log.push(format!("expensive: {p}"));
                }
            }
        }

        pub fn log(&self) -> &[String] {
            &self.log
        }
    }
    """,
    [T("logs", "items [5, 50, 500], limit 40", "{ let mut s = Shop::new(vec![5, 50, 500]); s.log_expensive(40); s.log().to_vec() }", 'vec!["expensive: 50", "expensive: 500"]')],
    [T("none", "items [1], limit 40", "{ let mut s = Shop::new(vec![1]); s.log_expensive(40); s.log().len() }", "0")],
    [("rust", "`self.items()` borrows all of `self` for as long as the loop runs. What borrows only the `items` field?")],
    ("Getters hide which field they touch, so the compiler assumes all of `self`. Inside the impl, use the field directly.", "O(n)", "O(k)"),
    "Why can't the borrow checker see through the getter's body?",
    ["Borrow checking is per function: a getter borrows all of `self`."],
    rules=dict(methods=["clone", "to_vec"]),
))

# ---------------------------------------------------------------- borrow-checker limits (hard)

P.append(fix(
    "fix-get-or-insert", "Fix: get-or-insert without the entry API", "hard", "borrow-checker-limits", ["NLL case 3", "E0502"],
    "`get_or_insert` doesn't compile, even though it's correct. This is a known limit of today's borrow checker. Fix it without the entry API.",
    """
    use std::collections::HashMap;

    /// The value for `key`, inserting `default` first if it's missing.
    pub fn get_or_insert<'m>(map: &'m mut HashMap<u32, String>, key: u32, default: &str) -> &'m String {
        if let Some(v) = map.get(&key) {
            return v;
        }
        map.insert(key, default.to_string());
        &map[&key]
    }
    """,
    """
    use std::collections::HashMap;

    /// The value for `key`, inserting `default` first if it's missing.
    pub fn get_or_insert<'m>(map: &'m mut HashMap<u32, String>, key: u32, default: &str) -> &'m String {
        if !map.contains_key(&key) {
            map.insert(key, default.to_string());
        }
        &map[&key]
    }
    """,
    [T("existing", "{1: \"one\"}, key 1", '{ let mut m = std::collections::HashMap::from([(1, "one".to_string())]); get_or_insert(&mut m, 1, "x").clone() }', '"one".to_string()'),
     T("missing", "{}, key 2", '{ let mut m = std::collections::HashMap::new(); let v = get_or_insert(&mut m, 2, "two").clone(); (v, m.len()) }', '("two".to_string(), 1)')],
    [T("default_not_used_twice", "call twice for key 3", '{ let mut m = std::collections::HashMap::new(); get_or_insert(&mut m, 3, "a"); get_or_insert(&mut m, 3, "b").clone() }', '"a".to_string()')],
    [("rust", "Returning `v` from inside the `if let` makes the borrow last for `'m` on every path, including the one that inserts."),
     ("approach", "Check with something that returns a `bool`, not a reference, then look the key up once more.")],
    ("This is NLL \"problem case #3\": conditionally returning a borrow extends it to the whole function. Polonius, the next borrow checker, accepts the original. The fix costs one extra lookup.", "O(1)", "O(1)"),
    "Why does the entry API avoid this problem entirely?",
    ["NLL problem case 3: a conditionally returned borrow is live on every path.", "Restructure so the check returns a value, not a reference."],
    rules=dict(methods=["entry", "clone"]),
))

P.append(fix(
    "fix-conditional-return-of-borrow", "Fix: conditional return of a borrow", "hard", "borrow-checker-limits", ["NLL case 3", "Polonius"],
    "`first_long_or_push` returns the first word longer than `n`, or pushes `\"fallback\"` and returns that. It's correct, but it doesn't compile.",
    """
    /// The first word longer than `n`; otherwise pushes "fallback" and returns it.
    pub fn first_long_or_push(words: &mut Vec<String>, n: usize) -> &String {
        for w in words.iter() {
            if w.len() > n {
                return w;
            }
        }
        words.push("fallback".to_string());
        words.last().expect("just pushed")
    }
    """,
    """
    /// The first word longer than `n`; otherwise pushes "fallback" and returns it.
    pub fn first_long_or_push(words: &mut Vec<String>, n: usize) -> &String {
        if let Some(i) = words.iter().position(|w| w.len() > n) {
            return &words[i];
        }
        words.push("fallback".to_string());
        words.last().expect("just pushed")
    }
    """,
    [T("found", "[\"a\", \"long\"], n = 2", '{ let mut v = vec!["a".to_string(), "long".to_string()]; first_long_or_push(&mut v, 2).clone() }', '"long".to_string()'),
     T("fallback", "[\"a\"], n = 5", '{ let mut v = vec!["a".to_string()]; let r = first_long_or_push(&mut v, 5).clone(); (r, v.len()) }', '("fallback".to_string(), 2)')],
    [T("empty", "[], n = 0", "{ let mut v = vec![]; first_long_or_push(&mut v, 0).clone() }", '"fallback".to_string()')],
    [("rust", "Find an index first. An index doesn't borrow the Vec, so the push path is free to mutate it.")],
    ("Searching for a `usize` ends the borrow before the decision, so neither path conflicts.", "O(n)", "O(1)"),
    "Could you write a test that proves this is safe even though rustc rejects the original?",
    ["Return indices from searches when a later branch needs to mutate."],
))

P.append(write(
    "get-disjoint-mut", "get_disjoint_mut with index checks", "hard", "borrow-checker-limits", ["get_disjoint_mut", "Result"],
    """
    Move `amount` from account `from` to account `to`. Return `Err("same account")`,
    `Err("no such account")` or `Err("insufficient funds")` without changing anything when the move isn't allowed.
    """,
    """
    pub fn transfer(balances: &mut [i64], from: usize, to: usize, amount: i64) -> Result<(), &'static str> {
        todo!()
    }
    """,
    """
    use std::slice::GetDisjointMutError;

    pub fn transfer(balances: &mut [i64], from: usize, to: usize, amount: i64) -> Result<(), &'static str> {
        let [a, b] = balances.get_disjoint_mut([from, to]).map_err(|e| match e {
            GetDisjointMutError::OverlappingIndices => "same account",
            GetDisjointMutError::IndexOutOfBounds => "no such account",
        })?;
        if *a < amount {
            return Err("insufficient funds");
        }
        *a -= amount;
        *b += amount;
        Ok(())
    }
    """,
    [T("moves", "[10, 0], 0 → 1, 4", "{ let mut b = [10, 0]; (transfer(&mut b, 0, 1, 4), b) }", "(Ok(()), [6, 4])"),
     T("same", "0 → 0", "{ let mut b = [10]; transfer(&mut b, 0, 0, 1) }", 'Err("same account")')],
    [T("out_of_bounds", "0 → 7", "{ let mut b = [10, 0]; transfer(&mut b, 0, 7, 1) }", 'Err("no such account")'),
     T("insufficient", "[1, 0], 0 → 1, 5", "{ let mut b = [1, 0]; (transfer(&mut b, 0, 1, 5), b) }", '(Err("insufficient funds"), [1, 0])')],
    [("rust", "`slice::get_disjoint_mut([i, j])` returns `[&mut T; 2]`, or an error saying which check failed.")],
    ("std checks bounds and overlap once and hands back an array of `&mut`, with no `unsafe` in your code.", "O(1)", "O(1)"),
    "How would you generalise this to N accounts in one atomic batch?",
    ["`get_disjoint_mut` does the index checks for you."],
    related=("L2", "S3"),
))

P.append(write(
    "cell-for-copy", "When Cell beats RefCell", "hard", "borrow-checker-limits", ["Cell", "interior mutability"],
    "Each `Node` counts its visits through a shared `&Node`. Use `Cell<u32>`; no `RefCell`, no `&mut`.",
    """
    use std::cell::Cell;

    pub struct Node {
        pub name: String,
        visits: Cell<u32>,
    }

    impl Node {
        pub fn new(name: &str) -> Self {
            todo!()
        }

        /// Records a visit and returns the new count.
        pub fn visit(&self) -> u32 {
            todo!()
        }

        pub fn visits(&self) -> u32 {
            todo!()
        }
    }
    """,
    """
    use std::cell::Cell;

    pub struct Node {
        pub name: String,
        visits: Cell<u32>,
    }

    impl Node {
        pub fn new(name: &str) -> Self {
            Node { name: name.to_string(), visits: Cell::new(0) }
        }

        /// Records a visit and returns the new count.
        pub fn visit(&self) -> u32 {
            let n = self.visits.get() + 1;
            self.visits.set(n);
            n
        }

        pub fn visits(&self) -> u32 {
            self.visits.get()
        }
    }
    """,
    [T("counts", "visit 3 times", '{ let n = Node::new("a"); n.visit(); n.visit(); (n.visit(), n.visits()) }', "(3, 3)"),
     T("shared_refs", "two &Node to the same node", '{ let n = Node::new("a"); let (x, y) = (&n, &n); x.visit(); y.visit(); n.visits() }', "2")],
    [T("in_a_vec", "visit through a Vec<&Node>", '{ let a = Node::new("a"); let b = Node::new("b"); let all = vec![&a, &b, &a]; for n in &all { n.visit(); } (a.visits(), b.visits()) }', "(2, 1)")],
    [("rust", "`Cell` moves `Copy` values in and out with `get`/`set` and never hands out a reference, so there's nothing to track at runtime.")],
    ("`Cell` is zero-cost interior mutability for `Copy` types; `RefCell` adds a borrow counter and can panic. Neither is `Sync`.", "O(1)", "O(1)"),
    "Why is `Cell` safe even though it mutates through `&self`?",
    ["`Cell<T>` for `Copy` values: no references out, no runtime checks."],
    related=("L2", "S7"),
))

P.append(fix(
    "fix-borrowmuterror", "Fix: BorrowMutError at runtime", "hard", "borrow-checker-limits", ["RefCell", "panic"],
    "`Registry::add` compiles but panics with `already borrowed`. Fix it.",
    """
    use std::cell::RefCell;

    pub struct Registry {
        names: RefCell<Vec<String>>,
    }

    impl Registry {
        pub fn new() -> Self {
            Registry { names: RefCell::new(Vec::new()) }
        }

        /// Adds `name` unless it's already there.
        pub fn add(&self, name: &str) {
            let names = self.names.borrow();
            if !names.iter().any(|n| n == name) {
                self.names.borrow_mut().push(name.to_string());
            }
        }

        pub fn len(&self) -> usize {
            self.names.borrow().len()
        }
    }
    """,
    """
    use std::cell::RefCell;

    pub struct Registry {
        names: RefCell<Vec<String>>,
    }

    impl Registry {
        pub fn new() -> Self {
            Registry { names: RefCell::new(Vec::new()) }
        }

        /// Adds `name` unless it's already there.
        pub fn add(&self, name: &str) {
            let exists = self.names.borrow().iter().any(|n| n == name);
            if !exists {
                self.names.borrow_mut().push(name.to_string());
            }
        }

        pub fn len(&self) -> usize {
            self.names.borrow().len()
        }
    }
    """,
    [T("adds_once", "add \"a\" twice, \"b\" once", '{ let r = Registry::new(); r.add("a"); r.add("a"); r.add("b"); r.len() }', "2")],
    [T("empty", "new registry", "Registry::new().len()", "0")],
    [("rust", "`borrow()` returns a guard that holds the shared borrow until it's dropped. When is `names` dropped?")],
    ("The guard lived to the end of the function, so `borrow_mut` found it still active and panicked. Ending the shared borrow in the same statement fixes it.", "O(n)", "O(1)"),
    "Why does RefCell panic instead of returning an error by default, and when would you use `try_borrow_mut`?",
    ["`RefCell` enforces the borrow rules at runtime, through guards.", "Guard lifetimes are scopes; end them early."],
    related=("L2", "S7"),
))

P.append(fix(
    "fix-refcell-guard-across-call", "Fix: a RefCell guard held across a call", "hard", "borrow-checker-limits", ["Ref", "RefMut", "panic"],
    "`deposit` compiles but panics. Fix it so it records the new total after each deposit.",
    """
    use std::cell::RefCell;

    pub struct Bank {
        balances: RefCell<Vec<i64>>,
        audit: RefCell<Vec<String>>,
    }

    impl Bank {
        pub fn new(accounts: usize) -> Self {
            Bank { balances: RefCell::new(vec![0; accounts]), audit: RefCell::new(Vec::new()) }
        }

        fn total(&self) -> i64 {
            self.balances.borrow().iter().sum()
        }

        /// Adds `amount` to account `i` and records the new total.
        pub fn deposit(&self, i: usize, amount: i64) {
            let mut balances = self.balances.borrow_mut();
            balances[i] += amount;
            self.audit.borrow_mut().push(format!("total {}", self.total()));
        }

        pub fn audit(&self) -> Vec<String> {
            self.audit.borrow().to_vec()
        }
    }
    """,
    """
    use std::cell::RefCell;

    pub struct Bank {
        balances: RefCell<Vec<i64>>,
        audit: RefCell<Vec<String>>,
    }

    impl Bank {
        pub fn new(accounts: usize) -> Self {
            Bank { balances: RefCell::new(vec![0; accounts]), audit: RefCell::new(Vec::new()) }
        }

        fn total(&self) -> i64 {
            self.balances.borrow().iter().sum()
        }

        /// Adds `amount` to account `i` and records the new total.
        pub fn deposit(&self, i: usize, amount: i64) {
            self.balances.borrow_mut()[i] += amount;
            let total = self.total();
            self.audit.borrow_mut().push(format!("total {total}"));
        }

        pub fn audit(&self) -> Vec<String> {
            self.audit.borrow().to_vec()
        }
    }
    """,
    [T("records", "deposit 5 into 0, 7 into 1", "{ let b = Bank::new(2); b.deposit(0, 5); b.deposit(1, 7); b.audit() }", 'vec!["total 5", "total 12"]')],
    [T("negative", "deposit -3", "{ let b = Bank::new(1); b.deposit(0, -3); b.audit() }", 'vec!["total -3"]')],
    [("rust", "`total()` calls `borrow()` while `balances`, a `RefMut` guard, is still alive in `deposit`.")],
    ("A guard that outlives its statement is the usual cause of RefCell panics, and the call hides it. Writing through a temporary guard ends it at the semicolon.", "O(n)", "O(1)"),
    "How would you find this bug in a large codebase before it panics in production?",
    ["`RefMut` guards held across calls into the same RefCell."],
    related=("L2", "S7"),
))

P.append(fix(
    "fix-refcell-to-split-borrow", "Fix: RefCell where a split borrow suffices", "hard", "borrow-checker-limits", ["RefCell", "split borrows"],
    "`Cart` uses a `RefCell` to get around a borrow error that a split borrow solves. Remove the `RefCell`. Keep the same public methods.",
    """
    use std::cell::RefCell;

    pub struct Cart {
        items: RefCell<Vec<u32>>,
        total: u32,
    }

    impl Cart {
        pub fn new() -> Self {
            Cart { items: RefCell::new(Vec::new()), total: 0 }
        }

        pub fn add(&mut self, price: u32) {
            self.items.borrow_mut().push(price);
            self.total += price;
        }

        /// Doubles every price and keeps the total in step.
        pub fn double_all(&mut self) {
            for p in self.items.borrow_mut().iter_mut() {
                self.total += *p;
                *p *= 2;
            }
        }

        pub fn total(&self) -> u32 {
            self.total
        }

        pub fn items(&self) -> Vec<u32> {
            self.items.borrow().to_vec()
        }
    }
    """,
    """
    pub struct Cart {
        items: Vec<u32>,
        total: u32,
    }

    impl Cart {
        pub fn new() -> Self {
            Cart { items: Vec::new(), total: 0 }
        }

        pub fn add(&mut self, price: u32) {
            self.items.push(price);
            self.total += price;
        }

        /// Doubles every price and keeps the total in step.
        pub fn double_all(&mut self) {
            for p in self.items.iter_mut() {
                self.total += *p;
                *p *= 2;
            }
        }

        pub fn total(&self) -> u32 {
            self.total
        }

        pub fn items(&self) -> Vec<u32> {
            self.items.to_vec()
        }
    }
    """,
    [T("doubles", "add 3, 4; double", "{ let mut c = Cart::new(); c.add(3); c.add(4); c.double_all(); (c.items(), c.total()) }", "(vec![6, 8], 14)")],
    [T("empty", "double an empty cart", "{ let mut c = Cart::new(); c.double_all(); (c.items(), c.total()) }", "(vec![], 0)")],
    [("rust", "Inside one method, `self.items.iter_mut()` and `self.total` borrow different fields. Why was the RefCell ever needed?")],
    ("RefCell turned a compile-time guarantee into a runtime check that could panic. With `&mut self` and field paths, the split borrow needs neither.", "O(n)", "O(1)"),
    "When is RefCell genuinely the right tool?",
    ["Reach for split borrows before interior mutability."],
    rules=dict(types=["RefCell", "Cell"]),
    related=("L2", "S7"),
))


EXTRA = {
    "fix-mutate-through-shared-ref": T("negative", "balance 10, amount -3", "{ let mut a = [Account { balance: 10 }]; deposit_all(&mut a, -3); a[0].balance }", "7"),
    "fix-borrow-kept-alive": T("mixed_case", "names = [\"Rust\", \"go\", \"C\"]", '{ let mut v = vec!["Rust".to_string(), "go".to_string(), "C".to_string()]; shout_first(&mut v); v }', 'vec!["RUST!".to_string(), "go!".to_string(), "C!".to_string()]'),
    "end-borrow-before-mutating": T("first_longest_wins", "[\"ab\", \"cd\"]", '{ let mut v = vec!["ab".to_string(), "cd".to_string()]; append_longest(&mut v); v.last().cloned() }', 'Some("cd!".to_string())'),
    "fix-read-after-clear": T("single", "[\"hello\"]", '{ let mut v = vec!["hello".to_string()]; longest_then_clear(&mut v) }', "5"),
    "entry-returns-a-borrow": T("existing_kept", "\"k\" already maps to [9]", '{ let mut m = std::collections::HashMap::from([("k".to_string(), vec![9])]); get_or_create(&mut m, "k").push(1); m["k"].clone() }', "vec![9, 1]"),
    "helpers-take-mut": T("both_trimmed", "\" Go\", \"GO  \"", '{ let (mut a, mut b) = (" Go".to_string(), "GO  ".to_string()); (same_after_normalizing(&mut a, &mut b), b) }', '(true, "go".to_string())'),
    "two-phase-borrows": T("zero_times", "v = [4], n = 0", "{ let mut v = vec![4]; push_lengths(&mut v, 0); v }", "vec![4]"),
    "fix-two-mut-into-players": T("backwards", "scores [0, 10], move 10 from 1 to 0", "{ let mut p = [Player { score: 0 }, Player { score: 10 }]; transfer(&mut p, 1, 0, 10); (p[0].score, p[1].score) }", "(10, 0)"),
    "explicit-reborrow-generic-sink": T("appends", "sink = [0], xs = [1]", "{ let mut v = vec![0]; emit_twice(&mut v, &[1]); v }", "vec![0, 1, 1]"),
    "fix-remove-while-iterating": T("nothing_matches", "[\"a\"], prefix \"z\"", '{ let mut v = vec!["a".to_string()]; remove_prefixed(&mut v, "z"); v.len() }', "1"),
    "retain-mut": T("all_zero", "[0, 0]", "{ let mut v = vec![0, 0]; drop_zeros_and_halve(&mut v); v }", "vec![]"),
    "fix-push-while-iterating": T("two_starred", "[\"a*\", \"b*\"]", '{ let mut v: Vec<String> = ["a*", "b*"].map(String::from).to_vec(); expand(&mut v); v.len() }', "6"),
    "collect-then-mutate": T("rounds_down", "[1, 2]", "{ let mut v = [1, 2]; bump_below_average(&mut v); v }", "[1, 2]"),
    "extract-if": T("all_expired", "deadlines 1, 2; now 10", '{ let mut v = vec![Job { name: "a", deadline: 1 }, Job { name: "b", deadline: 2 }]; let gone = take_expired(&mut v, 10); (gone.len(), v.len()) }', "(2, 0)"),
    "fix-map-mutation-during-iteration": T("empty", "{}", "{ let mut m: std::collections::HashMap<String, u32> = std::collections::HashMap::new(); drop_zero(&mut m); m.len() }", "0"),
    "fix-field-borrow-and-mut-method": T("empty_append", "text \"a\", append \"\"", '{ let mut e = Editor { text: "a".into(), history: vec![] }; e.append(""); (e.text, e.history.len()) }', '("a".to_string(), 1)'),
    "destructure-self": T("keeps_max", "max 10, xs = [3]", "{ let mut s = Stats { values: vec![], total: 0.0, max: 10.0 }; s.record_all(&[3.0]); s.max }", "10.0"),
    "fix-swap-without-swap": T("adjacent", "[\"x\", \"y\"], 0 ↔ 1", '{ let mut v = ["x", "y"].map(String::from); swap_items(&mut v, 0, 1); v }', '["y", "x"].map(String::from)'),
    "view-struct": T("keeps_tags", "tags [\"draft\"]", '{ let mut d = Document { title: "t".into(), body: String::new(), tags: vec!["draft".into()] }; d.header().retitle("u"); d.tags }', 'vec!["draft".to_string(), "edited".to_string()]'),
    "fix-borrow-through-getter": T("at_limit", "items [40], limit 40", "{ let mut s = Shop::new(vec![40]); s.log_expensive(40); s.log().len() }", "0"),
    "fix-borrowmuterror": T("order_kept", "add \"b\", \"a\"", '{ let r = Registry::new(); r.add("b"); r.add("a"); r.add("b"); r.len() }', "2"),
    "fix-refcell-guard-across-call": T("same_account", "deposit 1 into 0 twice", "{ let b = Bank::new(1); b.deposit(0, 1); b.deposit(0, 1); b.audit() }", 'vec!["total 1", "total 2"]'),
    "fix-refcell-to-split-borrow": T("double_twice", "add 1; double twice", "{ let mut c = Cart::new(); c.add(1); c.double_all(); c.double_all(); (c.items(), c.total()) }", "(vec![4], 4)"),
}
for p in P:
    if p["slug"] in EXTRA:
        p["visible"].append(EXTRA[p["slug"]])

STAGES = [
    ("shared-vs-unique", "Shared vs unique", "easy"),
    ("where-borrows-end", "Where borrows end", "easy"),
    ("reborrows", "Reborrows", "medium"),
    ("iterator-invalidation", "Iterator invalidation", "medium"),
    ("split-borrows", "Split borrows", "medium"),
    ("borrow-checker-limits", "Borrow-checker limits", "hard"),
]

if __name__ == "__main__":
    n = write_track("l2-borrowing", "L2", "Borrowing", "L", "core", 2,
                    "Aliasing XOR mutation: reason about what each borrow covers and how long it lives, instead of fighting the compiler.",
                    STAGES, P, keep={"two-mutable-borrows-of-self"})
    print("L2", n)
