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

# ---------------------------------------------------------------- test hardening
# Per problem: more visible cases (the rules that are easy to misread), hidden edge cases, a seeded random
# comparison against a brute-force model, a scale test where complexity matters, and `wrong` solutions that
# `anneal verify` checks the tests reject. Fix-mode wrong solutions obey the problem's rules.
MORE = {}

MORE["fix-push-while-holding-a-reference"] = dict(
    visible=[
        T("negatives", "v = [-5, -9], x = -7", "{ let mut v = vec![-5, -9]; (add_and_max(&mut v, -7), v) }", "(-5, vec![-5, -9, -7])"),
        T("max_in_middle", "v = [1, 8, 2], x = 3", "{ let mut v = vec![1, 8, 2]; add_and_max(&mut v, 3) }", "8"),
        T("x_equals_max", "v = [4, 2], x = 4", "{ let mut v = vec![4, 2]; (add_and_max(&mut v, 4), v) }", "(4, vec![4, 2, 4])"),
    ],
    hidden=[
        T("max_first", "v = [8, 1, 2], x = 3", "{ let mut v = vec![8, 1, 2]; add_and_max(&mut v, 3) }", "8"),
        T("all_negative_x_larger", "v = [-9, -8], x = -1", "{ let mut v = vec![-9, -8]; add_and_max(&mut v, -1) }", "-1"),
        T("i32_extremes", "v = [i32::MIN], x = i32::MAX", "{ let mut v = vec![i32::MIN]; (add_and_max(&mut v, i32::MAX), v) }", "(i32::MAX, vec![i32::MIN, i32::MAX])"),
        T("only_min", "v = [i32::MIN], x = i32::MIN", "{ let mut v = vec![i32::MIN]; add_and_max(&mut v, i32::MIN) }", "i32::MIN"),
        T("duplicates", "v = [7, 7, 7], x = 7", "{ let mut v = vec![7, 7, 7]; (add_and_max(&mut v, 7), v) }", "(7, vec![7, 7, 7, 7])"),
        T("empty_min", "v = [], x = i32::MIN", "{ let mut v = vec![]; (add_and_max(&mut v, i32::MIN), v) }", "(i32::MIN, vec![i32::MIN])"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2001);
            for _ in 0..300 {
                let n = rng.below(10);
                let v: Vec<i32> = rng.vec(n, -50, 50);
                let x = rng.int(-50, 50) as i32;
                let want = v.iter().copied().chain([x]).max().unwrap();
                let mut after = v.clone();
                after.push(x);
                let mut got_v = v.clone();
                let got = add_and_max(&mut got_v, x);
                check!(format!("v = {v:?}, x = {x}"), (got, got_v), (want, after));
            }
        }
        """,
    ],
    wrong=dict(
        zero_default="""
            /// Pushes `x` and returns the largest value, which may be `x`.
            pub fn add_and_max(v: &mut Vec<i32>, x: i32) -> i32 {
                let max = v.iter().copied().max().unwrap_or(0);
                v.push(x);
                max.max(x)
            }
        """,
        last_is_largest="""
            /// Pushes `x` and returns the largest value, which may be `x`.
            pub fn add_and_max(v: &mut Vec<i32>, x: i32) -> i32 {
                let max = v.last().copied().unwrap_or(x);
                v.push(x);
                max.max(x)
            }
        """,
    ),
)

COUNTER_WRONG = """
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

        pub fn busiest(&self) -> Option<usize> {
            BODY
        }
    }
"""
MORE["many-readers-one-writer"] = dict(
    visible=[
        T("tie_lowest", "3 slots, hits on 2, 0", "{ let mut c = Counter::new(3); c.hit(2); c.hit(0); c.busiest() }", "Some(0)"),
        T("last_slot_wins", "4 slots, hits on 3, 3, 1", "{ let mut c = Counter::new(4); c.hit(3); c.hit(3); c.hit(1); (c.total(), c.busiest()) }", "(3, Some(3))"),
        T("no_slots", "0 slots", "(Counter::new(0).total(), Counter::new(0).busiest())", "(0, None)"),
    ],
    hidden=[
        T("single_slot", "1 slot, 3 hits", "{ let mut c = Counter::new(1); for _ in 0..3 { c.hit(0); } (c.total(), c.busiest()) }", "(3, Some(0))"),
        T("tie_later_first", "4 slots, hits on 3, 1", "{ let mut c = Counter::new(4); c.hit(3); c.hit(1); c.busiest() }", "Some(1)"),
        T("zero_hits_total", "5 slots, no hits", "{ let c = Counter::new(5); (c.total(), c.busiest()) }", "(0, Some(0))"),
        T("readers_alongside", "two &Counter at once", "{ let mut c = Counter::new(2); c.hit(1); let (r1, r2) = (&c, &c); (r1.total(), r2.total(), r1.busiest(), r2.busiest()) }", "(1, 1, Some(1), Some(1))"),
        T("many_hits", "1 slot, 100000 hits", "{ let mut c = Counter::new(1); for _ in 0..100_000 { c.hit(0); } c.total() }", "100_000"),
        T("many_slots", "1000 slots, slot 999 hit twice", "{ let mut c = Counter::new(1000); c.hit(999); c.hit(999); c.hit(0); c.busiest() }", "Some(999)"),
        T("overtakes", "hits on 0, 1, 1", "{ let mut c = Counter::new(2); c.hit(0); c.hit(1); c.hit(1); c.busiest() }", "Some(1)"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2002);
            for _ in 0..300 {
                let slots = 1 + rng.below(8);
                let k = rng.below(30);
                let hits: Vec<usize> = (0..k).map(|_| rng.below(slots)).collect();
                let mut c = Counter::new(slots);
                let mut model = vec![0u32; slots];
                for &h in &hits {
                    c.hit(h);
                    model[h] += 1;
                }
                let max = *model.iter().max().unwrap();
                let want = (model.iter().sum::<u32>(), model.iter().position(|&m| m == max));
                check!(format!("{slots} slots, hits on {hits:?}"), (c.total(), c.busiest()), want);
            }
        }
        """,
    ],
    wrong=dict(
        last_maximum=COUNTER_WRONG.replace("BODY", "self.hits.iter().enumerate().max_by_key(|&(_, h)| *h).map(|(i, _)| i)"),
        none_without_hits=COUNTER_WRONG.replace("BODY", """let max = *self.hits.iter().max()?;
            if max == 0 {
                return None;
            }
            self.hits.iter().position(|&h| h == max)"""),
    ),
)

MORE["fix-mut-from-shared-self"] = dict(
    visible=[
        T("push_after_edit", "push 1; set top to 7; push 2", "{ let mut s = Stack::new(); s.push(1); *s.top_mut().unwrap() = 7; s.push(2); s.items_for_test() }", "vec![7, 2]"),
        T("only_top_changes", "push 5, 6; set top to 0", "{ let mut s = Stack::new(); s.push(5); s.push(6); if let Some(t) = s.top_mut() { *t = 0; } s.items_for_test() }", "vec![5, 0]"),
        T("single", "push 3; double the top", "{ let mut s = Stack::new(); s.push(3); *s.top_mut().unwrap() *= 2; s.items_for_test() }", "vec![6]"),
    ],
    hidden=[
        T("repeated_edits", "push 1; add 1 to the top 5 times", "{ let mut s = Stack::new(); s.push(1); for _ in 0..5 { *s.top_mut().unwrap() += 1; } s.items_for_test() }", "vec![6]"),
        T("to_min", "push 0; set top to i32::MIN", "{ let mut s = Stack::new(); s.push(0); *s.top_mut().unwrap() = i32::MIN; s.items_for_test() }", "vec![i32::MIN]"),
        T("none_then_some", "new: None; push 4: Some(4)", "{ let mut s = Stack::new(); let a = s.top_mut().is_none(); s.push(4); (a, s.top_mut().copied()) }", "(true, Some(4))"),
        T("many_items", "push 0..1000; set top to -1", "{ let mut s = Stack::new(); for i in 0..1000 { s.push(i); } *s.top_mut().unwrap() = -1; let v = s.items_for_test(); (v.len(), v[998], v[999]) }", "(1000, 998, -1)"),
        T("duplicates", "push 5, 5; set top to 0", "{ let mut s = Stack::new(); s.push(5); s.push(5); *s.top_mut().unwrap() = 0; s.items_for_test() }", "vec![5, 0]"),
        T("edit_is_seen_by_next_call", "push 2; set top to 9; read top", "{ let mut s = Stack::new(); s.push(2); *s.top_mut().unwrap() = 9; s.top_mut().copied() }", "Some(9)"),
        T("max_value", "push i32::MAX - 1; add 1", "{ let mut s = Stack::new(); s.push(i32::MAX - 1); *s.top_mut().unwrap() += 1; s.items_for_test() }", "vec![i32::MAX]"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2003);
            for _ in 0..300 {
                let mut s = Stack::new();
                let mut model: Vec<i32> = Vec::new();
                let mut ops = Vec::new();
                let n = rng.below(12);
                for _ in 0..n {
                    if rng.bool() {
                        let x = rng.int(-100, 100) as i32;
                        s.push(x);
                        model.push(x);
                        ops.push(format!("push {x}"));
                    } else {
                        let d = rng.int(-9, 9) as i32;
                        if let Some(t) = s.top_mut() {
                            *t += d;
                        }
                        if let Some(t) = model.last_mut() {
                            *t += d;
                        }
                        ops.push(format!("top += {d}"));
                    }
                }
                check!(ops.join(", "), s.items_for_test(), model);
            }
        }
        """,
    ],
    wrong=dict(
        leaks_a_copy="""
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
                    Some(Box::leak(Box::new(*self.items.last()?)))
                }
            }

            impl Stack {
                /// For tests.
                pub fn items_for_test(&self) -> Vec<i32> {
                    self.items.to_vec()
                }
            }
        """,
    ),
)

MORE["most-repeated-word"] = dict(
    visible=[
        T("single_word", "\"hello\"", 'most_repeated("hello")', 'Some("hello")'),
        T("tie_alphabetical", "\"x y y x\"", 'most_repeated("x y y x")', 'Some("x")'),
        T("case_sensitive", "\"A a a A A\"", 'most_repeated("A a a A A")', 'Some("A")'),
    ],
    hidden=[
        T("only_spaces", "\"   \"", 'most_repeated("   ")', "None"),
        T("tabs_and_newlines", "\"a\\tb\\nb  a\\n\\nb\"", 'most_repeated("a\\tb\\nb  a\\n\\nb")', 'Some("b")'),
        T("unicode", "\"café naïve café\"", 'most_repeated("café naïve café")', 'Some("café")'),
        T("punctuation_kept", "\"hi, hi hi,\"", 'most_repeated("hi, hi hi,")', 'Some("hi,")'),
        T("three_way_tie", "\"c b a\"", 'most_repeated("c b a")', 'Some("a")'),
        T("borrows_the_input", "\"x y x\"", '{ let t = String::from("x y x"); let w = most_repeated(&t).unwrap(); t.as_bytes().as_ptr_range().contains(&w.as_ptr()) }', "true"),
        T("leading_trailing_space", "\"  z z y  \"", 'most_repeated("  z z y  ")', 'Some("z")'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2004);
            for _ in 0..300 {
                let len = rng.below(16);
                let text = rng.string(len, "ab c");
                let words: Vec<&str> = text.split_whitespace().collect();
                let mut want: Option<(usize, &str)> = None;
                for &w in &words {
                    let c = words.iter().filter(|&&x| x == w).count();
                    if want.map_or(true, |(bc, bw)| c > bc || (c == bc && w < bw)) {
                        want = Some((c, w));
                    }
                }
                check!(format!("text = {text:?}"), most_repeated(&text), want.map(|(_, w)| w));
            }
        }

        #[test]
        fn scale_200k_words() {
            let mut text = String::new();
            for i in 0..200_000 {
                text.push_str(&format!("w{} ", i % 100_000));
            }
            text.push_str("w77777");
            check!("200000 words, 100000 distinct, then w77777 once more", most_repeated(&text), Some("w77777"));
        }
        """,
    ],
    wrong=dict(
        linear_search="""
            pub fn most_repeated(text: &str) -> Option<&str> {
                let mut counts: Vec<(&str, usize)> = Vec::new();
                for w in text.split_whitespace() {
                    match counts.iter_mut().find(|(k, _)| *k == w) {
                        Some((_, c)) => *c += 1,
                        None => counts.push((w, 1)),
                    }
                }
                counts.into_iter().max_by(|a, b| a.1.cmp(&b.1).then_with(|| b.0.cmp(a.0))).map(|(w, _)| w)
            }
        """,
        tie_alphabetically_last="""
            use std::collections::HashMap;

            pub fn most_repeated(text: &str) -> Option<&str> {
                let mut counts: HashMap<&str, usize> = HashMap::new();
                for w in text.split_whitespace() {
                    *counts.entry(w).or_insert(0) += 1;
                }
                counts.into_iter().max_by(|a, b| a.1.cmp(&b.1).then_with(|| a.0.cmp(b.0))).map(|(w, _)| w)
            }
        """,
    ),
)

MORE["fix-mutate-through-shared-ref"] = dict(
    visible=[
        T("three_accounts", "balances [0, -5, 100], amount 1", "{ let mut a = [Account { balance: 0 }, Account { balance: -5 }, Account { balance: 100 }]; deposit_all(&mut a, 1); (a[0].balance, a[1].balance, a[2].balance) }", "(1, -4, 101)"),
        T("zero_amount", "balance 3, amount 0", "{ let mut a = [Account { balance: 3 }]; deposit_all(&mut a, 0); a[0].balance }", "3"),
        T("empty", "no accounts", "{ let mut a: [Account; 0] = []; deposit_all(&mut a, 5); a.len() }", "0"),
    ],
    hidden=[
        T("single", "balance 7, amount 3", "{ let mut a = [Account { balance: 7 }]; deposit_all(&mut a, 3); a[0].balance }", "10"),
        T("to_max", "balance i64::MAX - 1, amount 1", "{ let mut a = [Account { balance: i64::MAX - 1 }]; deposit_all(&mut a, 1); a[0].balance }", "i64::MAX"),
        T("to_min", "balance 0, amount i64::MIN", "{ let mut a = [Account { balance: 0 }]; deposit_all(&mut a, i64::MIN); a[0].balance }", "i64::MIN"),
        T("same_balances", "balances [2, 2, 2], amount 2", "{ let mut a = [Account { balance: 2 }, Account { balance: 2 }, Account { balance: 2 }]; deposit_all(&mut a, 2); (a[0].balance, a[1].balance, a[2].balance) }", "(4, 4, 4)"),
        T("in_a_vec", "1000 accounts at 0, amount 3", "{ let mut a: Vec<Account> = (0..1000).map(|_| Account { balance: 0 }).collect(); deposit_all(&mut a, 3); a.iter().map(|x| x.balance).sum::<i64>() }", "3000"),
        T("called_twice", "balance 0; +1 then +2", "{ let mut a = [Account { balance: 0 }]; deposit_all(&mut a, 1); deposit_all(&mut a, 2); a[0].balance }", "3"),
        T("sub_slice", "balances [0, 0, 0]; deposit into [1..]", "{ let mut a = [Account { balance: 0 }, Account { balance: 0 }, Account { balance: 0 }]; deposit_all(&mut a[1..], 4); (a[0].balance, a[1].balance, a[2].balance) }", "(0, 4, 4)"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2005);
            for _ in 0..300 {
                let n = rng.below(10);
                let start: Vec<i64> = rng.vec(n, -1000, 1000);
                let amount = rng.int(-1000, 1000);
                let mut a: Vec<Account> = start.iter().map(|&b| Account { balance: b }).collect();
                deposit_all(&mut a, amount);
                let got: Vec<i64> = a.iter().map(|x| x.balance).collect();
                let want: Vec<i64> = start.iter().map(|b| b + amount).collect();
                check!(format!("balances {start:?}, amount {amount}"), got, want);
            }
        }
        """,
    ],
    wrong=dict(
        mutates_copies="""
            pub struct Account {
                pub balance: i64,
            }

            /// Adds `amount` to every account.
            pub fn deposit_all(accounts: &[Account], amount: i64) {
                for mut a in accounts.iter().map(|a| Account { balance: a.balance }) {
                    a.balance += amount;
                }
            }
        """,
    ),
)

MORE["split-first-mut"] = dict(
    visible=[
        T("negative_head", "v = [-1, 0, 1]", "{ let mut v = [-1, 0, 1]; add_head_to_rest(&mut v); v }", "[-1, -1, 0]"),
        T("head_not_doubled", "v = [2, 2, 2]", "{ let mut v = [2, 2, 2]; add_head_to_rest(&mut v); v }", "[2, 4, 4]"),
        T("empty", "v = []", "{ let mut v: [i32; 0] = []; add_head_to_rest(&mut v); v }", "[]"),
    ],
    hidden=[
        T("two", "v = [3, 4]", "{ let mut v = [3, 4]; add_head_to_rest(&mut v); v }", "[3, 7]"),
        T("zero_head", "v = [0, 5, 6]", "{ let mut v = [0, 5, 6]; add_head_to_rest(&mut v); v }", "[0, 5, 6]"),
        T("i32_bounds", "v = [i32::MIN, i32::MAX]", "{ let mut v = [i32::MIN, i32::MAX]; add_head_to_rest(&mut v); v }", "[i32::MIN, -1]"),
        T("large_values", "v = [1000000000, 1000000000]", "{ let mut v = [1_000_000_000, 1_000_000_000]; add_head_to_rest(&mut v); v }", "[1_000_000_000, 2_000_000_000]"),
        T("same_rest", "v = [5, 1, 1]", "{ let mut v = [5, 1, 1]; add_head_to_rest(&mut v); v }", "[5, 6, 6]"),
        T("not_a_prefix_sum", "v = [1, 1, 1, 1]", "{ let mut v = vec![1, 1, 1, 1]; add_head_to_rest(&mut v); v }", "vec![1, 2, 2, 2]"),
        T("big_vec", "v = [3, 0, 0, …] (100000 values)", "{ let mut v = vec![0; 100_000]; v[0] = 3; add_head_to_rest(&mut v); (v[0], v[1], v[99_999]) }", "(3, 3, 3)"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2006);
            for _ in 0..300 {
                let n = rng.below(10);
                let v: Vec<i32> = rng.vec(n, -1000, 1000);
                let want: Vec<i32> = v.iter().enumerate().map(|(i, &x)| if i == 0 { x } else { x + v[0] }).collect();
                let mut got = v.clone();
                add_head_to_rest(&mut got);
                check!(format!("v = {v:?}"), got, want);
            }
        }
        """,
    ],
    wrong=dict(
        includes_head="""
            pub fn add_head_to_rest(v: &mut [i32]) {
                if v.is_empty() {
                    return;
                }
                let head = v[0];
                for x in v.iter_mut() {
                    *x += head;
                }
            }
        """,
        prefix_sum="""
            pub fn add_head_to_rest(v: &mut [i32]) {
                for i in 1..v.len() {
                    v[i] += v[i - 1];
                }
            }
        """,
    ),
)

MORE["fix-borrow-kept-alive"] = dict(
    visible=[
        T("already_upper", "names = [\"ABC\", \"d\"]", '{ let mut v = vec!["ABC".to_string(), "d".to_string()]; shout_first(&mut v); v }', 'vec!["ABC!".to_string(), "d!".to_string()]'),
        T("only_first_uppercased", "names = [\"a\", \"b\", \"c\"]", '{ let mut v = vec!["a".to_string(), "b".to_string(), "c".to_string()]; shout_first(&mut v); v }', 'vec!["A!".to_string(), "b!".to_string(), "c!".to_string()]'),
        T("one", "names = [\"x\"]", '{ let mut v = vec!["x".to_string()]; shout_first(&mut v); v }', 'vec!["X!".to_string()]'),
    ],
    hidden=[
        T("ascii_only", "names = [\"straße\", \"b\"]", '{ let mut v = vec!["straße".to_string(), "b".to_string()]; shout_first(&mut v); v }', 'vec!["STRAßE!".to_string(), "b!".to_string()]'),
        T("accents_untouched", "names = [\"é\"]", '{ let mut v = vec!["é".to_string()]; shout_first(&mut v); v }', 'vec!["é!".to_string()]'),
        T("letters_and_digits", "names = [\"a1b2\"]", '{ let mut v = vec!["a1b2".to_string()]; shout_first(&mut v); v }', 'vec!["A1B2!".to_string()]'),
        T("empty_first", "names = [\"\", \"x\"]", '{ let mut v = vec![String::new(), "x".to_string()]; shout_first(&mut v); v }', 'vec!["!".to_string(), "x!".to_string()]'),
        T("duplicates", "names = [\"x\", \"x\"]", '{ let mut v = vec!["x".to_string(), "x".to_string()]; shout_first(&mut v); v }', 'vec!["X!".to_string(), "x!".to_string()]'),
        T("spaces", "names = [\"hi there\"]", '{ let mut v = vec!["hi there".to_string()]; shout_first(&mut v); v }', 'vec!["HI THERE!".to_string()]'),
        T("many", "1000 names \"n\"", '{ let mut v = vec!["n".to_string(); 1000]; shout_first(&mut v); (v.len(), v[0].clone(), v[999].clone()) }', '(1000, "N!".to_string(), "n!".to_string())'),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2007);
            for _ in 0..300 {
                let n = 1 + rng.below(5);
                let names: Vec<String> = (0..n).map(|_| { let l = rng.below(4); rng.string(l, "abXY1é") }).collect();
                let want: Vec<String> = names.iter().enumerate().map(|(i, s)| if i == 0 { format!("{}!", s.to_ascii_uppercase()) } else { format!("{s}!") }).collect();
                let mut got = names.clone();
                shout_first(&mut got);
                check!(format!("names = {names:?}"), got, want);
            }
        }
        """,
    ],
    wrong=dict(
        unicode_uppercase="""
            /// Uppercases the first name, then appends "!" to every name.
            pub fn shout_first(names: &mut Vec<String>) {
                for n in names.iter_mut() {
                    n.push('!');
                }
                names[0] = names[0].to_uppercase();
            }
        """,
    ),
)

MORE["end-borrow-before-mutating"] = dict(
    visible=[
        T("single", "[\"x\"]", '{ let mut v = vec!["x".to_string()]; append_longest(&mut v); v }', 'vec!["x".to_string(), "x!".to_string()]'),
        T("longest_first", "[\"abc\", \"a\", \"b\"]", '{ let mut v = vec!["abc".to_string(), "a".to_string(), "b".to_string()]; append_longest(&mut v); v }', 'vec!["abc".to_string(), "a".to_string(), "b".to_string(), "abc!".to_string()]'),
        T("empty", "[]", "{ let mut v: Vec<String> = vec![]; append_longest(&mut v); v.len() }", "0"),
    ],
    hidden=[
        T("longest_in_middle", "[\"a\", \"abcd\", \"ab\"]", '{ let mut v = vec!["a".to_string(), "abcd".to_string(), "ab".to_string()]; append_longest(&mut v); v.last().cloned() }', 'Some("abcd!".to_string())'),
        T("tie_takes_last", "[\"aa\", \"bb\", \"c\"]", '{ let mut v = vec!["aa".to_string(), "bb".to_string(), "c".to_string()]; append_longest(&mut v); v.last().cloned() }', 'Some("bb!".to_string())'),
        T("empty_word", "[\"\"]", '{ let mut v = vec![String::new()]; append_longest(&mut v); v }', 'vec![String::new(), "!".to_string()]'),
        T("unicode", "[\"日本語\", \"ab\"]", '{ let mut v = vec!["日本語".to_string(), "ab".to_string()]; append_longest(&mut v); v.last().cloned() }', 'Some("日本語!".to_string())'),
        T("grows_by_one", "10 words", "{ let mut v: Vec<String> = (0..10).map(|i| i.to_string()).collect(); append_longest(&mut v); v.len() }", "11"),
        T("original_untouched", "[\"b\", \"aaa\", \"c\"]", '{ let mut v = vec!["b".to_string(), "aaa".to_string(), "c".to_string()]; append_longest(&mut v); v }', 'vec!["b".to_string(), "aaa".to_string(), "c".to_string(), "aaa!".to_string()]'),
        T("called_twice", "[\"ab\"], twice", '{ let mut v = vec!["ab".to_string()]; append_longest(&mut v); append_longest(&mut v); v }', 'vec!["ab".to_string(), "ab!".to_string(), "ab!!".to_string()]'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2008);
            for _ in 0..300 {
                let n = rng.below(6);
                let words: Vec<String> = (0..n).map(|_| { let l = rng.below(5); rng.string(l, "ab") }).collect();
                let mut want = words.clone();
                if let Some(m) = words.iter().map(|w| w.len()).max() {
                    let i = words.iter().rposition(|w| w.len() == m).unwrap();
                    want.push(format!("{}!", words[i]));
                }
                let mut got = words.clone();
                append_longest(&mut got);
                check!(format!("words = {words:?}"), got, want);
            }
        }
        """,
    ],
    wrong=dict(
        first_longest="""
            pub fn append_longest(words: &mut Vec<String>) {
                let shouted = match words.iter().reduce(|a, b| if b.len() > a.len() { b } else { a }) {
                    Some(longest) => format!("{longest}!"),
                    None => return,
                };
                words.push(shouted);
            }
        """,
        shouts_on_empty="""
            pub fn append_longest(words: &mut Vec<String>) {
                let longest = words.iter().max_by_key(|w| w.len()).map_or("", |w| w.as_str());
                let shouted = format!("{longest}!");
                words.push(shouted);
            }
        """,
    ),
)

MORE["fix-read-after-clear"] = dict(
    visible=[
        T("tie", "[\"ab\", \"cd\", \"e\"]", '{ let mut v = vec!["ab".to_string(), "cd".to_string(), "e".to_string()]; let n = longest_then_clear(&mut v); (n, v.len()) }', "(2, 0)"),
        T("longest_first", "[\"ccc\", \"a\"]", '{ let mut v = vec!["ccc".to_string(), "a".to_string()]; longest_then_clear(&mut v) }', "3"),
        T("empty", "[]", "{ let mut v: Vec<String> = vec![]; longest_then_clear(&mut v) }", "0"),
    ],
    hidden=[
        T("empty_strings", "[\"\", \"\"]", "{ let mut v = vec![String::new(), String::new()]; longest_then_clear(&mut v) }", "0"),
        T("unicode_bytes", "[\"日本\"]", '{ let mut v = vec!["日本".to_string()]; longest_then_clear(&mut v) }', "6"),
        T("longest_last", "[\"a\", \"bb\", \"ccc\"]", '{ let mut v = vec!["a".to_string(), "bb".to_string(), "ccc".to_string()]; longest_then_clear(&mut v) }', "3"),
        T("reuse_after_clear", "clear, push \"z\", clear again", '{ let mut v = vec!["abc".to_string()]; longest_then_clear(&mut v); v.push("z".to_string()); (longest_then_clear(&mut v), v.is_empty()) }', "(1, true)"),
        T("many", "1000 words of lengths i % 50", '{ let mut v: Vec<String> = (0..1000).map(|i| "x".repeat(i % 50)).collect(); (longest_then_clear(&mut v), v.len()) }', "(49, 0)"),
        T("one_long_many_short", "[\"a\" × 5, \"abcdefgh\"]", '{ let mut v = vec!["a".to_string(); 5]; v.push("abcdefgh".to_string()); longest_then_clear(&mut v) }', "8"),
        T("single_empty", "[\"\"]", "{ let mut v = vec![String::new()]; (longest_then_clear(&mut v), v.len()) }", "(0, 0)"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2009);
            for _ in 0..300 {
                let n = rng.below(8);
                let words: Vec<String> = (0..n).map(|_| { let l = rng.below(6); rng.string(l, "aé") }).collect();
                let want = words.iter().map(|w| w.len()).max().unwrap_or(0);
                let mut v = words.clone();
                let got = longest_then_clear(&mut v);
                check!(format!("words = {words:?}"), (got, v.len()), (want, 0));
            }
        }
        """,
    ],
    wrong=dict(
        count_not_length="""
            /// Clears `words` and returns the length of the longest one (0 if empty).
            pub fn longest_then_clear(words: &mut Vec<String>) -> usize {
                let longest = words.len();
                words.clear();
                longest
            }
        """,
        first_word="""
            /// Clears `words` and returns the length of the longest one (0 if empty).
            pub fn longest_then_clear(words: &mut Vec<String>) -> usize {
                let longest = words.first().map(|w| w.len());
                words.clear();
                longest.unwrap_or(0)
            }
        """,
    ),
)

MORE["entry-returns-a-borrow"] = dict(
    visible=[
        T("new_is_empty", "missing key \"n\"", '{ let mut m = std::collections::HashMap::new(); get_or_create(&mut m, "n").is_empty() }', "true"),
        T("does_not_replace", "\"k\" already maps to [1, 2]", '{ let mut m = std::collections::HashMap::from([("k".to_string(), vec![1, 2])]); get_or_create(&mut m, "k").len() }', "2"),
        T("separate_keys", "\"a\" and \"b\"", '{ let mut m = std::collections::HashMap::new(); get_or_create(&mut m, "a").push(1); get_or_create(&mut m, "b"); m.len() }', "2"),
    ],
    hidden=[
        T("empty_key", "key \"\"", '{ let mut m = std::collections::HashMap::new(); get_or_create(&mut m, "").push(5); m[""].clone() }', "vec![5]"),
        T("unicode_key", "key \"ключ\"", '{ let mut m = std::collections::HashMap::new(); get_or_create(&mut m, "ключ").push(1); m.contains_key("ключ") }', "true"),
        T("mutate_through_return", "extend then retain", '{ let mut m = std::collections::HashMap::new(); let v = get_or_create(&mut m, "a"); v.extend([1, 2, 3]); v.retain(|&x| x != 2); m["a"].clone() }', "vec![1, 3]"),
        T("case_sensitive", "\"a\" and \"A\"", '{ let mut m = std::collections::HashMap::new(); get_or_create(&mut m, "a"); get_or_create(&mut m, "A"); m.len() }', "2"),
        T("many_keys", "10000 keys", "{ let mut m = std::collections::HashMap::new(); for i in 0..10_000u32 { get_or_create(&mut m, &i.to_string()).push(i); } (m.len(), m[\"9999\"].clone()) }", "(10_000, vec![9999])"),
        T("other_keys_untouched", "{a: [1]}, create \"b\"", '{ let mut m = std::collections::HashMap::from([("a".to_string(), vec![1])]); get_or_create(&mut m, "b").push(2); (m["a"].clone(), m["b"].clone()) }', "(vec![1], vec![2])"),
        T("max_value", "push u32::MAX", '{ let mut m = std::collections::HashMap::new(); get_or_create(&mut m, "x").push(u32::MAX); m["x"].clone() }', "vec![u32::MAX]"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2010);
            for _ in 0..200 {
                let mut m: std::collections::HashMap<String, Vec<u32>> = std::collections::HashMap::new();
                let mut model: Vec<(String, Vec<u32>)> = Vec::new();
                let mut log = Vec::new();
                let n = rng.below(12);
                for _ in 0..n {
                    let key = rng.string(1, "abc");
                    let x = rng.below(100) as u32;
                    let push = rng.bool();
                    let v = get_or_create(&mut m, &key);
                    if push {
                        v.push(x);
                    }
                    let pos = match model.iter().position(|(k, _)| *k == key) {
                        Some(p) => p,
                        None => {
                            model.push((key.clone(), vec![]));
                            model.len() - 1
                        }
                    };
                    if push {
                        model[pos].1.push(x);
                    }
                    log.push(if push { format!("{key} push {x}") } else { key.clone() });
                }
                let mut got: Vec<(String, Vec<u32>)> = m.into_iter().collect();
                got.sort();
                model.sort();
                check!(log.join(", "), got, model);
            }
        }
        """,
    ],
    wrong=dict(
        replaces_existing="""
            use std::collections::HashMap;

            pub fn get_or_create<'m>(map: &'m mut HashMap<String, Vec<u32>>, key: &str) -> &'m mut Vec<u32> {
                map.insert(key.to_string(), Vec::new());
                map.get_mut(key).unwrap()
            }
        """,
        forgets_to_insert="""
            use std::collections::HashMap;

            pub fn get_or_create<'m>(map: &'m mut HashMap<String, Vec<u32>>, key: &str) -> &'m mut Vec<u32> {
                if !map.contains_key(key) {
                    return Box::leak(Box::new(Vec::new()));
                }
                map.get_mut(key).unwrap()
            }
        """,
    ),
)

MORE["fix-moved-mut-into-generic"] = dict(
    visible=[
        T("unicode", "s = \"é\"", "{ let mut o = String::new(); write_twice(&mut o, \"é\"); o }", "\"éé\".to_string()"),
        T("called_twice", "write \"ab\" twice, twice", "{ let mut o = String::new(); write_twice(&mut o, \"ab\"); write_twice(&mut o, \"ab\"); o }", "\"abababab\".to_string()"),
        T("empty", "s = \"\"", "{ let mut o = String::from(\"z\"); write_twice(&mut o, \"\"); o }", "\"z\".to_string()"),
    ],
    hidden=[
        T("single_char", "s = \"a\"", "{ let mut o = String::new(); write_twice(&mut o, \"a\"); o }", "\"aa\".to_string()"),
        T("with_newline", "s = \"a\\n\"", "{ let mut o = String::new(); write_twice(&mut o, \"a\\n\"); o }", "\"a\\na\\n\".to_string()"),
        T("long", "s = 1000 × \"x\"", "{ let mut o = String::new(); let s = \"x\".repeat(1000); write_twice(&mut o, &s); o.len() }", "2000"),
        T("emoji", "s = \"🦀\"", "{ let mut o = String::new(); write_twice(&mut o, \"🦀\"); o }", "\"🦀🦀\".to_string()"),
        T("existing_unicode", "out = \"ü\", s = \"-\"", "{ let mut o = String::from(\"ü\"); write_twice(&mut o, \"-\"); o }", "\"ü--\".to_string()"),
        T("spaces", "out = \"a\", s = \" \"", "{ let mut o = String::from(\"a\"); write_twice(&mut o, \" \"); o }", "\"a  \".to_string()"),
        T("both_empty", "out = \"\", s = \"\"", "{ let mut o = String::new(); write_twice(&mut o, \"\"); o }", "String::new()"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2011);
            for _ in 0..300 {
                let lo = rng.below(4);
                let start = rng.string(lo, "xyé");
                let ls = rng.below(4);
                let s = rng.string(ls, "ab é");
                let mut o = start.clone();
                write_twice(&mut o, &s);
                check!(format!("out = {start:?}, s = {s:?}"), o, format!("{start}{s}{s}"));
            }
        }
        """,
    ],
    wrong=dict(
        writes_into_a_copy="""
            use std::fmt::Write;

            fn put<W: Write>(mut w: W, s: &str) {
                w.write_str(s).expect("writing to a String can't fail");
            }

            /// Writes `s` into `out`, twice.
            pub fn write_twice(out: &mut String, s: &str) {
                put(out.to_string(), s);
                put(out, s);
            }
        """,
    ),
)

HELPERS_WRONG = """
    pub fn normalize(s: &mut String) {
        let trimmed = BODY;
        *s = trimmed;
    }

    pub fn same_after_normalizing(a: &mut String, b: &mut String) -> bool {
        normalize(a);
        normalize(b);
        a == b
    }
"""
MORE["helpers-take-mut"] = dict(
    visible=[
        T("normalize_only", "\"  MiXeD  \"", '{ let mut s = "  MiXeD  ".to_string(); normalize(&mut s); s }', '"mixed".to_string()'),
        T("inner_spaces_kept", "\"a  b\", \"a b\"", '{ let (mut a, mut b) = ("a  b".to_string(), "a b".to_string()); same_after_normalizing(&mut a, &mut b) }', "false"),
        T("empty_strings", "\"\", \"\"", "{ let (mut a, mut b) = (String::new(), String::new()); (same_after_normalizing(&mut a, &mut b), a) }", "(true, String::new())"),
    ],
    hidden=[
        T("only_spaces", "\"   \", \"\"", '{ let (mut a, mut b) = ("   ".to_string(), String::new()); (same_after_normalizing(&mut a, &mut b), a) }', "(true, String::new())"),
        T("unicode_lowercase", "\"ÉCOLE\", \"école\"", '{ let (mut a, mut b) = ("ÉCOLE".to_string(), "école".to_string()); (same_after_normalizing(&mut a, &mut b), a) }', '(true, "école".to_string())'),
        T("tabs_newlines", "\"\\tHi\\n\", \"hi\"", '{ let (mut a, mut b) = ("\\tHi\\n".to_string(), "hi".to_string()); (same_after_normalizing(&mut a, &mut b), a) }', '(true, "hi".to_string())'),
        T("both_changed", "\"X \", \" x\"", '{ let (mut a, mut b) = ("X ".to_string(), " x".to_string()); same_after_normalizing(&mut a, &mut b); (a, b) }', '("x".to_string(), "x".to_string())'),
        T("different_after_trim", "\"ab\", \"a b\"", '{ let (mut a, mut b) = ("ab".to_string(), "a b".to_string()); same_after_normalizing(&mut a, &mut b) }', "false"),
        T("trailing_only", "\"go  \", \"go\"", '{ let (mut a, mut b) = ("go  ".to_string(), "go".to_string()); same_after_normalizing(&mut a, &mut b) }', "true"),
        T("normalize_idempotent", "normalize \" A \" twice", '{ let mut s = " A ".to_string(); normalize(&mut s); normalize(&mut s); s }', '"a".to_string()'),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2012);
            for _ in 0..300 {
                let la = rng.below(6);
                let a0 = rng.string(la, " aAéÉ\\t");
                let lb = rng.below(6);
                let b0 = rng.string(lb, " aAéÉ\\t");
                let (mut a, mut b) = (a0.clone(), b0.clone());
                let got = same_after_normalizing(&mut a, &mut b);
                let (na, nb) = (a0.trim().to_lowercase(), b0.trim().to_lowercase());
                check!(format!("a = {a0:?}, b = {b0:?}"), (got, a, b), (na == nb, na, nb));
            }
        }
        """,
    ],
    wrong=dict(
        ascii_lowercase=HELPERS_WRONG.replace("BODY", "s.trim().to_ascii_lowercase()"),
        trims_start_only=HELPERS_WRONG.replace("BODY", "s.trim_start().to_lowercase()"),
    ),
)

MORE["two-phase-borrows"] = dict(
    visible=[
        T("one", "v = [], n = 1", "{ let mut v = vec![]; push_lengths(&mut v, 1); v }", "vec![0]"),
        T("existing", "v = [9], n = 2", "{ let mut v = vec![9]; push_lengths(&mut v, 2); v }", "vec![9, 1, 2]"),
        T("zero_on_empty", "v = [], n = 0", "{ let mut v = vec![]; push_lengths(&mut v, 0); v }", "Vec::<usize>::new()"),
    ],
    hidden=[
        T("long_existing", "v = [5, 5, 5], n = 1", "{ let mut v = vec![5, 5, 5]; push_lengths(&mut v, 1); v }", "vec![5, 5, 5, 3]"),
        T("thousand", "v = [], n = 1000", "{ let mut v = vec![]; push_lengths(&mut v, 1000); (v.len(), v[999]) }", "(1000, 999)"),
        T("called_twice", "n = 2, then n = 2", "{ let mut v = vec![]; push_lengths(&mut v, 2); push_lengths(&mut v, 2); v }", "vec![0, 1, 2, 3]"),
        T("from_ten", "v = [0; 10], n = 3", "{ let mut v = vec![0; 10]; push_lengths(&mut v, 3); v[10..].to_vec() }", "vec![10, 11, 12]"),
        T("values_equal_index", "v = [], n = 50", "{ let mut v = vec![]; push_lengths(&mut v, 50); v.iter().enumerate().all(|(i, &x)| i == x) }", "true"),
        T("large", "v = [], n = 200000", "{ let mut v = vec![]; push_lengths(&mut v, 200_000); (v.len(), v[199_999]) }", "(200_000, 199_999)"),
        T("big_values_kept", "v = [usize::MAX], n = 1", "{ let mut v = vec![usize::MAX]; push_lengths(&mut v, 1); v }", "vec![usize::MAX, 1]"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2013);
            for _ in 0..300 {
                let n0 = rng.below(5);
                let start: Vec<usize> = rng.vec(n0, 0, 9);
                let n = rng.below(6);
                let mut v = start.clone();
                push_lengths(&mut v, n);
                let mut want = start.clone();
                for _ in 0..n {
                    want.push(want.len());
                }
                check!(format!("v = {start:?}, n = {n}"), v, want);
            }
        }
        """,
    ],
    wrong=dict(
        pushes_the_counter="""
            pub fn push_lengths(v: &mut Vec<usize>, n: usize) {
                for i in 0..n {
                    v.push(i);
                }
            }
        """,
        length_after_push="""
            pub fn push_lengths(v: &mut Vec<usize>, n: usize) {
                for _ in 0..n {
                    v.push(0);
                    let last = v.len() - 1;
                    v[last] = v.len();
                }
            }
        """,
    ),
)

PLAYERS_WRONG = """
    pub struct Player {
        pub score: u32,
    }

    /// Moves `points` from player `from` to player `to`.
    pub fn transfer(players: &mut [Player], from: usize, to: usize, points: u32) {
        BODY
    }
"""
MORE["fix-two-mut-into-players"] = dict(
    visible=[
        T("zero_points", "scores [3, 4], move 0 from 0 to 1", "{ let mut p = [Player { score: 3 }, Player { score: 4 }]; transfer(&mut p, 0, 1, 0); (p[0].score, p[1].score) }", "(3, 4)"),
        T("same_player", "scores [5], move 3 from 0 to 0", "{ let mut p = [Player { score: 5 }]; transfer(&mut p, 0, 0, 3); p[0].score }", "5"),
        T("middle_untouched", "scores [1, 2, 3], move 1 from 0 to 2", "{ let mut p = [Player { score: 1 }, Player { score: 2 }, Player { score: 3 }]; transfer(&mut p, 0, 2, 1); (p[0].score, p[1].score, p[2].score) }", "(0, 2, 4)"),
    ],
    hidden=[
        T("three_players", "scores [5, 5, 5], move 3 from 2 to 0", "{ let mut p = [Player { score: 5 }, Player { score: 5 }, Player { score: 5 }]; transfer(&mut p, 2, 0, 3); (p[0].score, p[1].score, p[2].score) }", "(8, 5, 2)"),
        T("all_points", "scores [7, 0], move 7 from 0 to 1", "{ let mut p = [Player { score: 7 }, Player { score: 0 }]; transfer(&mut p, 0, 1, 7); (p[0].score, p[1].score) }", "(0, 7)"),
        T("u32_max", "scores [u32::MAX, 0], move all", "{ let mut p = [Player { score: u32::MAX }, Player { score: 0 }]; transfer(&mut p, 0, 1, u32::MAX); (p[0].score, p[1].score) }", "(0, u32::MAX)"),
        T("repeated", "scores [0, 9], move 3 from 1 to 0, three times", "{ let mut p = [Player { score: 0 }, Player { score: 9 }]; for _ in 0..3 { transfer(&mut p, 1, 0, 3); } (p[0].score, p[1].score) }", "(9, 0)"),
        T("same_player_full", "scores [u32::MAX], move 5 from 0 to 0", "{ let mut p = [Player { score: u32::MAX }]; transfer(&mut p, 0, 0, 5); p[0].score }", "u32::MAX"),
        T("same_player_all", "scores [4], move 4 from 0 to 0", "{ let mut p = [Player { score: 4 }]; transfer(&mut p, 0, 0, 4); p[0].score }", "4"),
        T("in_a_vec", "1000 players with 1 point; move from 999 to 0", "{ let mut p: Vec<Player> = (0..1000).map(|_| Player { score: 1 }).collect(); transfer(&mut p, 999, 0, 1); (p[0].score, p[999].score) }", "(2, 0)"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2014);
            for _ in 0..300 {
                let n = 1 + rng.below(5);
                let scores: Vec<u32> = rng.vec(n, 0, 20);
                let from = rng.below(n);
                let to = rng.below(n);
                let points = rng.int(0, scores[from] as i64) as u32;
                let mut p: Vec<Player> = scores.iter().map(|&s| Player { score: s }).collect();
                transfer(&mut p, from, to, points);
                let mut want = scores.clone();
                want[from] -= points;
                want[to] += points;
                check!(format!("scores {scores:?}, move {points} from {from} to {to}"), p.iter().map(|x| x.score).collect::<Vec<_>>(), want);
            }
        }
        """,
    ],
    wrong=dict(
        adds_first=PLAYERS_WRONG.replace("BODY", """players[to].score += points;
        players[from].score -= points;"""),
        swapped_direction=PLAYERS_WRONG.replace("BODY", """players[from].score += points;
        players[to].score -= points;"""),
    ),
)

SINK_WRONG = """
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
        BODY
    }
"""
MORE["explicit-reborrow-generic-sink"] = dict(
    visible=[
        T("order_kept", "xs = [3, 1, 2]", "{ let mut v = vec![]; emit_twice(&mut v, &[3, 1, 2]); v }", "vec![3, 1, 2, 3, 1, 2]"),
        T("single", "xs = [5]", "{ let mut v = vec![]; emit_twice(&mut v, &[5]); v }", "vec![5, 5]"),
        T("empty", "xs = []", "{ let mut v = vec![1]; emit_twice(&mut v, &[]); v }", "vec![1]"),
    ],
    hidden=[
        T("negatives", "xs = [-1, i32::MIN]", "{ let mut v = vec![]; emit_twice(&mut v, &[-1, i32::MIN]); v }", "vec![-1, i32::MIN, -1, i32::MIN]"),
        T("duplicates", "xs = [2, 2]", "{ let mut v = vec![]; emit_twice(&mut v, &[2, 2]); v }", "vec![2, 2, 2, 2]"),
        T("existing_kept", "sink = [9, 9], xs = [1]", "{ let mut v = vec![9, 9]; emit_twice(&mut v, &[1]); v }", "vec![9, 9, 1, 1]"),
        T("large", "xs = 0..10000", "{ let xs: Vec<i32> = (0..10_000).collect(); let mut v = vec![]; emit_twice(&mut v, &xs); (v.len(), v[9_999], v[10_000]) }", "(20_000, 9_999, 0)"),
        T("max", "xs = [i32::MAX]", "{ let mut v = vec![]; emit_twice(&mut v, &[i32::MAX]); v }", "vec![i32::MAX, i32::MAX]"),
        T("called_twice", "xs = [4], twice", "{ let mut v = vec![]; emit_twice(&mut v, &[4]); emit_twice(&mut v, &[4]); v }", "vec![4, 4, 4, 4]"),
        T("two_distinct", "xs = [1, 2]", "{ let mut v = vec![0]; emit_twice(&mut v, &[1, 2]); v }", "vec![0, 1, 2, 1, 2]"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2015);
            for _ in 0..300 {
                let n0 = rng.below(4);
                let start: Vec<i32> = rng.vec(n0, -9, 9);
                let n = rng.below(6);
                let xs: Vec<i32> = rng.vec(n, -100, 100);
                let mut v = start.clone();
                emit_twice(&mut v, &xs);
                let want: Vec<i32> = start.iter().chain(&xs).chain(&xs).copied().collect();
                check!(format!("sink = {start:?}, xs = {xs:?}"), v, want);
            }
        }
        """,
    ],
    wrong=dict(
        each_value_twice=SINK_WRONG.replace("BODY", """for &x in xs {
            sink.put(x);
            sink.put(x);
        }"""),
        into_a_copy=SINK_WRONG.replace("BODY", """emit_all(sink.to_vec(), xs);
        emit_all(sink, xs);"""),
    ),
)

REMOVE_WRONG = """
    /// Removes every name starting with `prefix`.
    pub fn remove_prefixed(names: &mut Vec<String>, prefix: &str) {
        let mut i = 0;
        while i < names.len() {
            BODY
        }
    }
"""
MORE["fix-remove-while-iterating"] = dict(
    visible=[
        T("empty_prefix", "[\"a\", \"b\"], prefix \"\"", '{ let mut v = vec!["a".to_string(), "b".to_string()]; remove_prefixed(&mut v, ""); v }', "Vec::<String>::new()"),
        T("contains_not_prefix", "[\"a_tmp\"], prefix \"tmp\"", '{ let mut v = vec!["a_tmp".to_string()]; remove_prefixed(&mut v, "tmp"); v }', 'vec!["a_tmp".to_string()]'),
        T("adjacent", "[\"x1\", \"x2\", \"y\"], prefix \"x\"", '{ let mut v: Vec<String> = ["x1", "x2", "y"].map(String::from).to_vec(); remove_prefixed(&mut v, "x"); v }', 'vec!["y".to_string()]'),
    ],
    hidden=[
        T("empty_list", "[], prefix \"a\"", '{ let mut v: Vec<String> = vec![]; remove_prefixed(&mut v, "a"); v.len() }', "0"),
        T("all_match", "[\"x\", \"xx\", \"xxx\"], prefix \"x\"", '{ let mut v: Vec<String> = ["x", "xx", "xxx"].map(String::from).to_vec(); remove_prefixed(&mut v, "x"); v.len() }', "0"),
        T("exact_match", "[\"tmp\"], prefix \"tmp\"", '{ let mut v = vec!["tmp".to_string()]; remove_prefixed(&mut v, "tmp"); v.len() }', "0"),
        T("case_sensitive", "[\"Tmp\", \"tmp\"], prefix \"tmp\"", '{ let mut v: Vec<String> = ["Tmp", "tmp"].map(String::from).to_vec(); remove_prefixed(&mut v, "tmp"); v }', 'vec!["Tmp".to_string()]'),
        T("prefix_longer", "[\"tm\"], prefix \"tmp\"", '{ let mut v = vec!["tm".to_string()]; remove_prefixed(&mut v, "tmp"); v }', 'vec!["tm".to_string()]'),
        T("unicode_prefix", "[\"élan\", \"elan\"], prefix \"é\"", '{ let mut v: Vec<String> = ["élan", "elan"].map(String::from).to_vec(); remove_prefixed(&mut v, "é"); v }', 'vec!["elan".to_string()]'),
        T("order_kept", "[\"b1\", \"a\", \"b2\", \"c\", \"b3\"], prefix \"b\"", '{ let mut v: Vec<String> = ["b1", "a", "b2", "c", "b3"].map(String::from).to_vec(); remove_prefixed(&mut v, "b"); v }', 'vec!["a".to_string(), "c".to_string()]'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2016);
            for _ in 0..300 {
                let n = rng.below(8);
                let names: Vec<String> = (0..n).map(|_| { let l = rng.below(4); rng.string(l, "ab") }).collect();
                let pl = rng.below(3);
                let prefix = rng.string(pl, "ab");
                let want: Vec<String> = names.iter().filter(|s| !s.starts_with(prefix.as_str())).cloned().collect();
                let mut got = names.clone();
                remove_prefixed(&mut got, &prefix);
                check!(format!("names = {names:?}, prefix = {prefix:?}"), got, want);
            }
        }

        #[test]
        fn scale_300k_matches_first() {
            let mut v: Vec<String> = (0..300_000).map(|i| if i < 150_000 { format!("tmp{i}") } else { format!("keep{i}") }).collect();
            remove_prefixed(&mut v, "tmp");
            check!("150000 names \\"tmp…\\" then 150000 others, prefix \\"tmp\\"", (v.len(), v[0].as_str() == "keep150000"), (150_000, true));
        }
        """,
    ],
    wrong=dict(
        remove_in_a_loop=REMOVE_WRONG.replace("BODY", """if names[i].starts_with(prefix) {
                names.remove(i);
            } else {
                i += 1;
            }"""),
        skips_after_remove=REMOVE_WRONG.replace("BODY", """if names[i].starts_with(prefix) {
                names.remove(i);
            }
            i += 1;"""),
    ),
)

MORE["retain-mut"] = dict(
    visible=[
        T("negatives", "[-3, 0, -4]", "{ let mut v = vec![-3, 0, -4]; drop_zeros_and_halve(&mut v); v }", "vec![-1, -2]"),
        T("halves_to_zero", "[1, 2]", "{ let mut v = vec![1, 2]; drop_zeros_and_halve(&mut v); v }", "vec![0, 1]"),
        T("empty", "[]", "{ let mut v: Vec<i32> = vec![]; drop_zeros_and_halve(&mut v); v }", "Vec::<i32>::new()"),
    ],
    hidden=[
        T("no_zeros", "[8, 6]", "{ let mut v = vec![8, 6]; drop_zeros_and_halve(&mut v); v }", "vec![4, 3]"),
        T("odd", "[7]", "{ let mut v = vec![7]; drop_zeros_and_halve(&mut v); v }", "vec![3]"),
        T("i32_min", "[i32::MIN]", "{ let mut v = vec![i32::MIN]; drop_zeros_and_halve(&mut v); v }", "vec![-1_073_741_824]"),
        T("i32_max", "[i32::MAX]", "{ let mut v = vec![i32::MAX]; drop_zeros_and_halve(&mut v); v }", "vec![1_073_741_823]"),
        T("minus_one", "[-1]", "{ let mut v = vec![-1]; drop_zeros_and_halve(&mut v); v }", "vec![0]"),
        T("zeros_between", "[0, 2, 0, 0, 4, 0]", "{ let mut v = vec![0, 2, 0, 0, 4, 0]; drop_zeros_and_halve(&mut v); v }", "vec![1, 2]"),
        T("single_zero", "[0]", "{ let mut v = vec![0]; drop_zeros_and_halve(&mut v); v }", "Vec::<i32>::new()"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2017);
            for _ in 0..300 {
                let n = rng.below(10);
                let v: Vec<i32> = rng.vec(n, -5, 5);
                let want: Vec<i32> = v.iter().filter(|&&x| x != 0).map(|&x| x / 2).collect();
                let mut got = v.clone();
                drop_zeros_and_halve(&mut got);
                check!(format!("v = {v:?}"), got, want);
            }
        }

        #[test]
        fn scale_800k_zeros_first() {
            let mut v = vec![0; 400_000];
            v.resize(800_000, 6);
            drop_zeros_and_halve(&mut v);
            check!("400000 zeros then 400000 sixes", (v.len(), v[0], v[399_999]), (400_000, 3, 3));
        }
        """,
    ],
    wrong=dict(
        halve_then_check="""
            pub fn drop_zeros_and_halve(v: &mut Vec<i32>) {
                v.retain_mut(|x| {
                    *x /= 2;
                    *x != 0
                });
            }
        """,
        shift_right="""
            pub fn drop_zeros_and_halve(v: &mut Vec<i32>) {
                v.retain_mut(|x| {
                    if *x == 0 {
                        return false;
                    }
                    *x >>= 1;
                    true
                });
            }
        """,
        remove_in_a_loop="""
            pub fn drop_zeros_and_halve(v: &mut Vec<i32>) {
                let mut i = 0;
                while i < v.len() {
                    if v[i] == 0 {
                        v.remove(i);
                    } else {
                        v[i] /= 2;
                        i += 1;
                    }
                }
            }
        """,
    ),
)

MORE["fix-push-while-iterating"] = dict(
    visible=[
        T("star_in_middle", "[\"a*b\"]", '{ let mut v = vec!["a*b".to_string()]; expand(&mut v); v }', 'vec!["a*b"]'),
        T("order", "[\"b*\", \"x\", \"a*\"]", '{ let mut v: Vec<String> = ["b*", "x", "a*"].map(String::from).to_vec(); expand(&mut v); v }', 'vec!["b*", "x", "a*", "b*.1", "b*.2", "a*.1", "a*.2"]'),
        T("none", "[\"x\"]", '{ let mut v = vec!["x".to_string()]; expand(&mut v); v.len() }', "1"),
    ],
    hidden=[
        T("empty", "[]", "{ let mut v: Vec<String> = vec![]; expand(&mut v); v.len() }", "0"),
        T("only_star", "[\"*\"]", '{ let mut v = vec!["*".to_string()]; expand(&mut v); v }', 'vec!["*", "*.1", "*.2"]'),
        T("double_star", "[\"a**\"]", '{ let mut v = vec!["a**".to_string()]; expand(&mut v); v }', 'vec!["a**", "a**.1", "a**.2"]'),
        T("unicode", "[\"é*\"]", '{ let mut v = vec!["é*".to_string()]; expand(&mut v); v }', 'vec!["é*", "é*.1", "é*.2"]'),
        T("duplicates", "[\"a*\", \"a*\"]", '{ let mut v: Vec<String> = ["a*", "a*"].map(String::from).to_vec(); expand(&mut v); v }', 'vec!["a*", "a*", "a*.1", "a*.2", "a*.1", "a*.2"]'),
        T("star_first", "[\"*a\"]", '{ let mut v = vec!["*a".to_string()]; expand(&mut v); v }', 'vec!["*a"]'),
        T("many", "1000 starred tasks", '{ let mut v: Vec<String> = (0..1000).map(|i| format!("t{i}*")).collect(); expand(&mut v); (v.len(), v[1000].clone(), v[2999].clone()) }', '(3000, "t0*.1".to_string(), "t999*.2".to_string())'),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2018);
            for _ in 0..300 {
                let n = rng.below(6);
                let tasks: Vec<String> = (0..n).map(|_| { let l = rng.below(4); rng.string(l, "a*") }).collect();
                let mut want = tasks.clone();
                for t in &tasks {
                    if t.ends_with('*') {
                        want.push(format!("{t}.1"));
                        want.push(format!("{t}.2"));
                    }
                }
                let mut got = tasks.clone();
                expand(&mut got);
                check!(format!("tasks = {tasks:?}"), got, want);
            }
        }
        """,
    ],
    wrong=dict(
        subtasks_inline="""
            /// For each task ending in '*', appends "<task>.1" and "<task>.2".
            pub fn expand(tasks: &mut Vec<String>) {
                let mut out = Vec::new();
                for t in tasks.iter() {
                    out.push(format!("{t}"));
                    if t.ends_with('*') {
                        out.push(format!("{t}.1"));
                        out.push(format!("{t}.2"));
                    }
                }
                *tasks = out;
            }
        """,
        contains_star="""
            /// For each task ending in '*', appends "<task>.1" and "<task>.2".
            pub fn expand(tasks: &mut Vec<String>) {
                let extra: Vec<String> = tasks
                    .iter()
                    .filter(|t| t.contains('*'))
                    .flat_map(|t| [format!("{t}.1"), format!("{t}.2")])
                    .collect();
                tasks.extend(extra);
            }
        """,
    ),
)

MORE["collect-then-mutate"] = dict(
    visible=[
        T("single", "[7]", "{ let mut v = [7]; bump_below_average(&mut v); v }", "[7]"),
        T("uses_the_original_average", "[0, 0, 30]", "{ let mut v = [0, 0, 30]; bump_below_average(&mut v); v }", "[10, 10, 30]"),
        T("empty", "[]", "{ let mut v: [u32; 0] = []; bump_below_average(&mut v); v }", "[]"),
    ],
    hidden=[
        T("floor_average", "[1, 2, 4]", "{ let mut v = [1, 2, 4]; bump_below_average(&mut v); v }", "[11, 2, 4]"),
        T("strictly_below", "[0, 10]", "{ let mut v = [0, 10]; bump_below_average(&mut v); v }", "[10, 10]"),
        T("no_overflow", "[u32::MAX, u32::MAX, 0]", "{ let mut v = [u32::MAX, u32::MAX, 0]; bump_below_average(&mut v); v }", "[u32::MAX, u32::MAX, 10]"),
        T("zeros", "[0, 0, 1]", "{ let mut v = [0, 0, 1]; bump_below_average(&mut v); v }", "[0, 0, 1]"),
        T("duplicates", "[3, 3, 9]", "{ let mut v = [3, 3, 9]; bump_below_average(&mut v); v }", "[13, 13, 9]"),
        T("bump_passes_average", "[10, 20, 30, 40]", "{ let mut v = [10, 20, 30, 40]; bump_below_average(&mut v); v }", "[20, 30, 30, 40]"),
        T("all_zero", "[0, 0]", "{ let mut v = [0, 0]; bump_below_average(&mut v); v }", "[0, 0]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2019);
            for _ in 0..300 {
                let n = rng.below(8);
                let v: Vec<u32> = rng.vec(n, 0, 50);
                let mut want = v.clone();
                if n > 0 {
                    let avg = v.iter().map(|&s| s as u64).sum::<u64>() / n as u64;
                    for s in want.iter_mut() {
                        if (*s as u64) < avg {
                            *s += 10;
                        }
                    }
                }
                let mut got = v.clone();
                bump_below_average(&mut got);
                check!(format!("scores = {v:?}"), got, want);
            }
        }

        #[test]
        fn scale_200k() {
            let mut v: Vec<u32> = (0..200_000).map(|i| i % 100).collect();
            bump_below_average(&mut v);
            check!("scores = [0, 1, …, 99] × 2000 (average 49)", (v.iter().map(|&x| x as u64).sum::<u64>(), v[0], v[48], v[49]), (10_880_000, 10, 58, 49));
        }
        """,
    ],
    wrong=dict(
        average_in_the_loop="""
            pub fn bump_below_average(scores: &mut [u32]) {
                for i in 0..scores.len() {
                    let avg = scores.iter().map(|&s| s as u64).sum::<u64>() / scores.len() as u64;
                    if (scores[i] as u64) < avg {
                        scores[i] += 10;
                    }
                }
            }
        """,
        u32_sum="""
            pub fn bump_below_average(scores: &mut [u32]) {
                if scores.is_empty() {
                    return;
                }
                let avg = scores.iter().sum::<u32>() / scores.len() as u32;
                for s in scores.iter_mut().filter(|s| **s < avg) {
                    *s += 10;
                }
            }
        """,
    ),
)

JOB = """
    #[derive(Debug, PartialEq)]
    pub struct Job {
        pub name: &'static str,
        pub deadline: u64,
    }

    pub fn take_expired(jobs: &mut Vec<Job>, now: u64) -> Vec<Job> {
        BODY
    }
"""
MORE["extract-if"] = dict(
    visible=[
        T("at_deadline_kept", "deadline 10; now 10", '{ let mut v = vec![Job { name: "a", deadline: 10 }]; let gone = take_expired(&mut v, 10); (gone.len(), v.len()) }', "(0, 1)"),
        T("order_both", "deadlines 1, 9, 2, 8, 3; now 5", '{ let mut v = vec![Job { name: "a", deadline: 1 }, Job { name: "b", deadline: 9 }, Job { name: "c", deadline: 2 }, Job { name: "d", deadline: 8 }, Job { name: "e", deadline: 3 }]; let gone = take_expired(&mut v, 5); (gone.iter().map(|j| j.name).collect::<Vec<_>>(), v.iter().map(|j| j.name).collect::<Vec<_>>()) }', '(vec!["a", "c", "e"], vec!["b", "d"])'),
        T("empty", "no jobs", "{ let mut v: Vec<Job> = vec![]; let gone = take_expired(&mut v, 5); (gone.len(), v.len()) }", "(0, 0)"),
    ],
    hidden=[
        T("now_zero", "deadline 0; now 0", '{ let mut v = vec![Job { name: "a", deadline: 0 }]; (take_expired(&mut v, 0).len(), v.len()) }', "(0, 1)"),
        T("u64_max", "deadline u64::MAX - 1; now u64::MAX", '{ let mut v = vec![Job { name: "a", deadline: u64::MAX - 1 }, Job { name: "b", deadline: u64::MAX }]; let gone = take_expired(&mut v, u64::MAX); (gone.len(), v[0].name) }', '(1, "b")'),
        T("same_deadlines", "deadlines 5, 5; now 6", '{ let mut v = vec![Job { name: "a", deadline: 5 }, Job { name: "b", deadline: 5 }]; let gone = take_expired(&mut v, 6); (gone.len(), v.len()) }', "(2, 0)"),
        T("returns_the_jobs", "deadlines 1, 20; now 10", '{ let mut v = vec![Job { name: "a", deadline: 1 }, Job { name: "b", deadline: 20 }]; take_expired(&mut v, 10) }', 'vec![Job { name: "a", deadline: 1 }]'),
        T("many", "1000 jobs with deadlines 0..1000; now 500", '{ let mut v: Vec<Job> = (0..1000).map(|d| Job { name: "j", deadline: d }).collect(); let gone = take_expired(&mut v, 500); (gone.len(), v.len(), gone[499].deadline, v[0].deadline) }', "(500, 500, 499, 500)"),
        T("called_twice", "deadlines 3, 7; now 5 then 8", '{ let mut v = vec![Job { name: "a", deadline: 3 }, Job { name: "b", deadline: 7 }]; let x = take_expired(&mut v, 5).len(); let y = take_expired(&mut v, 8).len(); (x, y, v.len()) }', "(1, 1, 0)"),
        """
        #[test]
        fn random_vs_model() {
            const NAMES: [&str; 5] = ["a", "b", "c", "d", "e"];
            let mut rng = anneal_prelude::Rng::new(2020);
            for _ in 0..300 {
                let n = rng.below(8);
                let specs: Vec<(&'static str, u64)> = (0..n).map(|_| { let name = *rng.pick(&NAMES); (name, rng.below(10) as u64) }).collect();
                let now = rng.below(11) as u64;
                let make = |keep: bool| -> Vec<Job> { specs.iter().filter(|s| (s.1 < now) != keep).map(|&(name, deadline)| Job { name, deadline }).collect() };
                let mut jobs: Vec<Job> = specs.iter().map(|&(name, deadline)| Job { name, deadline }).collect();
                let gone = take_expired(&mut jobs, now);
                check!(format!("jobs = {specs:?}, now = {now}"), (gone, jobs), (make(false), make(true)));
            }
        }

        #[test]
        fn scale_300k_expired_first() {
            let mut v: Vec<Job> = (0..300_000u64).map(|i| Job { name: "j", deadline: if i < 150_000 { i } else { 1_000_000 + i } }).collect();
            let gone = take_expired(&mut v, 150_000);
            check!("150000 expired jobs then 150000 live ones", (gone.len(), v.len(), gone[149_999].deadline, v[0].deadline), (150_000, 150_000, 149_999, 1_150_000));
        }
        """,
    ],
    wrong=dict(
        remove_in_a_loop=JOB.replace("BODY", """let mut gone = Vec::new();
        let mut i = 0;
        while i < jobs.len() {
            if jobs[i].deadline < now {
                gone.push(jobs.remove(i));
            } else {
                i += 1;
            }
        }
        gone"""),
        at_deadline_counts=JOB.replace("BODY", "jobs.extract_if(.., |j| j.deadline <= now).collect()"),
        swap_remove=JOB.replace("BODY", """let mut gone = Vec::new();
        let mut i = 0;
        while i < jobs.len() {
            if jobs[i].deadline < now {
                gone.push(jobs.swap_remove(i));
            } else {
                i += 1;
            }
        }
        gone"""),
    ),
)

MAP_WRONG = """
    use std::collections::HashMap;

    /// Removes every entry whose count is zero.
    pub fn drop_zero(counts: &mut HashMap<String, u32>) {
        BODY
    }
"""
MORE["fix-map-mutation-during-iteration"] = dict(
    visible=[
        T("none_zero", "{a: 1, b: 2}", '{ let mut m = std::collections::HashMap::from([("a".to_string(), 1), ("b".to_string(), 2)]); drop_zero(&mut m); m }', f'{HM}::from([("a".to_string(), 1), ("b".to_string(), 2)])'),
        T("all_zero", "{a: 0, b: 0}", '{ let mut m = std::collections::HashMap::from([("a".to_string(), 0), ("b".to_string(), 0)]); drop_zero(&mut m); m.len() }', "0"),
        T("values_untouched", "{a: 5, b: 0, c: 7}", '{ let mut m = std::collections::HashMap::from([("a".to_string(), 5), ("b".to_string(), 0), ("c".to_string(), 7)]); drop_zero(&mut m); m }', f'{HM}::from([("a".to_string(), 5), ("c".to_string(), 7)])'),
    ],
    hidden=[
        T("single_zero", "{a: 0}", '{ let mut m = std::collections::HashMap::from([("a".to_string(), 0)]); drop_zero(&mut m); m.len() }', "0"),
        T("u32_max_kept", "{a: u32::MAX}", '{ let mut m = std::collections::HashMap::from([("a".to_string(), u32::MAX)]); drop_zero(&mut m); m }', f'{HM}::from([("a".to_string(), u32::MAX)])'),
        T("unicode_keys", "{ä: 0, ö: 1}", '{ let mut m = std::collections::HashMap::from([("ä".to_string(), 0), ("ö".to_string(), 1)]); drop_zero(&mut m); m }', f'{HM}::from([("ö".to_string(), 1)])'),
        T("empty_key", "{\"\": 0, x: 3}", '{ let mut m = std::collections::HashMap::from([(String::new(), 0), ("x".to_string(), 3)]); drop_zero(&mut m); m }', f'{HM}::from([("x".to_string(), 3)])'),
        T("many", "10000 keys, every third zero", "{ let mut m: std::collections::HashMap<String, u32> = (0..10_000u32).map(|i| (i.to_string(), i % 3)).collect(); drop_zero(&mut m); m.len() }", "6666"),
        T("ones_kept", "{a: 1, b: 0}", '{ let mut m = std::collections::HashMap::from([("a".to_string(), 1), ("b".to_string(), 0)]); drop_zero(&mut m); m.contains_key("a") && !m.contains_key("b") }', "true"),
        T("called_twice", "{a: 0, b: 1}, twice", '{ let mut m = std::collections::HashMap::from([("a".to_string(), 0), ("b".to_string(), 1)]); drop_zero(&mut m); drop_zero(&mut m); m.len() }', "1"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2021);
            for _ in 0..300 {
                let n = rng.below(8);
                let entries: Vec<(String, u32)> = (0..n).map(|_| { let k = rng.string(1, "abcde"); (k, rng.below(3) as u32) }).collect();
                let mut m: std::collections::HashMap<String, u32> = entries.iter().cloned().collect();
                let mut want: Vec<(String, u32)> = m.iter().filter(|(_, &v)| v != 0).map(|(k, &v)| (k.clone(), v)).collect();
                want.sort();
                drop_zero(&mut m);
                let mut got: Vec<(String, u32)> = m.into_iter().collect();
                got.sort();
                check!(format!("entries = {entries:?}"), got, want);
            }
        }

        #[test]
        fn scale_200k() {
            let mut m: std::collections::HashMap<String, u32> = (0..200_000u32).map(|i| (format!("k{i}"), i % 2)).collect();
            drop_zero(&mut m);
            check!("200000 keys, every other one zero", (m.len(), m.values().all(|&v| v == 1)), (100_000, true));
        }
        """,
    ],
    wrong=dict(
        find_then_remove=MAP_WRONG.replace("BODY", """while let Some(k) = counts.iter().find(|(_, v)| **v == 0).map(|(k, _)| k.to_string()) {
            counts.remove(&k);
        }"""),
        drops_first_only=MAP_WRONG.replace("BODY", """let zero = counts.iter().find(|(_, v)| **v == 0).map(|(k, _)| k.to_string());
        if let Some(k) = zero {
            counts.remove(&k);
        }"""),
    ),
)

EDITOR_WRONG = """
    pub struct Editor {
        pub text: String,
        pub history: Vec<String>,
    }

    impl Editor {
        /// Saves the current text, then appends `more`.
        pub fn append(&mut self, more: &str) {
            BODY
        }
    }
"""
MORE["fix-field-borrow-and-mut-method"] = dict(
    visible=[
        T("unicode", "text \"é\", append \"ß\"", '{ let mut e = Editor { text: "é".into(), history: vec![] }; e.append("ß"); (e.text, e.history) }', '("éß".to_string(), vec!["é".to_string()])'),
        T("existing_history", "history [\"old\"], text \"t\", append \"x\"", '{ let mut e = Editor { text: "t".into(), history: vec!["old".into()] }; e.append("x"); e.history }', 'vec!["old".to_string(), "t".to_string()]'),
        T("twice", "append \"x\" then \"y\"", '{ let mut e = Editor { text: String::new(), history: vec![] }; e.append("x"); e.append("y"); e.history }', 'vec![String::new(), "x".to_string()]'),
    ],
    hidden=[
        T("three_appends", "append \"a\", \"b\", \"c\"", '{ let mut e = Editor { text: String::new(), history: vec![] }; e.append("a"); e.append("b"); e.append("c"); (e.text, e.history) }', '("abc".to_string(), vec![String::new(), "a".to_string(), "ab".to_string()])'),
        T("snapshot_is_before", "text \"x\", append \"y\"", '{ let mut e = Editor { text: "x".into(), history: vec![] }; e.append("y"); e.history }', 'vec!["x".to_string()]'),
        T("empty_both", "text \"\", append \"\"", '{ let mut e = Editor { text: String::new(), history: vec![] }; e.append(""); (e.text, e.history) }', "(String::new(), vec![String::new()])"),
        T("long", "text 1000 × \"a\"", '{ let mut e = Editor { text: "a".repeat(1000), history: vec![] }; e.append("b"); (e.history[0].len(), e.text.len()) }', "(1000, 1001)"),
        T("newline", "text \"a\\n\", append \"b\"", '{ let mut e = Editor { text: "a\\n".into(), history: vec![] }; e.append("b"); (e.text, e.history) }', '("a\\nb".to_string(), vec!["a\\n".to_string()])'),
        T("many_appends", "100 appends of \"x\"", '{ let mut e = Editor { text: String::new(), history: vec![] }; for _ in 0..100 { e.append("x"); } (e.history.len(), e.history[99].len(), e.text.len()) }', "(100, 99, 100)"),
        T("same_text_twice", "text \"q\", append \"\" twice", '{ let mut e = Editor { text: "q".into(), history: vec![] }; e.append(""); e.append(""); e.history }', 'vec!["q".to_string(), "q".to_string()]'),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2022);
            for _ in 0..300 {
                let n = rng.below(6);
                let parts: Vec<String> = (0..n).map(|_| { let l = rng.below(3); rng.string(l, "ab") }).collect();
                let mut e = Editor { text: String::new(), history: vec![] };
                let (mut text, mut history) = (String::new(), Vec::new());
                for p in &parts {
                    e.append(p);
                    history.push(text.clone());
                    text.push_str(p);
                }
                check!(format!("appends {parts:?}"), (e.text, e.history), (text, history));
            }
        }
        """,
    ],
    wrong=dict(
        saves_after=EDITOR_WRONG.replace("BODY", """self.text.push_str(more);
            self.history.push(self.text.to_string());"""),
        saves_the_addition=EDITOR_WRONG.replace("BODY", """self.history.push(more.to_string());
            self.text.push_str(more);"""),
    ),
)

PAIR_WRONG = """
    pub fn pair_mut<T>(v: &mut [T], i: usize, j: usize) -> Option<(&mut T, &mut T)> {
        if CHECK {
            return None;
        }
        let (lo, hi) = (i.min(j), i.max(j));
        let (left, right) = v.split_at_mut(hi);
        let (a, b) = (&mut left[lo], &mut right[0]);
        RET
    }
"""
MORE["pair-mut"] = dict(
    visible=[
        T("adjacent", "v = [1, 2], i = 0, j = 1", "{ let mut v = [1, 2]; if let Some((a, b)) = pair_mut(&mut v, 0, 1) { std::mem::swap(a, b); } v }", "[2, 1]"),
        T("order_kept", "i = 2, j = 0", "{ let mut v = [10, 20, 30]; let (a, b) = pair_mut(&mut v, 2, 0).unwrap(); (*a, *b) }", "(30, 10)"),
        T("i_out_of_bounds", "v = [1, 2], i = 2, j = 0", "pair_mut(&mut [1, 2], 2, 0).is_none()", "true"),
    ],
    hidden=[
        T("empty_slice", "v = [], i = 0, j = 1", "pair_mut::<i32>(&mut [], 0, 1).is_none()", "true"),
        T("both_out_equal", "v = [1, 2], i = j = 5", "pair_mut(&mut [1, 2], 5, 5).is_none()", "true"),
        T("j_is_len", "v = [1, 2, 3], i = 0, j = 3", "pair_mut(&mut [1, 2, 3], 0, 3).is_none()", "true"),
        T("strings", "v = [\"a\", \"b\"], push to both", '{ let mut v = vec!["a".to_string(), "b".to_string()]; if let Some((a, b)) = pair_mut(&mut v, 1, 0) { a.push(\'1\'); b.push(\'0\'); } v }', 'vec!["a0".to_string(), "b1".to_string()]'),
        T("last_and_first", "v = 0..10, i = 9, j = 0", "{ let mut v: Vec<i32> = (0..10).collect(); let (a, b) = pair_mut(&mut v, 9, 0).unwrap(); (*a, *b) }", "(9, 0)"),
        T("usize_max", "i = usize::MAX", "pair_mut(&mut [1, 2], usize::MAX, 0).is_none()", "true"),
        T("writes_land", "v = [0, 0, 0], set v[1] = 7, v[2] = 8", "{ let mut v = [0, 0, 0]; let (a, b) = pair_mut(&mut v, 1, 2).unwrap(); *a = 7; *b = 8; v }", "[0, 7, 8]"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2023);
            for _ in 0..300 {
                let n = rng.below(6);
                let v0: Vec<i32> = rng.vec(n, 0, 99);
                let i = rng.below(n + 2);
                let j = rng.below(n + 2);
                let mut v = v0.clone();
                let got = pair_mut(&mut v, i, j).map(|(a, b)| {
                    let r = (*a, *b);
                    *a = -1;
                    *b = -2;
                    r
                });
                let mut want_v = v0.clone();
                let want = if i != j && i < n && j < n {
                    want_v[i] = -1;
                    want_v[j] = -2;
                    Some((v0[i], v0[j]))
                } else {
                    None
                };
                check!(format!("v = {v0:?}, i = {i}, j = {j}"), (got, v), (want, want_v));
            }
        }
        """,
    ],
    wrong=dict(
        only_checks_j=PAIR_WRONG.replace("CHECK", "i == j || j >= v.len()").replace("RET", "Some(if i < j { (a, b) } else { (b, a) })"),
        sorted_order=PAIR_WRONG.replace("CHECK", "i == j || i >= v.len() || j >= v.len()").replace("RET", "Some((a, b))"),
    ),
)

STATS_WRONG = """
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
            BODY
        }
    }
"""
MORE["destructure-self"] = dict(
    visible=[
        T("negatives", "max f64::MIN, xs = [-2.0, -1.0]", "{ let mut s = Stats { values: vec![], total: 0.0, max: f64::MIN }; s.record_all(&[-2.0, -1.0]); (s.total, s.max) }", "(-3.0, -1.0)"),
        T("total_accumulates", "total 10.0, xs = [1.0, 2.0]", "{ let mut s = Stats { values: vec![], total: 10.0, max: 0.0 }; s.record_all(&[1.0, 2.0]); s.total }", "13.0"),
        T("empty", "xs = []", "{ let mut s = Stats { values: vec![], total: 1.0, max: 0.0 }; s.record_all(&[]); (s.values.len(), s.total) }", "(0, 1.0)"),
    ],
    hidden=[
        T("single", "xs = [5.0]", "{ let mut s = Stats { values: vec![], total: 0.0, max: f64::MIN }; s.record_all(&[5.0]); (s.values, s.total, s.max) }", "(vec![5.0], 5.0, 5.0)"),
        T("appends_to_existing", "values [1.0], xs = [2.0, 3.0]", "{ let mut s = Stats { values: vec![1.0], total: 1.0, max: 1.0 }; s.record_all(&[2.0, 3.0]); s.values }", "vec![1.0, 2.0, 3.0]"),
        T("max_from_xs", "max 0.0, xs = [0.5, 0.25]", "{ let mut s = Stats { values: vec![], total: 0.0, max: 0.0 }; s.record_all(&[0.5, 0.25]); s.max }", "0.5"),
        T("order_kept", "xs = [3.0, 1.0, 2.0]", "{ let mut s = Stats { values: vec![], total: 0.0, max: 0.0 }; s.record_all(&[3.0, 1.0, 2.0]); s.values }", "vec![3.0, 1.0, 2.0]"),
        T("duplicates", "xs = [2.0, 2.0]", "{ let mut s = Stats { values: vec![], total: 0.0, max: f64::MIN }; s.record_all(&[2.0, 2.0]); (s.values.len(), s.total, s.max) }", "(2, 4.0, 2.0)"),
        T("many", "1000 × 1.0", "{ let mut s = Stats { values: vec![], total: 0.0, max: 0.0 }; s.record_all(&vec![1.0; 1000]); (s.values.len(), s.total, s.max) }", "(1000, 1000.0, 1.0)"),
        T("called_twice", "xs = [1.0], then [4.0]", "{ let mut s = Stats { values: vec![], total: 0.0, max: f64::MIN }; s.record_all(&[1.0]); s.record_all(&[4.0]); (s.values, s.total, s.max) }", "(vec![1.0, 4.0], 5.0, 4.0)"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2024);
            for _ in 0..300 {
                let n0 = rng.below(4);
                let v0: Vec<f64> = (0..n0).map(|_| rng.int(-50, 50) as f64).collect();
                let total0 = rng.int(-100, 100) as f64;
                let max0 = rng.int(-60, 60) as f64;
                let k = rng.below(6);
                let xs: Vec<f64> = (0..k).map(|_| rng.int(-50, 50) as f64).collect();
                let mut s = Stats { values: v0.clone(), total: total0, max: max0 };
                s.record_all(&xs);
                let mut values = v0.clone();
                values.extend(&xs);
                let want = (values, total0 + xs.iter().sum::<f64>(), xs.iter().fold(max0, |m, &x| m.max(x)));
                check!(format!("values {v0:?}, total {total0}, max {max0}, xs = {xs:?}"), (s.values, s.total, s.max), want);
            }
        }
        """,
    ],
    wrong=dict(
        overwrites_total=STATS_WRONG.replace("BODY", """let Stats { values, total, max } = self;
            *total = 0.0;
            for &x in xs {
                update(values, total, max, x);
            }"""),
        ignores_old_max=STATS_WRONG.replace("BODY", """let Stats { values, total, max } = self;
            *max = f64::MIN;
            for &x in xs {
                update(values, total, max, x);
            }"""),
    ),
)

SWAP_WRONG = """
    /// Swaps the elements at `i` and `j`.
    pub fn swap_items(v: &mut [String], i: usize, j: usize) {
        BODY
    }
"""
MORE["fix-swap-without-swap"] = dict(
    visible=[
        T("unicode", "[\"é\", \"ß\"], 0 ↔ 1", '{ let mut v = ["é", "ß"].map(String::from); swap_items(&mut v, 0, 1); v }', '["ß", "é"].map(String::from)'),
        T("same_index", "1 ↔ 1", '{ let mut v = ["a", "b"].map(String::from); swap_items(&mut v, 1, 1); v }', '["a", "b"].map(String::from)'),
        T("reversed", "2 ↔ 0", '{ let mut v = ["a", "b", "c"].map(String::from); swap_items(&mut v, 2, 0); v }', '["c", "b", "a"].map(String::from)'),
    ],
    hidden=[
        T("middle", "[\"a\", \"b\", \"c\", \"d\"], 1 ↔ 2", '{ let mut v = ["a", "b", "c", "d"].map(String::from); swap_items(&mut v, 1, 2); v }', '["a", "c", "b", "d"].map(String::from)'),
        T("empty_strings", "[\"\", \"x\"], 0 ↔ 1", '{ let mut v = ["", "x"].map(String::from); swap_items(&mut v, 0, 1); v }', '["x", ""].map(String::from)'),
        T("same_values", "[\"a\", \"a\"], 0 ↔ 1", '{ let mut v = ["a", "a"].map(String::from); swap_items(&mut v, 0, 1); v }', '["a", "a"].map(String::from)'),
        T("last_first", "5 names, 4 ↔ 0", '{ let mut v = ["a", "b", "c", "d", "e"].map(String::from); swap_items(&mut v, 4, 0); v }', '["e", "b", "c", "d", "a"].map(String::from)'),
        T("swap_back", "0 ↔ 2 twice", '{ let mut v = ["a", "b", "c"].map(String::from); swap_items(&mut v, 0, 2); swap_items(&mut v, 2, 0); v }', '["a", "b", "c"].map(String::from)'),
        T("single_same", "[\"z\"], 0 ↔ 0", '{ let mut v = ["z"].map(String::from); swap_items(&mut v, 0, 0); v }', '["z"].map(String::from)'),
        T("in_a_vec", "1000 names, 0 ↔ 999", "{ let mut v: Vec<String> = (0..1000).map(|i| i.to_string()).collect(); swap_items(&mut v, 0, 999); (v[0].clone(), v[999].clone(), v[500].clone()) }", '("999".to_string(), "0".to_string(), "500".to_string())'),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2025);
            for _ in 0..300 {
                let n = 1 + rng.below(6);
                let v0: Vec<String> = (0..n).map(|_| { let l = rng.below(3); rng.string(l, "ab") }).collect();
                let i = rng.below(n);
                let j = rng.below(n);
                let mut want = v0.clone();
                want.swap(i, j);
                let mut got = v0.clone();
                swap_items(&mut got, i, j);
                check!(format!("v = {v0:?}, {i} ↔ {j}"), got, want);
            }
        }
        """,
    ],
    wrong=dict(
        no_same_index_check=SWAP_WRONG.replace("BODY", """let (lo, hi) = (i.min(j), i.max(j));
        let (left, right) = v.split_at_mut(hi);
        let (a, b) = (&mut left[lo], &mut right[0]);
        let tmp = std::mem::take(a);
        *a = std::mem::take(b);
        *b = tmp;"""),
        assumes_i_before_j=SWAP_WRONG.replace("BODY", """if i == j {
            return;
        }
        let (left, right) = v.split_at_mut(j);
        let (a, b) = (&mut left[i], &mut right[0]);
        let tmp = std::mem::take(a);
        *a = std::mem::take(b);
        *b = tmp;"""),
        takes_twice=SWAP_WRONG.replace("BODY", """if i == j {
            return;
        }
        let (lo, hi) = (i.min(j), i.max(j));
        let (left, right) = v.split_at_mut(hi);
        let (a, b) = (&mut left[lo], &mut right[0]);
        *a = std::mem::take(b);
        *b = std::mem::take(a);"""),
    ),
)

VIEW_WRONG = """
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
            BODY
        }
    }
"""
MORE["view-struct"] = dict(
    visible=[
        T("shorter_title", "title \"abc\", retitle \"x\"", '{ let mut d = Document { title: "abc".into(), body: String::new(), tags: vec![] }; d.header().retitle("x"); d.title }', '"x".to_string()'),
        T("empty_title", "retitle \"\"", '{ let mut d = Document { title: "t".into(), body: String::new(), tags: vec![] }; d.header().retitle(""); (d.title, d.tags) }', '(String::new(), vec!["edited".to_string()])'),
        T("twice", "retitle twice", '{ let mut d = Document { title: String::new(), body: String::new(), tags: vec![] }; let mut h = d.header(); h.retitle("a"); h.retitle("b"); d.tags.len() }', "2"),
    ],
    hidden=[
        T("unicode_title", "retitle \"日本\"", '{ let mut d = Document { title: "t".into(), body: String::new(), tags: vec![] }; d.header().retitle("日本"); d.title }', '"日本".to_string()'),
        T("header_fields_point_into_doc", "push through the header's fields", '{ let mut d = Document { title: "a".into(), body: String::new(), tags: vec![] }; let h = d.header(); h.title.push_str("!"); h.tags.push("t".into()); (d.title, d.tags) }', '("a!".to_string(), vec!["t".to_string()])'),
        T("body_untouched", "body \"keep\"", '{ let mut d = Document { title: "t".into(), body: "keep".into(), tags: vec![] }; d.header().retitle("u"); d.body }', '"keep".to_string()'),
        T("twice_last_wins", "retitle \"a\" then \"b\"", '{ let mut d = Document { title: String::new(), body: String::new(), tags: vec![] }; let mut h = d.header(); h.retitle("a"); h.retitle("b"); (d.title, d.tags) }', '("b".to_string(), vec!["edited".to_string(), "edited".to_string()])'),
        T("existing_tags_order", "tags [\"x\", \"y\"]", '{ let mut d = Document { title: String::new(), body: String::new(), tags: vec!["x".into(), "y".into()] }; d.header().retitle("t"); d.tags }', 'vec!["x".to_string(), "y".to_string(), "edited".to_string()]'),
        T("same_title", "title \"t\", retitle \"t\"", '{ let mut d = Document { title: "t".into(), body: String::new(), tags: vec![] }; d.header().retitle("t"); d.title }', '"t".to_string()'),
        T("long_title", "retitle with 1000 chars", '{ let mut d = Document { title: "old".into(), body: String::new(), tags: vec![] }; let t = "z".repeat(1000); d.header().retitle(&t); d.title.len() }', "1000"),
        T("body_readable_after", "body stays usable", '{ let mut d = Document { title: String::new(), body: "b".into(), tags: vec![] }; { let mut h = d.header(); h.retitle("n"); } d.body.push_str("!"); d.body }', '"b!".to_string()'),
    ],
    wrong=dict(
        no_clear=VIEW_WRONG.replace("BODY", """self.title.push_str(new_title);
            self.tags.push("edited".to_string());"""),
        tag_first=VIEW_WRONG.replace("BODY", """self.title.clear();
            self.title.push_str(new_title);
            self.tags.insert(0, "edited".to_string());"""),
    ),
)

SHOP_WRONG = """
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
            BODY
        }

        pub fn log(&self) -> &[String] {
            &self.log
        }
    }
"""
MORE["fix-borrow-through-getter"] = dict(
    visible=[
        T("order", "items [9, 1, 8], limit 5", "{ let mut s = Shop::new(vec![9, 1, 8]); s.log_expensive(5); s.log().to_vec() }", 'vec!["expensive: 9", "expensive: 8"]'),
        T("empty_items", "items [], limit 0", "{ let mut s = Shop::new(vec![]); s.log_expensive(0); s.log().len() }", "0"),
        T("none", "items [1], limit 40", "{ let mut s = Shop::new(vec![1]); s.log_expensive(40); s.log().len() }", "0"),
    ],
    hidden=[
        T("all_expensive", "items [100, 200], limit 0", "{ let mut s = Shop::new(vec![100, 200]); s.log_expensive(0); s.log().to_vec() }", 'vec!["expensive: 100", "expensive: 200"]'),
        T("limit_near_max", "items [u32::MAX], limit u32::MAX - 1", "{ let mut s = Shop::new(vec![u32::MAX]); s.log_expensive(u32::MAX - 1); s.log().to_vec() }", 'vec!["expensive: 4294967295"]'),
        T("limit_max", "items [u32::MAX], limit u32::MAX", "{ let mut s = Shop::new(vec![u32::MAX]); s.log_expensive(u32::MAX); s.log().len() }", "0"),
        T("duplicates", "items [7, 7], limit 6", "{ let mut s = Shop::new(vec![7, 7]); s.log_expensive(6); s.log().len() }", "2"),
        T("called_twice", "items [9], limit 5, twice", "{ let mut s = Shop::new(vec![9]); s.log_expensive(5); s.log_expensive(5); s.log().to_vec() }", 'vec!["expensive: 9", "expensive: 9"]'),
        T("zero_price", "items [0], limit 0", "{ let mut s = Shop::new(vec![0]); s.log_expensive(0); s.log().len() }", "0"),
        T("many", "items 0..10000, limit 4999", "{ let mut s = Shop::new((0..10_000).collect()); s.log_expensive(4999); (s.log().len(), s.log()[0].clone()) }", '(5000, "expensive: 5000".to_string())'),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2026);
            for _ in 0..300 {
                let n = rng.below(8);
                let items: Vec<u32> = rng.vec(n, 0, 20);
                let limit = rng.int(0, 20) as u32;
                let want: Vec<String> = items.iter().filter(|&&p| p > limit).map(|p| format!("expensive: {p}")).collect();
                let mut s = Shop::new(items.clone());
                s.log_expensive(limit);
                check!(format!("items {items:?}, limit {limit}"), s.log().to_vec(), want);
            }
        }
        """,
    ],
    wrong=dict(
        at_limit_counts=SHOP_WRONG.replace("BODY", """for p in &self.items {
                if *p >= limit {
                    self.log.push(format!("expensive: {p}"));
                }
            }"""),
        stops_at_first_cheap=SHOP_WRONG.replace("BODY", """for p in self.items.iter().take_while(|p| **p > limit) {
                self.log.push(format!("expensive: {p}"));
            }"""),
    ),
)

GOI_WRONG = """
    use std::collections::HashMap;

    /// The value for `key`, inserting `default` first if it's missing.
    pub fn get_or_insert<'m>(map: &'m mut HashMap<u32, String>, key: u32, default: &str) -> &'m String {
        BODY
    }
"""
MORE["fix-get-or-insert"] = dict(
    visible=[
        T("empty_default", "{}, key 0, default \"\"", '{ let mut m = std::collections::HashMap::new(); let v = get_or_insert(&mut m, 0, "").clone(); (v, m.len()) }', "(String::new(), 1)"),
        T("existing_not_replaced", "{1: \"one\"}, key 1, default \"x\"", '{ let mut m = std::collections::HashMap::from([(1, "one".to_string())]); get_or_insert(&mut m, 1, "x"); (m[&1].clone(), m.len()) }', '("one".to_string(), 1)'),
        T("different_keys", "keys 1 then 2", '{ let mut m = std::collections::HashMap::new(); get_or_insert(&mut m, 1, "a"); let v = get_or_insert(&mut m, 2, "b").clone(); (v, m.len()) }', '("b".to_string(), 2)'),
    ],
    hidden=[
        T("many_keys", "1000 keys", '{ let mut m = std::collections::HashMap::new(); for k in 0..1000 { get_or_insert(&mut m, k, "v"); } m.len() }', "1000"),
        T("u32_max_key", "key u32::MAX", '{ let mut m = std::collections::HashMap::new(); get_or_insert(&mut m, u32::MAX, "big").clone() }', '"big".to_string()'),
        T("unicode_default", "default \"ünï\"", '{ let mut m = std::collections::HashMap::new(); get_or_insert(&mut m, 7, "ünï").clone() }', '"ünï".to_string()'),
        T("returns_the_stored_value", "the result points into the map", '{ let mut m = std::collections::HashMap::new(); let p: *const String = get_or_insert(&mut m, 5, "v"); p == &m[&5] as *const String }', "true"),
        T("existing_empty_value", "{4: \"\"}, key 4, default \"d\"", '{ let mut m = std::collections::HashMap::from([(4, String::new())]); get_or_insert(&mut m, 4, "d").clone() }', "String::new()"),
        T("others_untouched", "{1: \"a\"}, key 2", '{ let mut m = std::collections::HashMap::from([(1, "a".to_string())]); get_or_insert(&mut m, 2, "b"); m[&1].clone() }', '"a".to_string()'),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2027);
            for _ in 0..200 {
                let mut m = std::collections::HashMap::new();
                let mut model: Vec<(u32, String)> = Vec::new();
                let mut log = Vec::new();
                let n = rng.below(10);
                for _ in 0..n {
                    let key = rng.below(5) as u32;
                    let d = rng.string(2, "xy");
                    log.push(format!("({key}, {d:?})"));
                    let got = get_or_insert(&mut m, key, &d).clone();
                    let want = match model.iter().find(|(k, _)| *k == key) {
                        Some((_, v)) => v.clone(),
                        None => {
                            model.push((key, d.clone()));
                            d.clone()
                        }
                    };
                    check!(log.join(", "), got, want);
                }
                check!(log.join(", "), m.len(), model.len());
            }
        }
        """,
    ],
    wrong=dict(
        always_inserts=GOI_WRONG.replace("BODY", """map.insert(key, default.to_string());
        &map[&key]"""),
        forgets_to_insert=GOI_WRONG.replace("BODY", """if !map.contains_key(&key) {
            return Box::leak(Box::new(default.to_string()));
        }
        &map[&key]"""),
    ),
)

FLP_WRONG = """
    /// The first word longer than `n`; otherwise pushes "fallback" and returns it.
    pub fn first_long_or_push(words: &mut Vec<String>, n: usize) -> &String {
        if let Some(i) = words.iter().FIND {
            return &words[i];
        }
        words.push("fallback".to_string());
        words.last().expect("just pushed")
    }
"""
MORE["fix-conditional-return-of-borrow"] = dict(
    visible=[
        T("exactly_n_is_not_longer", "[\"abc\"], n = 3", '{ let mut v = vec!["abc".to_string()]; let r = first_long_or_push(&mut v, 3).clone(); (r, v.len()) }', '("fallback".to_string(), 2)'),
        T("first_of_several", "[\"aaa\", \"bbbb\", \"ccccc\"], n = 2", '{ let mut v = vec!["aaa".to_string(), "bbbb".to_string(), "ccccc".to_string()]; first_long_or_push(&mut v, 2).clone() }', '"aaa".to_string()'),
        T("empty", "[], n = 0", "{ let mut v = vec![]; first_long_or_push(&mut v, 0).clone() }", '"fallback".to_string()'),
    ],
    hidden=[
        T("no_push_when_found", "[\"a\", \"b\", \"long\"], n = 3", '{ let mut v = vec!["a".to_string(), "b".to_string(), "long".to_string()]; let r = first_long_or_push(&mut v, 3).clone(); (r, v.len()) }', '("long".to_string(), 3)'),
        T("n_zero", "[\"x\"], n = 0", '{ let mut v = vec!["x".to_string()]; first_long_or_push(&mut v, 0).clone() }', '"x".to_string()'),
        T("existing_fallback_word", "[\"fallback\"], n = 8", '{ let mut v = vec!["fallback".to_string()]; first_long_or_push(&mut v, 8); v.len() }', "2"),
        T("unicode_bytes", "[\"日本\"], n = 5", '{ let mut v = vec!["日本".to_string()]; first_long_or_push(&mut v, 5).clone() }', '"日本".to_string()'),
        T("n_max", "[\"abc\"], n = usize::MAX", '{ let mut v = vec!["abc".to_string()]; first_long_or_push(&mut v, usize::MAX).clone() }', '"fallback".to_string()'),
        T("twice_pushes_twice", "[], n = 10, twice", "{ let mut v = vec![]; first_long_or_push(&mut v, 10); first_long_or_push(&mut v, 10); v.len() }", "2"),
        T("fallback_found_second_time", "[], n = 3, twice", "{ let mut v = vec![]; first_long_or_push(&mut v, 3); first_long_or_push(&mut v, 3); v.len() }", "1"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2028);
            for _ in 0..300 {
                let k = rng.below(5);
                let words: Vec<String> = (0..k).map(|_| { let l = rng.below(5); rng.string(l, "ab") }).collect();
                let n = rng.below(5);
                let mut want_v = words.clone();
                let want = match words.iter().position(|w| w.len() > n) {
                    Some(i) => words[i].clone(),
                    None => {
                        want_v.push("fallback".to_string());
                        "fallback".to_string()
                    }
                };
                let mut v = words.clone();
                let got = first_long_or_push(&mut v, n).clone();
                check!(format!("words = {words:?}, n = {n}"), (got, v), (want, want_v));
            }
        }
        """,
    ],
    wrong=dict(
        last_long=FLP_WRONG.replace("FIND", "rposition(|w| w.len() > n)"),
        at_least_n=FLP_WRONG.replace("FIND", "position(|w| w.len() >= n)"),
    ),
)

MORE["get-disjoint-mut"] = dict(
    visible=[
        T("exact_balance", "[5, 0], 0 → 1, 5", "{ let mut b = [5, 0]; (transfer(&mut b, 0, 1, 5), b) }", "(Ok(()), [0, 5])"),
        T("reverse", "[0, 10], 1 → 0, 3", "{ let mut b = [0, 10]; (transfer(&mut b, 1, 0, 3), b) }", "(Ok(()), [3, 7])"),
        T("same_checked_before_funds", "[0], 0 → 0, 5", "{ let mut b = [0]; transfer(&mut b, 0, 0, 5) }", 'Err("same account")'),
    ],
    hidden=[
        T("from_out_of_bounds", "[1, 2], 9 → 0", "{ let mut b = [1, 2]; transfer(&mut b, 9, 0, 1) }", 'Err("no such account")'),
        T("unchanged_on_error", "[10, 0], 0 → 7", "{ let mut b = [10, 0]; (transfer(&mut b, 0, 7, 1), b) }", '(Err("no such account"), [10, 0])'),
        T("negative_source", "[-5, 0], 0 → 1, 1", "{ let mut b = [-5, 0]; (transfer(&mut b, 0, 1, 1), b) }", '(Err("insufficient funds"), [-5, 0])'),
        T("zero_amount", "[0, 0], 0 → 1, 0", "{ let mut b = [0, 0]; (transfer(&mut b, 0, 1, 0), b) }", "(Ok(()), [0, 0])"),
        T("large_values", "[i64::MAX, 0], move all", "{ let mut b = [i64::MAX, 0]; (transfer(&mut b, 0, 1, i64::MAX), b) }", "(Ok(()), [0, i64::MAX])"),
        T("empty_slice", "[], 0 → 1", "{ let mut b: [i64; 0] = []; transfer(&mut b, 0, 1, 1) }", 'Err("no such account")'),
        T("middle_untouched", "[5, 5, 5], 0 → 2, 5", "{ let mut b = [5, 5, 5]; (transfer(&mut b, 0, 2, 5), b) }", "(Ok(()), [0, 5, 10])"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2029);
            for _ in 0..300 {
                let len = rng.below(4);
                let b0: Vec<i64> = rng.vec(len, -5, 20);
                let from = rng.below(len + 2);
                let to = rng.below(len + 2);
                let amount = rng.int(0, 25);
                if from == to && from >= len {
                    continue;
                }
                let mut want_b = b0.clone();
                let want = if from >= len || to >= len {
                    Err("no such account")
                } else if from == to {
                    Err("same account")
                } else if b0[from] < amount {
                    Err("insufficient funds")
                } else {
                    want_b[from] -= amount;
                    want_b[to] += amount;
                    Ok(())
                };
                let mut b = b0.clone();
                let got = transfer(&mut b, from, to, amount);
                check!(format!("balances {b0:?}, {from} → {to}, {amount}"), (got, b), (want, want_b));
            }
        }
        """,
    ],
    wrong=dict(
        funds_before_same="""
            pub fn transfer(balances: &mut [i64], from: usize, to: usize, amount: i64) -> Result<(), &'static str> {
                if from >= balances.len() || to >= balances.len() {
                    return Err("no such account");
                }
                if balances[from] < amount {
                    return Err("insufficient funds");
                }
                if from == to {
                    return Err("same account");
                }
                balances[from] -= amount;
                balances[to] += amount;
                Ok(())
            }
        """,
        needs_more_than_amount="""
            use std::slice::GetDisjointMutError;

            pub fn transfer(balances: &mut [i64], from: usize, to: usize, amount: i64) -> Result<(), &'static str> {
                let [a, b] = balances.get_disjoint_mut([from, to]).map_err(|e| match e {
                    GetDisjointMutError::OverlappingIndices => "same account",
                    GetDisjointMutError::IndexOutOfBounds => "no such account",
                })?;
                if *a <= amount {
                    return Err("insufficient funds");
                }
                *a -= amount;
                *b += amount;
                Ok(())
            }
        """,
    ),
)

NODE_WRONG = """
    use std::cell::Cell;

    pub struct Node {
        pub name: String,
        visits: Cell<u32>,
    }

    impl Node {
        pub fn new(name: &str) -> Self {
            Node { name: name.to_string(), visits: Cell::new(START) }
        }

        /// Records a visit and returns the new count.
        pub fn visit(&self) -> u32 {
            VISIT
        }

        pub fn visits(&self) -> u32 {
            self.visits.get()
        }
    }
"""
MORE["cell-for-copy"] = dict(
    visible=[
        T("new_is_zero", "new node \"x\"", 'Node::new("x").visits()', "0"),
        T("visit_returns_new_count", "first visit", 'Node::new("x").visit()', "1"),
        T("independent_nodes", "visit a twice, b never", '{ let a = Node::new("a"); let b = Node::new("b"); a.visit(); a.visit(); (a.visits(), b.visits()) }', "(2, 0)"),
    ],
    hidden=[
        T("name_kept", "name \"héllo\"", 'Node::new("héllo").name', '"héllo".to_string()'),
        T("empty_name", "name \"\"", 'Node::new("").name', "String::new()"),
        T("visits_does_not_count", "call visits() three times", '{ let n = Node::new("a"); n.visits(); n.visits(); n.visits() }', "0"),
        T("many", "10000 visits", '{ let n = Node::new("a"); for _ in 0..10_000 { n.visit(); } n.visits() }', "10_000"),
        T("through_rc", "two Rc handles to one node", '{ let n = std::rc::Rc::new(Node::new("a")); let m = std::rc::Rc::clone(&n); n.visit(); m.visit(); n.visits() }', "2"),
        T("returns_sequence", "visit three times", '{ let n = Node::new("a"); (n.visit(), n.visit(), n.visit()) }', "(1, 2, 3)"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2030);
            for _ in 0..200 {
                let k = 1 + rng.below(4);
                let nodes: Vec<Node> = (0..k).map(|i| Node::new(&i.to_string())).collect();
                let mut model = vec![0u32; k];
                let mut log = Vec::new();
                let steps = rng.below(12);
                for _ in 0..steps {
                    let i = rng.below(k);
                    log.push(i);
                    model[i] += 1;
                    check!(format!("visits {log:?}"), nodes[i].visit(), model[i]);
                }
                check!(format!("visits {log:?}"), nodes.iter().map(|n| n.visits()).collect::<Vec<_>>(), model);
            }
        }
        """,
    ],
    wrong=dict(
        returns_old_count=NODE_WRONG.replace("START", "0").replace("VISIT", """let n = self.visits.get();
            self.visits.set(n + 1);
            n"""),
        starts_at_one=NODE_WRONG.replace("START", "1").replace("VISIT", """let n = self.visits.get() + 1;
            self.visits.set(n);
            n"""),
    ),
)

REG_WRONG = """
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
            BODY
        }

        pub fn len(&self) -> usize {
            self.names.borrow().len()
        }
    }
"""
MORE["fix-borrowmuterror"] = dict(
    visible=[
        T("single", "add \"x\"", '{ let r = Registry::new(); r.add("x"); r.len() }', "1"),
        T("case_sensitive", "add \"a\", \"A\"", '{ let r = Registry::new(); r.add("a"); r.add("A"); r.len() }', "2"),
        T("empty", "new registry", "Registry::new().len()", "0"),
    ],
    hidden=[
        T("empty_name", "add \"\" twice", '{ let r = Registry::new(); r.add(""); r.add(""); r.len() }', "1"),
        T("unicode", "add \"é\" twice", '{ let r = Registry::new(); r.add("é"); r.add("é"); r.len() }', "1"),
        T("many_distinct", "1000 names", "{ let r = Registry::new(); for i in 0..1000 { r.add(&i.to_string()); } r.len() }", "1000"),
        T("many_duplicates", "1000 adds of 10 names", "{ let r = Registry::new(); for i in 0..1000 { r.add(&(i % 10).to_string()); } r.len() }", "10"),
        T("shared_refs", "add through two &Registry", '{ let r = Registry::new(); let (a, b) = (&r, &r); a.add("x"); b.add("y"); b.add("x"); r.len() }', "2"),
        T("prefix_is_different", "add \"ab\", \"a\"", '{ let r = Registry::new(); r.add("ab"); r.add("a"); r.len() }', "2"),
        T("spaces_matter", "add \"a\", \"a \"", '{ let r = Registry::new(); r.add("a"); r.add("a "); r.len() }', "2"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2031);
            for _ in 0..300 {
                let r = Registry::new();
                let mut model: Vec<String> = Vec::new();
                let n = rng.below(10);
                let mut log = Vec::new();
                for _ in 0..n {
                    let l = 1 + rng.below(2);
                    let name = rng.string(l, "aAb");
                    r.add(&name);
                    if !model.contains(&name) {
                        model.push(name.clone());
                    }
                    log.push(name);
                }
                check!(format!("adds {log:?}"), r.len(), model.len());
            }
        }
        """,
    ],
    wrong=dict(
        try_borrow_skips=REG_WRONG.replace("BODY", """let names = self.names.borrow();
            if !names.iter().any(|n| n == name) {
                if let Ok(mut m) = self.names.try_borrow_mut() {
                    m.push(name.to_string());
                }
            }"""),
        ignores_case=REG_WRONG.replace("BODY", """let exists = self.names.borrow().iter().any(|n| n.eq_ignore_ascii_case(name));
            if !exists {
                self.names.borrow_mut().push(name.to_string());
            }"""),
    ),
)

BANK_WRONG = """
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
            BODY
        }

        pub fn audit(&self) -> Vec<String> {
            self.audit.borrow().to_vec()
        }
    }
"""
MORE["fix-refcell-guard-across-call"] = dict(
    visible=[
        T("three_accounts", "deposit 1, 2, 3 into accounts 0, 1, 2", "{ let b = Bank::new(3); b.deposit(0, 1); b.deposit(1, 2); b.deposit(2, 3); b.audit() }", 'vec!["total 1", "total 3", "total 6"]'),
        T("withdraw", "deposit 10, then -4", "{ let b = Bank::new(1); b.deposit(0, 10); b.deposit(0, -4); b.audit() }", 'vec!["total 10", "total 6"]'),
        T("no_deposits", "new bank", "Bank::new(2).audit()", "Vec::<String>::new()"),
    ],
    hidden=[
        T("zero_deposit", "deposit 0", "{ let b = Bank::new(1); b.deposit(0, 0); b.audit() }", 'vec!["total 0"]'),
        T("large", "deposit i64::MAX / 2 into two accounts", "{ let b = Bank::new(2); b.deposit(0, i64::MAX / 2); b.deposit(1, i64::MAX / 2); b.audit()[1].clone() }", 'format!("total {}", i64::MAX - 1)'),
        T("many", "1000 deposits of 1", "{ let b = Bank::new(4); for i in 0..1000 { b.deposit(i % 4, 1); } let a = b.audit(); (a.len(), a[999].clone()) }", '(1000, "total 1000".to_string())'),
        T("other_accounts_count", "deposit 5 into 0, then 1 into 2", "{ let b = Bank::new(3); b.deposit(0, 5); b.deposit(2, 1); b.audit() }", 'vec!["total 5", "total 6"]'),
        T("back_to_zero", "deposit 7, then -7", "{ let b = Bank::new(2); b.deposit(1, 7); b.deposit(1, -7); b.audit() }", 'vec!["total 7", "total 0"]'),
        T("audit_is_a_copy", "read the audit twice", "{ let b = Bank::new(1); b.deposit(0, 2); let first = b.audit(); b.deposit(0, 2); (first.len(), b.audit().len()) }", "(1, 2)"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2032);
            for _ in 0..300 {
                let k = 1 + rng.below(4);
                let b = Bank::new(k);
                let mut total = 0i64;
                let mut want = Vec::new();
                let mut log = Vec::new();
                let n = rng.below(8);
                for _ in 0..n {
                    let i = rng.below(k);
                    let amount = rng.int(-50, 50);
                    b.deposit(i, amount);
                    total += amount;
                    want.push(format!("total {total}"));
                    log.push(format!("{amount} into {i}"));
                }
                check!(format!("{k} accounts; {}", log.join(", ")), b.audit(), want);
            }
        }
        """,
    ],
    wrong=dict(
        total_before_deposit=BANK_WRONG.replace("BODY", """let total = self.total();
            self.balances.borrow_mut()[i] += amount;
            self.audit.borrow_mut().push(format!("total {total}"));"""),
        records_the_account=BANK_WRONG.replace("BODY", """let balance = {
                let mut balances = self.balances.borrow_mut();
                balances[i] += amount;
                balances[i]
            };
            self.audit.borrow_mut().push(format!("total {balance}"));"""),
    ),
)

CART_WRONG = """
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
            BODY
        }

        pub fn total(&self) -> u32 {
            self.total
        }

        pub fn items(&self) -> Vec<u32> {
            self.items.to_vec()
        }
    }
"""
MORE["fix-refcell-to-split-borrow"] = dict(
    visible=[
        T("add_after_double", "add 1; double; add 5", "{ let mut c = Cart::new(); c.add(1); c.double_all(); c.add(5); (c.items(), c.total()) }", "(vec![2, 5], 7)"),
        T("no_double", "add 1, 2", "{ let mut c = Cart::new(); c.add(1); c.add(2); (c.items(), c.total()) }", "(vec![1, 2], 3)"),
        T("empty", "double an empty cart", "{ let mut c = Cart::new(); c.double_all(); (c.items(), c.total()) }", "(vec![], 0)"),
    ],
    hidden=[
        T("single", "add 7; double", "{ let mut c = Cart::new(); c.add(7); c.double_all(); (c.items(), c.total()) }", "(vec![14], 14)"),
        T("zero_price", "add 0; double", "{ let mut c = Cart::new(); c.add(0); c.double_all(); (c.items(), c.total()) }", "(vec![0], 0)"),
        T("duplicates", "add 3, 3; double", "{ let mut c = Cart::new(); c.add(3); c.add(3); c.double_all(); (c.items(), c.total()) }", "(vec![6, 6], 12)"),
        T("large", "add 2^30; double", "{ let mut c = Cart::new(); c.add(1 << 30); c.double_all(); (c.items(), c.total()) }", "(vec![1 << 31], 1 << 31)"),
        T("many", "1000 × add 1; double", "{ let mut c = Cart::new(); for _ in 0..1000 { c.add(1); } c.double_all(); (c.items().len(), c.total()) }", "(1000, 2000)"),
        T("new_is_empty", "new cart", "{ let c = Cart::new(); (c.items(), c.total()) }", "(vec![], 0)"),
        T("three_doubles", "add 1, 2; double 3 times", "{ let mut c = Cart::new(); c.add(1); c.add(2); c.double_all(); c.double_all(); c.double_all(); (c.items(), c.total()) }", "(vec![8, 16], 24)"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2033);
            for _ in 0..300 {
                let mut c = Cart::new();
                let mut items: Vec<u32> = Vec::new();
                let mut log = Vec::new();
                let n = rng.below(10);
                for _ in 0..n {
                    if rng.below(3) == 0 {
                        c.double_all();
                        items.iter_mut().for_each(|p| *p *= 2);
                        log.push("double".to_string());
                    } else {
                        let p = rng.below(100) as u32;
                        c.add(p);
                        items.push(p);
                        log.push(format!("add {p}"));
                    }
                }
                let total: u32 = items.iter().sum();
                check!(log.join(", "), (c.items(), c.total()), (items, total));
            }
        }
        """,
    ],
    wrong=dict(
        adds_the_doubled_price=CART_WRONG.replace("BODY", """for p in self.items.iter_mut() {
                *p *= 2;
                self.total += *p;
            }"""),
        doubles_a_copy=CART_WRONG.replace("BODY", """for mut p in self.items.to_vec() {
                self.total += p;
                p *= 2;
            }"""),
    ),
)

for p in P:
    m = MORE.get(p["slug"])
    if m:
        p["visible"] += m["visible"]
        # A hidden case promoted to visible leaves hidden.
        shown = {(t[3], t[4]) for t in p["visible"] if not isinstance(t, str)}
        p["hidden"] = [t for t in p["hidden"] if isinstance(t, str) or (t[3], t[4]) not in shown] + m["hidden"]
        p["wrong"] = m["wrong"]

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
