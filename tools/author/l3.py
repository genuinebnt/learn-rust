from author import T, write_track

P = []


def fix(slug, title, level, stage, tags, statement, starter, solution, visible, hidden, hints, notes, follow_up, teaches, rules=None, related=("L3",), wrong=None):
    return dict(slug=slug, title=title, mode="fix", level=level, stage=stage, tags=tags, statement=statement, starter=starter,
                solution=solution, visible=visible, hidden=hidden, hints=hints, notes=notes, follow_up=follow_up,
                teaches=teaches, rules=rules, related=list(related), wrong=wrong)


def write(slug, title, level, stage, tags, statement, starter, solution, visible, hidden, hints, notes, follow_up, teaches, related=("L3",), source=None, examples=(), wrong=None):
    return dict(slug=slug, title=title, level=level, stage=stage, tags=tags, statement=statement, starter=starter,
                solution=solution, visible=visible, hidden=hidden, hints=hints, notes=notes, follow_up=follow_up,
                teaches=teaches, related=list(related), source=source, examples=list(examples), wrong=wrong)


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


# ---------------------------------------------------------------- elision (easy)

GLOSS_HEAD = r"""
use std::collections::HashMap;

pub struct Glossary {
    terms: HashMap<String, String>,
}

/// The first word of `text`: everything before the first space.
pub fn first_word(text: &str) -> &str {
    text.split(' ').next().unwrap_or("")
}
"""

GLOSS_STARTER = GLOSS_HEAD + r"""
impl Glossary {
    pub fn new(pairs: &[(&str, &str)]) -> Self {
        Glossary { terms: pairs.iter().map(|&(w, d)| (w.to_string(), d.to_string())).collect() }
    }

    /// The definition of `word`.
    pub fn define(&self, word: &str) -> Option<&str> {
        self.terms.get(word).map(String::as_str)
    }

    /// The definition of `word`, or `word` itself when the glossary doesn't have it.
    pub fn define_or_echo(&self, word: &str) -> &str {
        self.define(word).unwrap_or(word)
    }

    /// Whichever of `a` and `b` has the longer definition (`a` on a tie; no definition counts as length 0).
    pub fn pick(&self, a: &str, b: &str) -> &str {
        let len = |w: &str| self.define(w).map_or(0, str::len);
        if len(b) > len(a) {
            b
        } else {
            a
        }
    }
}

/// The definition of the first word of `text`.
pub fn define_first(g: &Glossary, text: &str) -> Option<&str> {
    g.define(first_word(text))
}
"""

GLOSS_SOLUTION = GLOSS_STARTER
for _old, _new in [
    ("    pub fn define_or_echo(&self, word: &str) -> &str {", "    pub fn define_or_echo<'a>(&'a self, word: &'a str) -> &'a str {"),
    ("    pub fn pick(&self, a: &str, b: &str) -> &str {", "    pub fn pick<'w>(&self, a: &'w str, b: &'w str) -> &'w str {"),
    ("pub fn define_first(g: &Glossary, text: &str) -> Option<&str> {", "pub fn define_first<'g>(g: &'g Glossary, text: &str) -> Option<&'g str> {"),
]:
    GLOSS_SOLUTION = sub(GLOSS_SOLUTION, _old, _new)

G = 'let g = Glossary::new(&[("rust", "a language"), ("borrow", "a loan"), ("ok", "fine")]);'
GD = 'glossary {rust: "a language", borrow: "a loan", ok: "fine"}'

P.append(fix(
    "when-elision-picks-self", "Fix: which input the elided lifetime picks", "easy", "elision", ["elision rules", "E0106", "&self"],
    """
        Three signatures here don't compile, or compile to something callers can't use, because elision picked
        the wrong input for the output to borrow from. Fix them by writing the lifetimes that say what each
        output really borrows. The tests keep results after the other inputs are gone. `define` and
        `first_word` are right as they are.
    """,
    GLOSS_STARTER,
    GLOSS_SOLUTION,
    [T("define_or_echo_example", GD + "; define_or_echo rust, go", '(g.define_or_echo("rust"), g.define_or_echo("go"))', '("a language", "go")', setup=G),
     T("pick_outlives_the_glossary", GD + "; pick(ok, borrow), then drop the glossary", "w", '"borrow"', setup=G + '\nlet (a, b) = (String::from("ok"), String::from("borrow"));\nlet w = g.pick(&a, &b);\ndrop(g);'),
     T("define_first_outlives_the_text", GD + "; define_first of a temporary \"rust is fun\"", "d", 'Some("a language")', setup=G + '\nlet d = define_first(&g, &String::from("rust is fun"));'),
     T("pick_tie_goes_to_a", GD + "; pick(zzz, yyy): neither defined", 'g.pick("zzz", "yyy")', '"zzz"', setup=G),
     T("echo_of_a_temporary", GD + "; define_or_echo of a word that's dropped after the call", "s", '"x".to_string()', setup=G + '\nlet s = g.define_or_echo(&String::from("x")).to_string();'),
     T("first_word_example", "first_word(\"hello world\"), first_word(\"\")", '(first_word("hello world"), first_word(""))', '("hello", "")')],
    [T("define_missing", GD + "; define go", 'g.define("go")', "None", setup=G),
     T("pick_longer_second", GD + "; pick(ok, rust)", 'g.pick("ok", "rust")', '"rust"', setup=G),
     T("pick_equal_definitions", "glossary {a: \"xx\", b: \"yy\"}; pick(b, a)", 'g.pick("b", "a")', '"b"', setup='let g = Glossary::new(&[("a", "xx"), ("b", "yy")]);'),
     T("define_first_unknown", GD + "; define_first(\"go fast\")", 'define_first(&g, "go fast")', "None", setup=G),
     T("define_first_leading_space", GD + "; define_first(\" rust\")", 'define_first(&g, " rust")', "None", setup=G),
     T("empty_glossary", "empty glossary; define_or_echo \"\"", 'g.define_or_echo("")', '""', setup="let g = Glossary::new(&[]);"),
     T("echo_empty_definition", "glossary {e: \"\"}; define_or_echo e", 'g.define_or_echo("e")', '""', setup='let g = Glossary::new(&[("e", "")]);'),
     T("unicode", "glossary {日本: \"Japan\"}; define_first(\"日本 語\")", 'define_first(&g, "日本 語")', 'Some("Japan")', setup='let g = Glossary::new(&[("日本", "Japan")]);'),
     r"""
     #[test]
     fn random_vs_model() {
         let mut rng = anneal_prelude::Rng::new(6301);
         let words = ["a", "b", "c", "d"];
         for _ in 0..300 {
             let mut defs: Vec<(String, String)> = Vec::new();
             for w in words {
                 if rng.bool() {
                     let len = rng.below(4);
                     defs.push((w.to_string(), rng.string(len, "xy")));
                 }
             }
             let pairs: Vec<(&str, &str)> = defs.iter().map(|(w, d)| (w.as_str(), d.as_str())).collect();
             let g = Glossary::new(&pairs);
             let def = |w: &str| defs.iter().find(|e| e.0 == w).map(|e| e.1.clone());
             let (a, b) = (rng.pick(&words).to_string(), rng.pick(&words).to_string());
             let la = def(&a).map_or(0, |d| d.len());
             let lb = def(&b).map_or(0, |d| d.len());
             let want = if lb > la { b.clone() } else { a.clone() };
             check!(format!("defs {defs:?}; pick({a}, {b})"), g.pick(&a, &b).to_string(), want);
             check!(format!("defs {defs:?}; define_or_echo({a})"), g.define_or_echo(&a).to_string(), def(&a).unwrap_or(a.clone()));
             let text = format!("{b} {a}");
             check!(format!("defs {defs:?}; define_first({text:?})"), define_first(&g, &text).map(String::from), def(&b));
         }
     }
     """],
    [("rust", "The elision rules: each elided input lifetime is a separate parameter; with exactly one input lifetime, outputs get it; with `&self` or `&mut self`, outputs get `self`'s. Otherwise you must write it (E0106)."),
     ("rust", "`pick` returns `a` or `b`, never the glossary's data, but rule 3 ties its output to `&self`. `define_or_echo` can return either, so both inputs need the same lifetime."),
     ("rust", "`define_first` has two reference inputs and no `self`: elision gives up. The result comes from the glossary.")],
    ("""Elision only fills in the common cases, and it looks at the signature, not the body. Rule 1: each elided lifetime in the inputs is its own parameter. Rule 2: if there's exactly one input lifetime, every elided output lifetime is that one (`first_word`). Rule 3: if there's `&self` or `&mut self`, outputs get `self`'s lifetime (`define`). Anything else needs names. `pick` compiles only if its output is tied to `a` and `b`; rule 3 would tie it to `self` and reject returning `a`. `define_or_echo` may return data from either `self` or `word`, so both must share `'a`. `define_first` must say the result borrows from `g`, not `text`: the tests drop the text first.

Syntax to remember: `fn pick<'w>(&self, a: &'w str, b: &'w str) -> &'w str` · `fn define_or_echo<'a>(&'a self, word: &'a str) -> &'a str` · `fn define_first<'g>(g: &'g Glossary, text: &str) -> Option<&'g str>`.""", "O(1) expected per lookup", "O(1)"),
    "Rule 3 favours `self` even when a method returns data from an argument. Why was that the right default for the language?",
    ["The three elision rules.", "Name the lifetime of the input the output really borrows from.", "Tying outputs to too many inputs is also wrong."],
    rules=dict(methods=["clone", "to_owned", "leak"], lines=4),
    wrong=dict(
        pick_tie_goes_to_b=sub(GLOSS_SOLUTION, "if len(b) > len(a) {", "if len(b) >= len(a) {"),
        echo_empty=sub(GLOSS_SOLUTION, "self.define(word).unwrap_or(word)", 'self.define(word).unwrap_or("")'),
        first_word_trimmed=sub(GLOSS_SOLUTION, "    g.define(first_word(text))", "    g.define(first_word(text.trim_start()))"),
    ),
))

LOCAL_STARTER = r"""
use std::borrow::Cow;

/// `text` lowercased, with its words joined by "-". When `text` is already in that form (no whitespace, no
/// char that lowercasing changes), the result borrows `text` instead of allocating.
pub fn slug(text: &str) -> &str {
    let s = text.split_whitespace().collect::<Vec<_>>().join("-").to_lowercase();
    &s
}

/// The non-blank lines of `text`, trimmed, in order.
pub fn clean_lines(text: &str) -> &[&str] {
    let lines: Vec<&str> = text.lines().map(str::trim).filter(|l| !l.is_empty()).collect();
    &lines
}

/// The file name (the part after the last '/') of the path with the longest file name; the first on a tie.
pub fn longest_file_name(paths: Vec<String>) -> Option<&str> {
    paths.iter().map(|p| p.rsplit('/').next().unwrap()).max_by_key(|n| n.len())
}
"""

LOCAL_SOLUTION = r"""
use std::borrow::Cow;

/// `text` lowercased, with its words joined by "-". When `text` is already in that form (no whitespace, no
/// char that lowercasing changes), the result borrows `text` instead of allocating.
pub fn slug(text: &str) -> Cow<'_, str> {
    if text.chars().all(|c| !c.is_whitespace() && c.to_lowercase().eq([c])) {
        return Cow::Borrowed(text);
    }
    Cow::Owned(text.split_whitespace().collect::<Vec<_>>().join("-").to_lowercase())
}

/// The non-blank lines of `text`, trimmed, in order.
pub fn clean_lines(text: &str) -> Vec<&str> {
    text.lines().map(str::trim).filter(|l| !l.is_empty()).collect()
}

/// The file name (the part after the last '/') of the path with the longest file name; the first on a tie.
pub fn longest_file_name(paths: &[String]) -> Option<&str> {
    let mut best: Option<&str> = None;
    for p in paths {
        let name = p.rsplit('/').next().unwrap();
        if best.map_or(true, |b| name.len() > b.len()) {
            best = Some(name);
        }
    }
    best
}
"""


def paths_lit(xs):
    return "[" + ", ".join(f'"{x}"' for x in xs) + "].map(String::from)"


P.append(fix(
    "fix-return-ref-to-local", "Fix: returning references to locals (E0515, E0106)", "easy", "elision", ["E0515", "E0106", "Cow", "borrow or own"],
    """
        None of these compiles: each returns a reference to something the function itself owns, which dies at
        the end of the call. Change the return types (and for `longest_file_name`, the parameter) so that
        each result owns what it must and borrows what it can. `longest_file_name` also has a bug the compiler
        can't see; the doc comment is the spec.
    """,
    LOCAL_STARTER,
    LOCAL_SOLUTION,
    [T("slug_example", "slug(\"Hello  Big World\")", 'slug("Hello  Big World")', '"hello-big-world"'),
     T("slug_borrows_when_unchanged", "slug(\"already-a-slug\") is std::borrow::Cow::Borrowed", 'matches!(slug("already-a-slug"), std::borrow::Cow::Borrowed("already-a-slug"))', "true"),
     T("clean_lines_example", "clean_lines(\"  a \\n\\n b\\n   \")", 'clean_lines("  a \\n\\n b\\n   ")', 'vec!["a", "b"]'),
     T("longest_file_name_example", "[\"src/main.rs\", \"lib/very_long.rs\", \"x/y.rs\"]", "longest_file_name(&paths)", 'Some("very_long.rs")', setup=f'let paths = {paths_lit(["src/main.rs", "lib/very_long.rs", "x/y.rs"])};'),
     T("tie_goes_to_the_first", "[\"a/xx\", \"b/yy\"]", "longest_file_name(&paths)", 'Some("xx")', setup=f'let paths = {paths_lit(["a/xx", "b/yy"])};'),
     T("empty_inputs", "slug(\"\"), clean_lines(\"\"), longest_file_name([])", '(slug(""), clean_lines(""), longest_file_name(&[]))', '(std::borrow::Cow::Borrowed(""), Vec::<&str>::new(), None)')],
    [ALLOC_COUNTER,
     T("slug_uppercase_is_owned", "slug(\"ABC\") is owned", 'matches!(slug("ABC"), std::borrow::Cow::Owned(_))', "true"),
     T("slug_unicode", "slug(\"Ünïcode Straße\")", 'slug("Ünïcode Straße")', '"ünïcode-straße"'),
     T("slug_non_ascii_uppercase", "slug(\"Ünï\")", 'slug("Ünï")', '"ünï"'),
     T("slug_tabs_newlines", "slug(\"a\\tb\\nc\")", 'slug("a\\tb\\nc")', '"a-b-c"'),
     T("slug_leading_space_is_owned", "slug(\" a\")", '(slug(" a").clone(), matches!(slug(" a"), std::borrow::Cow::Owned(_)))', '(std::borrow::Cow::<str>::Borrowed("a"), true)'),
     T("no_slash", "[\"plain\", \"a/bc\"]", "longest_file_name(&paths)", 'Some("plain")', setup=f'let paths = {paths_lit(["plain", "a/bc"])};'),
     T("trailing_slash", "[\"dir/\", \"a/b\"]", "longest_file_name(&paths)", 'Some("b")', setup=f'let paths = {paths_lit(["dir/", "a/b"])};'),
     T("clean_lines_crlf", "clean_lines(\"x\\r\\ny\\r\\n\")", 'clean_lines("x\\r\\ny\\r\\n")', 'vec!["x", "y"]'),
     T("results_borrow_the_input", "clean_lines points into the text", 'clean_lines(&text)[0].as_ptr() == text[2..].as_ptr()', "true", setup='let text = String::from("  q\\n");'),
     r"""
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(6302);
         for _ in 0..300 {
             let len = rng.below(10);
             let text = rng.string(len, "aB -\n/");
             let want_slug = text.split_whitespace().collect::<Vec<_>>().join("-").to_lowercase();
             check!(format!("slug({text:?})"), slug(&text).into_owned(), want_slug.clone());
             check!(format!("slug({text:?}) borrows iff unchanged"), matches!(slug(&text), std::borrow::Cow::Borrowed(_)), want_slug == text);
             let want_lines: Vec<&str> = text.lines().map(str::trim).filter(|l| !l.is_empty()).collect();
             check!(format!("clean_lines({text:?})"), clean_lines(&text), want_lines.clone());
             let paths: Vec<String> = want_lines.iter().map(|l| l.to_string()).collect();
             let mut best: Option<&str> = None;
             for p in &paths {
                 let n = p.rsplit('/').next().unwrap();
                 if best.map_or(true, |b| n.len() > b.len()) {
                     best = Some(n);
                 }
             }
             check!(format!("longest_file_name({paths:?})"), longest_file_name(&paths), best);
         }
     }

     #[test]
     fn unchanged_slug_does_not_allocate() {
         let text = "already-lowercase-".repeat(10_000);
         let (s, n) = allocs(|| slug(&text).len());
         check!("slug of a 180000-byte slug: allocations", (s, n), (180_000, 0));
     }
     """],
    [("rust", "A `String` or `Vec` created inside the function is dropped when it returns, so no reference to it can escape (E0515). Return the owned value itself."),
     ("rust", "`slug` often doesn't need a new string at all. `Cow<'_, str>` is either `Borrowed(&str)` from the input or `Owned(String)`: decide which before allocating."),
     ("rust", "`fn f(paths: Vec<String>) -> Option<&str>` has no input lifetime for the output to borrow (E0106). If the function doesn't need to own the paths, take `&[String]`. And `max_by_key` returns the *last* maximum.")],
    ("""A reference can only point at something that outlives the call: an input, or `'static` data. Locals, including values built with `format!`, `join` or `collect`, die at the return, so the fix is to hand them back by value (`String`, `Vec<&str>`, whose elements still borrow the input). A parameter taken by value is a local too, which is why `longest_file_name(paths: Vec<String>) -> Option<&str>` has nothing to borrow from; taking `&[String]` makes the paths the caller's, and the result borrows them. `Cow` is the middle ground when the output is often identical to the input: borrow in that case and own only when something changed, so the common path allocates nothing. Separately, `Iterator::max_by_key` keeps the last of equal maxima; \"first on a tie\" needs a strict comparison.

Syntax to remember: `fn slug(text: &str) -> Cow<'_, str>` · `Cow::Borrowed(text)` / `Cow::Owned(s)` · `c.to_lowercase().eq([c])` (lowercasing leaves `c` alone).""", "O(n)", "O(n) only when the slug differs"),
    "When would you return `impl Iterator<Item = &str> + '_` from `clean_lines` instead of a `Vec`, and what would the caller give up?",
    ["Nothing created inside a function can be borrowed by its result.", "`Cow` borrows when it can and owns when it must.", "`max_by_key` returns the last maximum."],
    rules=dict(methods=["leak", "clone"]),
    wrong=dict(
        last_on_a_tie=sub(LOCAL_SOLUTION, "if best.map_or(true, |b| name.len() > b.len()) {", "if best.map_or(true, |b| name.len() >= b.len()) {"),
        always_owned=sub(LOCAL_SOLUTION, "    if text.chars().all(|c| !c.is_whitespace() && c.to_lowercase().eq([c])) {\n        return Cow::Borrowed(text);\n    }\n", ""),
        borrows_uppercase=sub(LOCAL_SOLUTION, "c.to_lowercase().eq([c])", "!c.is_ascii_uppercase()"),
    ),
))

LONGEST_STARTER = r"""
/// The longer of `a` and `b`; `a` on a tie.
pub fn longest(a: &str, b: &str) -> &str {
    if b.len() > a.len() {
        b
    } else {
        a
    }
}

/// The longest of `words` (the first on a tie), or None if there are none.
pub fn longest_of(words: &[&str]) -> Option<&str> {
    let mut best: Option<&str> = None;
    for &w in words {
        if best.map_or(true, |b| w.len() > b.len()) {
            best = Some(w);
        }
    }
    best
}

/// Makes `best` point at `line` if `line` is longer. Returns whether it did.
pub fn keep_longest(best: &mut &str, line: &str) -> bool {
    if line.len() > best.len() {
        *best = line;
        true
    } else {
        false
    }
}
"""

LONGEST_SOLUTION = LONGEST_STARTER
for _old, _new in [
    ("pub fn longest(a: &str, b: &str) -> &str {", "pub fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {"),
    ("pub fn longest_of(words: &[&str]) -> Option<&str> {\n    let mut best: Option<&str> = None;", "pub fn longest_of<'a>(words: &[&'a str]) -> Option<&'a str> {\n    let mut best: Option<&'a str> = None;"),
    ("pub fn keep_longest(best: &mut &str, line: &str) -> bool {", "pub fn keep_longest<'a>(best: &mut &'a str, line: &'a str) -> bool {"),
]:
    LONGEST_SOLUTION = sub(LONGEST_SOLUTION, _old, _new)

P.append(fix(
    "longest", "longest(a, b), and what the result borrows", "easy", "elision", ["E0106", "lifetime parameters", "&mut &'a str"],
    """
        None of these compiles. Fix the three signatures, with the lifetimes callers need: the tests keep
        `longest_of`'s result after the slice of words is gone, and store lines of their own into
        `keep_longest`'s `best`. No copying.
    """,
    LONGEST_STARTER,
    LONGEST_SOLUTION,
    [T("longest_example", "longest(\"hi\", \"hello\")", 'longest("hi", "hello")', '"hello"'),
     T("longest_tie", "longest(\"ab\", \"cd\")", 'longest("ab", "cd")', '"ab"'),
     T("longest_of_outlives_the_slice", "longest_of a temporary Vec of [\"a\", \"ccc\", \"bb\"]", "w", 'Some("ccc")',
       setup='let (a, b, c) = (String::from("a"), String::from("ccc"), String::from("bb"));\nlet w = longest_of(&vec![a.as_str(), b.as_str(), c.as_str()]);'),
     T("keep_longest_in_a_loop", "best = \"\"; keep_longest over lines of \"ab\\nabcd\\nxyzw\\na\"", "(best, changed)", '("abcd", 2)',
       setup='let text = String::from("ab\\nabcd\\nxyzw\\na");\nlet mut best: &str = "";\nlet mut changed = 0;\nfor line in text.lines() {\n    if keep_longest(&mut best, line) {\n        changed += 1;\n    }\n}'),
     T("longest_of_empty", "longest_of([])", "longest_of(&[])", "None")],
    [T("longest_empty_strings", "longest(\"\", \"\")", 'longest("", "")', '""'),
     T("longest_by_bytes", "longest(\"ééé\", \"abcd\")", 'longest("ééé", "abcd")', '"ééé"'),
     T("longest_of_first_tie", "longest_of([\"xy\", \"ab\", \"z\"])", 'longest_of(&["xy", "ab", "z"])', 'Some("xy")'),
     T("longest_of_single", "longest_of([\"\"])", 'longest_of(&[""])', 'Some("")'),
     T("keep_longest_tie_keeps", "best \"ab\"; keep_longest(\"cd\")", '{ let mut best = "ab"; (keep_longest(&mut best, "cd"), best) }', '(false, "ab")'),
     T("keep_longest_from_static", "best starts as a literal, then a line from a String", '{ let s = String::from("longer"); let mut best = "x"; keep_longest(&mut best, &s); best.to_string() }', '"longer".to_string()'),
     T("longest_mixed_lifetimes", "longest(literal, String) used while the String lives", '{ let s = String::from("dynamic"); longest("st", &s).len() }', "7"),
     T("result_is_an_input", "longest returns one of its inputs, not a copy", 'longest(&a, &b).as_ptr() == b.as_ptr()', "true", setup='let (a, b) = (String::from("x"), String::from("yy"));'),
     r"""
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(6303);
         for _ in 0..300 {
             let n = rng.below(6);
             let mut owned = Vec::new();
             for _ in 0..n {
                 let len = rng.below(5);
                 owned.push(rng.string(len, "ab"));
             }
             let words: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
             let mut want: Option<&str> = None;
             for &w in &words {
                 if want.map_or(true, |b| w.len() > b.len()) {
                     want = Some(w);
                 }
             }
             check!(format!("longest_of({words:?})"), longest_of(&words), want);
             let mut best = "";
             for &w in &words {
                 keep_longest(&mut best, w);
             }
             check!(format!("keep_longest over {words:?}"), best, want.unwrap_or(""));
             if n >= 2 {
                 let expect = if words[1].len() > words[0].len() { words[1] } else { words[0] };
                 check!(format!("longest({:?}, {:?})", words[0], words[1]), longest(words[0], words[1]), expect);
             }
         }
     }
     """],
    [("rust", "`longest` has two reference inputs and no `self`, so elision can't choose (E0106). The result may be either input, so both get the same lifetime `'a`: the result lives as long as the shorter of the two."),
     ("rust", "`longest_of(words: &[&str])` has two lifetimes hiding in one parameter: the slice's and the strings'. That's two input lifetimes, so elision gives up. Tying the output to the slice (`&'a [&'a str]`) compiles but dies with the slice; name only the strings' lifetime: `&[&'a str]`."),
     ("rust", "In `keep_longest(best: &mut &str, line: &str)` the three elided lifetimes are all different, so `*best = line` would store a reference that may die first. `line` must live as long as what `best` holds.")],
    ("""A lifetime parameter is a constraint the caller must satisfy, and the signature has to state exactly the one the body needs. `longest` may return either input, so both share `'a`, and the result lives no longer than the shorter-lived argument. `longest_of` is the subtle one: `&[&str]` hides two lifetimes, the borrow of the slice and the borrow of the strings. Tying the output to the slice would make the answer die with a temporary `Vec` even though it points into longer-lived strings. Naming the inner one (`&[&'a str] -> Option<&'a str>`) fixes that. `keep_longest` writes `line` into `*best`, so `line` must outlive what `best` holds: `&mut &'a str, &'a str`. The outer `&mut` keeps its own, shorter lifetime.

Syntax to remember: `fn longest<'a>(a: &'a str, b: &'a str) -> &'a str` · `fn longest_of<'a>(words: &[&'a str]) -> Option<&'a str>` · `fn keep_longest<'a>(best: &mut &'a str, line: &'a str) -> bool`.""", "O(n)", "O(1)"),
    "In `keep_longest`, why must the lifetime inside `&mut &'a str` match `line`'s exactly, while a `&'a str` argument can be shortened freely?",
    ["Two inputs, no `self`: write the lifetime.", "`&[&'a str]` has two lifetimes; tie outputs to the inner one.", "Storing through `&mut &'a T` requires the new value to live for `'a`."],
    rules=dict(methods=["clone", "to_string", "to_owned", "leak"], lines=5),
    wrong=dict(
        tie_goes_to_b=sub(LONGEST_SOLUTION, "    if b.len() > a.len() {", "    if b.len() >= a.len() {"),
        longest_of_last=sub(LONGEST_SOLUTION, "if best.map_or(true, |b| w.len() > b.len()) {", "if best.map_or(true, |b| w.len() >= b.len()) {"),
        keep_on_tie=sub(LONGEST_SOLUTION, "    if line.len() > best.len() {", "    if line.len() >= best.len() {"),
    ),
))

WRONG_INPUT_STARTER = r"""
use std::collections::HashMap;

/// The part of `line` after `prefix`, if `line` starts with it.
pub fn after<'a>(line: &'a str, prefix: &'a str) -> Option<&'a str> {
    line.strip_prefix(prefix)
}

/// The value for `key`.
pub fn lookup<'m>(map: &'m HashMap<String, String>, key: &'m str) -> Option<&'m str> {
    map.get(key).map(String::as_str)
}

/// `value`, or `default` when there's none.
pub fn or_default<'a>(value: Option<&'a str>, default: &'a str) -> &'a str {
    value.unwrap_or(default)
}

/// Settings looked up in `local` first, then in `global`. Global settings usually live for the whole
/// program; local ones for one request.
pub struct Layered<'g, 'l> {
    pub global: &'g [(&'g str, &'g str)],
    pub local: &'l [(&'l str, &'l str)],
}

impl<'g, 'l> Layered<'g, 'l> {
    pub fn get(&self, key: &str) -> Option<&'l str> {
        self.local.iter().chain(self.global.iter()).find(|e| e.0 == key).map(|e| e.1)
    }
}
"""

WRONG_INPUT_SOLUTION = WRONG_INPUT_STARTER
for _old, _new in [
    ("pub fn after<'a>(line: &'a str, prefix: &'a str) -> Option<&'a str> {", "pub fn after<'a>(line: &'a str, prefix: &str) -> Option<&'a str> {"),
    ("pub fn lookup<'m>(map: &'m HashMap<String, String>, key: &'m str) -> Option<&'m str> {", "pub fn lookup<'m>(map: &'m HashMap<String, String>, key: &str) -> Option<&'m str> {"),
    ("impl<'g, 'l> Layered<'g, 'l> {", "impl<'g: 'l, 'l> Layered<'g, 'l> {"),
]:
    WRONG_INPUT_SOLUTION = sub(WRONG_INPUT_SOLUTION, _old, _new)

GLOBAL = 'const GLOBAL: &[(&str, &str)] = &[("color", "auto"), ("pager", "less")];'

P.append(fix(
    "fix-output-borrows-wrong-input", "Fix: lifetimes that tie too much, or too little", "easy", "elision", ["over-constrained lifetimes", "'a: 'b", "outlives bounds"],
    """
        `after` and `lookup` compile, but tie their results to an input they don't borrow from, so the tests
        (which pass temporaries there) don't compile. `Layered::get` doesn't compile at all: it returns a
        global setting as if it were a local one. Fix all three with lifetimes alone. `or_default` is right as
        it is.
    """,
    WRONG_INPUT_STARTER,
    WRONG_INPUT_SOLUTION,
    [T("after_with_temporary_prefix", "after(\"key=value\", a temporary \"key=\")", "v", 'Some("value")', setup='let line = String::from("key=value");\nlet v = after(&line, &String::from("key="));'),
     T("lookup_with_temporary_key", "map {a: 1}; lookup of a temporary \"a\"", "v", 'Some("1")', setup='let map = std::collections::HashMap::from([("a".to_string(), "1".to_string())]);\nlet v = lookup(&map, &"a".to_string());'),
     T("layered_local_wins", "global {color: auto, pager: less}; local {color: never}", '(layered.get("color"), layered.get("pager"), layered.get("x"))', '(Some("never"), Some("less"), None)',
       setup=GLOBAL + '\nlet local = [("color", "never")];\nlet layered = Layered { global: GLOBAL, local: &local };'),
     T("layered_local_from_a_string", "local value borrowed from a request String", 'layered.get("user")', 'Some("ann")',
       setup=GLOBAL + '\nlet req = String::from("user=ann");\nlet (k, v) = req.split_once(\'=\').unwrap();\nlet local = [(k, v)];\nlet layered = Layered { global: GLOBAL, local: &local };'),
     T("or_default_example", "or_default(None, \"d\"), or_default(Some(\"v\"), \"d\")", '(or_default(None, "d"), or_default(Some("v"), "d"))', '("d", "v")')],
    [T("after_no_match", "after(\"abc\", \"x\")", 'after("abc", "x")', "None"),
     T("after_empty_prefix", "after(\"abc\", \"\")", 'after("abc", "")', 'Some("abc")'),
     T("after_whole_line", "after(\"abc\", \"abc\")", 'after("abc", "abc")', 'Some("")'),
     T("lookup_missing", "map {}; lookup x", 'lookup(&m, "x")', "None", setup="let m = std::collections::HashMap::new();"),
     T("layered_empty_local", "local {}", 'layered.get("pager")', 'Some("less")', setup=GLOBAL + '\nlet layered = Layered { global: GLOBAL, local: &[] };'),
     T("layered_first_local_duplicate", "local {a: 1, a: 2}", 'layered.get("a")', 'Some("1")', setup=GLOBAL + '\nlet local = [("a", "1"), ("a", "2")];\nlet layered = Layered { global: GLOBAL, local: &local };'),
     T("after_result_points_into_line", "after's result borrows the line", 'after(&line, "ab").unwrap().as_ptr() == line[2..].as_ptr()', "true", setup='let line = String::from("abcd");'),
     T("lookup_result_outlives_key_scope", "lookup result used after the key's block", "v.len()", "3", setup='let map = std::collections::HashMap::from([("k".to_string(), "val".to_string())]);\nlet v = {\n    let key = String::from("k");\n    lookup(&map, &key).unwrap()\n};'),
     r"""
     #[test]
     fn random_vs_model() {
         let mut rng = anneal_prelude::Rng::new(6304);
         for _ in 0..300 {
             let len = rng.below(5);
             let line = rng.string(len, "ab");
             let plen = rng.below(3);
             let prefix = rng.string(plen, "ab");
             check!(format!("after({line:?}, {prefix:?})"), after(&line, &prefix), line.strip_prefix(prefix.as_str()));
             let keys = ["a", "b", "c"];
             let global: Vec<(&str, &str)> = keys.iter().filter(|_| rng.bool()).map(|&k| (k, "g")).collect();
             let local: Vec<(&str, &str)> = keys.iter().filter(|_| rng.bool()).map(|&k| (k, "l")).collect();
             let layered = Layered { global: &global, local: &local };
             for k in keys {
                 let want = local.iter().chain(global.iter()).find(|e| e.0 == k).map(|e| e.1);
                 check!(format!("global {global:?}, local {local:?}; get({k})"), layered.get(k), want);
             }
         }
     }
     """],
    [("rust", "A lifetime on a parameter that the output doesn't borrow from still constrains the caller: they must keep that argument alive as long as the result. Give such parameters their own (elided) lifetime."),
     ("rust", "`Layered::get` returns `&'l str`, but a global value is a `&'g str`. That's fine only when `'g` outlives `'l`. Say so: `impl<'g: 'l, 'l>` (or `where 'g: 'l`)."),
     ("rust", "`or_default` really can return either input, so there one shared lifetime is right.")],
    ("""Over-constraining is the quiet lifetime bug: `after<'a>(line: &'a str, prefix: &'a str) -> Option<&'a str>` compiles, but forces every caller to keep `prefix` alive as long as the result, although the result only ever points into `line`. The fix is to leave `prefix` (and `lookup`'s `key`) with an elided lifetime of its own. The opposite case needs a relation between lifetimes: `get` may return a global value where a local-lifetime one is promised, which is sound only if `'g: 'l` (\"`'g` outlives `'l`\"). With that bound, `&'g str` shrinks to `&'l str` by covariance. The bound costs callers nothing here, since global settings are the longer-lived ones.

Syntax to remember: `fn after<'a>(line: &'a str, prefix: &str) -> Option<&'a str>` · `impl<'g: 'l, 'l> Layered<'g, 'l>` · or `struct Layered<'g: 'l, 'l>` / `where 'g: 'l`.""", "O(n)", "O(1)"),
    "Why does `'g: 'l` on the impl suffice, when the struct itself doesn't declare it?",
    ["Tie outputs only to the inputs they borrow from.", "`'a: 'b` lets a longer borrow stand in for a shorter one.", "Some functions genuinely need one lifetime for two inputs."],
    rules=dict(methods=["clone", "to_string", "to_owned", "leak"], lines=3),
    wrong=dict(
        global_wins=sub(WRONG_INPUT_SOLUTION, "self.local.iter().chain(self.global.iter())", "self.global.iter().chain(self.local.iter())"),
        after_contains=sub(WRONG_INPUT_SOLUTION, "    line.strip_prefix(prefix)\n", "    line.find(prefix).map(|i| &line[i + prefix.len()..])\n"),
        default_first=sub(WRONG_INPUT_SOLUTION, "    value.unwrap_or(default)\n", "    if default.is_empty() { value.unwrap_or(default) } else { default }\n"),
    ),
))

CAPTURE_STARTER = r"""
/// Words of `text` longer than `min` chars, as owned `String`s.
pub fn long_words(text: &str, min: usize) -> impl Iterator<Item = String> {
    text.split_whitespace().filter(move |w| w.chars().count() > min).map(String::from)
}

/// Pairs up `a` and `b` element by element (stopping at the shorter one).
pub fn pairs<'a, 'b>(a: &'a [u32], b: &'b [u32]) -> impl Iterator<Item = (u32, u32)> + 'a + 'b {
    a.iter().copied().zip(b.iter().copied())
}

/// The values of `v`, sorted, as a snapshot: later changes to `v` don't affect it.
pub fn sorted_snapshot(v: &Vec<u32>) -> impl Iterator<Item = u32> + '_ {
    let mut copy = v.to_vec();
    copy.sort_unstable();
    copy.into_iter()
}
"""

CAPTURE_SOLUTION = CAPTURE_STARTER
for _old, _new in [
    ("pub fn long_words(text: &str, min: usize) -> impl Iterator<Item = String> {", "pub fn long_words(text: &str, min: usize) -> impl Iterator<Item = String> + '_ {"),
    ("-> impl Iterator<Item = (u32, u32)> + 'a + 'b {", "-> impl Iterator<Item = (u32, u32)> + use<'a, 'b> {"),
    ("pub fn sorted_snapshot(v: &Vec<u32>) -> impl Iterator<Item = u32> + '_ {", "pub fn sorted_snapshot(v: &Vec<u32>) -> impl Iterator<Item = u32> + use<> {"),
]:
    CAPTURE_SOLUTION = sub(CAPTURE_SOLUTION, _old, _new)

P.append(fix(
    "fix-impl-trait-hides-borrow", "Fix: what an impl Trait return captures", "medium", "elision", ["E0700", "impl Trait", "+ '_", "use<..>", "precise capturing"],
    """
        Each function returns `impl Iterator`, and each says the wrong thing about what the hidden iterator
        borrows. `long_words` and `pairs` don't compile; `sorted_snapshot` compiles but claims to borrow `v`,
        so the tests (which change `v` while the snapshot is alive) don't. Fix only the return types.
    """,
    CAPTURE_STARTER,
    CAPTURE_SOLUTION,
    [T("long_words_example", "long_words(\"a quick brown fox\", 3)", 'long_words("a quick brown fox", 3).collect::<Vec<_>>()', 'vec!["quick".to_string(), "brown".to_string()]'),
     T("pairs_example", "pairs([1, 2, 3], [10, 20])", "pairs(&[1, 2, 3], &[10, 20]).collect::<Vec<_>>()", "vec![(1, 10), (2, 20)]"),
     T("pairs_lifetimes_differ", "pairs(a long-lived slice, a temporary Vec) collected in the temporary's scope", "got", "vec![(5, 7)]",
       setup="let a = vec![5u32, 6];\nlet got: Vec<(u32, u32)> = {\n    let b = vec![7u32];\n    pairs(&a, &b).collect()\n};"),
     T("snapshot_survives_changes", "take a snapshot of [3, 1, 2], then push 0 to v", "(snap.collect::<Vec<_>>(), v)", "(vec![1, 2, 3], vec![3, 1, 2, 0])",
       setup="let mut v = vec![3u32, 1, 2];\nlet snap = sorted_snapshot(&v);\nv.push(0);"),
     T("long_words_counts_chars", "long_words(\"héllo abc\", 4)", 'long_words("héllo abc", 4).collect::<Vec<_>>()', 'vec!["héllo".to_string()]')],
    [T("long_words_none", "long_words(\"a b\", 5)", 'long_words("a b", 5).count()', "0"),
     T("long_words_strict", "long_words(\"abcd abcde\", 4)", 'long_words("abcd abcde", 4).collect::<Vec<_>>()', 'vec!["abcde".to_string()]'),
     T("long_words_whitespace", "long_words(\"\\tlong\\nwords  \", 0)", 'long_words("\\tlong\\nwords  ", 0).collect::<Vec<_>>()', 'vec!["long".to_string(), "words".to_string()]'),
     T("pairs_empty", "pairs([], [1])", "pairs(&[], &[1]).count()", "0"),
     T("pairs_first_shorter", "pairs([1], [2, 3])", "pairs(&[1], &[2, 3]).collect::<Vec<_>>()", "vec![(1, 2)]"),
     T("snapshot_empty", "sorted_snapshot([])", "sorted_snapshot(&vec![]).count()", "0"),
     T("snapshot_duplicates", "sorted_snapshot([2, 2, 1])", "sorted_snapshot(&vec![2, 2, 1]).collect::<Vec<_>>()", "vec![1, 2, 2]"),
     T("snapshot_outlives_v", "snapshot, then drop v", "{ let s = { let v = vec![9u32, 8]; sorted_snapshot(&v) }; s.collect::<Vec<_>>() }", "vec![8, 9]"),
     r"""
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(6305);
         for _ in 0..300 {
             let (n, m) = (rng.below(6), rng.below(6));
             let a: Vec<u32> = rng.vec(n, 0, 9);
             let b: Vec<u32> = rng.vec(m, 0, 9);
             let want: Vec<(u32, u32)> = a.iter().copied().zip(b.iter().copied()).collect();
             check!(format!("pairs({a:?}, {b:?})"), pairs(&a, &b).collect::<Vec<_>>(), want);
             let mut v = a.clone();
             let snap = sorted_snapshot(&v);
             v.clear();
             let mut want = a.clone();
             want.sort();
             check!(format!("sorted_snapshot({a:?})"), snap.collect::<Vec<_>>(), want);
             let len = rng.below(12);
             let text = rng.string(len, "ab é");
             let min = rng.below(3);
             let want: Vec<String> = text.split_whitespace().filter(|w| w.chars().count() > min).map(String::from).collect();
             check!(format!("long_words({text:?}, {min})"), long_words(&text, min).collect::<Vec<_>>(), want);
         }
     }
     """],
    [("rust", "In edition 2021, a returned `impl Trait` captures the function's type parameters but not its lifetimes, unless the bounds mention them. `long_words`'s iterator borrows `text`, so say so: `+ '_`."),
     ("rust", "`+ 'a + 'b` means \"the hidden type outlives both `'a` and `'b`\", which a type holding a `&'a` and a `&'b` can't promise. Precise capturing says \"it may use these\" instead: `+ use<'a, 'b>`."),
     ("rust", "`sorted_snapshot` returns an iterator over its own copy; claiming `+ '_` makes callers keep `v` borrowed. `use<>` (or no bound at all in edition 2021) says it captures nothing.")],
    ("""The caller of a function returning `impl Trait` only sees the bounds, so the bounds must say which lifetimes the hidden type may hold. Edition 2021's rule: type parameters are captured automatically, lifetimes only if they appear in the bounds, hence E0700 for `long_words` until `+ '_` names the borrow. With two lifetimes, `+ 'a + 'b` is the wrong tool: it's an outlives bound, requiring the iterator to outlive each lifetime, which a type containing both references can't do unless one outlives the other. Precise capturing (`+ use<'a, 'b>`, stable since 1.82) states captures without outlives requirements. Edition 2024 flips the default: every in-scope lifetime is captured, and `use<>` (or `use<'a>`) opts out, which is what `sorted_snapshot` needs to let callers mutate `v` while the snapshot lives. Writing it now is correct in both editions.

Syntax to remember: `-> impl Iterator<Item = String> + '_` · `-> impl Iterator<Item = (u32, u32)> + use<'a, 'b>` · `-> impl Iterator<Item = u32> + use<>` · generic: `+ use<'a, T>` (list the type parameters too).""", "O(n)", "O(n) for the snapshot"),
    "Under edition 2024 rules, which of these three signatures would need a `use<..>` bound, and which would change meaning without one?",
    ["2021: `impl Trait` captures type parameters, not lifetimes, unless named.", "`use<'a, 'b>` states captures; `+ 'a` is an outlives bound.", "2024 captures everything by default; `use<>` opts out."],
    rules=dict(methods=["collect", "clone", "leak"], lines=3),
    wrong=dict(
        words_at_least_min=sub(CAPTURE_SOLUTION, "w.chars().count() > min", "w.chars().count() >= min"),
        counts_bytes=sub(CAPTURE_SOLUTION, "w.chars().count() > min", "w.len() > min"),
        snapshot_unsorted=sub(CAPTURE_SOLUTION, "    copy.sort_unstable();\n", ""),
    ),
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
       setup='let src = String::from("alpha 7");\nlet id;\n{\n    let mut c = Cursor::new(&src);\n    id = c.ident();\n}'),
     T("number_then_rest", '" 42 rest": number, rest', "(c.number(), c.rest())", '(Some(42), " rest")', setup='let mut c = Cursor::new(" 42 rest");'),
     T("empty_source", '"": number, ident, rest', "(c.number(), c.ident(), c.rest())", '(None, None, "")', setup='let mut c = Cursor::new("");'),
     T("failure_keeps_position", '"  x": number fails, rest is unchanged', "(c.number(), c.rest())", '(None, "  x")', setup='let mut c = Cursor::new("  x");')],
    [T("overflow", '"99999999999999999999"', "Cursor::new(\"99999999999999999999\").number()", "None"),
     T("u64_max", '"18446744073709551615"', 'Cursor::new("18446744073709551615").number()', "Some(u64::MAX)"),
     T("one_past_max_keeps_position", '" 18446744073709551616": number, rest', "(c.number(), c.rest())", '(None, " 18446744073709551616")',
       setup='let mut c = Cursor::new(" 18446744073709551616");'),
     T("leading_zeros", '"007"', 'Cursor::new("007").number()', "Some(7)"),
     T("number_then_ident_adjacent", '"12ab": number, ident, rest', "(c.number(), c.ident(), c.rest())", '(Some(12), Some("ab"), "")', setup='let mut c = Cursor::new("12ab");'),
     T("ident_stops_at_punct", '"a_1-b": ident, rest', "(c.ident(), c.rest())", '(Some("a_1"), "-b")', setup='let mut c = Cursor::new("a_1-b");'),
     T("non_ascii_ident_start", '"éa": ident, rest', "(c.ident(), c.rest())", '(None, "éa")', setup='let mut c = Cursor::new("éa");'),
     T("tabs_and_newlines", '"\\t\\n x \\n 5": ident, number, rest', "(c.ident(), c.number(), c.rest())", '(Some("x"), Some(5), "")', setup='let mut c = Cursor::new("\\t\\n x \\n 5");'),
     T("minus_is_not_a_digit", '"-5": number, rest', "(c.number(), c.rest())", '(None, "-5")', setup='let mut c = Cursor::new("-5");'),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(306);
         for _ in 0..300 {
             // Build a source from known tokens, then read it back with the matching method.
             let count = rng.below(5);
             let mut src = String::new();
             let mut tokens: Vec<(bool, String)> = Vec::new();
             for _ in 0..count {
                 let spaces = rng.below(3);
                 src.push_str(&" ".repeat(spaces));
                 if rng.bool() {
                     let len = rng.below(3);
                     let tok = rng.string(1, "ab_") + &rng.string(len, "ab_1");
                     src.push_str(&tok);
                     tokens.push((true, tok));
                 } else {
                     let len = 1 + rng.below(4);
                     let tok = rng.string(len, "0123456789");
                     src.push_str(&tok);
                     tokens.push((false, tok));
                 }
                 src.push(' ');
             }
             let mut c = Cursor::new(&src);
             for (is_ident, tok) in &tokens {
                 if *is_ident {
                     check!(format!("src = {src:?}, number() where an ident is"), c.number(), None);
                     check!(format!("src = {src:?}"), c.ident(), Some(tok.as_str()));
                 } else {
                     check!(format!("src = {src:?}, ident() where a number is"), c.ident(), None);
                     check!(format!("src = {src:?}"), c.number(), Some(tok.parse::<u64>().unwrap()));
                 }
             }
             check!(format!("src = {src:?}: rest at the end"), c.rest().trim(), "");
         }
     }
     """,
     T("digit_first", '"9abc": ident, then number, then ident', "(c.ident(), c.number(), c.ident())", '(None, Some(9), Some("abc"))', setup='let mut c = Cursor::new("9abc");'),
     T("underscore", '"_x1 rest"', 'Cursor::new("_x1 rest").ident()', 'Some("_x1")'),
     T("unicode_after", '"n é": ident, rest', "(c.ident(), c.rest())", '(Some("n"), " é")', setup='let mut c = Cursor::new("n é");')],
    [("rust", "Return `&'a str`, not a borrow of `self`: copy `self.src` (a `&'a str`, which is `Copy`) into a local and slice that."),
     ("approach", "Compute the new position first, and only store it once the token is known to be valid.")],
    ("The struct holds a borrow, so it can't outlive `src`, but the tokens are tied to `'a`, not to the cursor. `trim_start` measures whitespace without allocating.", "O(n) total", "O(1)"),
    "How would you add `peek` without duplicating the parsing code?",
    ["A struct that borrows its input: `Cursor<'a>`.", "Methods returning `&'a str` instead of `&self`-tied slices."],
    wrong=dict(
        skips_whitespace_on_failure="""
            pub struct Cursor<'a> {
                src: &'a str,
                pos: usize,
            }

            impl<'a> Cursor<'a> {
                pub fn new(src: &'a str) -> Self {
                    Cursor { src, pos: 0 }
                }

                fn skip_ws(&mut self) {
                    let rest = &self.src[self.pos..];
                    self.pos += rest.len() - rest.trim_start().len();
                }

                pub fn number(&mut self) -> Option<u64> {
                    self.skip_ws();
                    let rest = &self.src[self.pos..];
                    let len = rest.bytes().take_while(u8::is_ascii_digit).count();
                    let n = rest[..len].parse().ok()?;
                    self.pos += len;
                    Some(n)
                }

                pub fn ident(&mut self) -> Option<&'a str> {
                    self.skip_ws();
                    let src = self.src;
                    let rest = &src[self.pos..];
                    let b = rest.as_bytes();
                    if !b.first().is_some_and(|c| c.is_ascii_alphabetic() || *c == b'_') {
                        return None;
                    }
                    let len = b.iter().take_while(|c| c.is_ascii_alphanumeric() || **c == b'_').count();
                    self.pos += len;
                    Some(&rest[..len])
                }

                pub fn rest(&self) -> &'a str {
                    let src = self.src;
                    &src[self.pos..]
                }
            }
        """,
        wrapping_number="""
            pub struct Cursor<'a> {
                src: &'a str,
                pos: usize,
            }

            impl<'a> Cursor<'a> {
                pub fn new(src: &'a str) -> Self {
                    Cursor { src, pos: 0 }
                }

                fn skip_ws(&self) -> usize {
                    let rest = &self.src[self.pos..];
                    self.pos + (rest.len() - rest.trim_start().len())
                }

                pub fn number(&mut self) -> Option<u64> {
                    let start = self.skip_ws();
                    let rest = &self.src[start..];
                    let len = rest.bytes().take_while(u8::is_ascii_digit).count();
                    if len == 0 {
                        return None;
                    }
                    let n = rest.bytes().take(len).fold(0u64, |n, d| n.wrapping_mul(10).wrapping_add(u64::from(d - b'0')));
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
        ident_may_start_with_digit="""
            pub struct Cursor<'a> {
                src: &'a str,
                pos: usize,
            }

            impl<'a> Cursor<'a> {
                pub fn new(src: &'a str) -> Self {
                    Cursor { src, pos: 0 }
                }

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
                    let len = rest.bytes().take_while(|c| c.is_ascii_alphanumeric() || *c == b'_').count();
                    if len == 0 {
                        return None;
                    }
                    self.pos = start + len;
                    Some(&rest[..len])
                }

                pub fn rest(&self) -> &'a str {
                    let src = self.src;
                    &src[self.pos..]
                }
            }
        """,
    ),
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
     T("blank_doc", '["\\n"]', 'first_lines(&["\\n".to_string()])', 'vec![String::new()]'),
     T("none", "[]", "first_lines(&[]).len()", "0"),
     T("trailing_spaces", '["hi  "]', 'first_lines(&["hi  ".to_string()])', 'vec!["hi".to_string()]'),
     T("leading_blank_lines", '["\\n\\n  a\\nb"]', 'first_lines(&["\\n\\n  a\\nb".to_string()])', 'vec!["a".to_string()]')],
    [T("none", "[]", "first_lines(&[]).len()", "0"),
     T("empty_doc", '[""]', 'first_lines(&[String::new()])', 'vec![String::new()]'),
     T("inner_spaces_kept", '["a b \\nc"]', 'first_lines(&["a b \\nc".to_string()])', 'vec!["a b ".to_string()]'),
     T("crlf", '["a\\r\\nb"]', 'first_lines(&["a\\r\\nb".to_string()])', 'vec!["a".to_string()]'),
     T("unicode_whitespace", '["\\u{3000}x\\u{3000}"]', 'first_lines(&["\\u{3000}x\\u{3000}".to_string()])', 'vec!["x".to_string()]'),
     T("tabs", '["\\t\\tx\\ty"]', 'first_lines(&["\\t\\tx\\ty".to_string()])', 'vec!["x\\ty".to_string()]'),
     T("order_kept", '["b", "a", "c"]', 'first_lines(&["b".to_string(), "a".to_string(), "c".to_string()])', 'vec!["b".to_string(), "a".to_string(), "c".to_string()]'),
     T("many_docs", "1000 docs \"  n\\nrest\"", "first_lines(&docs)", "(0..1000).map(|i| i.to_string()).collect::<Vec<_>>()",
       setup='let docs: Vec<String> = (0..1000).map(|i| format!("  {i}\\nrest")).collect();'),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(307);
         for _ in 0..300 {
             let n = rng.below(4);
             let docs: Vec<String> = (0..n).map(|_| { let len = rng.below(8); rng.string(len, "a \\n") }).collect();
             let want: Vec<String> = docs.iter().map(|d| d.trim().split('\\n').next().unwrap_or("").to_string()).collect();
             check!(format!("docs = {docs:?}"), first_lines(&docs), want);
         }
     }
     """],
    [("rust", "Each `Excerpt` borrows from `trimmed`, which is dropped at the end of each loop iteration, but the excerpts are read after the loop."),
     ("rust", "`d.trim()` is already a `&str` borrowed from `docs`, which lives long enough. No need for a copy.")],
    ("Borrowing from the long-lived input instead of a per-iteration copy fixes the error and removes an allocation.", "O(total length)", "O(n)"),
    "If you really did need to transform each document, how would you keep the excerpts valid?",
    ["A struct's borrow must not outlive what it points at.", "Borrow from the caller's data, not a temporary copy."],
    rules=dict(methods=["clone", "to_owned"], lines=1),
    wrong=dict(
        drops_the_trim="""
            pub struct Excerpt<'a> {
                pub text: &'a str,
            }

            /// The first line of each document, after trimming the document.
            pub fn first_lines(docs: &[String]) -> Vec<String> {
                let mut excerpts = Vec::new();
                for d in docs {
                    let trimmed = d.as_str();
                    excerpts.push(Excerpt { text: trimmed.lines().next().unwrap_or("") });
                }
                excerpts.iter().map(|e| e.text.to_string()).collect()
            }
        """,
        trims_only_the_start="""
            pub struct Excerpt<'a> {
                pub text: &'a str,
            }

            /// The first line of each document, after trimming the document.
            pub fn first_lines(docs: &[String]) -> Vec<String> {
                let mut excerpts = Vec::new();
                for d in docs {
                    let trimmed = d.trim_start();
                    excerpts.push(Excerpt { text: trimmed.lines().next().unwrap_or("") });
                }
                excerpts.iter().map(|e| e.text.to_string()).collect()
            }
        """,
    ),
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
       setup='let text = String::from("x1\\nno\\n2x");\nlet found;\n{\n    let doc = Document::new(&text);\n    found = doc.lines_with("x");\n}'),
     T("tie", '"ab\\ncd"', 'Document::new("ab\\ncd").longest_line()', '"ab"'),
     T("empty_text", '""', '(d.longest_line(), d.lines_with("x"))', '("", Vec::<&str>::new())', setup='let d = Document::new("");'),
     T("no_line_matches", '"a\\nb", word "z"', 'Document::new("a\\nb").lines_with("z")', "Vec::<&str>::new()")],
    [T("tie", '"ab\\ncd"', 'Document::new("ab\\ncd").longest_line()', '"ab"'),
     T("single_line", '"only"', 'Document::new("only").longest_line()', '"only"'),
     T("crlf", '"ab\\r\\nc"', '(d.longest_line(), d.lines_with("b"))', '("ab", vec!["ab"])', setup='let d = Document::new("ab\\r\\nc");'),
     T("trailing_newline", '"a\\nbb\\n"', 'Document::new("a\\nbb\\n").lines_with("")', 'vec!["a", "bb"]'),
     T("case_sensitive", '"Rust\\nrust", word "rust"', 'Document::new("Rust\\nrust").lines_with("rust")', 'vec!["rust"]'),
     T("unicode", '"éé\\nabc", longest by bytes', 'Document::new("éé\\nabc").longest_line()', '"éé"'),
     T("blank_lines", '"\\n\\nx\\n"', 'Document::new("\\n\\nx\\n").longest_line()', '"x"'),
     T("word_in_the_middle", '"one two\\nthree", word "tw"', 'Document::new("one two\\nthree").lines_with("tw")', 'vec!["one two"]'),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(308);
         for _ in 0..300 {
             let n = rng.below(10);
             let text = rng.string(n, "ab\\n");
             let lines: Vec<&str> = text.split('\\n').collect();
             let lines = if text.ends_with('\\n') { &lines[..lines.len() - 1] } else { &lines[..] };
             let mut longest = "";
             for l in lines {
                 if l.len() > longest.len() {
                     longest = l;
                 }
             }
             let with_b: Vec<&str> = lines.iter().copied().filter(|l| l.contains('b')).collect();
             let d = Document::new(&text);
             check!(format!("text = {text:?}"), (d.longest_line(), d.lines_with("b")), (longest, with_b));
         }
     }
     """],
    [("rust", "An elided output in a `&self` method borrows from `self`, the short-lived `Document`. The lines really come from `text`, which lives for `'a`."),
     ("rust", "Say so: return `&'a str` and `Vec<&'a str>`.")],
    ("`&'a str` means 'as long as the text', `&str` from `&self` means 'as long as this Document'. The body compiles either way; only callers see the difference.", "O(n)", "O(k)"),
    "Why is the first version not wrong, just less useful?",
    ["Methods on borrowing structs can return the struct's lifetime.", "Elision picks `self`, which is often too short."],
    rules=dict(lines=2),
    wrong=dict(
        last_line_on_tie="""
            pub struct Document<'a> {
                text: &'a str,
            }

            impl<'a> Document<'a> {
                pub fn new(text: &'a str) -> Self {
                    Document { text }
                }

                /// The longest line; the first one on a tie.
                pub fn longest_line(&self) -> &'a str {
                    self.text.lines().fold("", |best, l| if l.len() >= best.len() { l } else { best })
                }

                /// Every line containing `word`.
                pub fn lines_with(&self, word: &str) -> Vec<&'a str> {
                    self.text.lines().filter(|l| l.contains(word)).collect()
                }
            }
        """,
        splits_on_newline="""
            pub struct Document<'a> {
                text: &'a str,
            }

            impl<'a> Document<'a> {
                pub fn new(text: &'a str) -> Self {
                    Document { text }
                }

                /// The longest line; the first one on a tie.
                pub fn longest_line(&self) -> &'a str {
                    self.text.split('\\n').fold("", |best, l| if l.len() > best.len() { l } else { best })
                }

                /// Every line containing `word`.
                pub fn lines_with(&self, word: &str) -> Vec<&'a str> {
                    self.text.split('\\n').filter(|l| l.contains(word)).collect()
                }
            }
        """,
    ),
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
       setup='let text = String::from("a--b");\nlet parts;\n{\n    let sep = String::from("--");\n    parts = Splitter::new(&text, &sep).parts();\n}'),
     T("no_sep", '"abc", ","', 'Splitter::new("abc", ",").parts()', 'vec!["abc"]'),
     T("first_without_sep", '"abc", ","', 'Splitter::new("abc", ",").first()', '"abc"'),
     T("empty_pieces_kept", '"a,,b,", ","', 'Splitter::new("a,,b,", ",").parts()', 'vec!["a", "", "b", ""]')],
    [T("no_sep", '"abc", ","', 'Splitter::new("abc", ",").parts()', 'vec!["abc"]'),
     T("empty_text", '"", ","', '(Splitter::new("", ",").first(), Splitter::new("", ",").parts())', '("", vec![""])'),
     T("leading_sep", '",a", ","', '(Splitter::new(",a", ",").first(), Splitter::new(",a", ",").parts())', '("", vec!["", "a"])'),
     T("text_is_sep", '"--", "--"', 'Splitter::new("--", "--").parts()', 'vec!["", ""]'),
     T("unicode_sep", '"a→b→c", "→"', 'Splitter::new("a→b→c", "→").parts()', 'vec!["a", "b", "c"]'),
     T("overlapping_sep", '"aaa", "aa"', 'Splitter::new("aaa", "aa").parts()', 'vec!["", "a"]'),
     T("both_outlive_sep", "first and parts, separator dropped", "(first, parts)", '("x", vec!["x", "y z"])',
       setup='let text = String::from("x;y z");\nlet (first, parts);\n{\n    let sep = String::from(";");\n    let s = Splitter::new(&text, &sep);\n    first = s.first();\n    parts = s.parts();\n}'),
     T("zero_copy", "pieces point into the text", "std::ptr::eq(parts[1].as_ptr(), text[2..].as_ptr())", "true",
       setup='let text = String::from("a,b");\nlet parts = Splitter::new(&text, ",").parts();'),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(309);
         for _ in 0..300 {
             let n = rng.below(10);
             let text = rng.string(n, "ab,");
             let sep = if rng.bool() { "," } else { "b," };
             // Reference: walk the text by hand.
             let mut want: Vec<&str> = Vec::new();
             let mut start = 0;
             let mut i = 0;
             while i + sep.len() <= text.len() {
                 if &text[i..i + sep.len()] == sep {
                     want.push(&text[start..i]);
                     i += sep.len();
                     start = i;
                 } else {
                     i += 1;
                 }
             }
             want.push(&text[start..]);
             let s = Splitter::new(&text, sep);
             check!(format!("text = {text:?}, sep = {sep:?}"), (s.first(), s.parts()), (want[0], want.clone()));
         }
     }
     """],
    [("rust", "One `'a` for both fields means `'a` can only be as long as the shorter borrow: the separator's."),
     ("rust", "Give the struct two lifetime parameters, and tie the outputs to the text's.")],
    ("With separate `'t` and `'s`, outputs borrow only from the text. Most structs need one lifetime; add a second exactly when outputs come from one field but not another.", "O(n)", "O(k)"),
    "When is one lifetime for several fields the right design?",
    ["A struct with two independent lifetime parameters.", "Outputs tied to one field, not the whole struct."],
    rules=dict(methods=["to_string", "to_owned", "clone", "into", "from"]),
    wrong=dict(
        first_is_empty_without_sep="""
            pub struct Splitter<'t, 's> {
                text: &'t str,
                sep: &'s str,
            }

            impl<'t, 's> Splitter<'t, 's> {
                pub fn new(text: &'t str, sep: &'s str) -> Self {
                    Splitter { text, sep }
                }

                pub fn first(&self) -> &'t str {
                    self.text.split_once(self.sep).map_or("", |(head, _)| head)
                }

                pub fn parts(&self) -> Vec<&'t str> {
                    self.text.split(self.sep).collect()
                }
            }
        """,
        drops_trailing_empty_piece="""
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
                    self.text.split_terminator(self.sep).collect()
                }
            }
        """,
        skips_empty_pieces="""
            pub struct Splitter<'t, 's> {
                text: &'t str,
                sep: &'s str,
            }

            impl<'t, 's> Splitter<'t, 's> {
                pub fn new(text: &'t str, sep: &'s str) -> Self {
                    Splitter { text, sep }
                }

                pub fn first(&self) -> &'t str {
                    self.text.split(self.sep).find(|p| !p.is_empty()).unwrap_or("")
                }

                pub fn parts(&self) -> Vec<&'t str> {
                    self.text.split(self.sep).filter(|p| !p.is_empty()).collect()
                }
            }
        """,
    ),
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
       setup='let src = String::from("a bb ccc dd");\nlet best;\n{\n    let t = Tokenizer::new(&src);\n    best = longest_ident(t);\n}'),
     T("empty", '""', 'Tokenizer::new("").count()', "0"),
     T("number_then_ident", '"12ab _x9"', 'Tokenizer::new("12ab _x9").collect::<Vec<_>>()', 'vec![Token::Number("12"), Token::Ident("ab"), Token::Ident("_x9")]'),
     T("no_idents", '"1 + 2"', 'longest_ident(Tokenizer::new("1 + 2"))', "None")],
    [T("unicode_punct", '"a→b"', 'Tokenizer::new("a→b").collect::<Vec<_>>()', "vec![Token::Ident(\"a\"), Token::Punct('→'), Token::Ident(\"b\")]"),
     T("leading_zeros", '"007"', 'Tokenizer::new("007").collect::<Vec<_>>()', 'vec![Token::Number("007")]'),
     T("punct_runs_split", '"==>"', 'Tokenizer::new("==>").collect::<Vec<_>>()', "vec![Token::Punct('='), Token::Punct('='), Token::Punct('>')]"),
     T("tabs_and_newlines", '"a\\n\\tb"', 'Tokenizer::new("a\\n\\tb").collect::<Vec<_>>()', 'vec![Token::Ident("a"), Token::Ident("b")]'),
     T("non_ascii_letter_is_punct", '"éa"', 'Tokenizer::new("éa").collect::<Vec<_>>()', "vec![Token::Punct('é'), Token::Ident(\"a\")]"),
     T("emoji", '"x😀1"', 'Tokenizer::new("x😀1").collect::<Vec<_>>()', "vec![Token::Ident(\"x\"), Token::Punct('😀'), Token::Number(\"1\")]"),
     T("zero_copy", "idents point into the source", "std::ptr::eq(id.as_ptr(), src[4..].as_ptr())", "true",
       setup='let src = String::from("1 + abc");\nlet Some(Token::Ident(id)) = Tokenizer::new(&src).nth(2) else { panic!("no ident") };'),
     T("blank", '"   "', 'Tokenizer::new("   ").count()', "0"),
     T("tie_first", '"ab cd"', 'longest_ident(Tokenizer::new("ab cd"))', 'Some("ab")'),
     T("numbers_are_not_idents", '"12345 ab"', 'longest_ident(Tokenizer::new("12345 ab"))', 'Some("ab")'),
     T("from_a_vec", "a Vec<Token> built by hand", 'longest_ident(vec![Token::Punct(\'x\'), Token::Ident("q")])', 'Some("q")'),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(310);
         for _ in 0..300 {
             let n = rng.below(12);
             let src = rng.string(n, "a_1 +é");
             // Reference: classify one char at a time.
             let cs: Vec<(usize, char)> = src.char_indices().collect();
             let mut want: Vec<Token> = Vec::new();
             let mut i = 0;
             while i < cs.len() {
                 let (at, c) = cs[i];
                 let mut j = i + 1;
                 if c == ' ' {
                     i = j;
                     continue;
                 }
                 if c == 'a' || c == '_' {
                     while j < cs.len() && matches!(cs[j].1, 'a' | '_' | '1') {
                         j += 1;
                     }
                 } else if c == '1' {
                     while j < cs.len() && cs[j].1 == '1' {
                         j += 1;
                     }
                 }
                 let end = if j < cs.len() { cs[j].0 } else { src.len() };
                 want.push(match c {
                     'a' | '_' => Token::Ident(&src[at..end]),
                     '1' => Token::Number(&src[at..end]),
                     _ => Token::Punct(c),
                 });
                 i = j;
             }
             let longest = want.iter().filter_map(|t| if let Token::Ident(s) = t { Some(*s) } else { None }).fold(None, |best: Option<&str>, s| match best {
                 Some(b) if b.len() >= s.len() => Some(b),
                 _ => Some(s),
             });
             check!(format!("src = {src:?}"), Tokenizer::new(&src).collect::<Vec<_>>(), want.clone());
             check!(format!("src = {src:?}: longest_ident"), longest_ident(Tokenizer::new(&src)), longest);
         }
     }
     """],
    [("rust", "`type Item = Token<'a>`: tokens borrow the source, not the tokenizer, so they can outlive it."),
     ("rust", "`s.split_at(len)` gives the token and the rest, both `&'a str`."),
     ("rust", "`longest_ident` only needs `IntoIterator<Item = Token<'a>>`, so it works on a `Tokenizer`, a `Vec`, or anything else.")],
    ("No token allocates. The iterator and the tokens are separate borrows of the source, which is why `longest_ident` can return data after the tokenizer is dropped.", "O(n)", "O(1)"),
    "Add byte offsets to each token for error messages. How does the type change?",
    ["Iterator items that borrow the input: `type Item = Token<'a>`.", "Generic functions over `IntoIterator<Item = Token<'a>>`."],
    source="W36", related=("L3", "S2"),
    wrong=dict(
        tie_goes_to_last="""
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
                    .max_by_key(|s| s.len())
            }
        """,
        unicode_letters_are_idents="""
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
                c.is_alphabetic() || c == '_'
            }

            impl<'a> Iterator for Tokenizer<'a> {
                type Item = Token<'a>;

                fn next(&mut self) -> Option<Token<'a>> {
                    let s = self.rest.trim_start();
                    let c = s.chars().next()?;
                    let len = if is_ident_start(c) {
                        s.find(|c: char| !(c.is_alphanumeric() || c == '_')).unwrap_or(s.len())
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
        byte_punct="""
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
                    let s = self.rest.trim_start();
                    let b = *s.as_bytes().first()?;
                    let is_ident = |b: u8| b.is_ascii_alphanumeric() || b == b'_';
                    let len = if b.is_ascii_alphabetic() || b == b'_' {
                        s.bytes().take_while(|&b| is_ident(b)).count()
                    } else if b.is_ascii_digit() {
                        s.bytes().take_while(u8::is_ascii_digit).count()
                    } else {
                        s.chars().next().map_or(1, char::len_utf8)
                    };
                    let (text, rest) = s.split_at(len);
                    self.rest = rest;
                    Some(if b.is_ascii_alphabetic() || b == b'_' {
                        Token::Ident(text)
                    } else if b.is_ascii_digit() {
                        Token::Number(text)
                    } else {
                        Token::Punct(b as char)
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
    ),
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
     T("bad_magic", 'b"XX\\x01\\x00\\x00"', 'parse_frame(b"XX\\x01\\x00\\x00")', "None"),
     T("empty_buffer", 'b""', "(parse_frame(b\"\"), parse_all(b\"\"))", "(None, Some(vec![]))"),
     T("truncated_payload", "length 5, only 3 bytes", 'parse_frame(b"AN\\x01\\x00\\x05abc")', "None"),
     T("two_frames", "two frames back to back", 'parse_all(b"AN\\x01\\x00\\x01aAN\\x02\\x00\\x00").map(|v| v.iter().map(|f| f.kind).collect::<Vec<_>>())', "Some(vec![1, 2])")],
    [T("truncated_payload", "length 5, only 3 bytes", 'parse_frame(b"AN\\x01\\x00\\x05abc")', "None"),
     T("length_is_big_endian", "length bytes [0x01, 0x00] = 256, 256 payload bytes", "parse_frame(&buf).map(|(f, rest)| (f.payload.len(), rest.len()))", "Some((256, 0))",
       setup='let mut buf = b"AN\\x09\\x01\\x00".to_vec();\nbuf.resize(5 + 256, 7);'),
     T("exact_fit", "length 2, exactly 2 bytes", 'parse_frame(b"AN\\x03\\x00\\x02hi")', 'Some((Frame { kind: 3, payload: &b"hi"[..] }, &[][..]))'),
     T("kind_255", "kind 0xFF", 'parse_frame(b"AN\\xff\\x00\\x00").map(|(f, _)| f.kind)', "Some(255)"),
     T("only_magic", 'b"AN"', 'parse_frame(b"AN")', "None"),
     T("second_frame_truncated", "a whole frame, then a frame missing its payload", 'parse_all(b"AN\\x01\\x00\\x00AN\\x02\\x00\\x03ab")', "None"),
     T("magic_case", 'b"an\\x01\\x00\\x00"', 'parse_frame(b"an\\x01\\x00\\x00")', "None"),
     T("max_length_frame", "length 0xFFFF with 65535 bytes", "parse_all(&buf).map(|v| v[0].payload.len())", "Some(65_535)",
       setup='let mut buf = b"AN\\x01\\xff\\xff".to_vec();\nbuf.resize(5 + 65_535, 0);'),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(311);
         for _ in 0..300 {
             let count = rng.below(4);
             let mut buf = Vec::new();
             let mut want: Vec<(u8, Vec<u8>)> = Vec::new();
             for _ in 0..count {
                 let kind = rng.int(0, 255) as u8;
                 let len = rng.below(300);
                 let payload: Vec<u8> = rng.vec(len, 0, 255);
                 buf.extend_from_slice(b"AN");
                 buf.push(kind);
                 buf.push((len >> 8) as u8);
                 buf.push(len as u8);
                 buf.extend_from_slice(&payload);
                 want.push((kind, payload));
             }
             let got = parse_all(&buf).map(|v| v.iter().map(|f| (f.kind, f.payload.to_vec())).collect::<Vec<_>>());
             check!(format!("{count} random frames"), got, Some(want.clone()));
             // Cutting any whole frame short makes the buffer invalid.
             if !buf.is_empty() {
                 let cut = rng.below(buf.len());
                 let whole = want.iter().scan(0, |end, (_, p)| { *end += 5 + p.len(); Some(*end) }).any(|end| end == cut);
                 let want_cut = if whole || cut == 0 { Some(()) } else { None };
                 check!(format!("{count} random frames cut to {cut} bytes"), parse_all(&buf[..cut]).map(|_| ()), want_cut);
             }
         }
     }

     #[test]
     fn scale_100k_frames() {
         let mut buf = Vec::new();
         for i in 0..100_000u32 {
             buf.extend_from_slice(b"AN");
             buf.push((i % 256) as u8);
             buf.extend_from_slice(&1u16.to_be_bytes());
             buf.push((i % 7) as u8);
         }
         let frames = parse_all(&buf).unwrap();
         check!("100000 one-byte frames", (frames.len(), frames[99_999].kind, frames[99_999].payload), (100_000, (99_999 % 256) as u8, &[(99_999 % 7) as u8][..]));
     }
     """,
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
    wrong=dict(
        little_endian_length="""
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
                let len = usize::from(u16::from_le_bytes(*len));
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
        rejects_exact_fit="""
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
                if rest.len() <= len && len > 0 {
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
        keeps_frames_before_junk="""
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
                while let Some((frame, rest)) = parse_frame(buf) {
                    frames.push(frame);
                    buf = rest;
                }
                Some(frames)
            }
        """,
    ),
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
       setup="let data = [1u8];\nlet mut r = Reader::new(&data);\nlet x = r.take(9);\nlet y = r.take(1);"),
     T("zero", "take 0 from empty", "Reader::new(&[]).take(0)", "Some(&[][..])"),
     T("everything_then_nothing", "data [7, 8]; take 2, take 1", "(a, b, r.remaining())", "(Some(&[7u8, 8][..]), None, 0)",
       setup="let data = [7u8, 8];\nlet mut r = Reader::new(&data);\nlet a = r.take(2);\nlet b = r.take(1);"),
     T("failed_take_keeps_position", "data [1, 2, 3]; take 1, take 5, remaining", "(a, b, r.remaining())", "(Some(&[1u8][..]), None, 2)",
       setup="let data = [1u8, 2, 3];\nlet mut r = Reader::new(&data);\nlet a = r.take(1);\nlet b = r.take(5);")],
    [T("zero", "take 0 from empty", "Reader::new(&[]).take(0)", "Some(&[][..])"),
     T("empty_take_one", "take 1 from empty", "Reader::new(&[]).take(1)", "None"),
     T("remaining_at_start", "data [1, 2, 3]", "Reader::new(&[1, 2, 3]).remaining()", "3"),
     T("zero_does_not_move", "data [5]; take 0, take 0, take 1", "(a, b, c)", "(Some(&[][..]), Some(&[][..]), Some(&[5u8][..]))",
       setup="let data = [5u8];\nlet mut r = Reader::new(&data);\nlet a = r.take(0);\nlet b = r.take(0);\nlet c = r.take(1);"),
     T("chunks_outlive_reader", "take twice, drop the reader, use both chunks", "(a, b)", "(Some(&[1u8][..]), Some(&[2u8, 3][..]))",
       setup="let data = vec![1u8, 2, 3];\nlet (a, b);\n{\n    let mut r = Reader::new(&data);\n    a = r.take(1);\n    b = r.take(2);\n}"),
     T("zero_copy", "chunk points into data", "std::ptr::eq(chunk.as_ptr(), data[2..].as_ptr())", "true",
       setup="let data = [0u8, 1, 2, 3];\nlet mut r = Reader::new(&data);\nr.take(2);\nlet chunk = r.take(2).unwrap();"),
     T("many_small_takes", "10000 bytes, 10000 takes of 1", "(sum, r.remaining())", "(10_000 * 7, 0)",
       setup="let data = vec![7u8; 10_000];\nlet mut r = Reader::new(&data);\nlet mut sum = 0u32;\nwhile let Some(c) = r.take(1) {\n    sum += c[0] as u32;\n}"),
     T("fails_then_exact", "data [1, 2]; take 3, then take 2", "(a, b)", "(None, Some(&[1u8, 2][..]))",
       setup="let data = [1u8, 2];\nlet mut r = Reader::new(&data);\nlet a = r.take(3);\nlet b = r.take(2);"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(312);
         for _ in 0..300 {
             let len = rng.below(10);
             let data: Vec<u8> = rng.vec(len, 0, 9);
             let mut r = Reader::new(&data);
             let mut pos = 0;
             for _ in 0..6 {
                 let n = rng.below(5);
                 let want = if pos + n <= data.len() { pos += n; Some(&data[pos - n..pos]) } else { None };
                 check!(format!("data = {data:?}, take({n}) at {pos}"), r.take(n), want);
                 check!(format!("data = {data:?}: remaining"), r.remaining(), data.len() - pos);
             }
         }
     }
     """],
    [("rust", "`&'a mut self` borrows the Reader mutably for all of `'a`, the lifetime of the data, so the first call locks it for good."),
     ("rust", "The chunk comes from `data: &'a [u8]`, not from `self`. The `&mut self` borrow can be short.")],
    ("Tying `&mut self` to the struct's own lifetime parameter is a classic trap: it compiles, and the struct becomes unusable after one call. The output lifetime `'a` alone says where the bytes come from.", "O(1)", "O(1)"),
    "Why does `&'a self` (shared) cause much less trouble than `&'a mut self`?",
    ["Never write `&'a mut self` with the struct's own `'a`.", "Outputs can use `'a` while `self` is borrowed briefly."],
    rules=dict(lines=1),
    wrong=dict(
        returns_a_short_chunk="""
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
                    let chunk = self.data.get(self.pos..(self.pos + n).min(self.data.len()))?;
                    self.pos += n;
                    Some(chunk)
                }

                pub fn remaining(&self) -> usize {
                    self.data.len() - self.pos
                }
            }
        """,
        moves_before_checking="""
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
                    self.pos += n;
                    let chunk = self.data.get(self.pos - n..self.pos)?;
                    Some(chunk)
                }

                pub fn remaining(&self) -> usize {
                    self.data.len().saturating_sub(self.pos)
                }
            }
        """,
    ),
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
       setup='let mut s = Stash::new();\ns.put(format!("user-{}", 42));\ns.put("lit");'),
     T("empty", "nothing stored", "Stash::new().all::<i64>().len()", "0"),
     T("types_are_exact", "put 1u64; all::<u32>()", "s.all::<u32>().len()", "0", setup="let mut s = Stash::new();\ns.put(1u64);"),
     T("insertion_order", "put 3i32, 1i32, 2i32", "s.all::<i32>()", "vec![&3, &1, &2]", setup="let mut s = Stash::new();\ns.put(3i32);\ns.put(1i32);\ns.put(2i32);")],
    [T("empty", "nothing stored", "Stash::new().all::<i64>().len()", "0"),
     T("types_are_exact", "put 1u64; all::<u32>()", "s.all::<u32>().len()", "0", setup="let mut s = Stash::new();\ns.put(1u64);"),
     T("string_vs_str", "put String \"a\", &str \"b\"", "(s.all::<String>().iter().map(|x| x.as_str()).collect::<Vec<_>>(), s.all::<&str>())", '(vec!["a"], vec![&"b"])',
       setup='let mut s = Stash::new();\ns.put(String::from("a"));\ns.put("b");'),
     T("box_is_its_own_type", "put Box<i32>(1), 2i32", "(s.all::<Box<i32>>().len(), s.all::<i32>())", "(1, vec![&2])",
       setup="let mut s = Stash::new();\ns.put(Box::new(1i32));\ns.put(2i32);"),
     T("unit_values", "put (), (), 1u8", "s.all::<()>().len()", "2", setup="let mut s = Stash::new();\ns.put(());\ns.put(());\ns.put(1u8);"),
     T("nested_owned", "put vec![String \"x\"]", "(v.len(), v[0].clone())", '(1, vec![String::from("x")])',
       setup='let mut s = Stash::new();\ns.put(vec![String::from("x")]);\nlet v = s.all::<Vec<String>>();'),
     T("options", "put Some(1u8), None::<u8>, Some(2u16)", "s.all::<Option<u8>>()", "vec![&Some(1u8), &None]",
       setup="let mut s = Stash::new();\ns.put(Some(1u8));\ns.put(None::<u8>);\ns.put(Some(2u16));"),
     T("many", "10000 u32 values and 10000 u64 values interleaved", "(v.len(), *v[0], *v[9_999])", "(10_000, 0, 9_999)",
       setup="let mut s = Stash::new();\nfor i in 0..10_000u32 {\n    s.put(i);\n    s.put(u64::from(i));\n}\nlet v = s.all::<u32>();"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(313);
         for _ in 0..300 {
             let n = rng.below(10);
             let mut s = Stash::new();
             let mut small: Vec<u8> = Vec::new();
             let mut wide: Vec<u16> = Vec::new();
             for _ in 0..n {
                 let v = rng.int(0, 255);
                 if rng.bool() {
                     s.put(v as u8);
                     small.push(v as u8);
                 } else {
                     s.put(v as u16);
                     wide.push(v as u16);
                 }
             }
             check!(format!("u8 values {small:?} and u16 values {wide:?}"), (s.all::<u8>(), s.all::<u16>()), (small.iter().collect::<Vec<_>>(), wide.iter().collect::<Vec<_>>()));
         }
     }
     """],
    [("rust", "`Any` is implemented for every `T: 'static`, so `T: Any` already implies the bound."),
     ("rust", "`Box<dyn Any>::downcast_ref::<T>()` returns `Some(&T)` only if the value is exactly a `T`.")],
    ("`T: 'static` rules out types holding short-lived borrows, because `Any` can't track lifetimes. Owned data like `String` and `Vec` always qualifies.", "O(n) for all", "O(n)"),
    "Why can't `Any` support types with non-'static lifetimes?",
    ["`T: 'static` means 'no short borrows inside', not 'lives forever'.", "`Any` and `downcast_ref`."],
    related=("L3", "L4"),
    wrong=dict(
        newest_first="""
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
                    self.items.insert(0, Box::new(value));
                }

                /// Every stored value of type `T`, in insertion order.
                pub fn all<T: Any>(&self) -> Vec<&T> {
                    self.items.iter().filter_map(|b| b.downcast_ref::<T>()).collect()
                }
            }
        """,
        stops_at_first_other_type="""
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
                    self.items.iter().skip_while(|b| !b.is::<T>()).map_while(|b| b.downcast_ref::<T>()).collect()
                }
            }
        """,
    ),
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
     T("config_error_line", '"a=1\\nb"', 'bad_line(&*sum_config("a=1\\nb").unwrap_err())', "Some(2)"),
     T("empty_text", '""', 'sum_config("").ok()', "Some(0)"),
     T("parse_error_kept", '"a=x"', 'sum_config("a=x").unwrap_err().is::<std::num::ParseIntError>()', "true"),
     T("blank_lines", '"a=1\\n\\n b=2 "', 'sum_config("a=1\\n\\n b=2 ").ok()', "Some(3)")],
    [T("parse_error_kept", '"a=x"', 'sum_config("a=x").unwrap_err().is::<std::num::ParseIntError>()', "true"),
     T("negatives", '"a=-5\\nb=2"', 'sum_config("a=-5\\nb=2").ok()', "Some(-3)"),
     T("only_blank_lines", '"\\n  \\n\\t"', 'sum_config("\\n  \\n\\t").ok()', "Some(0)"),
     T("first_equals_splits", '"a=b=1"', 'sum_config("a=b=1").unwrap_err().is::<std::num::ParseIntError>()', "true"),
     T("empty_key", '"=5"', 'sum_config("=5").ok()', "Some(5)"),
     T("empty_value", '"a="', 'sum_config("a=").unwrap_err().is::<std::num::ParseIntError>()', "true"),
     T("crlf", '"a=1\\r\\nb=2\\r\\n"', 'sum_config("a=1\\r\\nb=2\\r\\n").ok()', "Some(3)"),
     T("value_past_i64", '"a=9223372036854775808"', 'sum_config("a=9223372036854775808").unwrap_err().is::<std::num::ParseIntError>()', "true"),
     T("first_error_wins", '"x\\na=q"', 'bad_line(&*sum_config("x\\na=q").unwrap_err())', "Some(1)"),
     T("plain_error_is_not_config", "a boxed io::Error", 'bad_line(&std::io::Error::other("boom"))', "None"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(314);
         for _ in 0..300 {
             let n = rng.below(6);
             let mut lines = Vec::new();
             let mut want: Result<i64, Option<usize>> = Ok(0);
             for i in 0..n {
                 let line = match rng.below(4) {
                     0 => String::new(),
                     1 => format!("k{i}"),
                     2 => format!("k = {}", rng.int(-99, 99)),
                     _ => format!("k={}", rng.string(1, "x7")),
                 };
                 if let Ok(total) = want {
                     if !line.trim().is_empty() {
                         want = match line.split_once('=') {
                             None => Err(Some(i + 1)),
                             Some((_, v)) => v.trim().parse::<i64>().map(|v| total + v).map_err(|_| None),
                         };
                     }
                 }
                 lines.push(line);
             }
             let text = lines.join("\\n");
             let got = sum_config(&text).map_err(|e| bad_line(&*e));
             check!(format!("text = {text:?}"), got, want);
         }
     }
     """,
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
    wrong=dict(
        counts_only_nonblank_lines="""
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
                for (i, line) in text.lines().filter(|l| !l.trim().is_empty()).enumerate() {
                    let (_, value) = line.split_once('=').ok_or(ConfigError { line: i + 1 })?;
                    total += value.trim().parse::<i64>()?;
                }
                Ok(total)
            }

            pub fn bad_line(err: &(dyn Error + 'static)) -> Option<usize> {
                err.downcast_ref::<ConfigError>().map(|e| e.line)
            }
        """,
        every_error_is_a_config_error="""
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
                    let bad = ConfigError { line: i + 1 };
                    let (_, value) = line.split_once('=').ok_or(ConfigError { line: i + 1 })?;
                    total += value.trim().parse::<i64>().map_err(|_| bad)?;
                }
                Ok(total)
            }

            pub fn bad_line(err: &(dyn Error + 'static)) -> Option<usize> {
                err.downcast_ref::<ConfigError>().map(|e| e.line)
            }
        """,
        splits_at_last_equals="""
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
                    let (_, value) = line.rsplit_once('=').ok_or(ConfigError { line: i + 1 })?;
                    total += value.trim().parse::<i64>()?;
                }
                Ok(total)
            }

            pub fn bad_line(err: &(dyn Error + 'static)) -> Option<usize> {
                err.downcast_ref::<ConfigError>().map(|e| e.line)
            }
        """,
    ),
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
     T("empty", "[], 3 threads", "parallel_sum(&[], 3)", "0"),
     T("zero_chunks", "[1, 2, 3], 0 threads", "parallel_sum(&[1, 2, 3], 0)", "6"),
     T("uneven_split", "[1, 2, 3, 4, 5, 6, 7], 3 threads", "parallel_sum(&[1, 2, 3, 4, 5, 6, 7], 3)", "28"),
     T("data_still_usable", "sum twice, then read data", "(parallel_sum(&data, 2), parallel_sum(&data, 3), data.len())", "(10, 10, 4)",
       setup="let data = vec![1u64, 2, 3, 4];")],
    [T("zero_chunks", "[1, 2, 3], 0 threads", "parallel_sum(&[1, 2, 3], 0)", "6"),
     T("single", "[42], 4 threads", "parallel_sum(&[42], 4)", "42"),
     T("one_thread", "1..=10, 1 thread", "parallel_sum(&data, 1)", "55", setup="let data: Vec<u64> = (1..=10).collect();"),
     T("remainder_chunk", "10 values, 3 threads", "parallel_sum(&data, 3)", "55", setup="let data: Vec<u64> = (1..=10).collect();"),
     T("large_values", "[u64::MAX / 4; 3], 3 threads", "parallel_sum(&[u64::MAX / 4; 3], 3)", "3 * (u64::MAX / 4)"),
     T("zeros", "[0; 100], 7 threads", "parallel_sum(&[0; 100], 7)", "0"),
     T("empty_zero_threads", "[], 0 threads", "parallel_sum(&[], 0)", "0"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(315);
         for _ in 0..200 {
             let n = rng.below(20);
             let data: Vec<u64> = rng.vec(n, 0, 1_000_000);
             let chunks = rng.below(8);
             check!(format!("data = {data:?}, chunks = {chunks}"), parallel_sum(&data, chunks), data.iter().sum::<u64>());
         }
     }
     """,
     T("more_threads_than_items", "[1, 2, 3], 10 threads", "parallel_sum(&[1, 2, 3], 10)", "6"),
     T("big", "10⁶ ones, 8 threads", "parallel_sum(&data, 8)", "1_000_000", setup="let data = vec![1u64; 1_000_000];")],
    [("rust", "`thread::spawn` requires `F: 'static`: the thread might outlive this function, and `data` with it."),
     ("rust", "`thread::scope` guarantees every thread spawned in it is joined before it returns, so the closures may borrow `data`.")],
    ("Scoped threads prove to the compiler that the borrow outlives the threads. The usual alternatives, `Arc<Vec<_>>` or `to_vec`, copy or reshape the data.", "O(n / threads) wall time", "O(threads)"),
    "When would you still choose `thread::spawn` with `Arc` over scoped threads?",
    ["Why `thread::spawn` needs `'static`.", "`thread::scope` for borrowing across threads."],
    rules=dict(methods=["to_vec", "to_owned", "clone", "leak", "into_boxed_slice"], types=["Arc", "Rc"]),
    related=("L3", "C1"),
    wrong=dict(
        chunks_exact_drops_the_tail="""
            use std::thread;

            /// Sums `data` using up to `chunks` threads.
            pub fn parallel_sum(data: &[u64], chunks: usize) -> u64 {
                let size = data.len().div_ceil(chunks.max(1)).max(1);
                thread::scope(|s| {
                    let handles: Vec<_> = data
                        .chunks_exact(size)
                        .map(|chunk| s.spawn(move || chunk.iter().sum::<u64>()))
                        .collect();
                    handles.into_iter().map(|h| h.join().expect("worker panicked")).sum()
                })
            }
        """,
        at_most_chunks_threads="""
            use std::thread;

            /// Sums `data` using up to `chunks` threads.
            pub fn parallel_sum(data: &[u64], chunks: usize) -> u64 {
                let size = (data.len() / chunks.max(1)).max(1);
                thread::scope(|s| {
                    let handles: Vec<_> = data
                        .chunks(size)
                        .take(chunks.max(1))
                        .map(|chunk| s.spawn(move || chunk.iter().sum::<u64>()))
                        .collect();
                    handles.into_iter().map(|h| h.join().expect("worker panicked")).sum()
                })
            }
        """,
    ),
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
     T("empty", '""', 'all_names("")', 'vec!["root", "admin"]'),
     T("one", 'input "x" from a String', "all_names(&input)", 'vec!["x", "root", "admin"]', setup='let input = String::from("x");'),
     T("trailing_newline", '"a\\n"', 'all_names("a\\n")', 'vec!["a", "root", "admin"]'),
     T("blank_line_kept", '"a\\n\\nb"', 'all_names("a\\n\\nb")', 'vec!["a", "", "b", "root", "admin"]')],
    [T("one", 'input "x" from a String', "all_names(&input).len()", "3", setup='let input = String::from("x");'),
     T("crlf", '"a\\r\\nb"', 'all_names("a\\r\\nb")', 'vec!["a", "b", "root", "admin"]'),
     T("root_already_there", '"root"', 'all_names("root")', 'vec!["root", "root", "admin"]'),
     T("unicode", '"émile\\nzoë"', 'all_names("émile\\nzoë")', 'vec!["émile", "zoë", "root", "admin"]'),
     T("spaces_kept", '" a "', 'all_names(" a ")', 'vec![" a ", "root", "admin"]'),
     T("names_point_into_input", "first name points into the String", "std::ptr::eq(names[0].as_ptr(), input.as_ptr())", "true",
       setup='let input = String::from("bob");\nlet names = all_names(&input);'),
     T("defaults_last", "1000 names", "(names.len(), names[999], names[1000], names[1001])", '(1002, "n999", "root", "admin")',
       setup='let input: String = (0..1000).map(|i| format!("n{i}\\n")).collect();\nlet names = all_names(&input);'),
     T("only_newlines", '"\\n\\n"', 'all_names("\\n\\n")', 'vec!["", "", "root", "admin"]'),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(316);
         for _ in 0..300 {
             let n = rng.below(10);
             let input = rng.string(n, "ab\\n");
             let mut want: Vec<&str> = input.split('\\n').collect();
             if input.is_empty() || input.ends_with('\\n') {
                 want.pop();
             }
             want.push("root");
             want.push("admin");
             check!(format!("input = {input:?}"), all_names(&input), want);
         }
     }
     """],
    [("rust", "`&'static str` coerces to `&'a str`, so why not `Vec<&'a str>` to `Vec<&'static str>` behind a `&mut`?"),
     ("rust", "Through `&mut`, the function could also read the Vec as `&'static str`s, or store longer-lived references into it, so the element type must match exactly: `&mut T` is invariant in `T`."),
     ("rust", "Make `add_defaults` generic over the element lifetime. Pushing a `&'static str` into a `Vec<&'a str>` is fine.")],
    ("Covariance lets `&'static str` shrink to `&'a str`. Behind `&mut`, the type can't change at all, because the callee could write a short-lived value where a long-lived one is expected, or vice versa. The generic version asks for exactly what it needs.", "O(n)", "O(n)"),
    "Show the unsound program the compiler would accept if `&mut T` were covariant.",
    ["`&mut T` is invariant in `T`.", "Generalise the callee instead of the caller."],
    rules=dict(lines=1),
    wrong=dict(
        defaults_into_a_scratch_vec="""
            fn add_defaults(names: &mut Vec<&'static str>) {
                names.push("root");
                names.push("admin");
            }

            /// The names in `input` (one per line), then the defaults.
            pub fn all_names(input: &str) -> Vec<&str> {
                let mut names: Vec<&str> = input.lines().collect();
                add_defaults(&mut Vec::new());
                names
            }
        """,
        only_the_defaults="""
            fn add_defaults(names: &mut Vec<&'static str>) {
                names.push("root");
                names.push("admin");
            }

            /// The names in `input` (one per line), then the defaults.
            pub fn all_names(input: &str) -> Vec<&str> {
                let mut names: Vec<&str> = Vec::new();
                add_defaults(&mut names);
                names
            }
        """,
    ),
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
     T("deque_spread", "VecDeque [5, 1]", "Stats::new(std::collections::VecDeque::from([5u32, 1])).spread()", "Some(4)"),
     T("empty", "empty Vec", "(s.mean(), s.spread(), s.count_above(0))", "(None, None, 0)", setup="let s = Stats::new(Vec::<u32>::new());"),
     T("strictly_above", "[1, 5, 9], above 5", "Stats::new(vec![1u32, 5, 9]).count_above(5)", "1"),
     T("fractional_mean", "BTreeSet {1, 10}", "Stats::new(std::collections::BTreeSet::from([1u32, 10])).mean()", "Some(5.5)")],
    [T("array", "[4, 4, 4]", "Stats::new([4u32, 4, 4]).spread()", "Some(0)"),
     T("single", "[7]", "(s.mean(), s.spread(), s.count_above(6))", "(Some(7.0), Some(0), 1)", setup="let s = Stats::new(vec![7u32]);"),
     T("sum_past_u32", "[u32::MAX, u32::MAX]", "Stats::new(vec![u32::MAX, u32::MAX]).mean()", "Some(u32::MAX as f64)"),
     T("full_spread", "[0, u32::MAX]", "Stats::new([0u32, u32::MAX]).spread()", "Some(u32::MAX)"),
     T("btreeset_dedups", "BTreeSet from [3, 3, 9]", "Stats::new(std::collections::BTreeSet::from([3u32, 3, 9])).mean()", "Some(6.0)"),
     T("linked_list", "LinkedList [2, 8, 5]", "(s.spread(), s.count_above(4))", "(Some(6), 2)",
       setup="let s = Stats::new(std::collections::LinkedList::from([2u32, 8, 5]));"),
     T("above_max", "[1, 2], above u32::MAX", "Stats::new(vec![1u32, 2]).count_above(u32::MAX)", "0"),
     T("unsorted_spread", "[5, 1, 9, 3]", "Stats::new(vec![5u32, 1, 9, 3]).spread()", "Some(8)"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(317);
         for _ in 0..300 {
             let n = rng.below(10);
             let v: Vec<u32> = rng.vec(n, 0, 20);
             let t = rng.int(0, 20) as u32;
             let mean = if n == 0 { None } else { Some(v.iter().map(|&x| x as f64).sum::<f64>() / n as f64) };
             let spread = if n == 0 { None } else { Some(v.iter().max().unwrap() - v.iter().min().unwrap()) };
             let above = v.iter().filter(|&&x| x > t).count();
             let s = Stats::new(v.clone());
             check!(format!("data = {v:?}, threshold = {t}"), (s.mean(), s.spread(), s.count_above(t)), (mean, spread, above));
         }
     }

     #[test]
     fn scale_1m() {
         let s = Stats::new((0..1_000_000u32).collect::<Vec<_>>());
         check!("0..1000000", (s.mean(), s.spread(), s.count_above(999_990)), (Some(499_999.5), Some(999_999), 9));
     }
     """,
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
    wrong=dict(
        integer_mean="""
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
                    (n > 0).then(|| (sum / n) as f64)
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
        u32_sum="""
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
                    let (sum, n) = self.data.into_iter().fold((0u32, 0u32), |(s, n), &x| (s + x, n + 1));
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
        at_or_above="""
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
                    self.data.into_iter().filter(|&&x| x >= threshold).count()
                }
            }
        """,
    ),
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
       setup='let source = String::from("a b");\nlet first;\n{\n    let mut p = Parser::<Whitespace>::new(&source);\n    first = p.advance();\n}'),
     T("comma", '"a, b,,c , " with Comma', "tokens", 'vec!["a", "b", "c"]',
       setup='let mut p = Parser::<Comma>::new("a, b,,c , ");\nlet tokens: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();'),
     T("before_first", "current() before advance", 'Parser::<Whitespace>::new("x").current()', "None"),
     T("empty", '"" with Whitespace', '(p.advance(), p.current())', "(None, None)", setup='let mut p = Parser::<Whitespace>::new("");')],
    [T("comma", '"a, b,,c , " with Comma', "tokens", 'vec!["a", "b", "c"]',
       setup='let mut p = Parser::<Comma>::new("a, b,,c , ");\nlet tokens: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();'),
     T("before_first", "current() before advance", 'Parser::<Whitespace>::new("x").current()', "None"),
     T("empty", '"   " with Whitespace', 'Parser::<Whitespace>::new("   ").advance()', "None"),
     T("comma_keeps_inner_spaces", '" new york , la" with Comma', "tokens", 'vec!["new york", "la"]',
       setup='let mut p = Parser::<Comma>::new(" new york , la");\nlet tokens: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();'),
     T("tabs_and_newlines", '"\\ta\\n b\\r\\n" with Whitespace', "tokens", 'vec!["a", "b"]',
       setup='let mut p = Parser::<Whitespace>::new("\\ta\\n b\\r\\n");\nlet tokens: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();'),
     T("unicode", '"héllo wörld" with Whitespace', "tokens", 'vec!["héllo", "wörld"]',
       setup='let mut p = Parser::<Whitespace>::new("héllo wörld");\nlet tokens: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();'),
     T("stays_none_after_end", '"x": advance three times, then current', "(p.advance(), p.advance(), p.advance(), p.current())", '(Some("x"), None, None, None)',
       setup='let mut p = Parser::<Whitespace>::new("x");'),
     T("only_commas", '" , ,," with Comma', 'Parser::<Comma>::new(" , ,,").advance()', "None"),
     T("comma_newline_is_whitespace", '"a,\\n b" with Comma', "tokens", 'vec!["a", "b"]',
       setup='let mut p = Parser::<Comma>::new("a,\\n b");\nlet tokens: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();'),
     T("whitespace_keeps_commas", '"a,b c" with Whitespace', "tokens", 'vec!["a,b", "c"]',
       setup='let mut p = Parser::<Whitespace>::new("a,b c");\nlet tokens: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();'),
     T("next_token_direct", 'Comma::next_token(" a , b")', 'Comma::next_token(" a , b")', 'Some(("a", ", b"))'),
     T("zero_copy", "token points into the source", "std::ptr::eq(tok.as_ptr(), source[2..].as_ptr())", "true",
       setup='let source = String::from("  hi");\nlet tok = Parser::<Whitespace>::new(&source).advance().unwrap();'),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(318);
         for _ in 0..300 {
             let n = rng.below(12);
             let src = rng.string(n, "ab ,\\t");
             let want_ws: Vec<&str> = src.split(|c: char| c == ' ' || c == '\\t').filter(|t| !t.is_empty()).collect();
             let want_comma: Vec<&str> = src.split(',').map(|t| t.trim()).filter(|t| !t.is_empty()).collect();
             let mut p = Parser::<Whitespace>::new(&src);
             let got_ws: Vec<&str> = std::iter::from_fn(|| p.advance()).collect();
             let mut q = Parser::<Comma>::new(&src);
             let got_comma: Vec<&str> = std::iter::from_fn(|| q.advance()).collect();
             check!(format!("src = {src:?}"), (got_ws, got_comma), (want_ws, want_comma));
         }
     }
     """],
    [("approach", "Store the unread part of the source (`&'a str`) and the current token (`Option<&'a str>`). No `String` inside the parser."),
     ("rust", "`T` never appears in a field, so the compiler rejects it as unused. `PhantomData<T>` records it at zero size."),
     ("rust", "`next_token(input: &str) -> Option<(&str, &str)>` elides to one lifetime: both halves borrow `input`.")],
    ("Moving the owner out of the struct removes the self-reference: the parser is just two slices of someone else's text. If you truly need owner and view together, reach for a crate (`ouroboros`, `self_cell`) or store offsets instead of references.", "O(n) total", "O(1)"),
    "Rewrite `Parser` to own its `String` by storing byte offsets instead of references. What do you give up?",
    ["Why self-referential structs can't be written safely.", "`PhantomData` for type parameters that pick behaviour."],
    source="W38", related=("L3", "L4"),
    wrong=dict(
        comma_keeps_trailing_spaces="""
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
                    Some((token, rest))
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
        current_sticks_after_end="""
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
                        None => return None,
                    };
                    self.current
                }

                pub fn current(&self) -> Option<&'a str> {
                    self.current
                }
            }
        """,
        spaces_only="""
            use std::marker::PhantomData;

            pub trait Tokenize {
                /// Splits the next token off `input`, returning (token, remainder).
                fn next_token(input: &str) -> Option<(&str, &str)>;
            }

            pub struct Whitespace;

            pub struct Comma;

            impl Tokenize for Whitespace {
                fn next_token(input: &str) -> Option<(&str, &str)> {
                    let input = input.trim_start_matches(' ');
                    if input.is_empty() {
                        return None;
                    }
                    let end = input.find(' ').unwrap_or(input.len());
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
    ),
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
     T("owned_input", 'input from a String: "x\\n  y  "', "trimmed_lines(&input)", 'vec!["x", "y"]', setup='let input = String::from("x\\n  y  ");'),
     T("empty", '""', 'trimmed_lines("")', "Vec::<&str>::new()"),
     T("inner_spaces_kept", '"  a b  "', 'trimmed_lines("  a b  ")', 'vec!["a b"]'),
     T("all_blank", '" \\n\\t\\n"', 'trimmed_lines(" \\n\\t\\n").len()', "0")],
    [T("all_blank", '" \\n\\t\\n"', 'trimmed_lines(" \\n\\t\\n").len()', "0"),
     T("single_line", '"solo"', 'trimmed_lines("solo")', 'vec!["solo"]'),
     T("tabs", '"\\ta\\t\\n\\tb"', 'trimmed_lines("\\ta\\t\\n\\tb")', 'vec!["a", "b"]'),
     T("crlf", '"a \\r\\n b\\r\\n"', 'trimmed_lines("a \\r\\n b\\r\\n")', 'vec!["a", "b"]'),
     T("unicode_whitespace", '"\\u{3000}é\\u{a0}"', 'trimmed_lines("\\u{3000}é\\u{a0}")', 'vec!["é"]'),
     T("order_kept", '"c\\nb\\na"', 'trimmed_lines("c\\nb\\na")', 'vec!["c", "b", "a"]'),
     T("points_into_input", "the trimmed line points into the String", "std::ptr::eq(lines[0].as_ptr(), input[2..].as_ptr())", "true",
       setup='let input = String::from("  hi  ");\nlet lines = trimmed_lines(&input);'),
     T("many_lines", "1000 lines \"  n  \"", "(lines.len(), lines[999])", '(1000, "999")',
       setup='let input: String = (0..1000).map(|i| format!("  {i}  \\n")).collect();\nlet lines = trimmed_lines(&input);'),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(319);
         for _ in 0..300 {
             let n = rng.below(12);
             let text = rng.string(n, "ab \\n");
             let want: Vec<&str> = text.split('\\n').map(|l| l.trim_matches(' ')).filter(|l| !l.is_empty()).collect();
             check!(format!("text = {text:?}"), trimmed_lines(&text), want);
         }
     }
     """],
    [("rust", "An annotated `|s: &str|` closure takes any lifetime, but its return type gets one fixed lifetime, so the compiler can't connect the output to the input."),
     ("rust", "A `fn` item gets the full elision rules: `fn trim(s: &str) -> &str` means 'returns a borrow of `s`'. `.map(str::trim)` works too.")],
    ("Closure signatures are inferred, and inference doesn't apply the elision rule that links an output to an input. Named functions (or `str::trim` directly) state the relationship.", "O(n)", "O(k)"),
    "How could a closure be made to work here without turning it into a fn?",
    ["Closures don't get lifetime elision for their return type.", "Prefer `fn` items or method paths when a callback returns a borrow."],
    rules=dict(lines=3),
    wrong=dict(
        trims_only_the_start="""
            /// Every line of `text`, trimmed, skipping blank ones.
            pub fn trimmed_lines(text: &str) -> Vec<&str> {
                text.lines().map(str::trim_start).filter(|l| !l.is_empty()).collect()
            }
        """,
        splits_into_words="""
            /// Every line of `text`, trimmed, skipping blank ones.
            pub fn trimmed_lines(text: &str) -> Vec<&str> {
                text.split_whitespace().collect()
            }
        """,
    ),
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
     T("empty", "allowed []", 'make_filter(&[])("x")', "false"),
     T("many_calls", 'allowed ["a"]', 'words.iter().filter(|w| f(w)).count()', "2",
       setup='let allowed = vec!["a"];\nlet f = make_filter(&allowed);\nlet words = ["a", "b", "a"];'),
     T("exact_match_only", 'allowed ["red"]: "re", "reds"', '(f("re"), f("reds"), f("red"))', "(false, false, true)",
       setup='let allowed = ["red"];\nlet f = make_filter(&allowed);'),
     T("case_sensitive", 'allowed ["Red"]: "red"', 'make_filter(&["Red"])("red")', "false")],
    [T("many_calls", 'allowed ["a"]', 'words.iter().filter(|w| f(w)).count()', "2",
       setup='let allowed = vec!["a"];\nlet f = make_filter(&allowed);\nlet words = ["a", "b", "a"];'),
     T("empty_word_allowed", 'allowed [""]: ""', '(f(""), f("x"))', "(true, false)", setup='let allowed = [""];\nlet f = make_filter(&allowed);'),
     T("empty_word_not_allowed", 'allowed ["a"]: ""', 'make_filter(&["a"])("")', "false"),
     T("unicode", 'allowed ["café"]: "café", "cafe"', '(f("café"), f("cafe"))', "(true, false)", setup='let allowed = ["café"];\nlet f = make_filter(&allowed);'),
     T("duplicates", 'allowed ["x", "x"]', 'make_filter(&["x", "x"])("x")', "true"),
     T("word_from_a_short_string", "the word is a String dropped right after the call", "ok", "true",
       setup='let allowed = ["tmp"];\nlet f = make_filter(&allowed);\nlet ok = { let w = String::from("tmp"); f(&w) };'),
     T("whitespace_matters", 'allowed ["a"]: " a"', 'make_filter(&["a"])(" a")', "false"),
     T("many_allowed", "allowed n0..n999, ask n999 and n1000", '(f("n999"), f("n1000"))', "(true, false)",
       setup='let owned: Vec<String> = (0..1000).map(|i| format!("n{i}")).collect();\nlet allowed: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();\nlet f = make_filter(&allowed);'),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(320);
         for _ in 0..300 {
             let n = rng.below(4);
             let owned: Vec<String> = (0..n).map(|_| { let len = rng.below(3); rng.string(len, "ab") }).collect();
             let allowed: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
             let len = rng.below(3);
             let word = rng.string(len, "ab");
             let f = make_filter(&allowed);
             check!(format!("allowed = {allowed:?}, word = {word:?}"), f(&word), allowed.contains(&word.as_str()));
         }
     }
     """],
    [("rust", "`Box<dyn Trait>` with no lifetime means `Box<dyn Trait + 'static>`: the closure may not borrow anything short-lived."),
     ("rust", "Add a lifetime bound to the trait object: `+ 'a`. `+ '_` won't do here, because `&[&str]` has two elided lifetimes."),
     ("rust", "`&'a [&str]` implies the inner strings outlive `'a`, so naming just the outer one is enough.")],
    ("Trait objects carry a lifetime bound, just like references. The default in a `Box` is `'static`; a closure capturing `allowed` lives only as long as `allowed`, so the box has to say so.", "O(k) per call", "O(1)"),
    "When would you return `impl Fn(&str) -> bool + 'a` instead of a Box?",
    ["Default `'static` bounds on boxed trait objects.", "`+ 'a` for trait objects that borrow."],
    rules=dict(lines=1),
    wrong=dict(
        prefix_match="""
            /// A predicate that accepts exactly the words in `allowed`.
            pub fn make_filter<'a>(allowed: &'a [&str]) -> Box<dyn Fn(&str) -> bool + 'a> {
                Box::new(move |w| allowed.iter().any(|&a| a.starts_with(w)))
            }
        """,
        ignores_case="""
            /// A predicate that accepts exactly the words in `allowed`.
            pub fn make_filter<'a>(allowed: &'a [&str]) -> Box<dyn Fn(&str) -> bool + 'a> {
                Box::new(move |w| allowed.iter().any(|&a| a.eq_ignore_ascii_case(w)))
            }
        """,
    ),
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
    if p.get("wrong") is None:
        p.pop("wrong", None)

if __name__ == "__main__":
    n = write_track("l3-lifetimes", "L3", "Lifetimes", "L", "core", 3,
                    "Lifetimes say what a reference borrows from. Most of the work is choosing which input an output is tied to.",
                    STAGES, P)
    print("L3", n)
