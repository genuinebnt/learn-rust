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


def fixp(slug, title, level, stage, tags, statement, starter, solution, visible, hidden, hints, notes, follow_up, teaches, rules=None, related=("L2",), wrong=None):
    return dict(slug=slug, title=title, mode="fix", level=level, stage=stage, tags=tags, statement=statement, starter=starter,
                solution=solution, visible=visible, hidden=hidden, hints=hints, notes=notes, follow_up=follow_up,
                teaches=teaches, rules=rules, related=list(related), wrong=wrong)


def writep(slug, title, level, stage, tags, statement, starter, solution, visible, hidden, hints, notes, follow_up, teaches, related=("L2",), wrong=None):
    return dict(slug=slug, title=title, level=level, stage=stage, tags=tags, statement=statement, starter=starter,
                solution=solution, visible=visible, hidden=hidden, hints=hints, notes=notes, follow_up=follow_up,
                teaches=teaches, related=list(related), wrong=wrong)


def sub(s, old, new):
    """str.replace that fails loudly when `old` isn't there (a wrong solution that silently equals the reference)."""
    assert old in s, f"not found: {old[:60]!r}"
    return s.replace(old, new)


# Counts heap allocations made on the current test thread, for tests that check nothing is copied per item.
ALLOC_COUNTER = r"""
use std::alloc::{GlobalAlloc, Layout, System};
use std::cell::Cell;

struct CountingAlloc;

thread_local! {
    static ALLOCS: Cell<usize> = const { Cell::new(0) };
}

unsafe impl GlobalAlloc for CountingAlloc {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        let _ = ALLOCS.try_with(|n| n.set(n.get() + 1));
        unsafe { System.alloc(layout) }
    }

    unsafe fn realloc(&self, ptr: *mut u8, layout: Layout, new_size: usize) -> *mut u8 {
        let _ = ALLOCS.try_with(|n| n.set(n.get() + 1));
        unsafe { System.realloc(ptr, layout, new_size) }
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        unsafe { System.dealloc(ptr, layout) }
    }
}

#[global_allocator]
static GLOBAL: CountingAlloc = CountingAlloc;

/// Runs `f` and returns its result with the number of allocations (and reallocations) it made.
fn allocs<R>(f: impl FnOnce() -> R) -> (R, usize) {
    let before = ALLOCS.with(|n| n.get());
    let r = f();
    (r, ALLOCS.with(|n| n.get()) - before)
}
"""


# ---------------------------------------------------------------- shared vs unique (easy)

SERIES_HEAD = r"""
/// A time series: `points[i]` was reported by `labels[i]`.
pub struct Series {
    pub points: Vec<i64>,
    pub labels: Vec<String>,
}

impl Series {
    pub fn new() -> Self {
        Series { points: Vec::new(), labels: Vec::new() }
    }

    /// Records `x`, reported by `label`. Returns the label of the record holder after this point (the `String`
    /// stored in `labels`, not a copy) and how far `x` beat the old record: `None` when it didn't beat it or when
    /// it's the first point. The record holder is the first label that reported the maximum, so a tie doesn't
    /// take the record.
"""

SERIES_STARTER = SERIES_HEAD + r"""    pub fn record(&mut self, x: i64, label: String) -> (&str, Option<i64>) {
        let best = self.points.iter().max();
        let holder = best.map(|b| &self.labels[self.points.iter().position(|p| p == b).unwrap()]);
        self.points.push(x);
        self.labels.push(label);
        match best {
            Some(&b) if x <= b => (holder.unwrap(), None),
            Some(&b) => (&label, Some(x - b)),
            None => (&label, None),
        }
    }
}
"""

SERIES_SOLUTION = SERIES_HEAD + r"""    pub fn record(&mut self, x: i64, label: String) -> (&str, Option<i64>) {
        let best = self.points.iter().copied().max();
        let holder = best.map(|b| self.points.iter().position(|&p| p == b).unwrap());
        self.points.push(x);
        self.labels.push(label);
        let newest = self.labels.len() - 1;
        match (best, holder) {
            (Some(b), Some(i)) if x <= b => (&self.labels[i], None),
            (Some(b), _) => (&self.labels[newest], Some(x - b)),
            _ => (&self.labels[newest], None),
        }
    }
}
"""

SERIES_RUN = r"""
/// Records every (x, label) in order and returns the last result, owned.
fn run(points: &[(i64, &str)]) -> (String, Option<i64>) {
    let mut s = Series::new();
    let mut last = (String::new(), None);
    for &(x, l) in points {
        let (h, g) = s.record(x, l.to_string());
        last = (h.to_string(), g);
    }
    last
}
"""


def series_case(name, pts, holder, gain):
    desc = ", ".join(f'({x}, "{l}")' for x, l in pts)
    call = "run(&[" + ", ".join(f'({x}, "{l}")' for x, l in pts) + "])"
    return T(name, f"record {desc}", call, f'("{holder}".to_string(), {gain})')


P.append(fixp(
    "fix-push-while-holding-a-reference", "Fix: push while holding a reference", "easy", "shared-vs-unique", ["E0502", "E0382", "indices over references"],
    """
        `Series::record` doesn't compile. It reads the current record before pushing the new point, and answers
        with a reference to the record holder's label. Fix it without copying any label: the `&str` it returns
        must be the `String` stored in `labels`.
    """,
    SERIES_STARTER,
    SERIES_SOLUTION,
    [SERIES_RUN,
     series_case("first_point", [(5, "a")], "a", "None"),
     series_case("new_record", [(5, "a"), (9, "b")], "b", "Some(4)"),
     series_case("below_the_record", [(5, "a"), (3, "b")], "a", "None"),
     series_case("tie_keeps_the_holder", [(5, "a"), (5, "b")], "a", "None"),
     series_case("first_to_reach_the_max", [(5, "a"), (9, "b"), (9, "c"), (2, "d")], "b", "None"),
     series_case("negatives", [(-5, "a"), (-2, "b")], "b", "Some(3)")],
    [SERIES_RUN,
     series_case("record_after_a_tie", [(4, "a"), (4, "b"), (6, "c")], "c", "Some(2)"),
     series_case("same_label_twice", [(1, "x"), (3, "x"), (2, "y")], "x", "None"),
     series_case("empty_label", [(1, ""), (0, "z")], "", "None"),
     series_case("chain_of_records", [(1, "a"), (2, "b"), (4, "c"), (8, "d")], "d", "Some(4)"),
     series_case("far_apart", [(-1_000_000_000_000, "lo"), (1_000_000_000_000, "hi")], "hi", "Some(2000000000000)"),
     series_case("all_equal", [(0, "p"), (0, "q"), (0, "r")], "p", "None"),
     series_case("unicode_labels", [(2, "é"), (7, "日本")], "日本", "Some(5)"),
     r"""
     #[test]
     fn holder_is_the_stored_label() {
         let mut s = Series::new();
         let seven = "seven".to_string();
         let moved = seven.as_ptr();
         s.record(7, seven);
         check!("record (7, \"seven\"): the label String is moved in, not copied", s.labels[0].as_ptr() == moved, true);
         let p = s.record(3, "three".to_string()).0.as_ptr();
         check!("then (3, \"three\"): the returned &str is labels[0] itself", p == s.labels[0].as_ptr(), true);
         let p = s.record(8, "eight".to_string()).0.as_ptr();
         check!("then (8, \"eight\"): the returned &str is labels[2] itself", p == s.labels[2].as_ptr(), true);
         check!("points afterwards", s.points.clone(), vec![7, 3, 8]);
     }

     #[test]
     fn random_vs_model() {
         let mut rng = anneal_prelude::Rng::new(6201);
         for _ in 0..300 {
             let n = 1 + rng.below(8);
             let mut s = Series::new();
             let (mut pts, mut labs): (Vec<i64>, Vec<String>) = (Vec::new(), Vec::new());
             let mut log = Vec::new();
             for i in 0..n {
                 let x = rng.int(-4, 4);
                 let l = format!("{}{i}", rng.string(1, "ab"));
                 log.push(format!("({x}, {l:?})"));
                 let want = match pts.iter().copied().max() {
                     Some(b) if x <= b => (labs[pts.iter().position(|&p| p == b).unwrap()].clone(), None),
                     Some(b) => (l.clone(), Some(x - b)),
                     None => (l.clone(), None),
                 };
                 pts.push(x);
                 labs.push(l.clone());
                 let (h, g) = s.record(x, l);
                 check!(format!("record {}", log.join(", ")), (h.to_string(), g), want);
             }
         }
     }
     """],
    [("rust", "`best` is an `Option<&i64>` into `points` and `holder` an `Option<&String>` into `labels`, and both are read after the pushes. A push can reallocate the `Vec` and leave them dangling. What do you actually need from each one?"),
     ("rust", "An `i64` is `Copy`: keep the number, not a reference to it. For the label, keep its index. An index stays valid across a push, and you can borrow `labels[i]` again once the pushes are done."),
     ("rust", "`label` is moved into `labels`, so `&label` afterwards is a use after move, and would point at a parameter anyway. The newest label is `labels[len - 1]`.")],
    ("""A shared borrow into a `Vec` forbids mutating that `Vec` until the borrow's last use, because `push` may reallocate. The fix keeps what survives the push: `copied()` turns `Option<&i64>` into `Option<i64>`, and the holder becomes an index. Borrow the stored label again after both pushes; the returned `&str` then borrows `self`, which is what the elided lifetime says.

Note what does compile: `holder` borrowing `labels` doesn't conflict with `self.points.push`, because the two fields are disjoint. Only the push to the same field conflicts.

Aside: with `Vec<String>` the label's bytes live in their own heap buffer and don't move when `labels` reallocates, yet the borrow checker still rejects the `&String`: it tracks the borrow of `labels`, not where the bytes are.""", "O(n) per record (the scan)", "O(1) extra"),
    "`Vec<String>` reallocating moves the `String` headers but not their bytes. Could a `&str` into a label survive a push in principle, and what would it take to express that safely?",
    ["A shared borrow into a Vec blocks every mutation of that Vec until its last use.", "Keep `Copy` values and indices across a mutation, not references.", "Disjoint fields borrow independently."],
    rules=dict(methods=["clone", "cloned", "to_owned", "to_string"]),
    wrong=dict(
        tie_takes_the_record=sub(SERIES_SOLUTION, "if x <= b", "if x < b"),
        last_holder_of_the_max=sub(SERIES_SOLUTION, "position(|&p| p == b)", "rposition(|&p| p == b)"),
        leaked_copy=sub(SERIES_SOLUTION, "(Some(b), Some(i)) if x <= b => (&self.labels[i], None),", "(Some(b), Some(i)) if x <= b => (Box::leak(self.labels[i].as_str().into()), None),"),
    ),
))

INBOX_HEAD = r"""
#[derive(Debug, PartialEq)]
pub struct Msg {
    pub id: u32,
    pub from: String,
    pub body: String,
    pub read: bool,
    pub reply: Option<String>,
}

/// Messages in arrival order, oldest first. Ids are unique.
pub struct Inbox {
    msgs: Vec<Msg>,
}
"""

INBOX_IMPL = r"""
impl Inbox {
    pub fn new() -> Self {
        Inbox { msgs: Vec::new() }
    }

    pub fn push(&mut self, id: u32, from: &str, body: &str) {
        self.msgs.push(Msg { id, from: from.to_string(), body: body.to_string(), read: false, reply: None });
    }

    pub fn get(&self, id: u32) -> Option<&Msg> {
        self.msgs.iter().find(|m| m.id == id)
    }

    pub fn get_mut(&mut self, id: u32) -> Option<&mut Msg> {
        self.msgs.iter_mut().find(|m| m.id == id)
    }

    pub fn unread(&self) -> Vec<&Msg> {
        self.msgs.iter().filter(|m| !m.read).collect()
    }

    pub fn reply_to(&self, id: u32) -> Option<&str> {
        self.get(id)?.reply.as_deref()
    }

    pub fn mark_read(&mut self, id: u32) -> bool {
        match self.get_mut(id) {
            Some(m) if !m.read => {
                m.read = true;
                true
            }
            _ => false,
        }
    }

    pub fn reply_mut(&mut self, id: u32) -> Option<&mut String> {
        Some(self.get_mut(id)?.reply.get_or_insert_with(String::new))
    }

    pub fn newest_unread_mut(&mut self) -> Option<&mut Msg> {
        self.msgs.iter_mut().rev().find(|m| !m.read)
    }
}
"""

INBOX_TAIL = r"""
/// Marks every unread message from `boss` read, appends "on it" to the reply of the newest message still
/// unread (if there is one), and returns the ids still unread, oldest first.
pub fn triage(inbox: &mut Inbox, boss: &str) -> Vec<u32> {
    let from_boss: Vec<u32> = inbox.unread().iter().filter(|m| m.from == boss).map(|m| m.id).collect();
    for id in from_boss {
        inbox.mark_read(id);
    }
    if let Some(m) = inbox.newest_unread_mut() {
        m.reply.get_or_insert_with(String::new).push_str("on it");
    }
    inbox.unread().iter().map(|m| m.id).collect()
}
"""

INBOX_SOLUTION = INBOX_HEAD + INBOX_IMPL + INBOX_TAIL
INBOX_SETUP = 'let mut inbox = Inbox::new();\ninbox.push(1, "ann", "hello");\ninbox.push(2, "boss", "report?");\ninbox.push(3, "bob", "lunch");'
INBOX_DESC = 'inbox 1 ann "hello", 2 boss "report?", 3 bob "lunch"'

P.append(fixp(
    "many-readers-one-writer", "Many readers, one writer", "easy", "shared-vs-unique", ["&self vs &mut self", "Option<&T>", "as_deref", "get_or_insert_with", "iter_mut"],
    """
        `triage` uses an `Inbox` API that doesn't exist yet. Write `impl Inbox` with these methods. Pick each
        receiver and return type yourself: a method that only reads must be callable while other readers are
        alive (the tests hold two at once), and nothing may copy a message or its text.

        - `new()` and `push(id, from, body)`: a new message is unread and has no reply.
        - `get(id)`: the message, borrowed. `get_mut(id)`: the message, for editing.
        - `unread()`: the unread messages, borrowed, oldest first, in a `Vec`.
        - `reply_to(id)`: the reply's text as a string slice, `None` if there's no such message or no reply.
        - `mark_read(id)`: marks it read and returns whether it was unread (`false` for an unknown id).
        - `reply_mut(id)`: the reply for editing in place, created empty when the message has none yet; `None`
          for an unknown id.
        - `newest_unread_mut()`: the most recent unread message, for editing.
    """,
    INBOX_HEAD + "\n// TODO: impl Inbox.\n" + INBOX_TAIL,
    INBOX_SOLUTION,
    [T("readers_together", f"{INBOX_DESC}; reply to 2 is \"on it\"; get(1).body and reply_to(2) held at once",
       "(first.map(|m| m.body.as_str()), second)", '(Some("hello"), Some("on it"))',
       setup=INBOX_SETUP + '\ninbox.reply_mut(2).unwrap().push_str("on it");\nlet first = inbox.get(1);\nlet second = inbox.reply_to(2);'),
     T("mark_read_says_if_it_changed", f"{INBOX_DESC}; mark_read(1) twice, then mark_read(9)", "(inbox.mark_read(1), inbox.mark_read(1), inbox.mark_read(9))", "(true, false, false)", setup=INBOX_SETUP),
     T("reply_mut_creates_then_edits", f"{INBOX_DESC}; reply_mut(3) += \"no\", then += \"pe\"",
       "(inbox.reply_to(3), inbox.reply_to(1))", '(Some("nope"), None)',
       setup=INBOX_SETUP + '\ninbox.reply_mut(3).unwrap().push_str("no");\ninbox.reply_mut(3).unwrap().push_str("pe");'),
     T("newest_unread_skips_read", f"{INBOX_DESC}; mark_read(3); newest_unread_mut", "inbox.newest_unread_mut().map(|m| m.id)", "Some(2)",
       setup=INBOX_SETUP + "\ninbox.mark_read(3);"),
     T("triage_example", f"{INBOX_DESC}; triage(boss = \"boss\")", '(triage(&mut inbox, "boss"), inbox.reply_to(3), inbox.reply_to(2))', '(vec![1, 3], Some("on it"), None)', setup=INBOX_SETUP),
     T("unknown_ids", f"{INBOX_DESC}; id 9", "(inbox.reply_mut(9).is_none(), inbox.get_mut(9).is_none(), inbox.get(9).is_none(), inbox.reply_to(9))", "(true, true, true, None)", setup=INBOX_SETUP)],
    [T("empty_inbox", "new inbox", "(inbox.unread().len(), inbox.newest_unread_mut().is_none(), triage(&mut inbox, \"x\"))", "(0, true, vec![])", setup="let mut inbox = Inbox::new();"),
     T("unread_oldest_first", f"{INBOX_DESC}; mark_read(2)", "inbox.unread().iter().map(|m| m.id).collect::<Vec<_>>()", "vec![1, 3]", setup=INBOX_SETUP + "\ninbox.mark_read(2);"),
     T("reply_mut_keeps_existing", f"{INBOX_DESC}; reply_mut(1) = \"a\", then reply_mut(1) += \"b\"", "inbox.reply_to(1)", 'Some("ab")',
       setup=INBOX_SETUP + '\n*inbox.reply_mut(1).unwrap() = "a".to_string();\ninbox.reply_mut(1).unwrap().push_str("b");'),
     T("empty_reply_is_some", f"{INBOX_DESC}; reply_mut(1) without writing", "inbox.reply_to(1)", 'Some("")', setup=INBOX_SETUP + "\ninbox.reply_mut(1);"),
     T("get_mut_edits_in_place", f"{INBOX_DESC}; get_mut(2).body = \"done\"", "inbox.get(2).map(|m| m.body.as_str())", 'Some("done")',
       setup=INBOX_SETUP + '\ninbox.get_mut(2).unwrap().body = "done".to_string();'),
     T("all_read", f"{INBOX_DESC}; mark_read 1, 2, 3", "(inbox.newest_unread_mut().is_none(), inbox.unread().len())", "(true, 0)",
       setup=INBOX_SETUP + "\nfor id in 1..=3 {\n    inbox.mark_read(id);\n}"),
     T("triage_everything_from_boss", "inbox 1 boss, 2 boss; triage(\"boss\")", '(triage(&mut inbox, "boss"), inbox.reply_to(1), inbox.reply_to(2))', "(vec![], None, None)",
       setup='let mut inbox = Inbox::new();\ninbox.push(1, "boss", "a");\ninbox.push(2, "boss", "b");'),
     T("triage_appends_to_existing_reply", f"{INBOX_DESC}; reply to 3 is \"ok, \"; triage(\"nobody\")", '(triage(&mut inbox, "nobody"), inbox.reply_to(3))', '(vec![1, 2, 3], Some("ok, on it"))',
       setup=INBOX_SETUP + '\ninbox.reply_mut(3).unwrap().push_str("ok, ");'),
     T("triage_skips_already_read_boss_mail", f"{INBOX_DESC}; mark_read(2); triage(\"boss\"); mark_read(2)", '{ triage(&mut inbox, "boss"); inbox.mark_read(2) }', "false", setup=INBOX_SETUP + "\ninbox.mark_read(2);"),
     r"""
     #[test]
     fn many_readers_at_once() {
         let mut inbox = Inbox::new();
         inbox.push(7, "a", "x");
         inbox.push(8, "b", "y");
         let all = inbox.unread();
         let one = inbox.get(8);
         let reply = inbox.reply_to(7);
         check!("unread(), get(8) and reply_to(7) held together", (all.len(), one.map(|m| m.from.as_str()), reply), (2, Some("b"), None));
     }

     #[test]
     fn random_vs_model() {
         let mut rng = anneal_prelude::Rng::new(6202);
         for _ in 0..300 {
             let mut inbox = Inbox::new();
             // (id, read, reply)
             let mut model: Vec<(u32, bool, Option<String>)> = Vec::new();
             let mut ops = Vec::new();
             for step in 0..12u32 {
                 match rng.below(4) {
                     0 => {
                         inbox.push(step, "f", "b");
                         model.push((step, false, None));
                         ops.push(format!("push {step}"));
                     }
                     1 => {
                         let id = rng.below(step as usize + 1) as u32;
                         let want = match model.iter_mut().find(|m| m.0 == id) {
                             Some(m) if !m.1 => {
                                 m.1 = true;
                                 true
                             }
                             _ => false,
                         };
                         ops.push(format!("mark_read {id}"));
                         check!(ops.join(", "), inbox.mark_read(id), want);
                     }
                     2 => {
                         let id = rng.below(step as usize + 1) as u32;
                         let s = rng.string(1, "xy");
                         if let Some(r) = inbox.reply_mut(id) {
                             r.push_str(&s);
                         }
                         if let Some(m) = model.iter_mut().find(|m| m.0 == id) {
                             m.2.get_or_insert_with(String::new).push_str(&s);
                         }
                         ops.push(format!("reply_mut {id} += {s}"));
                     }
                     _ => {
                         let got = inbox.newest_unread_mut().map(|m| m.id);
                         let want = model.iter().rev().find(|m| !m.1).map(|m| m.0);
                         ops.push("newest_unread_mut".to_string());
                         check!(ops.join(", "), got, want);
                     }
                 }
             }
             let unread: Vec<u32> = inbox.unread().iter().map(|m| m.id).collect();
             let want_unread: Vec<u32> = model.iter().filter(|m| !m.1).map(|m| m.0).collect();
             check!(format!("{}; unread ids", ops.join(", ")), unread, want_unread);
             for m in &model {
                 check!(format!("{}; reply_to({})", ops.join(", "), m.0), inbox.reply_to(m.0), m.2.as_deref());
             }
         }
     }
     """],
    [("rust", "Readers take `&self` and hand out borrows tied to it: `Option<&Msg>`, `Vec<&Msg>`, `Option<&str>`. Writers take `&mut self` and hand out `Option<&mut Msg>` or `Option<&mut String>`."),
     ("rust", "`Option<String>` to `Option<&str>` is `as_deref()`. `get_or_insert_with(String::new)` fills a `None` in place and returns `&mut String`. `iter_mut().rev().find(..)` searches from the newest.")],
    ("""A method that only reads takes `&self`, so any number of callers can hold its results at once; a method that hands out `&mut` must take `&mut self`, and then nothing else can use the inbox until that borrow ends. `triage` shows the practical consequence: it collects the boss's ids (plain `u32`s) before marking, because `mark_read` needs `&mut self` while `unread()`'s `Vec<&Msg>` would still borrow the inbox.

Syntax to remember: `self.msgs.iter().find(|m| m.id == id)` · `self.msgs.iter_mut().rev().find(|m| !m.read)` · `self.get(id)?.reply.as_deref()` · `Some(self.get_mut(id)?.reply.get_or_insert_with(String::new))`.""", "O(n) per lookup", "O(1) extra; `unread` O(k)"),
    "`unread()` returns `Vec<&Msg>`. What would returning `impl Iterator<Item = &Msg> + '_` change for `triage`?",
    ["`&self` methods can run while other shared borrows are alive; `&mut self` methods can't.", "`Option<String>` → `Option<&str>` with `as_deref`.", "`get_or_insert_with` fills an `Option` in place and returns `&mut T`."],
    related=("L2", "S1"),
    wrong=dict(
        mark_read_always_true=sub(INBOX_SOLUTION, "Some(m) if !m.read => {", "Some(m) => {"),
        oldest_unread=sub(INBOX_SOLUTION, "self.msgs.iter_mut().rev().find(|m| !m.read)", "self.msgs.iter_mut().find(|m| !m.read)"),
        reply_mut_resets=sub(INBOX_SOLUTION, "Some(self.get_mut(id)?.reply.get_or_insert_with(String::new))", "let m = self.get_mut(id)?;\n        m.reply = Some(String::new());\n        m.reply.as_mut()"),
    ),
))

WAREHOUSE_HEAD = r"""
use std::collections::HashMap;

#[derive(Debug, Default, PartialEq)]
pub struct Stock {
    pub qty: u32,
    pub reserved: u32,
}

pub struct Warehouse {
    items: HashMap<String, Stock>,
    last: Option<String>,
    log: Vec<String>,
}
"""

WAREHOUSE_STARTER = WAREHOUSE_HEAD + r"""
impl Warehouse {
    pub fn new() -> Self {
        Warehouse { items: HashMap::new(), last: None, log: Vec::new() }
    }

    /// Remembers `name` as the last item touched.
    fn touch(&self, name: &str) {
        self.last = Some(name.to_string());
    }

    /// Adds `qty` units of `name`, creating the item if needed.
    pub fn receive(&mut self, name: &str, qty: u32) {
        self.items.entry(name.to_string()).or_default().qty += qty;
        self.touch(name);
    }

    /// Reserves up to `qty` free units of `name` and returns how many it reserved. An unknown item reserves
    /// nothing and isn't touched.
    pub fn reserve(&mut self, name: &str, qty: u32) -> u32 {
        let Some(s) = self.items.get(name) else { return 0 };
        self.touch(name);
        let n = qty.min(s.qty - s.reserved);
        s.reserved += n;
        n
    }

    /// Units of `name` that aren't reserved.
    pub fn available(&self, name: &str) -> u32 {
        self.items.get(name).map_or(0, |s| s.qty - s.reserved)
    }

    /// The last item touched.
    pub fn last(&self) -> Option<&str> {
        self.last.as_deref()
    }

    /// Appends `tag` to the remembered last-touched name. The item itself keeps its name.
    pub fn tag_last(&mut self, tag: &str) {
        if let Some(name) = &self.last {
            name.push_str(tag);
        }
    }

    /// Ships every reservation: reserved units leave stock. Logs "<name>: <units>" for each item shipped,
    /// sorted by name, and returns how many items shipped.
    pub fn ship_all(&mut self) -> usize {
        let mut lines = Vec::new();
        for (name, s) in self.items.iter() {
            if s.reserved > 0 {
                lines.push(format!("{name}: {}", s.reserved));
                s.qty -= s.reserved;
                s.reserved = 0;
            }
        }
        lines.sort();
        let shipped = lines.len();
        self.log.extend(lines);
        shipped
    }

    /// How many items have fewer than `limit` units available.
    pub fn count_low(&self, limit: u32) -> usize {
        let mut n = 0;
        let bump = || n += 1;
        for s in self.items.values() {
            if s.qty - s.reserved < limit {
                bump();
            }
        }
        n
    }

    pub fn log(&self) -> &[String] {
        &self.log
    }
}
"""

WAREHOUSE_SOLUTION = WAREHOUSE_STARTER
for _old, _new in [
    ("fn touch(&self, name: &str)", "fn touch(&mut self, name: &str)"),
    ("        let Some(s) = self.items.get(name) else { return 0 };\n        self.touch(name);\n        let n = qty.min(s.qty - s.reserved);\n        s.reserved += n;\n        n",
     "        let Some(s) = self.items.get_mut(name) else { return 0 };\n        let n = qty.min(s.qty - s.reserved);\n        s.reserved += n;\n        self.touch(name);\n        n"),
    ("if let Some(name) = &self.last {", "if let Some(name) = &mut self.last {"),
    ("for (name, s) in self.items.iter() {", "for (name, s) in self.items.iter_mut() {"),
    ("let bump = || n += 1;", "let mut bump = || n += 1;"),
]:
    WAREHOUSE_SOLUTION = sub(WAREHOUSE_SOLUTION, _old, _new)
WH_SETUP = 'let mut w = Warehouse::new();\nw.receive("bolt", 10);\nw.receive("nut", 4);'
WH_DESC = "receive bolt 10, nut 4"

P.append(fixp(
    "fix-mut-from-shared-self", "Fix: &mut in every position", "easy", "shared-vs-unique", ["E0596", "E0594", "E0499", "iter_mut", "get_mut", "FnMut"],
    """
        `Warehouse` doesn't compile: in several places it has shared access where it needs unique access. Each
        one is written differently: a receiver, a map lookup, an iterator, a pattern on an `Option` field, a
        closure. Fix them. `available` and `last` only read, and callers hold their results side by side, so
        they must stay as they are.
    """,
    WAREHOUSE_STARTER,
    WAREHOUSE_SOLUTION,
    [T("receive_and_reserve", f"{WH_DESC}; reserve bolt 3", '(w.reserve("bolt", 3), w.available("bolt"), w.last())', '(3, 7, Some("bolt"))', setup=WH_SETUP),
     T("reserve_caps_at_available", f"{WH_DESC}; reserve nut 3, then nut 3", '(w.reserve("nut", 3), w.reserve("nut", 3), w.available("nut"))', "(3, 1, 0)", setup=WH_SETUP),
     T("unknown_item_not_touched", f"{WH_DESC}; reserve ghost 1", '(w.reserve("ghost", 1), w.last())', '(0, Some("nut"))', setup=WH_SETUP),
     T("readers_side_by_side", f"{WH_DESC}; available(bolt) and last() held together", "(a, l)", '(10, Some("nut"))', setup=WH_SETUP + '\nlet l = w.last();\nlet a = w.available("bolt");'),
     T("tag_last", f"{WH_DESC}; tag_last \"*\" twice", '(w.last(), w.available("nut"), w.available("nut*"))', '(Some("nut**"), 4, 0)', setup=WH_SETUP + '\nw.tag_last("*");\nw.tag_last("*");'),
     T("ship_all_logs_sorted", f"{WH_DESC}; reserve nut 1, bolt 2; ship_all", "(w.ship_all(), w.log().to_vec(), w.available(\"bolt\"), w.available(\"nut\"))",
       '(2, vec!["bolt: 2".to_string(), "nut: 1".to_string()], 8, 3)', setup=WH_SETUP + '\nw.reserve("nut", 1);\nw.reserve("bolt", 2);'),
     T("count_low", f"{WH_DESC}; reserve bolt 7; count_low(4)", 'w.count_low(4)', "1", setup=WH_SETUP + '\nw.reserve("bolt", 7);')],
    [T("empty_warehouse", "new warehouse", "(w.count_low(1), w.ship_all(), w.log().len(), w.last())", "(0, 0, 0, None)", setup="let mut w = Warehouse::new();"),
     T("tag_without_last", "new warehouse; tag_last \"x\"", "w.last()", "None", setup='let mut w = Warehouse::new();\nw.tag_last("x");'),
     T("receive_adds_up", "receive a 2, a 3", '(w.available("a"), w.last())', '(5, Some("a"))', setup='let mut w = Warehouse::new();\nw.receive("a", 2);\nw.receive("a", 3);'),
     T("reserve_zero_touches", f"{WH_DESC}; reserve bolt 0", '(w.reserve("bolt", 0), w.last())', '(0, Some("bolt"))', setup=WH_SETUP),
     T("reserve_when_all_reserved", f"{WH_DESC}; reserve nut 4, then nut 1", '(w.reserve("nut", 1), w.last(), w.available("nut"))', '(0, Some("nut"), 0)', setup=WH_SETUP + '\nw.reserve("nut", 4);'),
     T("ship_twice", f"{WH_DESC}; reserve bolt 10; ship_all twice", '(w.ship_all(), w.ship_all(), w.available("bolt"), w.log().len())', "(1, 0, 0, 1)", setup=WH_SETUP + '\nw.reserve("bolt", 10);'),
     T("log_accumulates", f"{WH_DESC}; reserve nut 1; ship; reserve bolt 1, nut 1; ship", "w.log().to_vec()", 'vec!["nut: 1", "bolt: 1", "nut: 1"]',
       setup=WH_SETUP + '\nw.reserve("nut", 1);\nw.ship_all();\nw.reserve("bolt", 1);\nw.reserve("nut", 1);\nw.ship_all();'),
     T("count_low_counts_reserved", f"{WH_DESC}; reserve bolt 9; count_low(2), count_low(5), count_low(0)", "(w.count_low(2), w.count_low(5), w.count_low(0))", "(1, 2, 0)", setup=WH_SETUP + '\nw.reserve("bolt", 9);'),
     T("tag_then_receive", f"{WH_DESC}; tag_last \"!\"; receive bolt 1", '(w.last(), w.available("bolt"))', '(Some("bolt"), 11)', setup=WH_SETUP + '\nw.tag_last("!");\nw.receive("bolt", 1);'),
     r"""
     #[test]
     fn random_vs_model() {
         use std::collections::BTreeMap;
         let mut rng = anneal_prelude::Rng::new(6203);
         let names = ["a", "b", "c"];
         for _ in 0..300 {
             let mut w = Warehouse::new();
             let mut model: BTreeMap<&str, (u32, u32)> = BTreeMap::new();
             let mut last: Option<String> = None;
             let mut log: Vec<String> = Vec::new();
             let mut ops = Vec::new();
             for _ in 0..10 {
                 let name = *rng.pick(&names);
                 let q = rng.below(5) as u32;
                 match rng.below(4) {
                     0 => {
                         w.receive(name, q);
                         model.entry(name).or_default().0 += q;
                         last = Some(name.to_string());
                         ops.push(format!("receive {name} {q}"));
                     }
                     1 => {
                         let want = match model.get_mut(name) {
                             Some(s) => {
                                 let n = q.min(s.0 - s.1);
                                 s.1 += n;
                                 last = Some(name.to_string());
                                 n
                             }
                             None => 0,
                         };
                         ops.push(format!("reserve {name} {q}"));
                         check!(ops.join(", "), w.reserve(name, q), want);
                     }
                     2 => {
                         let mut n = 0;
                         for (k, s) in model.iter_mut() {
                             if s.1 > 0 {
                                 log.push(format!("{k}: {}", s.1));
                                 s.0 -= s.1;
                                 s.1 = 0;
                                 n += 1;
                             }
                         }
                         ops.push("ship_all".to_string());
                         check!(ops.join(", "), w.ship_all(), n);
                     }
                     _ => {
                         let want = model.values().filter(|s| s.0 - s.1 < q).count();
                         ops.push(format!("count_low {q}"));
                         check!(ops.join(", "), w.count_low(q), want);
                     }
                 }
             }
             check!(format!("{}; last, log", ops.join(", ")), (w.last(), w.log().to_vec()), (last.as_deref(), log.clone()));
             for n in names {
                 let want = model.get(n).map_or(0, |s| s.0 - s.1);
                 check!(format!("{}; available({n})", ops.join(", ")), w.available(n), want);
             }
         }
     }
     """],
    [("rust", "Read each error for where the shared access comes from: a `&self` receiver, `get` instead of `get_mut`, `iter` instead of `iter_mut`, `&self.last` in a pattern, and a closure binding that isn't `mut` (calling an `FnMut` needs `&mut` to the closure)."),
     ("rust", "Once `reserve` holds `s` from `get_mut`, `self.touch(name)` borrows all of `self` while `s` is still used. Where can the call go so the borrows don't overlap?")],
    ("""`&` is shared access and `&mut` unique access, and each position has its own spelling: the receiver (`&mut self`), the lookup (`get_mut`), the iterator (`iter_mut`, which also makes the pattern `(name, s)` bind `s: &mut Stock`), a pattern on a field (`&mut self.last`, or `self.last.as_mut()`), and a closure that mutates what it captured (it's `FnMut`, so calling it borrows it mutably: `let mut bump`).

In `reserve`, `s` borrows one entry of `self.items`, but `self.touch(name)` borrows all of `self`, so the call moves after the last use of `s`. It must stay after the `let else`, too: an unknown item isn't touched. `ship_all` pushes to `lines` while iterating `self.items` mutably, which is fine, and `available` and `last` keep `&self`.""", "O(1) per call; O(n log n) ship_all", "O(n) ship_all"),
    "Why does calling an `FnMut` closure need a `mut` binding, when calling an `Fn` closure doesn't?",
    ["Every position that grants access has a shared and a unique spelling.", "A method call borrows all of `self`; a field borrow only the field.", "Calling an `FnMut` borrows the closure mutably."],
    rules=dict(methods=["clone", "take", "replace"], lines=8),
    wrong=dict(
        touch_before_lookup=sub(WAREHOUSE_SOLUTION, "        let Some(s) = self.items.get_mut(name) else { return 0 };\n        let n = qty.min(s.qty - s.reserved);\n        s.reserved += n;\n        self.touch(name);\n",
                                "        self.touch(name);\n        let Some(s) = self.items.get_mut(name) else { return 0 };\n        let n = qty.min(s.qty - s.reserved);\n        s.reserved += n;\n"),
        count_low_at_limit=sub(WAREHOUSE_SOLUTION, "if s.qty - s.reserved < limit {", "if s.qty - s.reserved <= limit {"),
        ships_without_clearing=sub(WAREHOUSE_SOLUTION, "                s.qty -= s.reserved;\n                s.reserved = 0;\n", "                s.qty -= s.reserved;\n"),
    ),
))

WORDS_SOLUTION = r"""
use std::collections::HashMap;
use std::hash::{Hash, Hasher};

/// A word that compares and hashes ignoring ASCII case.
struct Word<'a>(&'a str);

impl PartialEq for Word<'_> {
    fn eq(&self, other: &Self) -> bool {
        self.0.eq_ignore_ascii_case(other.0)
    }
}

impl Eq for Word<'_> {}

impl Hash for Word<'_> {
    fn hash<H: Hasher>(&self, state: &mut H) {
        for b in self.0.bytes() {
            state.write_u8(b.to_ascii_lowercase());
        }
        state.write_u8(0xff);
    }
}

pub fn top_words(text: &str, k: usize) -> Vec<(&str, usize)> {
    // word -> (count, index of its first appearance)
    let mut counts: HashMap<Word, (usize, usize)> = HashMap::new();
    for (i, w) in text.split(|c: char| !c.is_alphanumeric()).filter(|w| !w.is_empty()).enumerate() {
        counts.entry(Word(w)).or_insert((0, i)).0 += 1;
    }
    let mut top: Vec<(&str, usize, usize)> = counts.into_iter().map(|(w, (n, first))| (w.0, n, first)).collect();
    top.sort_unstable_by(|a, b| b.1.cmp(&a.1).then(a.2.cmp(&b.2)));
    top.into_iter().take(k).map(|(w, n, _)| (w, n)).collect()
}
"""

WORDS_DOC = r"""
/// The `k` most frequent words of `text` with their counts, most frequent first; a tie goes to the word that
/// appeared first. A word is a maximal run of alphanumeric chars (`char::is_alphanumeric`). Words that differ
/// only in ASCII case are the same word, reported with the spelling it first appeared with, as a slice of `text`.
"""


def words_case(name, text, k, want):
    rust_text = text.replace('"', '\\"')
    exp = "vec![" + ", ".join(f'("{w}", {n})' for w, n in want) + "]"
    if not want:
        exp = "Vec::<(&str, usize)>::new()"
    return T(name, f'text = "{rust_text}", k = {k}', f'top_words("{rust_text}", {k})', exp)


P.append(writep(
    "most-repeated-word", "Count words without cloning", "easy", "shared-vs-unique", ["&str", "HashMap", "Hash", "borrowed keys"],
    """
        Return the `k` most frequent words of `text` with their counts: most frequent first, a tie going to the
        word that appeared first. A word is a maximal run of alphanumeric chars. Words that differ only in ASCII
        case are the same word (`Rust`, `rust`, `RUST`), reported with the spelling it first appeared with.

        Every word you return is a slice of `text`, and you may not allocate per word: a hidden test counts
        allocations on a long text.
    """,
    "use std::collections::HashMap;\n" + WORDS_DOC + "pub fn top_words(text: &str, k: usize) -> Vec<(&str, usize)> {\n    todo!()\n}\n",
    WORDS_SOLUTION.replace("pub fn top_words", WORDS_DOC.strip("\n") + "\npub fn top_words"),
    [words_case("example", "the cat and the hat and the bat", 2, [("the", 3), ("and", 2)]),
     words_case("case_folds_to_first_spelling", "Rust rust RUST go Go", 5, [("Rust", 3), ("go", 2)]),
     words_case("tie_goes_to_first_seen", "b a a b c", 3, [("b", 2), ("a", 2), ("c", 1)]),
     words_case("punctuation_splits", "well-known, well: known!", 2, [("well", 2), ("known", 2)]),
     words_case("k_beyond_distinct", "x y", 10, [("x", 1), ("y", 1)]),
     words_case("empty_text", "", 3, []),
     words_case("k_zero", "a a", 0, [])],
    [ALLOC_COUNTER,
     words_case("only_separators", "  ,,; - ", 2, []),
     words_case("digits_are_word_chars", "v2 V2 route66", 2, [("v2", 2), ("route66", 1)]),
     words_case("apostrophe_splits", "don't DON'T", 3, [("don", 2), ("t", 2)]),
     words_case("unicode_letters", "café Café CAFÉ", 3, [("café", 2), ("CAFÉ", 1)]),
     words_case("non_ascii_separator", "a—b—a", 2, [("a", 2), ("b", 1)]),
     words_case("newlines_and_tabs", "one\\ttwo\\nTWO\\n\\none", 1, [("one", 2)]),
     words_case("later_word_overtakes", "a b b", 1, [("b", 2)]),
     words_case("single_word", "Solo", 1, [("Solo", 1)]),
     r"""
     #[test]
     fn words_borrow_the_text() {
         let text = String::from("Beta alpha BETA");
         let got = top_words(&text, 2);
         let range = text.as_bytes().as_ptr_range();
         check!("\"Beta alpha BETA\": every word points into the text", got.iter().all(|(w, _)| range.contains(&w.as_ptr())), true);
         check!("\"Beta alpha BETA\": and is the first spelling", got[0].0.as_ptr() == text.as_ptr(), true);
     }

     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(6204);
         for _ in 0..300 {
             let len = rng.below(24);
             let text = rng.string(len, "aAbB c.");
             let k = rng.below(5);
             let words: Vec<&str> = text.split(|c: char| !c.is_alphanumeric()).filter(|w| !w.is_empty()).collect();
             // (lowercase, first spelling, count, first index)
             let mut seen: Vec<(String, &str, usize, usize)> = Vec::new();
             for (i, w) in words.iter().enumerate() {
                 let low = w.to_ascii_lowercase();
                 match seen.iter_mut().find(|s| s.0 == low) {
                     Some(s) => s.2 += 1,
                     None => seen.push((low, w, 1, i)),
                 }
             }
             seen.sort_by(|a, b| b.2.cmp(&a.2).then(a.3.cmp(&b.3)));
             let want: Vec<(&str, usize)> = seen.iter().take(k).map(|s| (s.1, s.2)).collect();
             check!(format!("text = {text:?}, k = {k}"), top_words(&text, k), want);
         }
     }

     #[test]
     fn long_text_allocates_per_distinct_word() {
         let spellings = ["Rust", "rust", "RUST", "go", "Go", "zig"];
         let mut text = String::new();
         for i in 0..200_000 {
             text.push_str(spellings[i % 6]);
             text.push(' ');
         }
         let (got, n) = allocs(|| top_words(&text, 3));
         check!("200000 words, 6 spellings of 3 words", got, vec![("Rust", 100_001), ("go", 66_666), ("zig", 33_333)]);
         check!("200000 words: at most 64 allocations (a String per word would be 200000)", n <= 64, true);
     }
     """],
    [("rust", "Key the map by `&str` slices of `text` so nothing is copied. Returning keys of a map that owns `String`s wouldn't compile: they'd borrow the map, which dies at the end of the function."),
     ("rust", "Case-insensitive keys without allocating: wrap the slice in your own type and implement `PartialEq`, `Eq` and `Hash` by hand so they ignore ASCII case. `entry` keeps the key it was first inserted with.")],
    ("""The words borrow `text`, so the result's elided lifetime ties it to `text`, not to the map: that's why the map can be dropped while the slices are returned. Folding case with `to_lowercase()` per word would work but allocate a `String` per word; a newtype key whose `Hash` and `Eq` ignore ASCII case keeps every key a borrowed slice, and `entry` keeps the first spelling because an existing key is never replaced. `Hash` must agree with `Eq`: equal words must hash the same, so hash the lowercased bytes.

Syntax to remember: `struct Word<'a>(&'a str);` · `impl Hash for Word<'_> { fn hash<H: Hasher>(&self, state: &mut H) { .. } }` · `impl Eq for Word<'_> {}` · `self.0.eq_ignore_ascii_case(other.0)` · `sort_unstable_by(|a, b| b.1.cmp(&a.1).then(a.2.cmp(&b.2)))`.""", "O(n + d log d) for d distinct words", "O(d)"),
    "Unicode case folding (`É` and `é`) can change a word's length. Why can't a borrowed key fold it the way this one folds ASCII?",
    ["Borrowed keys: `HashMap<&str, _>` or a newtype over `&str`.", "A hand-written `Hash` must agree with `Eq`.", "Returning slices of the input, not of a local map."],
    related=("L2", "S4"),
    wrong=dict(
        lowercase_string_keys=r"""
            use std::collections::HashMap;

            pub fn top_words(text: &str, k: usize) -> Vec<(&str, usize)> {
                let mut counts: HashMap<String, (usize, usize, &str)> = HashMap::new();
                for (i, w) in text.split(|c: char| !c.is_alphanumeric()).filter(|w| !w.is_empty()).enumerate() {
                    counts.entry(w.to_ascii_lowercase()).or_insert((0, i, w)).0 += 1;
                }
                let mut top: Vec<(usize, usize, &str)> = counts.into_values().collect();
                top.sort_unstable_by(|a, b| b.0.cmp(&a.0).then(a.1.cmp(&b.1)));
                top.into_iter().take(k).map(|(n, _, w)| (w, n)).collect()
            }
        """,
        ties_alphabetical=sub(WORDS_SOLUTION, "then(a.2.cmp(&b.2))", "then(a.0.cmp(b.0))"),
        case_sensitive=sub(WORDS_SOLUTION, "self.0.eq_ignore_ascii_case(other.0)", "self.0 == other.0").replace("state.write_u8(b.to_ascii_lowercase());", "state.write_u8(b);"),
        whitespace_words=sub(WORDS_SOLUTION, "text.split(|c: char| !c.is_alphanumeric()).filter(|w| !w.is_empty())", "text.split_whitespace()"),
    ),
))

ACCOUNTS_HEAD = r"""
#[derive(Debug, PartialEq)]
pub struct Account {
    pub id: u32,
    pub balance: i64,
}
"""

ACCOUNTS_STARTER = ACCOUNTS_HEAD + r"""
/// Pays `pct` percent interest (rounded toward zero) into every selected account.
pub fn pay_interest(selected: &[&mut Account], pct: i64) {
    for a in selected {
        a.balance += a.balance * pct / 100;
    }
}

/// Points `richest` at whichever of `richest` and `candidate` has the larger balance; a tie keeps `richest`.
pub fn keep_richest<'a>(richest: &mut &'a Account, candidate: &'a Account) {
    if candidate.balance > richest.balance {
        *richest = candidate;
    }
}

/// Moves `amount` from `from` into `to`.
pub fn top_up(to: &mut &Account, from: &mut Account, amount: i64) {
    from.balance -= amount;
    to.balance += amount;
}

/// Pays interest to every account with a balance of at least `min`, and returns their ids in order.
pub fn reward(accounts: &mut [Account], min: i64, pct: i64) -> Vec<u32> {
    let selected: Vec<&mut Account> = accounts.iter_mut().filter(|a| a.balance >= min).collect();
    pay_interest(&selected, pct);
    selected.iter().map(|a| a.id).collect()
}

/// The id of the richest account (the first one on a tie), or None if there are none.
pub fn richest_id(accounts: &[Account]) -> Option<u32> {
    let (first, rest) = accounts.split_first()?;
    let mut best = first;
    for a in rest {
        keep_richest(&mut best, a);
    }
    Some(best.id)
}
"""

ACCOUNTS_SOLUTION = ACCOUNTS_STARTER
for _old, _new in [
    ("pub fn pay_interest(selected: &[&mut Account], pct: i64) {\n    for a in selected {", "pub fn pay_interest(selected: &mut [&mut Account], pct: i64) {\n    for a in selected.iter_mut() {"),
    ("pub fn top_up(to: &mut &Account,", "pub fn top_up(to: &mut Account,"),
    ("    let selected: Vec<&mut Account>", "    let mut selected: Vec<&mut Account>"),
    ("pay_interest(&selected, pct);", "pay_interest(&mut selected, pct);"),
]:
    ACCOUNTS_SOLUTION = sub(ACCOUNTS_SOLUTION, _old, _new)


def acc(xs):
    return "vec![" + ", ".join(f"Account {{ id: {i}, balance: {b} }}" for i, b in xs) + "]"


P.append(fixp(
    "fix-mutate-through-shared-ref", "Fix: a &mut behind a & is read-only", "easy", "shared-vs-unique", ["E0594", "E0596", "&&mut T", "&mut &T"],
    """
        This doesn't compile. Two functions try to write through a reference that only grants reading, even
        though a `&mut` appears in their types. Fix the signatures and their callers. `keep_richest` and
        `richest_id` are correct: leave them alone.
    """,
    ACCOUNTS_STARTER,
    ACCOUNTS_SOLUTION,
    [T("reward_pays_selected", "balances [100, 50, 300], min 100, 10%", "{ let mut v = " + acc([(1, 100), (2, 50), (3, 300)]) + "; let ids = reward(&mut v, 100, 10); (ids, v.iter().map(|a| a.balance).collect::<Vec<_>>()) }", "(vec![1, 3], vec![110, 50, 330])"),
     T("interest_rounds_toward_zero", "balances [15, -15], min -100, 10%", "{ let mut v = " + acc([(1, 15), (2, -15)]) + "; reward(&mut v, -100, 10); (v[0].balance, v[1].balance) }", "(16, -16)"),
     T("top_up_moves_funds", "to 5, from 20, amount 7", "{ let (mut to, mut from) = (Account { id: 1, balance: 5 }, Account { id: 2, balance: 20 }); top_up(&mut to, &mut from, 7); (to.balance, from.balance) }", "(12, 13)"),
     T("richest_first_on_tie", "balances [3, 9, 9]", "richest_id(&" + acc([(1, 3), (2, 9), (3, 9)]) + ")", "Some(2)"),
     T("keep_richest_repoints", "richest 4, candidate 8", "{ let (a, b) = (Account { id: 1, balance: 4 }, Account { id: 2, balance: 8 }); let mut r = &a; keep_richest(&mut r, &b); r.id }", "2"),
     T("pay_interest_direct", "two selected accounts 200, 1000; 5%", "{ let (mut a, mut b) = (Account { id: 1, balance: 200 }, Account { id: 2, balance: 1000 }); pay_interest(&mut [&mut a, &mut b], 5); (a.balance, b.balance) }", "(210, 1050)")],
    [T("reward_none_selected", "balances [1, 2], min 10", "{ let mut v = " + acc([(1, 1), (2, 2)]) + "; (reward(&mut v, 10, 50), v[0].balance, v[1].balance) }", "(vec![], 1, 2)"),
     T("reward_empty", "no accounts", "reward(&mut [], 0, 10)", "vec![]"),
     T("reward_at_min", "balance 100, min 100, 1%", "{ let mut v = " + acc([(7, 100)]) + "; (reward(&mut v, 100, 1), v[0].balance) }", "(vec![7], 101)"),
     T("zero_percent", "balance 99, 0%", "{ let mut v = " + acc([(1, 99)]) + "; reward(&mut v, 0, 0); v[0].balance }", "99"),
     T("small_balance_no_interest", "balance 9, 10%", "{ let mut v = " + acc([(1, 9)]) + "; reward(&mut v, 0, 10); v[0].balance }", "9"),
     T("top_up_negative", "to 5, from 5, amount -3", "{ let (mut to, mut from) = (Account { id: 1, balance: 5 }, Account { id: 2, balance: 5 }); top_up(&mut to, &mut from, -3); (to.balance, from.balance) }", "(2, 8)"),
     T("richest_empty", "no accounts", "richest_id(&[])", "None"),
     T("richest_negative", "balances [-5, -2, -9]", "richest_id(&" + acc([(1, -5), (2, -2), (3, -9)]) + ")", "Some(2)"),
     T("keep_richest_tie", "richest 4, candidate 4", "{ let (a, b) = (Account { id: 1, balance: 4 }, Account { id: 2, balance: 4 }); let mut r = &a; keep_richest(&mut r, &b); r.id }", "1"),
     T("large_balances", "balance 10^15, 3%", "{ let mut v = " + acc([(1, 10**15)]) + "; reward(&mut v, 0, 3); v[0].balance }", str(10**15 + 3 * 10**13)),
     r"""
     #[test]
     fn random_vs_model() {
         let mut rng = anneal_prelude::Rng::new(6205);
         for _ in 0..300 {
             let n = rng.below(7);
             let balances: Vec<i64> = rng.vec(n, -500, 500);
             let min = rng.int(-500, 500);
             let pct = rng.int(0, 30);
             let mut v: Vec<Account> = balances.iter().enumerate().map(|(i, &b)| Account { id: i as u32, balance: b }).collect();
             let want_ids: Vec<u32> = v.iter().filter(|a| a.balance >= min).map(|a| a.id).collect();
             let want: Vec<i64> = balances.iter().map(|&b| if b >= min { b + b * pct / 100 } else { b }).collect();
             let ids = reward(&mut v, min, pct);
             let got: Vec<i64> = v.iter().map(|a| a.balance).collect();
             check!(format!("balances {balances:?}, min {min}, {pct}%"), (ids, got), (want_ids, want));
         }
     }
     """],
    [("rust", "`selected` is `&[&mut Account]`: a shared borrow of the slice. Everything reached through a `&` is read-only, including the `&mut` inside it; otherwise two copies of the `&` would hand out the same `&mut`."),
     ("rust", "`&mut &Account` lets you change which account the inner reference points at (that's what `keep_richest` does), but the account itself is still behind a `&`.")],
    ("""Mutability doesn't pass through a shared reference: `&&mut T` only reads the `T`, because `&` is `Copy` and two copies must not both write. So `pay_interest` needs `&mut [&mut Account]`, iterated with `iter_mut()` (which yields `&mut &mut Account`; field access derefs through both), and the caller passes `&mut selected` from a `mut` binding. The other direction, `&mut &T`, grants unique access to the *reference*: you may repoint it, as `keep_richest` does, but not write the `T`. `top_up` needs a plain `&mut Account`.

Syntax to remember: `fn f(xs: &mut [&mut T])` · `for x in xs.iter_mut() { x.field += 1 }` · `fn repoint<'a>(r: &mut &'a T, other: &'a T) { *r = other }`.""", "O(n)", "O(k) for the selection"),
    "`&mut &mut T` lets you write the `T`, but `&&mut T` doesn't. Why is the second rule needed for soundness?",
    ["`&` makes everything behind it read-only, including a `&mut`.", "`&mut &T` repoints a reference; it doesn't unlock the `T`."],
    rules=dict(methods=["clone"], lines=6),
    wrong=dict(
        interest_on_cents_after_division=sub(ACCOUNTS_SOLUTION, "a.balance += a.balance * pct / 100;", "a.balance += a.balance / 100 * pct;"),
        rewards_everyone=sub(ACCOUNTS_SOLUTION, "accounts.iter_mut().filter(|a| a.balance >= min).collect();", "accounts.iter_mut().collect();"),
        top_up_backwards=sub(ACCOUNTS_SOLUTION, "    from.balance -= amount;\n    to.balance += amount;", "    from.balance += amount;\n    to.balance -= amount;"),
    ),
))

SPLIT_STARTER = r"""
/// `names[0]` is a namespace. Prefixes every other name with "<namespace>::" in place, unless it already starts
/// with exactly that. An empty slice is left alone.
pub fn qualify(names: &mut [String]) {
    for i in 1..names.len() {
        let ns = &names[0];
        let done = names[i].strip_prefix(ns.as_str()).is_some_and(|rest| rest.starts_with("::"));
        if !done {
            names[i].insert_str(0, "::");
            names[i].insert_str(0, ns);
        }
    }
}

/// Seals every whole frame of `size` bytes (`size >= 2`) in `buf` and returns how many it sealed; bytes after
/// the last whole frame are left alone. In a frame, byte 0 is the key and the last byte the checksum: XOR every
/// byte in between with the key, then set the checksum to the wrapping sum of those new bytes.
pub fn seal_frames(buf: &mut [u8], size: usize) -> usize {
    let mut sealed = 0;
    for frame in buf.chunks_mut(size) {
        let key = &frame[0];
        let sum = &mut frame[size - 1];
        *sum = 0;
        for b in &mut frame[1..size - 1] {
            *b ^= *key;
            *sum = sum.wrapping_add(*b);
        }
        sealed += 1;
    }
    sealed
}

/// Swaps the first half of `v` with the last half in place. With an odd length the middle element stays:
/// [1, 2, 3, 4, 5] becomes [4, 5, 3, 1, 2].
pub fn swap_halves<T>(v: &mut [T]) {
    let half = v.len() / 2;
    let (front, back) = (&mut v[..half], &mut v[v.len() - half..]);
    front.swap_with_slice(back);
}
"""

SPLIT_SOLUTION = r"""
/// `names[0]` is a namespace. Prefixes every other name with "<namespace>::" in place, unless it already starts
/// with exactly that. An empty slice is left alone.
pub fn qualify(names: &mut [String]) {
    let Some((ns, rest)) = names.split_first_mut() else { return };
    for name in rest {
        let done = name.strip_prefix(ns.as_str()).is_some_and(|rest| rest.starts_with("::"));
        if !done {
            name.insert_str(0, "::");
            name.insert_str(0, ns);
        }
    }
}

/// Seals every whole frame of `size` bytes (`size >= 2`) in `buf` and returns how many it sealed; bytes after
/// the last whole frame are left alone. In a frame, byte 0 is the key and the last byte the checksum: XOR every
/// byte in between with the key, then set the checksum to the wrapping sum of those new bytes.
pub fn seal_frames(buf: &mut [u8], size: usize) -> usize {
    let mut sealed = 0;
    for frame in buf.chunks_exact_mut(size) {
        let (key, rest) = frame.split_first_mut().unwrap();
        let (sum, body) = rest.split_last_mut().unwrap();
        *sum = 0;
        for b in body {
            *b ^= *key;
            *sum = sum.wrapping_add(*b);
        }
        sealed += 1;
    }
    sealed
}

/// Swaps the first half of `v` with the last half in place. With an odd length the middle element stays:
/// [1, 2, 3, 4, 5] becomes [4, 5, 3, 1, 2].
pub fn swap_halves<T>(v: &mut [T]) {
    let half = v.len() / 2;
    let (front, rest) = v.split_at_mut(half);
    let back_start = rest.len() - half;
    front.swap_with_slice(&mut rest[back_start..]);
}
"""


def names_case(name, before, after):
    b = "[" + ", ".join(f'"{x}"' for x in before) + "]"
    a = "vec![" + ", ".join(f'"{x}"' for x in after) + "]" if after else "Vec::<String>::new()"
    return T(name, f"qualify({b})", f"{{ let src: [&str; {len(before)}] = {b}; let mut v: Vec<String> = src.iter().map(|s| s.to_string()).collect(); qualify(&mut v); v }}", a)


def frames_case(name, buf, size, sealed, after):
    return T(name, f"seal_frames({buf}, size {size})", f"{{ let mut b: Vec<u8> = vec!{buf}; let n = seal_frames(&mut b, {size}); (n, b) }}", f"({sealed}, vec!{after})")


def seal_py(buf, size):
    buf = list(buf)
    n = 0
    for s in range(0, len(buf) - size + 1, size):
        k = buf[s]
        tot = 0
        for j in range(s + 1, s + size - 1):
            buf[j] ^= k
            tot = (tot + buf[j]) % 256
        buf[s + size - 1] = tot
        n += 1
    return n, buf


def frames_auto(name, buf, size):
    n, after = seal_py(buf, size)
    return frames_case(name, buf, size, n, after)


P.append(fixp(
    "split-first-mut", "Fix: one &mut slice, several parts", "easy", "shared-vs-unique", ["E0502", "E0499", "split_first_mut", "split_last_mut", "split_at_mut", "chunks_exact_mut"],
    """
        None of these three functions compiles: each one needs a mutable borrow of one part of a slice while
        another part is borrowed too. Fix them without copying any `String`, building a new buffer, or moving values
        out with `mem::take` or `mem::replace`.
        `seal_frames` also has one bug the compiler can't see; the doc comments are the spec.
    """,
    SPLIT_STARTER,
    SPLIT_SOLUTION,
    [names_case("qualify_example", ["net", "tcp", "net::udp", "network"], ["net", "net::tcp", "net::udp", "net::network"]),
     names_case("qualify_empty_slice", [], []),
     frames_auto("seal_two_frames", [3, 1, 2, 0, 5, 5, 5, 0], 4),
     frames_auto("partial_frame_untouched", [1, 1, 1, 9, 9], 3),
     T("swap_halves_odd", "swap_halves([1, 2, 3, 4, 5])", "{ let mut v = [1, 2, 3, 4, 5]; swap_halves(&mut v); v }", "[4, 5, 3, 1, 2]"),
     T("swap_halves_strings", "swap_halves([\"a\", \"b\", \"c\", \"d\"])", '{ let mut v = ["a", "b", "c", "d"].map(String::from); swap_halves(&mut v); v }', '["c", "d", "a", "b"].map(String::from)')],
    [names_case("qualify_only_namespace", ["ns"], ["ns"]),
     names_case("qualify_prefix_without_colons", ["a", "ab", "a:b", "a::"], ["a", "a::ab", "a::a:b", "a::"]),
     names_case("qualify_empty_namespace", ["", "x", "::y"], ["", "::x", "::y"]),
     names_case("qualify_empty_name", ["n", ""], ["n", "n::"]),
     names_case("qualify_unicode", ["日本", "東京", "日本::大阪"], ["日本", "日本::東京", "日本::大阪"]),
     frames_auto("seal_size_two", [7, 7, 1, 2], 2),
     frames_auto("seal_wraps", [0, 200, 100, 0], 4),
     frames_auto("seal_buffer_shorter_than_frame", [1, 2], 3),
     frames_auto("seal_empty", [], 3),
     T("swap_halves_short", "swap_halves on [], [1], [1, 2]", "{ let (mut a, mut b, mut c): ([i32; 0], [i32; 1], [i32; 2]) = ([], [1], [1, 2]); swap_halves(&mut a); swap_halves(&mut b); swap_halves(&mut c); (b, c) }", "([1], [2, 1])"),
     r"""
     #[test]
     fn qualify_extends_in_place() {
         let mut v = vec!["ns".to_string(), String::with_capacity(64)];
         v[1].push_str("x");
         let before = v[1].as_ptr();
         qualify(&mut v);
         check!("qualify([\"ns\", \"x\" with spare capacity]): the String grows in place", (v[1].as_str(), v[1].as_ptr() == before), ("ns::x", true));
     }

     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(6206);
         for _ in 0..300 {
             let size = 2 + rng.below(4);
             let len = rng.below(14);
             let buf: Vec<u8> = rng.vec(len, 0, 255);
             let mut want = buf.clone();
             let mut n = 0;
             let total = want.len();
             for s in (0..).step_by(size).take_while(|s| s + size <= total) {
                 let k = want[s];
                 let mut tot = 0u8;
                 for j in s + 1..s + size - 1 {
                     want[j] ^= k;
                     tot = tot.wrapping_add(want[j]);
                 }
                 want[s + size - 1] = tot;
                 n += 1;
             }
             let mut got = buf.clone();
             let sealed = seal_frames(&mut got, size);
             check!(format!("seal_frames({buf:?}, size {size})"), (sealed, got), (n, want));

             let v: Vec<u32> = rng.vec(len, 0, 9);
             let h = len / 2;
             let mut want = v[len - h..].to_vec();
             want.extend_from_slice(&v[h..len - h]);
             want.extend_from_slice(&v[..h]);
             let mut got = v.clone();
             swap_halves(&mut got);
             check!(format!("swap_halves({v:?})"), got, want);
         }
     }

     #[test]
     fn big_buffer() {
         let mut buf = vec![1u8; 300_001];
         let n = seal_frames(&mut buf, 3);
         check!("300001 bytes of 1, size 3", (n, buf[0], buf[1], buf[2], buf[300_000]), (100_000, 1, 0, 0, 1));
         let mut v: Vec<u32> = (0..200_001).collect();
         swap_halves(&mut v);
         check!("swap_halves(0..200001)", (v[0], v[99_999], v[100_000], v[100_001], v[200_000]), (100_001, 200_000, 100_000, 0, 99_999));
     }
     """],
    [("rust", "`let ns = &names[0]` borrows the whole slice, so `names[i].insert_str(..)` can't borrow it mutably at the same time, even though `i != 0`. The compiler doesn't reason about index values."),
     ("rust", "`split_first_mut` gives `(&mut T, &mut [T])`, `split_last_mut` the last element and the rest, and `split_at_mut(mid)` two halves: borrows that can't overlap, so they can live together."),
     ("rust", "`chunks_mut` also yields a short last chunk; `chunks_exact_mut` yields only whole ones.")],
    ("""Indexing borrows the whole slice, so two index expressions can't hold a shared and a mutable borrow at once even when the indices differ: the borrow checker never compares index values. The `split_*_mut` methods prove the parts are disjoint (they check the lengths, then hand out non-overlapping borrows), so the parts can be used together. Copying the key byte out (`let key = frame[0];`) would also work for `u8`; for the `String` namespace, splitting is how you read one element while growing another without a copy.

Syntax to remember: `let Some((head, rest)) = v.split_first_mut() else { return };` · `let (last, init) = v.split_last_mut().unwrap();` · `let (a, b) = v.split_at_mut(mid);` · `for chunk in v.chunks_exact_mut(n)` · `a.swap_with_slice(b)` (equal lengths).""", "O(n)", "O(1)"),
    "Why is there `chunks_mut` but no `windows_mut`?",
    ["Indexing borrows the whole slice; the compiler doesn't compare indices.", "`split_first_mut`, `split_last_mut`, `split_at_mut` give disjoint `&mut` parts.", "`chunks_exact_mut` skips the partial tail."],
    rules=dict(methods=["clone", "to_string", "to_owned", "to_vec", "swap", "take", "replace"]),
    related=("L2", "S3"),
    wrong=dict(
        seals_partial_frame=sub(SPLIT_SOLUTION, "buf.chunks_exact_mut(size)", "buf.chunks_mut(size).filter(|f| f.len() >= 2)"),
        rotate_instead_of_swap=sub(SPLIT_SOLUTION, "    let (front, rest) = v.split_at_mut(half);\n    let back_start = rest.len() - half;\n    front.swap_with_slice(&mut rest[back_start..]);", "    v.rotate_left(half);"),
        qualify_skips_prefix_only=sub(SPLIT_SOLUTION, "let done = name.strip_prefix(ns.as_str()).is_some_and(|rest| rest.starts_with(\"::\"));", "let done = name.starts_with(ns.as_str());"),
    ),
))

# ---------------------------------------------------------------- where borrows end (easy)

BATCH_HEAD = r"""
/// Collects lines and appends them to `out` when it's dropped.
pub struct Batch<'a> {
    out: &'a mut Vec<String>,
    buf: Vec<String>,
}

impl<'a> Batch<'a> {
    pub fn new(out: &'a mut Vec<String>) -> Self {
        Batch { out, buf: Vec::new() }
    }

    pub fn line(&mut self, s: String) {
        self.buf.push(s);
    }
}

impl Drop for Batch<'_> {
    fn drop(&mut self) {
        self.out.append(&mut self.buf);
    }
}

/// Renders `items` into `out`:
/// - if `out` already has lines, its first line is a title: append " (cont.)" to it; otherwise push "untitled";
/// - push each item as "- <item>";
/// - through a `Batch`, add "<n> items, longest: <item>", naming the first of the longest items (by bytes), or
///   "-" when there are none.
/// Returns how many lines `out` has afterwards.
"""

RENDER_STARTER = BATCH_HEAD + r"""pub fn render(out: &mut Vec<String>, items: &[&str]) -> usize {
    let title = out.first_mut();
    if out.is_empty() {
        out.push("untitled".to_string());
    }
    if let Some(t) = title {
        t.push_str(" (cont.)");
    }
    let mut longest: Option<&str> = None;
    for item in items {
        out.push(format!("- {item}"));
        let line = &out[out.len() - 1][2..];
        if longest.map_or(true, |l| line.len() > l.len()) {
            longest = Some(line);
        }
    }
    let mut batch = Batch::new(out);
    batch.line(format!("{} items, longest: {}", items.len(), longest.unwrap_or("-")));
    out.len()
}
"""

RENDER_SOLUTION = BATCH_HEAD + r"""pub fn render(out: &mut Vec<String>, items: &[&str]) -> usize {
    match out.first_mut() {
        Some(title) => title.push_str(" (cont.)"),
        None => out.push("untitled".to_string()),
    }
    let mut longest: Option<&str> = None;
    for item in items {
        out.push(format!("- {item}"));
        if longest.map_or(true, |l| item.len() > l.len()) {
            longest = Some(item);
        }
    }
    let mut batch = Batch::new(out);
    batch.line(format!("{} items, longest: {}", items.len(), longest.unwrap_or("-")));
    drop(batch);
    out.len()
}
"""


def render_case(name, before, items, after):
    b = "vec![" + ", ".join(f'"{x}".to_string()' for x in before) + "]" if before else "Vec::<String>::new()"
    it = "[" + ", ".join(f'"{x}"' for x in items) + "]"
    want = "vec![" + ", ".join(f'"{x}".to_string()' for x in after) + "]"
    return T(name, f"out = {before}, items = {it}".replace("'", '"'), f"{{ let mut out = {b}; let items: [&str; {len(items)}] = {it}; let n = render(&mut out, &items); (n, out) }}", f"({len(after)}, {want})")


def render_py(before, items):
    out = list(before)
    if out:
        out[0] += " (cont.)"
    else:
        out.append("untitled")
    longest = None
    for it in items:
        out.append(f"- {it}")
        if longest is None or len(it.encode()) > len(longest.encode()):
            longest = it
    out.append(f"{len(items)} items, longest: {longest if longest is not None else '-'}")
    return out


def render_auto(name, before, items):
    return render_case(name, before, items, render_py(before, items))


P.append(fixp(
    "fix-borrow-kept-alive", "Fix: borrows that live longer than they look", "easy", "where-borrows-end", ["NLL", "E0502", "E0499", "Drop", "scopes"],
    """
        `render` doesn't compile. Three borrows each outlive the place where you'd expect them to end: one is
        used again after a mutation, one is carried into the next turn of a loop, and one belongs to a value
        that still has work to do when it's dropped. Fix it without cloning, and keep `Batch` as it is.
    """,
    RENDER_STARTER,
    RENDER_SOLUTION,
    [render_auto("new_document", [], ["apples", "kiwi"]),
     render_auto("continues_a_title", ["Shopping"], ["milk"]),
     render_auto("no_items", [], []),
     render_auto("first_longest_wins", [], ["ab", "cd", "e"]),
     render_auto("keeps_earlier_lines", ["T", "- x", "1 items, longest: x"], ["yy"]),
     render_auto("longest_is_by_bytes", [], ["ééé", "abcd"])],
    [render_auto("title_twice", ["T (cont.)"], []),
     render_auto("empty_title", [""], ["a"]),
     render_auto("empty_item", [], ["", "a"]),
     render_auto("only_empty_items", [], ["", ""]),
     render_auto("dash_item", [], ["-"]),
     render_auto("unicode_items", ["日誌"], ["東京", "abc"]),
     render_auto("later_longer", [], ["a", "bb", "ccc"]),
     T("called_twice", "render([\"a\"]) twice into one out", '{ let mut out = Vec::new(); render(&mut out, &["a"]); let n = render(&mut out, &["bb"]); (n, out) }',
       '(5, ["untitled (cont.)", "- a", "1 items, longest: a", "- bb", "1 items, longest: bb"].map(String::from).to_vec())'),
     r"""
     #[test]
     fn random_vs_model() {
         let mut rng = anneal_prelude::Rng::new(6207);
         for _ in 0..300 {
             let before_len = rng.below(3);
             let mut before = Vec::new();
             for _ in 0..before_len {
                 let len = rng.below(3);
                 before.push(rng.string(len, "Tt"));
             }
             let n = rng.below(6);
             let mut owned = Vec::new();
             for _ in 0..n {
                 let len = rng.below(4);
                 owned.push(rng.string(len, "ab"));
             }
             let items: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
             let mut want = before.clone();
             match want.first_mut() {
                 Some(t) => t.push_str(" (cont.)"),
                 None => want.push("untitled".to_string()),
             }
             let mut longest: Option<&str> = None;
             for it in &items {
                 want.push(format!("- {it}"));
                 if longest.map_or(true, |l| it.len() > l.len()) {
                     longest = Some(it);
                 }
             }
             want.push(format!("{} items, longest: {}", items.len(), longest.unwrap_or("-")));
             let mut out = before.clone();
             let got = render(&mut out, &items);
             check!(format!("out = {before:?}, items = {items:?}"), (got, out), (want.len(), want));
         }
     }

     #[test]
     fn many_items() {
         let owned: Vec<String> = (0..100_000).map(|i| if i == 77_777 { "x".repeat(9) } else { "y".repeat(i % 8) }).collect();
         let items: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
         let mut out = Vec::new();
         let n = render(&mut out, &items);
         check!("100000 items, one of 9 bytes", (n, out[n - 1].clone()), (100_002, "100000 items, longest: xxxxxxxxx".to_string()));
     }
     """],
    [("rust", "A borrow lasts until its last use. `title` is used after `out.push`, and a `&mut` from `first_mut` can't coexist with `is_empty` or `push`. Can one `match` both use the title and handle its absence?"),
     ("rust", "`longest` points into `out` and survives into the next turn of the loop, where `out.push` runs again. The items themselves are in `items`, which nobody mutates: borrow from there."),
     ("rust", "`Batch` has a `Drop` impl, so its borrow of `out` lasts until it's dropped at the end of the scope, not until its last use. End it explicitly (`drop(batch)`) or give it a block.")],
    ("""With non-lexical lifetimes a borrow ends at its last use, and three things count as a use that's easy to miss. A later read (`title` after the push): matching `out.first_mut()` handles both cases, and the `None` arm can push because no binding holds the borrow there. A loop: a reference stored in a variable that the next turn reads is live across the loop's back edge, so each `out.push` conflicts with the previous turn's `longest`. Borrowing from `items` instead removes the conflict, since the output was never needed. A destructor: a value whose type implements `Drop` uses its borrows when it's dropped, so `batch` holds `out` to the end of the scope. `drop(batch)` (or `{ let mut batch = ..; .. }`) ends it where you choose, which is also when the footer lands, so `out.len()` must come after.

This is why a `MutexGuard` or `RefMut` held in a `let` keeps its lock until the end of the block.""", "O(n)", "O(1) extra"),
    "`std::mem::forget(batch)` also makes this compile. What does it break?",
    ["A borrow ends at its last use: later reads, the next loop turn and `Drop` all count.", "Borrow from the input instead of the output you're building.", "End a guard with `drop(x)` or a block."],
    rules=dict(methods=["clone", "to_owned"]),
    wrong=dict(
        forgets_the_batch=sub(RENDER_SOLUTION, "    drop(batch);\n", "    std::mem::forget(batch);\n"),
        counts_before_the_footer=sub(RENDER_SOLUTION, "    let mut batch = Batch::new(out);\n    batch.line(format!(\"{} items, longest: {}\", items.len(), longest.unwrap_or(\"-\")));\n    drop(batch);\n    out.len()",
                                     "    let n = out.len();\n    let mut batch = Batch::new(out);\n    batch.line(format!(\"{} items, longest: {}\", items.len(), longest.unwrap_or(\"-\")));\n    n"),
        last_longest=sub(RENDER_SOLUTION, "item.len() > l.len()", "item.len() >= l.len()"),
    ),
))

INTERNER_HEAD = r"""
use std::collections::HashMap;

/// Stores each distinct name once. Callers compare and hash the `&str`s it hands out instead of copying names.
pub struct Interner {
    ids: HashMap<String, usize>,
    names: Vec<String>,
}

impl Interner {
    pub fn new() -> Self {
        Interner { ids: HashMap::new(), names: Vec::new() }
    }

    /// Stores `name` if it's new, and returns the stored name.
    pub fn intern(&mut self, name: &str) -> &str {
        let i = match self.ids.get(name) {
            Some(&i) => i,
            None => {
                self.ids.insert(name.to_string(), self.names.len());
                self.names.push(name.to_string());
                self.names.len() - 1
            }
        };
        &self.names[i]
    }

    /// The stored name equal to `name`, if it has been interned.
    pub fn get(&self, name: &str) -> Option<&str> {
        self.ids.get(name).map(|&i| self.names[i].as_str())
    }

    pub fn len(&self) -> usize {
        self.names.len()
    }
}
"""

INTERNER_STARTER = INTERNER_HEAD + r"""
/// Interns every name and returns the stored names, in the same order.
pub fn intern_all<'i>(interner: &'i mut Interner, names: &[&str]) -> Vec<&'i str> {
    let mut out = Vec::new();
    for n in names {
        out.push(interner.intern(n));
    }
    out
}

/// Interns both ends of every edge. Returns the edges as pairs of stored names, and how many names were new.
pub fn intern_edges<'i>(interner: &'i mut Interner, edges: &[(&str, &str)]) -> (Vec<(&'i str, &'i str)>, usize) {
    let before = interner.len();
    let mut out = Vec::new();
    for &(a, b) in edges {
        let a = interner.intern(a);
        let b = interner.intern(b);
        out.push((a, b));
    }
    (out, interner.len() - before)
}
"""

INTERNER_SOLUTION = INTERNER_HEAD + r"""
/// Interns every name and returns the stored names, in the same order.
pub fn intern_all<'i>(interner: &'i mut Interner, names: &[&str]) -> Vec<&'i str> {
    for n in names {
        interner.intern(n);
    }
    let interner: &'i Interner = interner;
    names.iter().map(|n| interner.get(n).unwrap()).collect()
}

/// Interns both ends of every edge. Returns the edges as pairs of stored names, and how many names were new.
pub fn intern_edges<'i>(interner: &'i mut Interner, edges: &[(&str, &str)]) -> (Vec<(&'i str, &'i str)>, usize) {
    let before = interner.len();
    for &(a, b) in edges {
        interner.intern(a);
        interner.intern(b);
    }
    let added = interner.len() - before;
    let interner = &*interner;
    let pairs = edges.iter().map(|&(a, b)| (interner.get(a).unwrap(), interner.get(b).unwrap())).collect();
    (pairs, added)
}
"""

P.append(fixp(
    "end-borrow-before-mutating", "Fix: a &mut method that returns a borrow", "easy", "where-borrows-end", ["E0499", "E0502", "&mut self -> &T", "reborrow as shared"],
    """
        `intern` takes `&mut self` and returns a `&str` into the interner. `intern_all` and `intern_edges` keep
        those `&str`s while calling `intern` again, and neither compiles. Fix both functions without changing
        `Interner` and without copying any name: the `&str`s they return must be the interner's stored names.
    """,
    INTERNER_STARTER,
    INTERNER_SOLUTION,
    [T("intern_all_example", "intern_all([\"a\", \"b\", \"a\"])", "(r.clone(), r[0].as_ptr() == r[2].as_ptr())", '(vec!["a", "b", "a"], true)',
       setup='let mut i = Interner::new();\nlet r = intern_all(&mut i, &["a", "b", "a"]);'),
     T("intern_all_then_len", "intern_all([\"x\", \"x\", \"y\"]), then len()", '{ intern_all(&mut i, &["x", "x", "y"]); i.len() }', "2", setup="let mut i = Interner::new();"),
     T("edges_example", "intern_edges([(\"a\", \"b\"), (\"b\", \"c\")])", "(pairs.clone(), added, pairs[0].1.as_ptr() == pairs[1].0.as_ptr())", '(vec![("a", "b"), ("b", "c")], 3, true)',
       setup='let mut i = Interner::new();\nlet (pairs, added) = intern_edges(&mut i, &[("a", "b"), ("b", "c")]);'),
     T("edges_counts_only_new_names", "intern \"a\" first, then intern_edges([(\"a\", \"z\")])", "(pairs, added)", '(vec![("a", "z")], 1)',
       setup='let mut i = Interner::new();\ni.intern("a");\nlet (pairs, added) = intern_edges(&mut i, &[("a", "z")]);'),
     T("empty_inputs", "intern_all([]), intern_edges([])", '{ let a = intern_all(&mut i, &[]).len(); let (p, n) = intern_edges(&mut i, &[]); (a, p.len(), n) }', "(0, 0, 0)", setup="let mut i = Interner::new();")],
    [T("self_loop_edge", "intern_edges([(\"a\", \"a\")])", "(pairs.clone(), added, pairs[0].0.as_ptr() == pairs[0].1.as_ptr())", '(vec![("a", "a")], 1, true)',
       setup='let mut i = Interner::new();\nlet (pairs, added) = intern_edges(&mut i, &[("a", "a")]);'),
     T("same_pointer_as_intern", "intern(\"k\"), then intern_all([\"k\"])", "p == q", "true",
       setup='let mut i = Interner::new();\nlet p = i.intern("k").as_ptr();\nlet q = intern_all(&mut i, &["k"])[0].as_ptr();'),
     T("all_already_known", "intern a, b; intern_edges([(\"b\", \"a\")])", "(pairs, added)", '(vec![("b", "a")], 0)',
       setup='let mut i = Interner::new();\ni.intern("a");\ni.intern("b");\nlet (pairs, added) = intern_edges(&mut i, &[("b", "a")]);'),
     T("empty_name", "intern_all([\"\", \"\"])", "(r.clone(), r[0].as_ptr() == r[1].as_ptr())", '(vec!["", ""], true)',
       setup='let mut i = Interner::new();\nlet r = intern_all(&mut i, &["", ""]);'),
     T("unicode_names", "intern_all([\"日本\", \"é\", \"日本\"])", "r", 'vec!["日本", "é", "日本"]', setup='let mut i = Interner::new();\nlet r = intern_all(&mut i, &["日本", "é", "日本"]);'),
     T("get_after_intern_all", "intern_all([\"m\"]), then get(\"m\"), get(\"n\")", '{ intern_all(&mut i, &["m"]); (i.get("m"), i.get("n")) }', '(Some("m"), None)', setup="let mut i = Interner::new();"),
     T("edges_order_kept", "intern_edges([(\"c\", \"b\"), (\"a\", \"c\")])", "(pairs, added)", '(vec![("c", "b"), ("a", "c")], 3)',
       setup='let mut i = Interner::new();\nlet (pairs, added) = intern_edges(&mut i, &[("c", "b"), ("a", "c")]);'),
     r"""
     #[test]
     fn random_vs_model() {
         let mut rng = anneal_prelude::Rng::new(6208);
         for _ in 0..300 {
             let n = rng.below(8);
             let mut owned = Vec::new();
             for _ in 0..n {
                 owned.push(rng.string(1, "abc"));
             }
             let names: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
             let mut i = Interner::new();
             let got = intern_all(&mut i, &names);
             // Equal names share one stored String.
             let mut shared = true;
             for x in 0..got.len() {
                 for y in 0..got.len() {
                     if (got[x] == got[y]) != (got[x].as_ptr() == got[y].as_ptr()) {
                         shared = false;
                     }
                 }
             }
             let got: Vec<String> = got.iter().map(|s| s.to_string()).collect();
             let mut distinct = names.clone();
             distinct.sort();
             distinct.dedup();
             check!(format!("intern_all({names:?})"), (got, shared, i.len()), (owned.clone(), true, distinct.len()));
         }
     }

     #[test]
     fn many_edges() {
         let owned: Vec<String> = (0..1000).map(|k| format!("n{k}")).collect();
         let edges: Vec<(&str, &str)> = (0..100_000).map(|k| (owned[k % 1000].as_str(), owned[(k * 7 + 3) % 1000].as_str())).collect();
         let mut i = Interner::new();
         let (pairs, added) = intern_edges(&mut i, &edges);
         check!("100000 edges over 1000 names", (pairs.len(), added, pairs[99_999]), (100_000, 1000, ("n999", "n996")));
     }
     """],
    [("rust", "A method `fn intern(&mut self, ..) -> &str` ties its result to the `&mut self` borrow. As long as the `&str` lives, the interner stays *mutably* borrowed: you can't call `intern` again, nor even `len`. There's no automatic downgrade to a shared borrow."),
     ("rust", "Do all the mutation first and throw the results away. Then reborrow the interner as shared (`let interner = &*interner;`) and look every name up with `get`, which takes `&self`: shared borrows can coexist.")],
    ("""A signature like `fn intern(&mut self, name: &str) -> &str` means the returned `&str` keeps `self` mutably borrowed for as long as it's used, even though it only reads. So the results of two calls can't be held at once. The fix splits the work into phases: intern everything (discarding the results), then turn the `&'i mut Interner` into a `&'i Interner` (`&*interner`, or a `let` with that type) and collect `get` results. Many shared borrows can coexist, and they can live for all of `'i` because the unique borrow is never used again. `intern_edges` must also read `len()` before taking those borrows, or compute it before them.

The other classic fix is an API change: return a `Copy` id (`Symbol(u32)`) from `intern` and add `resolve(&self, Symbol) -> &str`. That's what `rustc` and the `string-interner` crate do.""", "O(n) expected", "O(1) extra"),
    "`intern(&self, ..)` with interior mutability would let callers hold several results at once. What would the `names` storage have to guarantee for that to be sound?",
    ["`&mut self -> &T` keeps `self` mutably borrowed while the `&T` lives.", "Mutate first, then reborrow as shared (`&*r`) for many readers.", "Ids are the other way out."],
    rules=dict(methods=["clone", "to_owned", "leak"]),
    wrong=dict(
        counts_every_name=sub(INTERNER_SOLUTION, "    let added = interner.len() - before;\n", "    let added = 2 * edges.len() + before - before;\n"),
        counts_before_interning=sub(INTERNER_SOLUTION, "    let before = interner.len();\n    for &(a, b) in edges {\n        interner.intern(a);\n        interner.intern(b);\n    }\n    let added = interner.len() - before;\n",
                                    "    let added = interner.len();\n    for &(a, b) in edges {\n        interner.intern(a);\n        interner.intern(b);\n    }\n"),
        swaps_edge_ends=sub(INTERNER_SOLUTION, "(interner.get(a).unwrap(), interner.get(b).unwrap())", "(interner.get(b).unwrap(), interner.get(a).unwrap())"),
    ),
))

RUNS_DOC = r"""
use std::io::{self, BufRead};

/// Counts runs of consecutive lines with the same key. A line's key is the text before its first ':', or the
/// whole line (without its line ending) when it has none. Returns each run's key and length, in order.
"""

RUNS_STARTER = RUNS_DOC + r"""pub fn key_runs<R: BufRead>(mut input: R) -> io::Result<Vec<(String, usize)>> {
    let mut runs: Vec<(String, usize)> = Vec::new();
    let mut buf = String::new();
    let mut prev: Option<&str> = None;
    let mut count = 0;
    loop {
        buf.clear();
        if input.read_line(&mut buf)? == 0 {
            break;
        }
        let line = buf.trim_end_matches(['\n', '\r']);
        let key = line.split(':').next().unwrap_or(line);
        if prev == Some(key) {
            count += 1;
        } else {
            if let Some(p) = prev {
                runs.push((p.to_string(), count));
            }
            prev = Some(key);
            count = 1;
        }
    }
    if let Some(p) = prev {
        runs.push((p.to_string(), count));
    }
    Ok(runs)
}
"""

RUNS_SOLUTION = RUNS_DOC + r"""pub fn key_runs<R: BufRead>(mut input: R) -> io::Result<Vec<(String, usize)>> {
    let mut runs: Vec<(String, usize)> = Vec::new();
    let mut buf = String::new();
    let mut prev: Option<String> = None;
    let mut count = 0;
    loop {
        buf.clear();
        if input.read_line(&mut buf)? == 0 {
            break;
        }
        let line = buf.trim_end_matches(['\n', '\r']);
        let key = line.split(':').next().unwrap_or(line);
        if prev.as_deref() == Some(key) {
            count += 1;
        } else {
            if let Some(p) = prev.replace(key.to_string()) {
                runs.push((p, count));
            }
            count = 1;
        }
    }
    if let Some(p) = prev {
        runs.push((p, count));
    }
    Ok(runs)
}
"""


def runs_case(name, text, want):
    shown = text.replace("\n", "\\n").replace("\r", "\\r")
    exp = "vec![" + ", ".join(f'("{k}".to_string(), {n})' for k, n in want) + "]" if want else "Vec::<(String, usize)>::new()"
    return T(name, f'input "{shown}"', f'key_runs("{shown}".as_bytes()).unwrap()', exp)


P.append(fixp(
    "fix-read-after-clear", "Fix: a reused buffer and a borrow of the last line", "easy", "where-borrows-end", ["E0502", "BufRead::read_line", "Option::replace", "allocation"],
    """
        `key_runs` reads lines into one reused `String`, the usual way to avoid an allocation per line. It
        doesn't compile: the previous line's key is a slice of the buffer that `clear` and `read_line` are about
        to overwrite. Fix it. Keep the single `read_line` buffer, and allocate once per run, not once per line:
        a hidden test counts allocations.
    """,
    RUNS_STARTER,
    RUNS_SOLUTION,
    [runs_case("example", "a:1\na:2\nb:3\na:4\n", [("a", 2), ("b", 1), ("a", 1)]),
     runs_case("empty_input", "", []),
     runs_case("no_colon_uses_whole_line", "x\nx\ny\n", [("x", 2), ("y", 1)]),
     runs_case("first_colon_only", "k:v:w\nk:z\n", [("k", 2)]),
     runs_case("no_final_newline", "a:1\nb:2", [("a", 1), ("b", 1)]),
     runs_case("crlf", "a\r\na:2\r\n", [("a", 2)])],
    [ALLOC_COUNTER,
     runs_case("empty_lines", "\n\na\n", [("", 2), ("a", 1)]),
     runs_case("empty_key", ":x\n:y\nz\n", [("", 2), ("z", 1)]),
     runs_case("key_equals_line", "a\na:1\n", [("a", 2)]),
     runs_case("single_line", "only", [("only", 1)]),
     runs_case("alternating", "a\nb\na\nb\n", [("a", 1), ("b", 1), ("a", 1), ("b", 1)]),
     runs_case("unicode_keys", "日本:1\n日本:2\né\n", [("日本", 2), ("é", 1)]),
     runs_case("spaces_are_kept", " a:1\na:2\n", [(" a", 1), ("a", 1)]),
     runs_case("lone_cr_kept_inside", "a\rb\n", [("a\\rb", 1)]),
     r"""
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(6209);
         for _ in 0..300 {
             let n = rng.below(8);
             let mut text = String::new();
             for _ in 0..n {
                 let len = rng.below(4);
                 text.push_str(&rng.string(len, "ab:"));
                 text.push('\n');
             }
             let mut want: Vec<(String, usize)> = Vec::new();
             for line in text.lines() {
                 let key = line.split(':').next().unwrap();
                 match want.last_mut() {
                     Some((k, c)) if k == key => *c += 1,
                     _ => want.push((key.to_string(), 1)),
                 }
             }
             check!(format!("input {text:?}"), key_runs(text.as_bytes()).unwrap(), want);
         }
     }

     #[test]
     fn allocates_per_run_not_per_line() {
         let mut text = String::new();
         for i in 0..200_000 {
             text.push_str(&format!("key{}:{i}\n", i / 200));
         }
         let (runs, n) = allocs(|| key_runs(text.as_bytes()).unwrap());
         check!("200000 lines in 1000 runs of 200", (runs.len(), runs[999].clone()), (1000, ("key999".to_string(), 200)));
         check!("200000 lines in 1000 runs: at most 1100 allocations (one per line would be 200000)", n <= 1100, true);
     }
     """],
    [("rust", "`prev` is a `&str` into `buf`, and the next turn of the loop clears and refills `buf` while `prev` is still needed. What must the run's key be, if the buffer can't hold it?"),
     ("rust", "Own the key: `Option<String>`. Compare with `prev.as_deref() == Some(key)` so a repeated key costs nothing, and only on a new key swap the old one out with `prev.replace(key.to_string())`.")],
    ("""Reusing one buffer is exactly what makes a slice of it short-lived: `clear` and `read_line` need `&mut buf`, so no `&str` into it may survive to the next line. The key that has to outlive the line becomes an owned `String`, but only when it changes: `prev.as_deref() == Some(key)` compares without allocating, and `Option::replace` stores the new key and hands back the old one to push, so there's one allocation per run. Allocating `key.to_string()` on every line would compile too, and cost one allocation per line.

Syntax to remember: `while input.read_line(&mut buf)? != 0` (or `loop` with `buf.clear()` first) · `buf.trim_end_matches(['\\n', '\\r'])` · `prev.as_deref() == Some(key)` · `if let Some(old) = prev.replace(new) { .. }`.""", "O(total bytes)", "O(longest line + output)"),
    "`BufRead::lines()` would make this compile with no thought at all. What does it cost, and when is that fine?",
    ["A slice of a reused buffer can't outlive the next `clear`.", "Keep owned data only for what must survive, and only when it changes.", "`Option::replace` swaps in a new value and returns the old one."],
    rules=dict(methods=["clone", "to_owned", "lines"]),
    wrong=dict(
        allocates_per_line=r"""
            use std::io::{self, BufRead};

            pub fn key_runs<R: BufRead>(mut input: R) -> io::Result<Vec<(String, usize)>> {
                let mut runs: Vec<(String, usize)> = Vec::new();
                let mut buf = String::new();
                let mut prev: Option<String> = None;
                let mut count = 0;
                loop {
                    buf.clear();
                    if input.read_line(&mut buf)? == 0 {
                        break;
                    }
                    let line = buf.trim_end_matches(['\n', '\r']);
                    let key = line.split(':').next().unwrap_or(line).to_string();
                    if prev.as_ref() == Some(&key) {
                        count += 1;
                    } else {
                        if let Some(p) = prev.take() {
                            runs.push((p, count));
                        }
                        count = 1;
                    }
                    prev = Some(key);
                }
                if let Some(p) = prev {
                    runs.push((p, count));
                }
                Ok(runs)
            }
        """,
        drops_the_last_run=sub(RUNS_SOLUTION, "    if let Some(p) = prev {\n        runs.push((p, count));\n    }\n", ""),
        keeps_the_newline=sub(RUNS_SOLUTION, "let line = buf.trim_end_matches(['\\n', '\\r']);", "let line = buf.trim_end_matches('\\n');"),
    ),
))

INDEX_HEAD = r"""
use std::collections::HashMap;

pub struct Index {
    postings: HashMap<String, Vec<u32>>,
    hits: HashMap<String, u64>,
}
"""

INDEX_STARTER = INDEX_HEAD + r"""
impl Index {
    pub fn new() -> Self {
        Index { postings: HashMap::new(), hits: HashMap::new() }
    }

    /// Records that document `doc` contains each whitespace-separated word of `text`. A document is listed once
    /// per word, and documents are added in increasing id order. Must not allocate a key for a word the index
    /// already has.
    pub fn add(&mut self, doc: u32, text: &str) {
        todo!()
    }

    /// The documents containing `word`, in increasing order (empty if none).
    pub fn docs(&self, word: &str) -> &[u32] {
        todo!()
    }

    /// The posting list of `word`, created empty if it's missing, for the caller to edit.
    pub fn docs_mut(&mut self, word: &str) -> &mut Vec<u32> {
        todo!()
    }

    /// Counts a lookup of `word` and returns how many times it has been looked up, this one included. Must not
    /// allocate for a word looked up before.
    pub fn hit(&mut self, word: &str) -> u64 {
        todo!()
    }

    /// Removes `doc` from every posting list and drops lists that become empty. Returns how many lists changed.
    pub fn remove_doc(&mut self, doc: u32) -> usize {
        todo!()
    }

    /// How many words have a posting list.
    pub fn words(&self) -> usize {
        self.postings.len()
    }
}
"""

INDEX_SOLUTION = INDEX_HEAD + r"""
impl Index {
    pub fn new() -> Self {
        Index { postings: HashMap::new(), hits: HashMap::new() }
    }

    /// Records that document `doc` contains each whitespace-separated word of `text`. A document is listed once
    /// per word, and documents are added in increasing id order. Must not allocate a key for a word the index
    /// already has.
    pub fn add(&mut self, doc: u32, text: &str) {
        for w in text.split_whitespace() {
            match self.postings.get_mut(w) {
                Some(list) => {
                    if list.last() != Some(&doc) {
                        list.push(doc);
                    }
                }
                None => {
                    self.postings.insert(w.to_string(), vec![doc]);
                }
            }
        }
    }

    /// The documents containing `word`, in increasing order (empty if none).
    pub fn docs(&self, word: &str) -> &[u32] {
        self.postings.get(word).map_or(&[], Vec::as_slice)
    }

    /// The posting list of `word`, created empty if it's missing, for the caller to edit.
    pub fn docs_mut(&mut self, word: &str) -> &mut Vec<u32> {
        self.postings.entry(word.to_string()).or_default()
    }

    /// Counts a lookup of `word` and returns how many times it has been looked up, this one included. Must not
    /// allocate for a word looked up before.
    pub fn hit(&mut self, word: &str) -> u64 {
        if let Some(n) = self.hits.get_mut(word) {
            *n += 1;
            return *n;
        }
        self.hits.insert(word.to_string(), 1);
        1
    }

    /// Removes `doc` from every posting list and drops lists that become empty. Returns how many lists changed.
    pub fn remove_doc(&mut self, doc: u32) -> usize {
        let mut changed = 0;
        self.postings.retain(|_, list| {
            if let Ok(i) = list.binary_search(&doc) {
                list.remove(i);
                changed += 1;
            }
            !list.is_empty()
        });
        changed
    }

    /// How many words have a posting list.
    pub fn words(&self) -> usize {
        self.postings.len()
    }
}
"""

IX_SETUP = 'let mut ix = Index::new();\nix.add(1, "rust borrow check");\nix.add(2, "rust rust lifetimes");\nix.add(5, "borrow");'
IX_DESC = 'add 1 "rust borrow check", 2 "rust rust lifetimes", 5 "borrow"'

P.append(writep(
    "entry-returns-a-borrow", "The entry API and when not to use it", "easy", "where-borrows-end", ["HashMap::entry", "get_mut", "or_default", "retain", "allocation"],
    """
        Write the methods of `Index`, an inverted index from words to the documents that contain them, plus a
        count of lookups per word. Two methods must not allocate for a word they've seen before; a hidden test
        counts allocations. `docs_mut` returns a borrow into the map that the caller edits.
    """,
    INDEX_STARTER,
    INDEX_SOLUTION,
    [T("docs_example", IX_DESC, '(ix.docs("rust"), ix.docs("borrow"), ix.docs("check"))', "(&[1u32, 2][..], &[1u32, 5][..], &[1u32][..])", setup=IX_SETUP),
     T("unknown_word_is_empty", IX_DESC + "; docs(\"go\")", '(ix.docs("go"), ix.words())', "(&[][..], 4)", setup=IX_SETUP),
     T("docs_mut_creates_and_edits", IX_DESC + "; docs_mut(\"go\").push(9); docs_mut(\"rust\").retain(|&d| d != 1)", '(ix.docs("go"), ix.docs("rust"))', "(&[9u32][..], &[2u32][..])",
       setup=IX_SETUP + '\nix.docs_mut("go").push(9);\nix.docs_mut("rust").retain(|&d| d != 1);'),
     T("hit_counts", "hit rust, rust, go, rust", '(ix.hit("rust"), ix.hit("rust"), ix.hit("go"), ix.hit("rust"))', "(1, 2, 1, 3)", setup="let mut ix = Index::new();"),
     T("remove_doc", IX_DESC + "; remove_doc(1)", '(ix.remove_doc(1), ix.docs("rust"), ix.docs("check"), ix.words())', "(3, &[2u32][..], &[][..], 3)", setup=IX_SETUP),
     T("repeated_word_listed_once", IX_DESC + "; docs(\"rust\") after doc 2 said it twice", 'ix.docs("rust")', "&[1u32, 2][..]", setup=IX_SETUP)],
    [ALLOC_COUNTER,
     T("remove_unknown_doc", IX_DESC + "; remove_doc(3)", "(ix.remove_doc(3), ix.words())", "(0, 4)", setup=IX_SETUP),
     T("remove_all_docs", IX_DESC + "; remove_doc 1, 2, 5", "(ix.remove_doc(1), ix.remove_doc(2), ix.remove_doc(5), ix.words())", "(3, 2, 1, 0)", setup=IX_SETUP),
     T("empty_text", "add 1 \"\", add 2 \"   \"", "ix.words()", "0", setup='let mut ix = Index::new();\nix.add(1, "");\nix.add(2, "   ");'),
     T("case_sensitive", "add 1 \"Rust rust\"", '(ix.docs("Rust"), ix.docs("rust"), ix.docs("RUST"))', "(&[1u32][..], &[1u32][..], &[][..])", setup='let mut ix = Index::new();\nix.add(1, "Rust rust");'),
     T("tabs_and_newlines", "add 3 \"a\\tb\\n a\"", '(ix.docs("a"), ix.docs("b"))', "(&[3u32][..], &[3u32][..])", setup='let mut ix = Index::new();\nix.add(3, "a\\tb\\n a");'),
     T("hit_is_separate_from_docs", IX_DESC + "; hit(\"rust\")", '(ix.hit("rust"), ix.docs("rust"))', "(1, &[1u32, 2][..])", setup=IX_SETUP),
     T("docs_mut_existing_keeps_list", IX_DESC + "; docs_mut(\"borrow\") without editing", '{ ix.docs_mut("borrow"); (ix.docs("borrow"), ix.words()) }', "(&[1u32, 5][..], 4)", setup=IX_SETUP),
     T("docs_mut_missing_then_empty", "docs_mut(\"x\") on a new index", '{ ix.docs_mut("x"); (ix.docs("x"), ix.words()) }', "(&[][..], 1)", setup="let mut ix = Index::new();"),
     T("unicode_words", "add 4 \"日本 café 日本\"", '(ix.docs("日本"), ix.docs("café"))', "(&[4u32][..], &[4u32][..])", setup='let mut ix = Index::new();\nix.add(4, "日本 café 日本");'),
     r"""
     #[test]
     fn random_vs_model() {
         use std::collections::BTreeMap;
         let mut rng = anneal_prelude::Rng::new(6210);
         for _ in 0..200 {
             let mut ix = Index::new();
             let mut model: BTreeMap<String, Vec<u32>> = BTreeMap::new();
             let mut ops = Vec::new();
             let mut doc = 0;
             for _ in 0..8 {
                 if rng.below(3) > 0 {
                     doc += 1 + rng.below(2) as u32;
                     let len = rng.below(8);
                     let text = rng.string(len, "ab c");
                     ix.add(doc, &text);
                     for w in text.split_whitespace() {
                         let list = model.entry(w.to_string()).or_default();
                         if list.last() != Some(&doc) {
                             list.push(doc);
                         }
                     }
                     ops.push(format!("add {doc} {text:?}"));
                 } else {
                     let d = 1 + rng.below(doc as usize + 1) as u32;
                     let mut changed = 0;
                     model.retain(|_, list| {
                         if let Some(i) = list.iter().position(|&x| x == d) {
                             list.remove(i);
                             changed += 1;
                         }
                         !list.is_empty()
                     });
                     ops.push(format!("remove_doc {d}"));
                     check!(ops.join(", "), ix.remove_doc(d), changed);
                 }
             }
             check!(format!("{}; words()", ops.join(", ")), ix.words(), model.len());
             for w in ["a", "b", "ab", "ba", "c", "zz"] {
                 let want: &[u32] = model.get(w).map_or(&[], |v| v.as_slice());
                 check!(format!("{}; docs({w:?})", ops.join(", ")), ix.docs(w), want);
             }
         }
     }

     #[test]
     fn known_words_do_not_allocate() {
         let mut ix = Index::new();
         let words = ["alpha", "beta", "gamma", "delta"];
         for w in words {
             ix.hit(w);
         }
         let (_, n) = allocs(|| {
             for i in 0..100_000 {
                 ix.hit(words[i % 4]);
             }
         });
         check!("100000 hits on 4 known words: allocations", n, 0);
         check!("hits on alpha", ix.hit("alpha"), 25_002);
         let text = words.repeat(25_000).join(" ");
         ix.add(1, &text);
         let (_, n) = allocs(|| ix.add(2, &text));
         check!("add(2, 100000 words, 4 known): at most 16 allocations (a key per word would be 100000)", n <= 16, true);
         check!("docs(gamma)", ix.docs("gamma"), &[1u32, 2][..]);
     }
     """],
    [("rust", "`entry(key)` needs an owned key, so `entry(w.to_string())` allocates on every call, hit or miss. `get_mut(w)` looks up by `&str` (a `HashMap<String, _>` accepts any `&Q` where `String: Borrow<Q>`), and you insert only on a miss."),
     ("rust", "`if let Some(n) = map.get_mut(k) { .. return *n; }` then `insert` compiles: what's returned is a copy, not a borrow. `docs_mut` has to return a borrow, and there `entry(..).or_default()` is the simple answer."),
     ("rust", "`HashMap::retain(|k, v| ..)` hands the closure `&mut V`, so it can edit each list before deciding whether to keep it.")],
    ("""The entry API does one lookup and returns `&mut V` borrowed from the map, which is what `docs_mut` needs: `entry(word.to_string()).or_default()`. Its cost is the owned key, built on every call. On a hot path where most keys already exist, look up by `&str` first: `get_mut` for the hit, `insert` for the miss. That shape compiles because the hit branch returns a number, not a borrow; returning the `&mut` from `get_mut` early and inserting otherwise is the borrow checker's known blind spot (NLL problem case 3, in the Hard stage). `docs` returns a slice borrowed from `&self`; `map_or(&[], Vec::as_slice)` gives an empty slice for a missing word.

Syntax to remember: `map.entry(k).or_default()` · `map.entry(k).and_modify(|n| *n += 1).or_insert(1)` (also allocates `k` every time) · `map.get(word).map_or(&[], Vec::as_slice)` · `map.retain(|_, v| { ..; !v.is_empty() })`.""", "O(words) for add; O(1) expected per lookup; O(total postings) remove_doc", "O(1) extra"),
    "`hashbrown`'s `entry_ref` takes a borrowed key and allocates only on insert. Why can't std's `entry` do that with its current signature?",
    ["`entry` returns a borrow into the map, but costs an owned key.", "`get_mut` then `insert` avoids the allocation for hits.", "`retain` edits and filters a map in place."],
    related=("L2", "S4"),
    wrong=dict(
        hit_through_entry=sub(INDEX_SOLUTION, "        if let Some(n) = self.hits.get_mut(word) {\n            *n += 1;\n            return *n;\n        }\n        self.hits.insert(word.to_string(), 1);\n        1",
                              "        *self.hits.entry(word.to_string()).and_modify(|n| *n += 1).or_insert(1)"),
        add_through_entry=sub(INDEX_SOLUTION, "            match self.postings.get_mut(w) {\n                Some(list) => {\n                    if list.last() != Some(&doc) {\n                        list.push(doc);\n                    }\n                }\n                None => {\n                    self.postings.insert(w.to_string(), vec![doc]);\n                }\n            }",
                              "            let list = self.postings.entry(w.to_string()).or_default();\n            if list.last() != Some(&doc) {\n                list.push(doc);\n            }"),
        lists_a_doc_twice=sub(INDEX_SOLUTION, "                    if list.last() != Some(&doc) {\n                        list.push(doc);\n                    }", "                    list.push(doc);"),
        keeps_empty_lists=sub(INDEX_SOLUTION, "            !list.is_empty()\n", "            true\n"),
    ),
))

# ---------------------------------------------------------------- reborrows (medium)

REPORT_HEAD = r"""
use std::fmt::Write;

/// Writes `s` into `w`. Like most generic sinks, it takes the writer by value.
fn put<W: Write>(mut w: W, s: &str) {
    w.write_str(s).expect("writing to a String can't fail");
}

/// Adds `msg` to `alerts`, if there are alerts to add to.
fn note(alerts: Option<&mut Vec<String>>, msg: &str) {
    if let Some(a) = alerts {
        a.push(msg.to_string());
    }
}

/// Writes the first `header` lines as "[<line> / <line>]", then every remaining line as "; <line>". Each
/// remaining line that starts with '!' is also noted in `alerts` (when given), and the last note is
/// "<n> lines", where n counts the remaining lines. Returns n.
"""

REPORT_STARTER = REPORT_HEAD + r"""pub fn report<'a, I>(out: &mut String, mut lines: I, header: usize, alerts: Option<&mut Vec<String>>) -> usize
where
    I: Iterator<Item = &'a str>,
{
    let head: Vec<&str> = lines.take(header).collect();
    put(out, "[");
    put(out, &head.join(" / "));
    put(out, "]");
    let mut n = 0;
    for line in lines {
        put(out, "; ");
        put(out, line);
        if line.starts_with('!') {
            note(alerts, line);
        }
        n += 1;
    }
    note(alerts, &format!("{n} lines"));
    n
}
"""

REPORT_SOLUTION = REPORT_HEAD + r"""pub fn report<'a, I>(out: &mut String, mut lines: I, header: usize, mut alerts: Option<&mut Vec<String>>) -> usize
where
    I: Iterator<Item = &'a str>,
{
    let head: Vec<&str> = lines.by_ref().take(header).collect();
    put(&mut *out, "[");
    put(&mut *out, &head.join(" / "));
    put(&mut *out, "]");
    let mut n = 0;
    for line in lines {
        put(&mut *out, "; ");
        put(&mut *out, line);
        if line.starts_with('!') {
            note(alerts.as_deref_mut(), line);
        }
        n += 1;
    }
    note(alerts, &format!("{n} lines"));
    n
}
"""


def report_case(name, text, header, out, alerts, n, with_alerts=True):
    shown = text.replace("\n", "\\n")
    if with_alerts:
        al = "vec![" + ", ".join(f'"{a}".to_string()' for a in alerts) + "]" if alerts else "Vec::<String>::new()"
        call = f'{{ let mut out = String::new(); let mut alerts = Vec::new(); let n = report(&mut out, "{shown}".lines(), {header}, Some(&mut alerts)); (out, alerts, n) }}'
        return T(name, f'lines "{shown}", header {header}, with alerts', call, f'("{out}".to_string(), {al}, {n})')
    call = f'{{ let mut out = String::new(); let n = report(&mut out, "{shown}".lines(), {header}, None); (out, n) }}'
    return T(name, f'lines "{shown}", header {header}, no alerts', call, f'("{out}".to_string(), {n})')


def report_py(text, header):
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    head, rest = lines[:header], lines[header:]
    out = "[" + " / ".join(head) + "]" + "".join("; " + l for l in rest)
    alerts = [l for l in rest if l.startswith("!")] + [f"{len(rest)} lines"]
    return out, alerts, len(rest)


def report_auto(name, text, header, with_alerts=True):
    out, alerts, n = report_py(text, header)
    return report_case(name, text, header, out, alerts, n, with_alerts)


P.append(fixp(
    "fix-moved-mut-into-generic", "Fix: a &mut moved where you meant to lend it", "medium", "reborrows", ["E0382", "reborrow", "as_deref_mut", "Iterator::by_ref"],
    """
        `report` doesn't compile: three things it means to lend are moved instead, each of a different kind.
        Fix it without collecting all the lines first and without changing `put` or `note`.
    """,
    REPORT_STARTER,
    REPORT_SOLUTION,
    [report_auto("example", "Title\nv1\nok\n!disk full", 2),
     report_auto("no_header", "a\n!b", 0),
     report_auto("header_longer_than_input", "a\nb", 5),
     report_auto("without_alerts", "h\n!x\ny", 1, with_alerts=False),
     report_auto("empty_input", "", 1),
     T("appends_to_existing_output", "out = \">\", lines \"h\\nb\", header 1", '{ let mut out = String::from(">"); report(&mut out, "h\\nb".lines(), 1, None); out }', '">[h]; b".to_string()')],
    [report_auto("every_line_alert", "!a\n!b\n!c", 1),
     report_auto("bang_in_header_not_noted", "!h\nx", 1),
     report_auto("bang_not_first_char", "h\na!\n !b", 1),
     report_auto("empty_lines", "\n\nx\n", 1),
     report_auto("unicode", "日本\n!é", 1),
     report_auto("header_exactly_all", "a\nb", 2),
     report_auto("header_zero_empty", "", 0),
     T("keeps_existing_alerts", "alerts [\"old\"], lines \"h\\n!x\", header 1", '{ let mut out = String::new(); let mut alerts = vec!["old".to_string()]; report(&mut out, "h\\n!x".lines(), 1, Some(&mut alerts)); alerts }', 'vec!["old", "!x", "1 lines"]'),
     T("any_iterator", "lines from a Vec, header 1", '{ let v = vec!["a", "!b"]; let mut out = String::new(); let n = report(&mut out, v.into_iter(), 1, None); (out, n) }', '("[a]; !b".to_string(), 1)'),
     r"""
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(6211);
         for _ in 0..300 {
             let n = rng.below(7);
             let mut owned = Vec::new();
             for _ in 0..n {
                 let len = rng.below(3);
                 owned.push(rng.string(len, "!a"));
             }
             let header = rng.below(5);
             let lines: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
             let (head, rest) = lines.split_at(header.min(lines.len()));
             let mut want_out = format!("[{}]", head.join(" / "));
             let mut want_alerts: Vec<String> = Vec::new();
             for l in rest {
                 want_out.push_str(&format!("; {l}"));
                 if l.starts_with('!') {
                     want_alerts.push(l.to_string());
                 }
             }
             want_alerts.push(format!("{} lines", rest.len()));
             let mut out = String::new();
             let mut alerts = Vec::new();
             let got = report(&mut out, lines.iter().copied(), header, Some(&mut alerts));
             check!(format!("lines {lines:?}, header {header}"), (out, alerts, got), (want_out, want_alerts, rest.len()));
         }
     }

     #[test]
     fn long_input() {
         let text = "x\n!y\n".repeat(50_000);
         let mut out = String::new();
         let mut alerts = Vec::new();
         let n = report(&mut out, text.lines(), 2, Some(&mut alerts));
         check!("100000 lines, header 2", (n, alerts.len(), out.len(), alerts[49_999].clone()), (99_998, 50_000, 350_001, "99998 lines".to_string()));
     }
     """],
    [("rust", "Three moves: `out` (a `&mut String`) into `put`'s generic `W`, `lines` into `take`, and `alerts` (an `Option<&mut Vec<String>>`) into `note` inside a loop. None of them is `Copy`."),
     ("rust", "A `&mut` passed where the parameter type is exactly `&mut T` is reborrowed automatically; into a generic `W` it's moved. `&mut *out` lends a fresh, shorter borrow. Iterators have `by_ref()` for the same purpose."),
     ("rust", "For `Option<&mut T>`, `as_deref_mut()` gives an `Option<&mut T>` that reborrows the one inside, leaving `alerts` usable. `note` has one more call after the loop: that one can take `alerts` itself.")],
    ("""`&mut T` isn't `Copy`, so using one by value moves it. Rust inserts a reborrow (`&mut *out`) only where it knows the target type is a `&mut`; a generic parameter `W` isn't known to be one, so `put(out, ..)` moves `out` into `W = &mut String`. The same holds for anything that wraps a `&mut`: an `Option<&mut Vec<String>>` moves into `note`, and an iterator moves into `take` (its adapters take `self`). Each has its own way to lend: `&mut *out`; `alerts.as_deref_mut()` (or `alerts.as_mut().map(|a| &mut **a)`), which needs `mut alerts`; and `lines.by_ref()`, which is `&mut I`, itself an iterator. The last use of each can still move.

Syntax to remember: `put(&mut *out, s)` · `fn f(mut alerts: Option<&mut Vec<String>>)` then `alerts.as_deref_mut()` · `lines.by_ref().take(n)`.""", "O(total length)", "O(header)"),
    "`fmt::Write` has `impl<W: Write + ?Sized> Write for &mut W`. Without it, could `put(&mut *out, ..)` work at all?",
    ["A `&mut` moves into a generic parameter; `&mut *r` lends it instead.", "`Option<&mut T>::as_deref_mut()` reborrows the inner `&mut`.", "`Iterator::by_ref()` lends an iterator to a consuming adapter."],
    rules=dict(methods=["clone", "to_owned"], lines=9),
    wrong=dict(
        alerts_taken_once=sub(REPORT_SOLUTION, "note(alerts.as_deref_mut(), line);", "note(alerts.take(), line);"),
        header_counted=sub(REPORT_SOLUTION, "    let mut n = 0;\n", "    let mut n = head.len();\n"),
        head_joined_without_spaces=sub(REPORT_SOLUTION, 'head.join(" / ")', 'head.join("/")'),
    ),
))

METER_HEAD = r"""
/// A nested list of readings.
pub enum Item {
    One(i32),
    Many(Vec<Item>),
}

pub struct Meter {
    pub readings: Vec<i32>,
    pub offset: i32,
    pub log: Vec<String>,
}
"""

METER_STARTER = METER_HEAD + r"""
/// Calls `f` on every reading in `items`, depth first, in order.
fn walk<F: FnMut(i32)>(items: &[Item], mut f: F) {
    for it in items {
        match it {
            Item::One(x) => f(*x),
            Item::Many(inner) => walk(inner, f),
        }
    }
}

impl Meter {
    fn offset(&self) -> i32 {
        self.offset
    }

    /// Adds the offset to every recorded reading.
    pub fn calibrate(&mut self) {
        self.readings.iter_mut().for_each(|r| *r += self.offset());
    }

    /// Records every value of every batch. After each batch, logs "batch <i>: <n> above" where n counts the
    /// values above `limit` so far. Returns the final count.
    pub fn record(&mut self, batches: &[&[i32]], limit: i32) -> usize {
        let mut above = 0;
        let mut add = |x: i32| {
            self.readings.push(x);
            if x > limit {
                above += 1;
            }
        };
        for (i, batch) in batches.iter().enumerate() {
            for &x in *batch {
                add(x);
            }
            self.log.push(format!("batch {i}: {above} above"));
        }
        above
    }

    /// Records every reading in `items`, depth first, and returns their sum.
    pub fn record_nested(&mut self, items: &[Item]) -> i64 {
        let mut sum = 0;
        walk(items, |x| {
            self.readings.push(x);
            sum += x as i64;
        });
        sum
    }
}
"""

METER_SOLUTION = METER_HEAD + r"""
/// Calls `f` on every reading in `items`, depth first, in order.
fn walk<F: FnMut(i32)>(items: &[Item], f: &mut F) {
    for it in items {
        match it {
            Item::One(x) => f(*x),
            Item::Many(inner) => walk(inner, f),
        }
    }
}

impl Meter {
    fn offset(&self) -> i32 {
        self.offset
    }

    /// Adds the offset to every recorded reading.
    pub fn calibrate(&mut self) {
        self.readings.iter_mut().for_each(|r| *r += self.offset);
    }

    /// Records every value of every batch. After each batch, logs "batch <i>: <n> above" where n counts the
    /// values above `limit` so far. Returns the final count.
    pub fn record(&mut self, batches: &[&[i32]], limit: i32) -> usize {
        let mut above = 0;
        for (i, batch) in batches.iter().enumerate() {
            let mut add = |x: i32| {
                self.readings.push(x);
                if x > limit {
                    above += 1;
                }
            };
            for &x in *batch {
                add(x);
            }
            self.log.push(format!("batch {i}: {above} above"));
        }
        above
    }

    /// Records every reading in `items`, depth first, and returns their sum.
    pub fn record_nested(&mut self, items: &[Item]) -> i64 {
        let mut sum = 0;
        walk(items, &mut |x| {
            self.readings.push(x);
            sum += x as i64;
        });
        sum
    }
}
"""

METER_NEW = "let mut m = Meter { readings: vec![], offset: 0, log: vec![] };"

P.append(fixp(
    "fix-closure-borrows", "Fix: closures hold what they capture", "medium", "reborrows", ["E0502", "E0382", "closures", "disjoint captures", "FnMut", "&mut F"],
    """
        `Meter` doesn't compile. Each of its three methods uses a closure, and each closure borrows something
        for longer, or more broadly, than the code around it expects. Fix them. `walk` must stay generic over
        the closure type (no `dyn`), and no reading may be copied into a temporary collection.

        One fix that looks right for `walk` compiles, and then fails to build for a different reason. Read that
        error carefully.
    """,
    METER_STARTER,
    METER_SOLUTION,
    [T("calibrate_example", "readings [1, 2], offset 10; calibrate", "{ let mut m = Meter { readings: vec![1, 2], offset: 10, log: vec![] }; m.calibrate(); m.readings }", "vec![11, 12]"),
     T("record_logs_each_batch", "batches [[5, 20], [30], []], limit 10", "{ " + METER_NEW + " let n = m.record(&[&[5, 20], &[30], &[]], 10); (n, m.readings, m.log) }",
       '(2, vec![5, 20, 30], ["batch 0: 1 above", "batch 1: 2 above", "batch 2: 2 above"].map(String::from).to_vec())'),
     T("record_nested_depth_first", "[1, [2, [3]], 4]", "{ " + METER_NEW + " let s = m.record_nested(&[Item::One(1), Item::Many(vec![Item::One(2), Item::Many(vec![Item::One(3)])]), Item::One(4)]); (s, m.readings) }", "(10, vec![1, 2, 3, 4])"),
     T("record_nothing", "no batches", "{ " + METER_NEW + " (m.record(&[], 0), m.log.len()) }", "(0, 0)"),
     T("limit_is_strict", "batch [10, 11], limit 10", "{ " + METER_NEW + " m.record(&[&[10, 11]], 10) }", "1"),
     T("record_then_calibrate", "offset -1; record [[3]] limit 0; calibrate", "{ let mut m = Meter { readings: vec![], offset: -1, log: vec![] }; m.record(&[&[3]], 0); m.calibrate(); m.readings }", "vec![2]")],
    [T("calibrate_empty", "no readings", "{ let mut m = Meter { readings: vec![], offset: 5, log: vec![] }; m.calibrate(); m.readings.len() }", "0"),
     T("calibrate_twice", "readings [0], offset 3; calibrate twice", "{ let mut m = Meter { readings: vec![0], offset: 3, log: vec![] }; m.calibrate(); m.calibrate(); m.readings }", "vec![6]"),
     T("record_appends", "readings [9]; record [[1]] limit 5", "{ let mut m = Meter { readings: vec![9], offset: 0, log: vec![\"x\".to_string()] }; m.record(&[&[1]], 5); (m.readings, m.log.len()) }", "(vec![9, 1], 2)"),
     T("record_negative_limit", "batch [-3, -1, 0], limit -2", "{ " + METER_NEW + " m.record(&[&[-3, -1, 0]], -2) }", "2"),
     T("nested_empty", "[[], [[]]]", "{ " + METER_NEW + " (m.record_nested(&[Item::Many(vec![]), Item::Many(vec![Item::Many(vec![])])]), m.readings.len()) }", "(0, 0)"),
     T("nested_sum_is_i64", "[i32::MAX, i32::MAX]", "{ " + METER_NEW + " m.record_nested(&[Item::One(i32::MAX), Item::Many(vec![Item::One(i32::MAX)])]) }", "2 * i32::MAX as i64"),
     T("nested_order", "[[3, 1], 2]", "{ " + METER_NEW + " m.record_nested(&[Item::Many(vec![Item::One(3), Item::One(1)]), Item::One(2)]); m.readings }", "vec![3, 1, 2]"),
     T("record_count_carries_over", "batches [[11], [1], [12]], limit 10", "{ " + METER_NEW + " m.record(&[&[11], &[1], &[12]], 10); m.log }", '["batch 0: 1 above", "batch 1: 1 above", "batch 2: 2 above"].map(String::from).to_vec()'),
     r"""
     fn nest(depth: usize, leaf: i32) -> Item {
         let mut it = Item::One(leaf);
         for _ in 0..depth {
             it = Item::Many(vec![it]);
         }
         it
     }

     #[test]
     fn deep_and_wide() {
         let mut m = Meter { readings: vec![], offset: 1, log: vec![] };
         let items: Vec<Item> = (0..20_000).map(|i| nest(i % 5, i as i32)).collect();
         let s = m.record_nested(&items);
         m.calibrate();
         check!("20000 items nested up to 4 deep, then calibrate", (s, m.readings.len(), m.readings[19_999]), (199_990_000, 20_000, 20_000));
     }

     #[test]
     fn random_vs_model() {
         let mut rng = anneal_prelude::Rng::new(6212);
         for _ in 0..300 {
             let nb = rng.below(4);
             let mut batches: Vec<Vec<i32>> = Vec::new();
             for _ in 0..nb {
                 let len = rng.below(4);
                 batches.push(rng.vec(len, -5, 5));
             }
             let limit = rng.int(-3, 3) as i32;
             let offset = rng.int(-2, 2) as i32;
             let refs: Vec<&[i32]> = batches.iter().map(|b| b.as_slice()).collect();
             let mut m = Meter { readings: vec![], offset, log: vec![] };
             let n = m.record(&refs, limit);
             m.calibrate();
             let mut above = 0;
             let mut log = Vec::new();
             for (i, b) in batches.iter().enumerate() {
                 above += b.iter().filter(|&&x| x > limit).count();
                 log.push(format!("batch {i}: {above} above"));
             }
             let readings: Vec<i32> = batches.concat().iter().map(|x| x + offset).collect();
             check!(format!("batches {batches:?}, limit {limit}, offset {offset}"), (n, m.readings, m.log), (above, readings, log));
         }
     }
     """],
    [("rust", "In `calibrate`, the closure calls `self.offset()`, a method, so it captures all of `self` while `self.readings` is borrowed mutably. A closure that reads the field `self.offset` captures only that field (edition 2021)."),
     ("rust", "In `record`, `add` holds `&mut above` for as long as `add` lives, and it lives until its last call in the next batch. Could each batch get its own closure?"),
     ("rust", "`walk(inner, f)` moves `f` in a loop. `walk(inner, &mut f)` compiles, but each level instantiates `walk` with one more `&mut`: `walk::<&mut &mut &mut F>`, without end. Make `walk` take `f: &mut F` so every level passes the same type.")],
    ("""A closure's captures are borrows that last as long as the closure. `calibrate`'s closure calls a method on `self`, which captures `self` whole; since edition 2021, a closure that names a field (`self.offset`) captures only that path, so it's disjoint from `self.readings`. In `record`, `add` mutably borrows `above` until its last use, which the loop puts in the next batch, after the read in `format!`. Creating the closure inside the loop ends its borrow each time; `self.log.push` never conflicted, because `add` captures `self.readings`, not `self`.

`walk` moves `f` into the recursive call. `&mut f` fixes the move (`&mut F` implements `FnMut` too), but the recursion is then polymorphic: `walk::<F>` calls `walk::<&mut F>`, which calls `walk::<&mut &mut F>`, and monomorphization never ends. Taking `f: &mut F` keeps one type at every depth, and passing `f` down is an implicit reborrow.

Syntax to remember: `fn walk<F: FnMut(i32)>(items: &[Item], f: &mut F)` · `walk(items, &mut |x| { .. })` · `|r| *r += self.offset` (a field, not a method).""", "O(n)", "O(depth) stack"),
    "`&mut dyn FnMut(i32)` would also fix `walk`. What does it cost compared with `&mut F`?",
    ["A closure keeps its captures borrowed for as long as it lives.", "Edition 2021 closures capture field paths, not all of `self`.", "Recursing with `&mut f` on a generic `F` never stops instantiating; take `&mut F`."],
    rules=dict(methods=["clone", "collect", "to_vec"], types=["Cell", "RefCell"]),
    wrong=dict(
        count_per_batch=sub(sub(METER_SOLUTION, "        let mut above = 0;\n        for (i, batch) in batches.iter().enumerate() {\n            let mut add",
                                "        let mut total = 0;\n        for (i, batch) in batches.iter().enumerate() {\n            let mut above = 0;\n            let mut add"),
                            "            self.log.push(format!(\"batch {i}: {above} above\"));\n        }\n        above\n", "            self.log.push(format!(\"batch {i}: {above} above\"));\n            total += above;\n        }\n        total\n"),
        calibrate_with_stale_offset=sub(METER_SOLUTION, "self.readings.iter_mut().for_each(|r| *r += self.offset);", "let offset = self.offset().max(0);\n        self.readings.iter_mut().for_each(|r| *r += offset);"),
        walk_skips_nested=sub(METER_SOLUTION, "            Item::Many(inner) => walk(inner, f),\n", "            Item::Many(inner) => {\n                if let Some(Item::One(x)) = inner.first() {\n                    f(*x);\n                }\n            }\n"),
    ),
))

LIST_HEAD = r"""
pub struct Node {
    pub val: i32,
    pub next: Option<Box<Node>>,
}

/// A singly linked list. Lists can be long, so nothing here may recurse.
pub struct List {
    head: Option<Box<Node>>,
}

impl List {
    pub fn from_slice(xs: &[i32]) -> Self {
        let mut head = None;
        for &val in xs.iter().rev() {
            head = Some(Box::new(Node { val, next: head }));
        }
        List { head }
    }

    pub fn to_vec(&self) -> Vec<i32> {
        let mut out = Vec::new();
        let mut cur = self.head.as_deref();
        while let Some(node) = cur {
            out.push(node.val);
            cur = node.next.as_deref();
        }
        out
    }
"""

LIST_TAIL = r"""
impl Drop for List {
    fn drop(&mut self) {
        let mut cur = self.head.take();
        while let Some(mut node) = cur {
            cur = node.next.take();
        }
    }
}
"""

LIST_DOCS = dict(
    push_back="    /// Appends `val` at the end.\n    pub fn push_back(&mut self, val: i32) {\n",
    insert="    /// Inserts `val` just before the first element greater than `val` (at the end if there's none), so a\n    /// sorted list stays sorted and `val` goes after any equal elements.\n    pub fn insert_sorted(&mut self, val: i32) {\n",
    remove="    /// Removes every element `pred` accepts and returns how many it removed. `pred` sees each element once,\n    /// in order.\n    pub fn remove_if(&mut self, mut pred: impl FnMut(i32) -> bool) -> usize {\n",
    last="    /// The last element, for editing.\n    pub fn last_mut(&mut self) -> Option<&mut i32> {\n",
)

LIST_BODIES = dict(
    push_back="""        let mut cur = &mut self.head;
        while let Some(node) = cur {
            cur = &mut node.next;
        }
        *cur = Some(Box::new(Node { val, next: None }));
""",
    insert="""        let mut cur = &mut self.head;
        while cur.as_ref().is_some_and(|node| node.val <= val) {
            cur = &mut cur.as_mut().unwrap().next;
        }
        let rest = cur.take();
        *cur = Some(Box::new(Node { val, next: rest }));
""",
    remove="""        let mut removed = 0;
        let mut cur = &mut self.head;
        loop {
            match cur {
                None => break,
                Some(node) if pred(node.val) => {
                    *cur = node.next.take();
                    removed += 1;
                }
                Some(node) => cur = &mut node.next,
            }
        }
        removed
""",
    last="""        let mut cur = self.head.as_deref_mut()?;
        while let Some(next) = cur.next.as_deref_mut() {
            cur = next;
        }
        Some(&mut cur.val)
""",
)


def list_src(bodies):
    out = LIST_HEAD
    for k in ("push_back", "insert", "remove", "last"):
        out += "\n" + LIST_DOCS[k] + bodies[k] + "    }\n"
    return out + "}\n" + LIST_TAIL


LIST_SOLUTION = list_src(LIST_BODIES)
LIST_STARTER = list_src({k: "        todo!()\n" for k in LIST_BODIES}).replace("mut pred: impl", "pred: impl")


def with_body(key, body):
    b = dict(LIST_BODIES)
    b[key] = body
    return list_src(b)


P.append(writep(
    "mut-cursor-loop", "&mut cursors in a loop", "medium", "reborrows", ["&mut in loops", "Option<Box<T>>", "NLL", "as_deref_mut"],
    """
        Write four methods of a singly linked list, each by walking a `&mut` cursor down the list: `push_back`,
        `insert_sorted`, `remove_if` and `last_mut`. Lists in the tests are long, so no recursion (that's also
        why `Drop` is written out).

        The shortest cursor loops for two of these are rejected by today's borrow checker even though they're
        sound. When that happens, rearrange the loop rather than reaching for `unsafe` or a second pass.
    """,
    LIST_STARTER,
    LIST_SOLUTION,
    [T("push_back", "[1, 2]; push_back 3", "{ let mut l = List::from_slice(&[1, 2]); l.push_back(3); l.to_vec() }", "vec![1, 2, 3]"),
     T("insert_sorted_middle", "[1, 3, 5]; insert_sorted 4", "{ let mut l = List::from_slice(&[1, 3, 5]); l.insert_sorted(4); l.to_vec() }", "vec![1, 3, 4, 5]"),
     T("insert_after_equal", "[5, 3]; insert_sorted 5", "{ let mut l = List::from_slice(&[5, 3]); l.insert_sorted(5); l.to_vec() }", "vec![5, 3, 5]"),
     T("remove_if_example", "[1, 2, 3, 4, 6]; remove even", "{ let mut l = List::from_slice(&[1, 2, 3, 4, 6]); let n = l.remove_if(|x| x % 2 == 0); (n, l.to_vec()) }", "(3, vec![1, 3])"),
     T("last_mut_example", "[7, 8, 9]; last += 100", "{ let mut l = List::from_slice(&[7, 8, 9]); *l.last_mut().unwrap() += 100; l.to_vec() }", "vec![7, 8, 109]"),
     T("empty_list", "[]", "{ let mut l = List::from_slice(&[]); (l.last_mut().is_none(), l.remove_if(|_| true), { l.insert_sorted(1); l.to_vec() }) }", "(true, 0, vec![1])")],
    [T("push_back_empty", "[]; push_back 1, 2", "{ let mut l = List::from_slice(&[]); l.push_back(1); l.push_back(2); l.to_vec() }", "vec![1, 2]"),
     T("insert_at_front", "[2, 3]; insert_sorted 1", "{ let mut l = List::from_slice(&[2, 3]); l.insert_sorted(1); l.to_vec() }", "vec![1, 2, 3]"),
     T("insert_at_end", "[1, 2]; insert_sorted 9", "{ let mut l = List::from_slice(&[1, 2]); l.insert_sorted(9); l.to_vec() }", "vec![1, 2, 9]"),
     T("insert_unsorted", "[1, 9, 2]; insert_sorted 5", "{ let mut l = List::from_slice(&[1, 9, 2]); l.insert_sorted(5); l.to_vec() }", "vec![1, 5, 9, 2]"),
     T("remove_all", "[4, 4, 4]; remove 4", "{ let mut l = List::from_slice(&[4, 4, 4]); (l.remove_if(|x| x == 4), l.to_vec(), l.last_mut().is_none()) }", "(3, vec![], true)"),
     T("remove_adjacent", "[1, 2, 2, 3, 2]; remove 2", "{ let mut l = List::from_slice(&[1, 2, 2, 3, 2]); let n = l.remove_if(|x| x == 2); (n, l.to_vec()) }", "(3, vec![1, 3])"),
     T("remove_sees_each_once_in_order", "[5, 6, 7, 8]; remove every other visited", "{ let mut l = List::from_slice(&[5, 6, 7, 8]); let mut seen = vec![]; let mut k = 0; let n = l.remove_if(|x| { seen.push(x); k += 1; k % 2 == 1 }); (n, l.to_vec(), seen) }", "(2, vec![6, 8], vec![5, 6, 7, 8])"),
     T("last_after_remove", "[1, 2, 3]; remove 3; last", "{ let mut l = List::from_slice(&[1, 2, 3]); l.remove_if(|x| x == 3); l.last_mut().copied() }", "Some(2)"),
     T("push_after_last_edit", "[1]; last = 5; push_back 6", "{ let mut l = List::from_slice(&[1]); *l.last_mut().unwrap() = 5; l.push_back(6); l.to_vec() }", "vec![5, 6]"),
     r"""
     #[test]
     fn random_vs_model() {
         let mut rng = anneal_prelude::Rng::new(6213);
         for _ in 0..300 {
             let n = rng.below(6);
             let start: Vec<i32> = rng.vec(n, 0, 5);
             let mut l = List::from_slice(&start);
             let mut model = start.clone();
             let mut ops = Vec::new();
             for _ in 0..6 {
                 let v = rng.int(0, 5) as i32;
                 match rng.below(4) {
                     0 => {
                         l.push_back(v);
                         model.push(v);
                         ops.push(format!("push_back {v}"));
                     }
                     1 => {
                         l.insert_sorted(v);
                         let at = model.iter().position(|&x| x > v).unwrap_or(model.len());
                         model.insert(at, v);
                         ops.push(format!("insert_sorted {v}"));
                     }
                     2 => {
                         let before = model.len();
                         model.retain(|&x| x != v);
                         ops.push(format!("remove_if(== {v})"));
                         check!(format!("{start:?}; {}", ops.join(", ")), l.remove_if(|x| x == v), before - model.len());
                     }
                     _ => {
                         if let Some(x) = l.last_mut() {
                             *x += 10;
                         }
                         if let Some(x) = model.last_mut() {
                             *x += 10;
                         }
                         ops.push("last += 10".to_string());
                     }
                 }
             }
             check!(format!("{start:?}; {}", ops.join(", ")), l.to_vec(), model);
         }
     }

     #[test]
     fn long_list() {
         let xs: Vec<i32> = (0..200_000).collect();
         let mut l = List::from_slice(&xs);
         l.insert_sorted(199_998);
         l.push_back(7);
         let removed = l.remove_if(|x| x % 2 == 1);
         *l.last_mut().unwrap() = -1;
         let v = l.to_vec();
         check!("0..200000; insert_sorted 199998; push_back 7; remove odd; last = -1", (removed, v.len(), v[99_999], v[100_000]), (100_001, 100_001, 199_998, -1));
     }
     """],
    [("rust", "The cursor is `let mut cur = &mut self.head;` (an `&mut Option<Box<Node>>`) and advancing is `cur = &mut node.next;`. When the loop ends, `*cur` is the slot to write into."),
     ("rust", "`while let Some(node) = cur { if stop { break; } cur = &mut node.next; }` is rejected: the borrow in `node` flows into `cur` on one path, so NLL keeps it alive on the `break` path too. Test first with a shared look (`cur.as_ref().is_some_and(..)`), then take the `&mut` only to advance."),
     ("rust", "For `remove_if`, a `match` with one arm per case (`None`, `Some(node) if pred(node.val)`, `Some(node)`) gives each arm its own borrow, so the removing arm can assign to `*cur`.")],
    ("""A `&mut` cursor is reborrowed on every step: `cur = &mut node.next` borrows through the old `cur`, which is never used again, so the chain of borrows stays linear. `push_back` and `last_mut` are the plain loop. The other two hit a limit of NLL: in `while let Some(node) = cur { if cond { break } cur = &mut node.next }` the borrow held by `node` must outlive `cur` on the advancing path, and NLL's regions don't distinguish paths, so after `break` `*cur` still counts as borrowed (E0499/E0506; Polonius accepts it). The workarounds keep the `&mut` borrow off the stopping path: check through a shared borrow first and reborrow only to advance (`cur = &mut cur.as_mut().unwrap().next`), or match with guards so each arm binds its own borrow.

Syntax to remember: `let mut cur = &mut self.head;` · `while cur.as_ref().is_some_and(|n| n.val <= val) { cur = &mut cur.as_mut().unwrap().next; }` · `*cur = Some(Box::new(Node { val, next: cur.take() }))` · `match cur { Some(node) if pred(node.val) => *cur = node.next.take(), Some(node) => cur = &mut node.next, None => break }`.""", "O(n) per operation", "O(1)"),
    "Why must `List` implement `Drop` by hand, when `Box` already frees its contents?",
    ["A `&mut` cursor advances by reborrowing through itself.", "NLL rejects a borrow that flows into the cursor on one path and must be dead on another; check first, then borrow.", "Match arms with guards bind separate borrows."],
    related=("L2", "D5"),
    wrong=dict(
        insert_before_equal=sub(LIST_SOLUTION, "node.val <= val", "node.val < val"),
        remove_first_only=sub(LIST_SOLUTION, "                    *cur = node.next.take();\n                    removed += 1;\n", "                    *cur = node.next.take();\n                    removed += 1;\n                    break;\n"),
        last_is_head=with_body("last", "        self.head.as_deref_mut().map(|n| &mut n.val)\n"),
    ),
))

SCRIPT_DOC = r"""
/// Runs these steps on `v` in order. "len" always means the length at that step.
///  1. push len
///  2. swap the first and last elements
///  3. insert a copy of the first element at index len / 2
///  4. add len to the last element
///  5. move the last element to the front
///  6. rotate left by len / 3
///  7. remove every element smaller than the first
///  8. log len
///  9. drop the last len / 4 elements
/// 10. pad with two copies of the last element
/// 11. append a copy of the first len / 2 elements
/// 12. log how many elements are greater than the first
"""

SCRIPT_STARTER = SCRIPT_DOC + r"""pub fn script(v: &mut Vec<i32>, log: &mut Vec<usize>) {
    v.push(v.len() as i32);
    v.swap(0, v.len() - 1);
    v.insert(v.len() / 2, v[0]);
    v[v.len() - 1] += v.len() as i32;
    v.insert(0, v.pop().unwrap());
    v.rotate_left(v.len() / 3);
    v.retain(|&x| x >= v[0]);
    log.push(v.len());
    v.truncate(v.len() - v.len() / 4);
    v.resize(v.len() + 2, v[v.len() - 1]);
    v.extend_from_within(..v.len() / 2);
    log.push(v.iter().filter(|&&x| x > v[0]).count());
}
"""

SCRIPT_SOLUTION = SCRIPT_DOC + r"""pub fn script(v: &mut Vec<i32>, log: &mut Vec<usize>) {
    v.push(v.len() as i32);
    let n = v.len();
    v.swap(0, n - 1);
    v.insert(v.len() / 2, v[0]);
    let n = v.len();
    v[n - 1] += n as i32;
    let last = v.pop().unwrap();
    v.insert(0, last);
    let n = v.len();
    v.rotate_left(n / 3);
    let first = v[0];
    v.retain(|&x| x >= first);
    log.push(v.len());
    v.truncate(v.len() - v.len() / 4);
    v.resize(v.len() + 2, v[v.len() - 1]);
    v.extend_from_within(..v.len() / 2);
    log.push(v.iter().filter(|&&x| x > v[0]).count());
}
"""


def script_py(v):
    v = list(v)
    log = []
    v.append(len(v))
    v[0], v[-1] = v[-1], v[0]
    v.insert(len(v) // 2, v[0])
    v[-1] += len(v)
    last = v.pop()
    v.insert(0, last)
    k = len(v) // 3
    v = v[k:] + v[:k]
    first = v[0]
    v = [x for x in v if x >= first]
    log.append(len(v))
    v = v[:len(v) - len(v) // 4]
    v += [v[-1]] * 2
    v += v[:len(v) // 2]
    log.append(sum(1 for x in v if x > v[0]))
    return v, log


def script_case(name, v):
    after, log = script_py(v)
    rv = "vec![" + ", ".join(map(str, v)) + "]" if v else "Vec::<i32>::new()"
    return T(name, f"script({v})", f"{{ let mut v: Vec<i32> = {rv}; let mut log = Vec::new(); script(&mut v, &mut log); (v, log) }}",
             f"(vec![{', '.join(map(str, after))}], vec![{', '.join(map(str, log))}])")


P.append(fixp(
    "two-phase-borrows", "Fix: where two-phase borrows stop", "medium", "reborrows", ["two-phase borrows", "E0502", "E0499", "DerefMut", "IndexMut"],
    """
        `script` doesn't compile, but not every suspicious-looking line is at fault: `v.push(v.len() as i32)`
        compiles, and so do several others that read `v` inside a call that mutates it. Fix only the lines the
        compiler rejects, keeping each step's meaning.
    """,
    SCRIPT_STARTER,
    SCRIPT_SOLUTION,
    [script_case("empty", []),
     script_case("one", [7]),
     script_case("three", [1, 2, 3]),
     script_case("descending", [9, 5, 1, 0]),
     script_case("negatives", [-4, 8, -2, 6, 0])],
    [script_case("zeros", [0, 0, 0]),
     script_case("two", [5, 5]),
     script_case("six", [3, 1, 4, 1, 5, 9]),
     script_case("big_first", [100, 1, 2, 3, 4, 5, 6]),
     script_case("all_negative", [-1, -2, -3, -4]),
     script_case("mixed_eight", [2, 7, 1, 8, 2, 8, 1, 8]),
     script_case("ten", list(range(10))),
     script_case("ten_desc", list(range(10, 0, -1))),
     r"""
     fn model(v: &mut Vec<i32>) -> Vec<usize> {
         let mut log = Vec::new();
         let n = v.len() as i32;
         v.push(n);
         let n = v.len();
         v.swap(0, n - 1);
         let (at, first) = (v.len() / 2, v[0]);
         v.insert(at, first);
         let n = v.len();
         v[n - 1] += n as i32;
         let last = v.pop().unwrap();
         v.insert(0, last);
         let n = v.len();
         v.rotate_left(n / 3);
         let first = v[0];
         v.retain(|&x| x >= first);
         log.push(v.len());
         let n = v.len();
         v.truncate(n - n / 4);
         let last = v[v.len() - 1];
         v.push(last);
         v.push(last);
         let half = v[..v.len() / 2].to_vec();
         v.extend(half);
         let first = v[0];
         log.push(v.iter().filter(|&&x| x > first).count());
         log
     }

     #[test]
     fn random_vs_model() {
         let mut rng = anneal_prelude::Rng::new(6214);
         for _ in 0..400 {
             let n = rng.below(12);
             let start: Vec<i32> = rng.vec(n, -20, 20);
             let mut want = start.clone();
             let want_log = model(&mut want);
             let mut got = start.clone();
             let mut log = Vec::new();
             script(&mut got, &mut log);
             check!(format!("script({start:?})"), (got, log), (want, want_log));
         }
     }
     """],
    [("rust", "A two-phase borrow reserves the `&mut` for an autoref'd method call, lets the arguments read the value, then activates the borrow. That's why `v.push(v.len())` compiles. Which of the failing calls aren't `Vec`'s own methods?"),
     ("rust", "`swap` and `rotate_left` are slice methods: `v.swap(..)` first calls `DerefMut::deref_mut(v)` to get a `&mut [i32]`, and that call is an ordinary `&mut` borrow. `v[i] += x` goes through `IndexMut` the same way."),
     ("rust", "Two-phase only lets arguments *read*. `v.pop()` needs `&mut v` itself, and a closure argument keeps its borrow for the whole call. Hoist what the arguments need into a `let` just before the line, not at the top: the length changes between steps.")],
    ("""Two-phase borrows are the special case that makes `v.push(v.len())` legal: for an autoref'd method receiver (and compound assignment on primitives), the `&mut v` is only *reserved* while the arguments are evaluated, and they may read `v` in that time. It stops at four things here. A method found through `Deref` (`swap`, `rotate_left`, `get_mut`, `sort` are `[T]`'s methods, so `deref_mut` runs first and activates the borrow). An overloaded index (`v[v.len() - 1] += ..` calls `index_mut(&mut v, ..)` before the index is known). An argument that needs `&mut v` itself (`v.insert(0, v.pop().unwrap())`). And a closure argument (`retain(|&x| x >= v[0])`), which holds its borrow for the whole call. `Vec`'s own methods (`push`, `insert`, `truncate`, `resize`, `extend_from_within`) work, as does anything that mutates a *different* value (`log.push(..)`).

The trap in the fix is hoisting one `let n = v.len()` to the top: steps 1, 3 and 5 change the length.""", "O(n) per step", "O(1) extra"),
    "`v.swap(0, v.len() - 1)` compiles when `v: &mut [i32]` and fails when `v: &mut Vec<i32>`. Why?",
    ["Two-phase borrows: reserve the receiver's `&mut`, let arguments read, then activate.", "They don't cover `DerefMut` autoderef, `IndexMut`, `&mut` arguments or closures.", "Hoist a value just before the line that needs it."],
    rules=dict(methods=["clone", "to_vec"], lines=12),
    wrong=dict(
        length_hoisted_once=sub(sub(SCRIPT_SOLUTION, "    let n = v.len();\n    v[n - 1] += n as i32;\n", "    v[n - 1] += n as i32;\n"), "    let n = v.len();\n    v.rotate_left(n / 3);\n", "    v.rotate_left(n / 3);\n"),
        first_read_before_rotating=sub(SCRIPT_SOLUTION, "    let n = v.len();\n    v.rotate_left(n / 3);\n    let first = v[0];\n", "    let first = v[0];\n    let n = v.len();\n    v.rotate_left(n / 3);\n"),
        last_to_front_by_swap=sub(SCRIPT_SOLUTION, "    let last = v.pop().unwrap();\n    v.insert(0, last);\n", "    let n = v.len();\n    v.swap(0, n - 1);\n"),
    ),
))

ROUND_HEAD = r"""
use std::fmt::Write;

#[derive(Debug, PartialEq)]
pub struct Player {
    pub name: String,
    pub score: u32,
}

/// Appends `line` and a newline to any text sink, taken by value.
fn record<W: Write>(mut log: W, line: &str) {
    writeln!(log, "{line}").expect("writing to a String can't fail");
}

/// One round of a game. It borrows the players and the log from the caller for `'a`.
pub struct Round<'a> {
    players: &'a mut [Player],
    log: &'a mut String,
}
"""

ROUND_STARTER = ROUND_HEAD + r"""
impl<'a> Round<'a> {
    pub fn new(players: &'a mut [Player], log: &'a mut String) -> Self {
        Round { players, log }
    }

    /// Moves up to `points` from player `from` to player `to` (never more than `from` has), logs
    /// "<from's name> -> <to's name>: <moved>", and returns how many points moved.
    pub fn transfer(&mut self, from: usize, to: usize, points: u32) -> u32 {
        let a = &mut self.players[from];
        let b = &mut self.players[to];
        let moved = points.min(a.score);
        a.score -= moved;
        b.score += moved;
        record(self.log, &format!("{} -> {}: {moved}", a.name, b.name));
        moved
    }

    /// Renames player `i` and logs "<old> is now <new>".
    pub fn rename(&mut self, i: usize, new: &str) {
        let p = &mut self.players[i];
        let old = std::mem::replace(&mut p.name, new.to_string());
        record(self.log, &format!("{old} is now {}", p.name));
    }

    /// Ends the round: logs "round over" and hands the players back for the rest of `'a`.
    pub fn finish(&mut self) -> &'a mut [Player] {
        record(self.log, "round over");
        self.players
    }
}
"""

ROUND_SOLUTION = ROUND_HEAD + r"""
impl<'a> Round<'a> {
    pub fn new(players: &'a mut [Player], log: &'a mut String) -> Self {
        Round { players, log }
    }

    /// Moves up to `points` from player `from` to player `to` (never more than `from` has), logs
    /// "<from's name> -> <to's name>: <moved>", and returns how many points moved.
    pub fn transfer(&mut self, from: usize, to: usize, points: u32) -> u32 {
        let moved = points.min(self.players[from].score);
        self.players[from].score -= moved;
        self.players[to].score += moved;
        let (a, b) = (&self.players[from], &self.players[to]);
        record(&mut *self.log, &format!("{} -> {}: {moved}", a.name, b.name));
        moved
    }

    /// Renames player `i` and logs "<old> is now <new>".
    pub fn rename(&mut self, i: usize, new: &str) {
        let p = &mut self.players[i];
        let old = std::mem::replace(&mut p.name, new.to_string());
        record(&mut *self.log, &format!("{old} is now {}", p.name));
    }

    /// Ends the round: logs "round over" and hands the players back for the rest of `'a`.
    pub fn finish(self) -> &'a mut [Player] {
        record(self.log, "round over");
        self.players
    }
}
"""

ROUND_SETUP = 'let mut players = vec![Player { name: "ann".into(), score: 10 }, Player { name: "bo".into(), score: 3 }];\nlet mut log = String::new();'

P.append(fixp(
    "fix-two-mut-into-players", "Fix: a struct of &mut: reborrow, sequence, hand back", "medium", "reborrows", ["E0499", "E0507", "reborrow", "&mut fields", "mem::replace"],
    """
        `Round` holds two `&mut` borrowed from its caller, and none of its methods compiles. Fix them. After
        `finish`, the caller must be able to keep using the players for as long as the original borrow lasts,
        even once the `Round` itself is gone. Transferring from a player to the same player is allowed (it
        moves nothing but is logged).
    """,
    ROUND_STARTER,
    ROUND_SOLUTION,
    [T("transfer_and_finish", "ann 10, bo 3; transfer 0 -> 1, 4; finish", "(ps.iter().map(|p| p.score).collect::<Vec<_>>(), moved)", "(vec![6, 7], 4)",
       setup=ROUND_SETUP + "\nlet (ps, moved) = {\n    let mut r = Round::new(&mut players, &mut log);\n    let moved = r.transfer(0, 1, 4);\n    (r.finish(), moved)\n};"),
     T("log_lines", "ann 10, bo 3; transfer 1 -> 0, 3; rename 1 to \"cy\"; finish", "log", '"bo -> ann: 3\\nbo is now cy\\nround over\\n".to_string()',
       setup=ROUND_SETUP + '\n{\n    let mut r = Round::new(&mut players, &mut log);\n    r.transfer(1, 0, 3);\n    r.rename(1, "cy");\n    r.finish();\n}'),
     T("transfer_is_capped", "ann 10, bo 3; transfer 1 -> 0, 50", "(moved, players[0].score, players[1].score)", "(3, 13, 0)",
       setup=ROUND_SETUP + "\nlet moved = Round::new(&mut players, &mut log).transfer(1, 0, 50);"),
     T("same_player", "ann 10; transfer 0 -> 0, 5", "(moved, players[0].score, log)", '(5, 10, "ann -> ann: 5\\n".to_string())',
       setup=ROUND_SETUP + "\nlet moved = Round::new(&mut players, &mut log).transfer(0, 0, 5);"),
     T("players_outlive_the_round", "finish, then edit the players through the returned slice", "(players[0].name.clone(), players[1].score)", '("zed".to_string(), 99)',
       setup=ROUND_SETUP + '\nlet ps = Round::new(&mut players, &mut log).finish();\nps[0].name = "zed".to_string();\nps[1].score = 99;')],
    [T("zero_points", "transfer 0 -> 1, 0", "(moved, players[0].score, log)", '(0, 10, "ann -> bo: 0\\n".to_string())', setup=ROUND_SETUP + "\nlet moved = Round::new(&mut players, &mut log).transfer(0, 1, 0);"),
     T("from_empty_player", "bo 0; transfer 1 -> 0, 5", "(moved, players[0].score)", "(0, 10)", setup=ROUND_SETUP + "\nplayers[1].score = 0;\nlet moved = Round::new(&mut players, &mut log).transfer(1, 0, 5);"),
     T("exact_balance", "transfer 1 -> 0, 3", "(moved, players[1].score)", "(3, 0)", setup=ROUND_SETUP + "\nlet moved = Round::new(&mut players, &mut log).transfer(1, 0, 3);"),
     T("rename_twice", "rename 0 to x, then y", "(players[0].name.clone(), log)", '("y".to_string(), "ann is now x\\nx is now y\\n".to_string())',
       setup=ROUND_SETUP + '\n{\n    let mut r = Round::new(&mut players, &mut log);\n    r.rename(0, "x");\n    r.rename(0, "y");\n}'),
     T("rename_empty", "rename 1 to \"\"", "log", '"bo is now \\n".to_string()', setup=ROUND_SETUP + '\nRound::new(&mut players, &mut log).rename(1, "");'),
     T("log_is_appended", "log starts \"start\\n\"; finish", "log", '"start\\nround over\\n".to_string()', setup=ROUND_SETUP + '\nlog.push_str("start\\n");\nRound::new(&mut players, &mut log).finish();'),
     T("transfer_after_rename_uses_new_name", "rename 0 to \"al\"; transfer 0 -> 1, 1", "log", '"ann is now al\\nal -> bo: 1\\n".to_string()',
       setup=ROUND_SETUP + '\n{\n    let mut r = Round::new(&mut players, &mut log);\n    r.rename(0, "al");\n    r.transfer(0, 1, 1);\n}'),
     T("no_log_without_calls", "new round, dropped", "log.len()", "0", setup=ROUND_SETUP + "\nlet _ = Round::new(&mut players, &mut log);"),
     r"""
     #[test]
     fn random_vs_model() {
         let mut rng = anneal_prelude::Rng::new(6215);
         for _ in 0..300 {
             let n = 1 + rng.below(4);
             let start: Vec<u32> = rng.vec(n, 0, 9);
             let mut players: Vec<Player> = start.iter().enumerate().map(|(i, &s)| Player { name: format!("p{i}"), score: s }).collect();
             let mut model = start.clone();
             let mut want_log = String::new();
             let mut log = String::new();
             let mut ops = Vec::new();
             let mut moves = Vec::new();
             {
                 let mut r = Round::new(&mut players, &mut log);
                 for _ in 0..5 {
                     let (f, t, pts) = (rng.below(n), rng.below(n), rng.below(8) as u32);
                     let moved = pts.min(model[f]);
                     model[f] -= moved;
                     model[t] += moved;
                     want_log.push_str(&format!("p{f} -> p{t}: {moved}\n"));
                     ops.push(format!("transfer {f} -> {t}, {pts}"));
                     moves.push((r.transfer(f, t, pts), moved));
                 }
                 let ps = r.finish();
                 want_log.push_str("round over\n");
                 let got: Vec<u32> = ps.iter().map(|p| p.score).collect();
                 check!(format!("scores {start:?}; {}", ops.join(", ")), got, model.clone());
             }
             check!(format!("scores {start:?}; {}; moved and log", ops.join(", ")), (moves.iter().map(|m| m.0).collect::<Vec<_>>(), log), (moves.iter().map(|m| m.1).collect::<Vec<_>>(), want_log));
         }
     }
     """],
    [("rust", "`let a = &mut self.players[from]; let b = &mut self.players[to];` can't compile even for different indices, and `from == to` is allowed anyway. Do you need both at once? The scores are `u32`: read, then write each one in its own statement."),
     ("rust", "`record(self.log, ..)` tries to move the `&'a mut String` out of `*self`, which you only have through `&mut self` (E0507). `&mut *self.log` lends it for the call instead."),
     ("rust", "From `&mut self` you can only lend what's inside for as long as *that* borrow lasts, not for `'a`. To hand the players back for all of `'a`, `finish` has to take the `Round` by value.")],
    ("""A struct of `&'a mut` fields is a bundle of loans, and the rules for using them depend on how you hold the struct. Through `&mut self`, you can reborrow a field (`&mut *self.log`) for as long as `self` is borrowed, but you can't move it out: that's E0507, which a generic parameter like `record`'s `W` triggers because nothing reborrows implicitly there. Returning `&'a mut [Player]` from `&mut self` is impossible for the same reason: the longest reborrow you can make of `*self.players` is the lifetime of `&mut self`. Taking `self` by value owns the fields, so `finish(self)` can move `self.players` out with its full `'a`. The test that uses the players after the `Round` is gone checks exactly that.

`transfer` never needs two `&mut` at once: the scores are `Copy`, so compute `moved`, then update `from` and `to` in separate statements, which also makes `from == to` harmless. `split_at_mut` would need a special case for it. `rename` shows the disjoint case that does compile: `p` borrows `*self.players` while `&mut *self.log` borrows another field.""", "O(1) per call", "O(1)"),
    "`fn finish(&mut self) -> &mut [Player]` also compiles. Which caller code would it reject that `finish(self)` accepts?",
    ["Through `&mut self`, a `&mut` field can be reborrowed (`&mut *self.f`) but not moved out.", "Only a by-value `self` can hand a field back with its full lifetime.", "Sequence `Copy` reads and writes instead of holding two `&mut`."],
    rules=dict(methods=["clone", "swap", "take", "split_at_mut", "get_disjoint_mut"]),
    wrong=dict(
        uncapped=sub(sub(ROUND_SOLUTION, "let moved = points.min(self.players[from].score);", "let moved = points;"), "self.players[from].score -= moved;", "self.players[from].score = self.players[from].score.saturating_sub(moved);"),
        logs_to_before_from=sub(ROUND_SOLUTION, "let (a, b) = (&self.players[from], &self.players[to]);", "let (a, b) = (&self.players[to], &self.players[from]);"),
        finish_forgets_to_log=sub(ROUND_SOLUTION, "        record(self.log, \"round over\");\n        self.players", "        self.players"),
    ),
))

SINK_HEAD = r"""
pub trait Sink {
    fn put(&mut self, x: i32);
    /// How many values this sink has taken.
    fn len(&self) -> usize;
}

impl Sink for Vec<i32> {
    fn put(&mut self, x: i32) {
        self.push(x);
    }

    fn len(&self) -> usize {
        Vec::len(self)
    }
}

/// Counts values without keeping them.
pub struct Count(pub usize);

impl Sink for Count {
    fn put(&mut self, _: i32) {
        self.0 += 1;
    }

    fn len(&self) -> usize {
        self.0
    }
}

/// Sends every value to both sinks, `A` first.
pub struct Tee<A, B>(pub A, pub B);

impl<A: Sink, B: Sink> Sink for Tee<A, B> {
    fn put(&mut self, x: i32) {
        self.0.put(x);
        self.1.put(x);
    }

    fn len(&self) -> usize {
        self.0.len()
    }
}

/// Emits every value into `sink`. Like std's generic sinks, it takes the sink by value.
pub fn emit_all<S: Sink>(mut sink: S, xs: &[i32]) {
    for &x in xs {
        sink.put(x);
    }
}
"""

SINK_IMPLS = r"""
impl<S: Sink + ?Sized> Sink for &mut S {
    fn put(&mut self, x: i32) {
        (**self).put(x);
    }

    fn len(&self) -> usize {
        (**self).len()
    }
}

impl<S: Sink + ?Sized> Sink for Box<S> {
    fn put(&mut self, x: i32) {
        (**self).put(x);
    }

    fn len(&self) -> usize {
        (**self).len()
    }
}
"""

SINK_TAIL_STARTER = r"""
/// Emits `xs` into `sink` twice, then into `sink` and `count` together through a `Tee`. Returns how many values
/// `sink` holds afterwards.
pub fn pipeline(sink: &mut Vec<i32>, count: &mut Count, xs: &[i32]) -> usize {
    emit_all(sink, xs);
    emit_all(sink, xs);
    emit_all(Tee(sink, count), xs);
    sink.len()
}

/// Emits `xs` into every sink and returns their lengths afterwards.
pub fn fan_out(sinks: &mut [Box<dyn Sink>], xs: &[i32]) -> Vec<usize> {
    for s in sinks.iter_mut() {
        emit_all(s, xs);
    }
    sinks.iter().map(|s| s.len()).collect()
}
"""

SINK_TAIL_SOLUTION = sub(SINK_TAIL_STARTER, "    emit_all(sink, xs);\n    emit_all(sink, xs);\n    emit_all(Tee(sink, count), xs);", "    emit_all(&mut *sink, xs);\n    emit_all(&mut *sink, xs);\n    emit_all(Tee(&mut *sink, count), xs);")
SINK_SOLUTION = SINK_HEAD + SINK_IMPLS + SINK_TAIL_SOLUTION

P.append(fixp(
    "explicit-reborrow-generic-sink", "Lend a sink: impl Sink for &mut S", "medium", "reborrows", ["reborrow", "blanket impls", "?Sized", "Box<dyn Trait>"],
    """
        `emit_all` takes its sink by value, the way std's generic sinks and iterators do. `pipeline` and
        `fan_out` want to lend theirs instead, and don't compile. Make `&mut S` and `Box<S>` sinks for every
        sink `S`, trait objects included, the way std does for `io::Write` and `Iterator`. Then fix `pipeline`
        so it can still use `sink` after lending it.
    """,
    SINK_HEAD + "\n// TODO: Sink for &mut S and Box<S>.\n" + SINK_TAIL_STARTER,
    SINK_SOLUTION,
    [T("pipeline_example", "sink [], count 0, xs [7, 8]", "{ let (mut v, mut c) = (Vec::new(), Count(0)); let n = pipeline(&mut v, &mut c, &[7, 8]); (n, v, c.0) }", "(6, vec![7, 8, 7, 8, 7, 8], 2)"),
     T("fan_out_example", "sinks [Vec [1], Count(5)], xs [2, 3]", "{ let mut s: Vec<Box<dyn Sink>> = vec![Box::new(vec![1]), Box::new(Count(5))]; fan_out(&mut s, &[2, 3]) }", "vec![3, 7]"),
     T("lend_a_trait_object", "emit_all into a &mut dyn Sink, then read the Vec", "{ let mut v = vec![0]; { let d: &mut dyn Sink = &mut v; emit_all(d, &[4]); } v }", "vec![0, 4]"),
     T("box_is_a_sink", "emit_all into a Box<Count>", "{ let mut b = Box::new(Count(0)); emit_all(&mut b, &[1, 2, 3]); b.len() }", "3"),
     T("lend_twice", "emit_all(&mut v, [1]) twice", "{ let mut v = Vec::new(); emit_all(&mut v, &[1]); emit_all(&mut v, &[1]); v }", "vec![1, 1]")],
    [T("pipeline_empty", "xs []", "{ let (mut v, mut c) = (vec![9], Count(0)); (pipeline(&mut v, &mut c, &[]), c.0) }", "(1, 0)"),
     T("pipeline_keeps_existing", "sink [5], xs [1]", "{ let (mut v, mut c) = (vec![5], Count(1)); let n = pipeline(&mut v, &mut c, &[1]); (n, v, c.0) }", "(4, vec![5, 1, 1, 1], 2)"),
     T("fan_out_empty", "no sinks", "fan_out(&mut [], &[1])", "Vec::<usize>::new()"),
     T("nested_lending", "emit_all into &mut &mut Vec", "{ let mut v = Vec::new(); let mut r = &mut v; emit_all(&mut r, &[6]); emit_all(r, &[7]); v }", "vec![6, 7]"),
     T("box_dyn_by_value", "emit_all(Box<dyn Sink> by value) then nothing", "{ let b: Box<dyn Sink> = Box::new(Count(0)); let mut b = b; emit_all(&mut b, &[1]); emit_all(&mut b, &[2]); b.len() }", "2"),
     T("tee_of_lent_sinks", "Tee(&mut a, &mut b)", "{ let (mut a, mut b) = (Vec::new(), Count(0)); emit_all(Tee(&mut a, &mut b), &[1, 2]); (a, b.0) }", "(vec![1, 2], 2)"),
     T("tee_of_boxed", "Tee(Box<dyn Sink>, Count) through &mut", "{ let mut t = Tee(Box::new(vec![0]) as Box<dyn Sink>, Count(0)); emit_all(&mut t, &[3]); (t.0.len(), t.1.len()) }", "(2, 1)"),
     T("fan_out_repeated", "fan_out twice into [Count(0)]", "{ let mut s: Vec<Box<dyn Sink>> = vec![Box::new(Count(0))]; fan_out(&mut s, &[1, 1]); fan_out(&mut s, &[1]) }", "vec![3]"),
     r"""
     #[test]
     fn random_vs_model() {
         let mut rng = anneal_prelude::Rng::new(6216);
         for _ in 0..300 {
             let n = rng.below(6);
             let xs: Vec<i32> = rng.vec(n, -9, 9);
             let len = rng.below(3);
             let start: Vec<i32> = rng.vec(len, 0, 9);
             let c0 = rng.below(5);
             let mut v = start.clone();
             let mut c = Count(c0);
             let got = pipeline(&mut v, &mut c, &xs);
             let mut want = start.clone();
             for _ in 0..3 {
                 want.extend_from_slice(&xs);
             }
             check!(format!("sink {start:?}, count {c0}, xs {xs:?}"), (got, v, c.0), (want.len(), want, c0 + n));
         }
     }

     #[test]
     fn many_values() {
         let xs: Vec<i32> = (0..100_000).collect();
         let mut s: Vec<Box<dyn Sink>> = vec![Box::new(Vec::new()), Box::new(Count(0))];
         check!("fan_out 100000 values into [Vec, Count]", fan_out(&mut s, &xs), vec![100_000, 100_000]);
     }
     """],
    [("rust", "`impl<S: Sink + ?Sized> Sink for &mut S` forwards each method to the `S` behind the reference. Without `?Sized`, `S` can't be `dyn Sink`, so `&mut dyn Sink` wouldn't be a sink."),
     ("rust", "Inside that impl `self` is `&mut &mut S`. `self.put(x)` finds this very impl again and recurses forever; `(**self).put(x)` reaches the `S`."),
     ("rust", "With the impl in place, passing `sink` still moves the `&mut Vec<i32>`: the parameter is a generic `S`, so there's no implicit reborrow. `&mut *sink` lends a fresh one.")],
    ("""A function that takes a sink by value (`S: Sink`) can still be lent one, if `&mut S` is itself a sink: that's the blanket impl std writes for `io::Write`, `fmt::Write`, `Iterator`, `Hasher` and others. It forwards through `(**self)`, because `self.put(x)` on a `&mut &mut S` resolves to the same impl and recurses. `?Sized` lets `S` be `dyn Sink`, and a matching impl for `Box<S>` makes a `Box<dyn Sink>` a sink as well (so `&mut Box<dyn Sink>` is one too, which is what `fan_out` passes). Even with the impl, `emit_all(sink, xs)` moves `sink`, because implicit reborrows only happen where the parameter type is known to be `&mut`; `&mut *sink` lends it and leaves `sink` usable.

Syntax to remember: `impl<S: Sink + ?Sized> Sink for &mut S { fn put(&mut self, x: i32) { (**self).put(x) } }` · the same for `Box<S>` · `emit_all(&mut *sink, xs)`.""", "O(n)", "O(1)"),
    "Why does std implement `Iterator` for `&mut I` but not for `&I`?",
    ["A blanket `impl Trait for &mut T` lets by-value generic APIs borrow instead of consume.", "`(**self).method()` reaches the value behind `&mut &mut T`.", "`?Sized` admits trait objects."],
    related=("L2", "L4"),
    wrong=dict(
        box_counts_nothing=sub(SINK_SOLUTION, "impl<S: Sink + ?Sized> Sink for Box<S> {\n    fn put(&mut self, x: i32) {\n        (**self).put(x);\n    }\n\n    fn len(&self) -> usize {\n        (**self).len()\n    }",
                               "impl<S: Sink + ?Sized> Sink for Box<S> {\n    fn put(&mut self, x: i32) {\n        (**self).put(x);\n    }\n\n    fn len(&self) -> usize {\n        0\n    }"),
        tee_gets_a_copy=sub(SINK_SOLUTION, "emit_all(Tee(&mut *sink, count), xs);", "emit_all(Tee(Vec::new(), count), xs);"),
        mut_ref_puts_twice=sub(SINK_SOLUTION, "impl<S: Sink + ?Sized> Sink for &mut S {\n    fn put(&mut self, x: i32) {\n        (**self).put(x);\n    }",
                               "impl<S: Sink + ?Sized> Sink for &mut S {\n    fn put(&mut self, x: i32) {\n        if x != 0 {\n            (**self).put(x);\n        }\n    }"),
    ),
))

STEP_HEAD = r"""
/// Every `step`-th element of a slice, starting with the first, handed out as `&mut`.
pub struct StepMut<'a, T> {
    rest: &'a mut [T],
    step: usize,
}

/// `v[0], v[step], v[2 * step], ...` as `&mut`. Panics if `step` is 0.
pub fn step_mut<T>(v: &mut [T], step: usize) -> StepMut<'_, T> {
    assert!(step > 0, "step must be positive");
    StepMut { rest: v, step }
}
"""

STEP_STARTER = STEP_HEAD + r"""
impl<'a, T> Iterator for StepMut<'a, T> {
    type Item = &'a mut T;

    fn next(&mut self) -> Option<&'a mut T> {
        todo!()
    }

    /// Exact: how many elements are left.
    fn size_hint(&self) -> (usize, Option<usize>) {
        todo!()
    }
}

impl<T> DoubleEndedIterator for StepMut<'_, T> {
    fn next_back(&mut self) -> Option<Self::Item> {
        todo!()
    }
}

impl<T> ExactSizeIterator for StepMut<'_, T> {}
"""

STEP_SOLUTION = STEP_HEAD + r"""
impl<'a, T> Iterator for StepMut<'a, T> {
    type Item = &'a mut T;

    fn next(&mut self) -> Option<&'a mut T> {
        let rest = std::mem::take(&mut self.rest);
        let (first, tail) = rest.split_first_mut()?;
        let skip = (self.step - 1).min(tail.len());
        self.rest = &mut tail[skip..];
        Some(first)
    }

    /// Exact: how many elements are left.
    fn size_hint(&self) -> (usize, Option<usize>) {
        let n = self.rest.len().div_ceil(self.step);
        (n, Some(n))
    }
}

impl<T> DoubleEndedIterator for StepMut<'_, T> {
    fn next_back(&mut self) -> Option<Self::Item> {
        let rest = std::mem::take(&mut self.rest);
        if rest.is_empty() {
            return None;
        }
        let last = (rest.len() - 1) / self.step * self.step;
        let (init, tail) = rest.split_at_mut(last);
        self.rest = init;
        tail.first_mut()
    }
}

impl<T> ExactSizeIterator for StepMut<'_, T> {}
"""


P.append(writep(
    "stride-iter-mut", "An iterator that hands out &mut", "medium", "reborrows", ["IterMut", "mem::take", "split_first_mut", "reborrow lifetimes"],
    """
        Implement `next`, `size_hint` and `next_back` for `StepMut`, which yields every `step`-th element of a
        slice as `&mut`. The items must be able to live together (the tests collect them all and then write
        through each), and there's no `unsafe`.
    """,
    STEP_STARTER,
    STEP_SOLUTION,
    [T("every_other", "[1, 2, 3, 4, 5], step 2; add 10 to each", "{ let mut v = [1, 2, 3, 4, 5]; for x in step_mut(&mut v, 2) { *x += 10; } v }", "[11, 2, 13, 4, 15]"),
     T("items_live_together", "[1, 2, 3, 4], step 3; collect, then write through each", "{ let mut v = [1, 2, 3, 4]; let refs: Vec<&mut i32> = step_mut(&mut v, 3).collect(); for r in refs { *r = 0; } v }", "[0, 2, 3, 0]"),
     T("len_is_exact", "len of step_mut on 7 elements, steps 1, 2, 3, 7, 8", "{ let mut v = [0; 7]; (step_mut(&mut v, 1).len(), step_mut(&mut v, 2).len(), step_mut(&mut v, 3).len(), step_mut(&mut v, 7).len(), step_mut(&mut v, 8).len()) }", "(7, 4, 3, 1, 1)"),
     T("reversed", "[0, 1, 2, 3, 4, 5, 6], step 3, reversed", "{ let mut v = [0, 1, 2, 3, 4, 5, 6]; step_mut(&mut v, 3).rev().map(|x| *x).collect::<Vec<_>>() }", "vec![6, 3, 0]"),
     T("back_when_unaligned", "[0, 1, 2, 3, 4, 5], step 4: next_back", "{ let mut v = [0, 1, 2, 3, 4, 5]; step_mut(&mut v, 4).next_back().copied() }", "Some(4)"),
     T("empty", "[], step 2", "{ let mut v: [i32; 0] = []; let mut it = step_mut(&mut v, 2); (it.len(), it.next().is_none(), it.next_back().is_none()) }", "(0, true, true)")],
    [T("step_one", "[1, 2, 3], step 1", "{ let mut v = [1, 2, 3]; step_mut(&mut v, 1).map(|x| *x).collect::<Vec<_>>() }", "vec![1, 2, 3]"),
     T("step_larger_than_len", "[5, 6], step 10", "{ let mut v = [5, 6]; step_mut(&mut v, 10).map(|x| *x).collect::<Vec<_>>() }", "vec![5]"),
     T("both_ends_meet", "[0..9], step 2: next, next_back, next, next_back, next, next", "{ let mut v = [0, 1, 2, 3, 4, 5, 6, 7, 8]; let mut it = step_mut(&mut v, 2); let a = [it.next().copied(), it.next_back().copied(), it.next().copied(), it.next_back().copied(), it.next().copied(), it.next().copied()]; a }", "[Some(0), Some(8), Some(2), Some(6), Some(4), None]"),
     T("len_after_next_back", "[0..10], step 3: next_back then len", "{ let mut v = [0; 10]; let mut it = step_mut(&mut v, 3); it.next_back(); it.len() }", "3"),
     T("len_after_next", "[0..10], step 3: next then len", "{ let mut v = [0; 10]; let mut it = step_mut(&mut v, 3); it.next(); it.len() }", "3"),
     T("strings", "[\"a\", \"b\", \"c\"], step 2: push '!'", '{ let mut v = ["a", "b", "c"].map(String::from); for s in step_mut(&mut v, 2) { s.push(\'!\'); } v }', '["a!", "b", "c!"].map(String::from)'),
     T("single", "[9], step 1: next_back, then next", "{ let mut v = [9]; let mut it = step_mut(&mut v, 1); (it.next_back().copied(), it.next().is_none()) }", "(Some(9), true)"),
     T("zip_two_iterators", "swap v[0,2,4] with v[1,3,5] via split_at_mut halves", "{ let mut v = [1, 2, 3, 4, 5, 6]; let (a, b) = v.split_at_mut(3); for (x, y) in step_mut(a, 1).zip(step_mut(b, 1)) { std::mem::swap(x, y); } v }", "[4, 5, 6, 1, 2, 3]"),
     r"""
     #[test]
     fn step_zero_panics() {
         let mut v = [1, 2];
         let r = std::panic::catch_unwind(move || step_mut(&mut v, 0).count());
         check!("step_mut(.., 0) panics", r.is_err(), true);
     }

     #[test]
     fn random_vs_model() {
         let mut rng = anneal_prelude::Rng::new(6217);
         for _ in 0..400 {
             let n = rng.below(12);
             let step = 1 + rng.below(5);
             let v: Vec<i32> = (0..n as i32).collect();
             let mut left: Vec<i32> = v.iter().copied().step_by(step).collect();
             let mut got_v = v.clone();
             let mut it = step_mut(&mut got_v, step);
             let mut ops = Vec::new();
             for _ in 0..6 {
                 let back = rng.bool();
                 let want = if back { left.pop() } else if left.is_empty() { None } else { Some(left.remove(0)) };
                 let got = if back { it.next_back() } else { it.next() };
                 ops.push(if back { "next_back" } else { "next" });
                 let got = got.map(|x| {
                     let seen = *x;
                     *x = -1;
                     seen
                 });
                 check!(format!("0..{n}, step {step}: {}", ops.join(", ")), (got, it.len()), (want, left.len()));
             }
         }
     }

     #[test]
     fn big_slice() {
         let mut v: Vec<u32> = (0..1_000_000).collect();
         for x in step_mut(&mut v, 1000) {
             *x = 7;
         }
         let n = step_mut(&mut v, 3).len();
         check!("1000000 elements: step 1000 writes, then len at step 3", (n, v[999_000], v[999_001]), (333_334, 7, 999_001));
     }
     """],
    [("rust", "`self.rest.split_first_mut()` in `next` reborrows through `&mut self`, so the pieces live only as long as that call's borrow of `self`, not `'a` (\"lifetime may not live long enough\"). You need to move the `&'a mut [T]` out of `self`, not borrow it."),
     ("rust", "`&mut [T]` implements `Default` (the empty slice), so `std::mem::take(&mut self.rest)` moves the full-lifetime slice out and leaves an empty one. Split what you took, keep one piece, and put the rest back."),
     ("rust", "From the back, the last element this iterator would yield is at `(len - 1) / step * step`, not necessarily `len - 1`.")],
    ("""`next(&mut self) -> Option<&'a mut T>` promises items that outlive the `&mut self` borrow. Reborrowing `self.rest` can't deliver that: a reborrow of `*self.rest` through `&mut self` is limited to that borrow, or two calls to `next` could return aliasing `&mut`s. Moving the `&'a mut [T]` out of `self` is allowed: `mem::take` swaps in the empty slice and returns the original with its full `'a`. Split it into the item and the remainder (`split_first_mut`, or `split_at_mut` from the back), then store the remainder back. Each item is carved off and never reachable from the iterator again, which is why `collect()`ing them all is sound. std's `slice::IterMut` does the same with raw pointers.

Syntax to remember: `let rest = std::mem::take(&mut self.rest);` · `let (first, tail) = rest.split_first_mut()?;` · `self.rest = &mut tail[skip..];` · `len.div_ceil(step)`.""", "O(1) per item", "O(1)"),
    "Why can't you write a `windows_mut` iterator in this style, when `chunks_mut` works?",
    ["A reborrow through `&mut self` can't be returned with the outer lifetime `'a`.", "`mem::take` moves a `&'a mut [T]` out of a field (the empty slice is its default).", "Split, keep one piece, store the rest back."],
    related=("L2", "L3"),
    wrong=dict(
        skips_one_too_many=sub(STEP_SOLUTION, "let skip = (self.step - 1).min(tail.len());", "let skip = self.step.min(tail.len());"),
        size_hint_rounds_down=sub(STEP_SOLUTION, "let n = self.rest.len().div_ceil(self.step);", "let n = self.rest.len() / self.step;"),
        back_from_the_very_end=sub(STEP_SOLUTION, "let last = (rest.len() - 1) / self.step * self.step;", "let last = rest.len() - 1;"),
    ),
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
    # The hand-written problem keeps its files, but its position follows the spec.
    import os
    import re
    from author import ROOT
    toml = os.path.join(ROOT, "l2-borrowing", "problems", "two-mutable-borrows-of-self", "problem.toml")
    pos = [p["slug"] for p in P].index("two-mutable-borrows-of-self") + 1
    if os.path.exists(toml):
        text = open(toml).read()
        open(toml, "w").write(re.sub(r"(?m)^order = \d+$", f"order = {pos}", text))
    print("L2", n)
