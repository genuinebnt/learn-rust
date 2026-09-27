from author import T, write_track

P = []


def fix(slug, title, level, stage, tags, statement, starter, solution, visible, hidden, hints, notes, follow_up, teaches, rules=None, related=("L5",), source=None, wrong=None):
    return dict(slug=slug, title=title, mode="fix", level=level, stage=stage, tags=tags, statement=statement, starter=starter,
                solution=solution, visible=visible, hidden=hidden, hints=hints, notes=notes, follow_up=follow_up,
                teaches=teaches, rules=rules, related=list(related), source=source, wrong=wrong)


def write(slug, title, level, stage, tags, statement, starter, solution, visible, hidden, hints, notes, follow_up, teaches, related=("L5",), source=None, examples=(), wrong=None):
    return dict(slug=slug, title=title, level=level, stage=stage, tags=tags, statement=statement, starter=starter,
                solution=solution, visible=visible, hidden=hidden, hints=hints, notes=notes, follow_up=follow_up,
                teaches=teaches, related=list(related), source=source, examples=list(examples), wrong=wrong)



# ---------------------------------------------------------------- generic code (easy)
# The easy band is recall under pressure: each problem makes you write several generic constructs from memory.

STACK_CORE = """
use std::fmt;

/// A LIFO stack. Iterating yields items top first, the order `pop` would give them.
#[derive(Debug{derive_default})]
pub struct Stack<T> {{
    items: Vec<T>,
}}

impl<T> Stack<T> {{
    pub fn new() -> Self {{
        Stack {{ items: Vec::new() }}
    }}

    pub fn push(&mut self, item: T) {{
        self.items.push(item);
    }}

    pub fn pop(&mut self) -> Option<T> {{
        self.items.pop()
    }}

    pub fn peek(&self) -> Option<&T> {{
        self.items.last()
    }}

    pub fn len(&self) -> usize {{
        self.items.len()
    }}

    pub fn is_empty(&self) -> bool {{
        self.items.is_empty()
    }}
}}
"""


def stack_solution(own_iter="self.items.into_iter().rev()", own_ty="std::iter::Rev<std::vec::IntoIter<T>>",
                   ref_iter="self.items.iter().rev()", ref_ty="std::iter::Rev<std::slice::Iter<'a, T>>",
                   display_bound="fmt::Display", item_fmt='write!(f, "{x}")?;', display_iter="self"):
    return STACK_CORE.format(derive_default="") + f"""
// derive(Default) would add `T: Default`; an empty stack needs nothing from T.
impl<T> Default for Stack<T> {{
    fn default() -> Self {{
        Stack::new()
    }}
}}

/// Pushes in iteration order, so the last item ends up on top.
impl<T> FromIterator<T> for Stack<T> {{
    fn from_iter<I: IntoIterator<Item = T>>(iter: I) -> Self {{
        Stack {{ items: iter.into_iter().collect() }}
    }}
}}

impl<T> Extend<T> for Stack<T> {{
    fn extend<I: IntoIterator<Item = T>>(&mut self, iter: I) {{
        self.items.extend(iter);
    }}
}}

impl<T> IntoIterator for Stack<T> {{
    type Item = T;
    type IntoIter = {own_ty};

    fn into_iter(self) -> Self::IntoIter {{
        {own_iter}
    }}
}}

impl<'a, T> IntoIterator for &'a Stack<T> {{
    type Item = &'a T;
    type IntoIter = {ref_ty};

    fn into_iter(self) -> Self::IntoIter {{
        {ref_iter}
    }}
}}

/// `[top, ..., bottom]`
impl<T: {display_bound}> fmt::Display for Stack<T> {{
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {{
        write!(f, "[")?;
        for (i, x) in {display_iter}.into_iter().enumerate() {{
            if i > 0 {{
                write!(f, ", ")?;
            }}
            {item_fmt}
        }}
        write!(f, "]")
    }}
}}
"""


STACK_TOKEN = """
/// No derives at all: not Default, Clone, Debug or Display.
struct Token(u32);
"""

P.append(fix(
    "stack-plugs-into-std", "Stack<T> that plugs into std", "easy", "generic-code", ["generic impls", "IntoIterator", "FromIterator", "derive bounds"],
    """
        `Stack<T>` works, but it doesn't fit in with std, so the tests don't compile. Make these work for **any** `T`
        (the tests use a `Token` type with no derives):

        - `Stack::default()`;
        - `collect()` into a `Stack` and `extend` one (items are pushed in order, so the last one ends up on top);
        - `for x in stack` and `for x in &stack`, both **top first**;
        - `{}` printing as `[top, ..., bottom]` whenever `T: Display`.
    """,
    STACK_CORE.format(derive_default=", Default") + """
// TODO: Default, FromIterator, Extend, IntoIterator (by value and by reference), Display.
""",
    stack_solution(),
    [STACK_TOKEN,
     T("collect_then_pop", "(1..=3).collect(), then pop", "(s.pop(), s.len())", "(Some(3), 2)", setup="let mut s: Stack<i32> = (1..=3).collect();"),
     T("into_iter_top_first", "collect [1, 2, 3], then into_iter", "s.into_iter().collect::<Vec<_>>()", "vec![3, 2, 1]", setup="let s: Stack<i32> = vec![1, 2, 3].into_iter().collect();"),
     T("borrowing_loop", "for x in &s over [1, 2, 3], then len", "(seen, s.len())", "(vec![3, 2, 1], 3)",
       setup="let s: Stack<i32> = vec![1, 2, 3].into_iter().collect();\nlet mut seen = Vec::new();\nfor x in &s {\n    seen.push(*x);\n}"),
     T("display", "[1, 2, 3] and an empty stack", "(s.to_string(), Stack::<i32>::new().to_string())", '("[3, 2, 1]".to_string(), "[]".to_string())',
       setup="let s: Stack<i32> = vec![1, 2, 3].into_iter().collect();"),
     T("default_for_any_t", "Stack::<Token>::default(), push Token(7)", "(s.len(), s.pop().map(|t| t.0))", "(1, Some(7))",
       setup="let mut s = Stack::<Token>::default();\ns.push(Token(7));")],
    [STACK_TOKEN,
     T("extend_pushes_in_order", "push 1, extend [2, 3], pop", "(s.pop(), s.len())", "(Some(3), 2)",
       setup="let mut s = Stack::new();\ns.push(1);\ns.extend(vec![2, 3]);"),
     T("display_strings", 'collect ["a", "b"] as Strings', "s.to_string()", '"[b, a]"',
       setup='let s: Stack<String> = vec!["a".to_string(), "b".to_string()].into_iter().collect();'),
     T("display_nested", "a Stack<Stack<i32>>: push [1, 2], then an empty stack", "s.to_string()", '"[[], [2, 1]]"',
       setup="let mut s: Stack<Stack<i32>> = Stack::new();\ns.push(vec![1, 2].into_iter().collect());\ns.push(Stack::new());"),
     T("empty_iterations", "empty Stack<i32>: by-ref and by-value iteration", "((&s).into_iter().count(), s.into_iter().count())", "(0, 0)",
       setup="let s: Stack<i32> = Stack::default();"),
     T("collect_empty", "collect an empty iterator", "(s.is_empty(), s.peek().is_none())", "(true, true)",
       setup="let s: Stack<u8> = std::iter::empty().collect();"),
     T("no_clone_needed", "Tokens: collect, iterate by ref, then by value", "(by_ref, by_val)", "(vec![3, 2, 1], vec![3, 2, 1])",
       setup="let s: Stack<Token> = (1..=3).map(Token).collect();\nlet by_ref: Vec<u32> = (&s).into_iter().map(|t| t.0).collect();\nlet by_val: Vec<u32> = s.into_iter().map(|t| t.0).collect();"),
     T("first_of_into_iter_is_peek", "collect \"xyz\" chars", "(s.peek().copied(), s.into_iter().next())", "(Some('z'), Some('z'))",
       setup="let s: Stack<char> = \"xyz\".chars().collect();"),
     T("extend_with_strings_by_ref_loop", "extend with words, then sum lengths by ref", "(total, s.len())", "(10, 3)",
       setup='let mut s: Stack<String> = Stack::new();\ns.extend("one three ab".split(\' \').map(String::from));\nlet mut total = 0;\nfor w in &s {\n    total += w.len();\n}'),
     T("drops_unconsumed_items", "Rc clones: take one from into_iter, drop the rest", "std::rc::Rc::strong_count(&rc)", "1",
       setup="let rc = std::rc::Rc::new(0);\nlet s: Stack<std::rc::Rc<i32>> = (0..3).map(|_| rc.clone()).collect();\nlet mut it = s.into_iter();\nlet first = it.next();\ndrop(it);\ndrop(first);"),
     """
     #[test]
     fn random_vs_vec_model() {
         let mut rng = anneal_prelude::Rng::new(4501);
         for _ in 0..300 {
             let n = rng.below(6);
             let start: Vec<i32> = rng.vec(n, -9, 9);
             let m = rng.below(4);
             let more: Vec<i32> = rng.vec(m, -9, 9);
             let mut s: Stack<i32> = start.clone().into_iter().collect();
             s.extend(more.clone());
             let mut model = start.clone();
             model.extend(more.clone());
             let top_first: Vec<i32> = model.iter().rev().copied().collect();
             let shown = format!("[{}]", top_first.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(", "));
             let by_ref: Vec<i32> = (&s).into_iter().copied().collect();
             let text = s.to_string();
             let by_val: Vec<i32> = s.into_iter().collect();
             check!(format!("collect {start:?}, extend {more:?}"), (by_ref, text, by_val), (top_first.clone(), shown, top_first));
         }
     }
     """],
    [("rust", "`#[derive(Default)]` expands to `impl<T: Default> Default for Stack<T>`. Write the impl by hand with no bound."),
     ("rust", "`IntoIterator` has two associated types. By value: `type IntoIter = Rev<vec::IntoIter<T>>`. By reference: `impl<'a, T> IntoIterator for &'a Stack<T>` with `type Item = &'a T`."),
     ("rust", "`FromIterator` and `Extend` each have one generic method: `fn from_iter<I: IntoIterator<Item = T>>(iter: I) -> Self`.")],
    ("""Each trait is a generic impl on `Stack<T>`; only `Display` needs a bound, so only that impl has one. Syntax to remember:
`impl<T> FromIterator<T> for Stack<T> { fn from_iter<I: IntoIterator<Item = T>>(iter: I) -> Self }`,
`impl<'a, T> IntoIterator for &'a Stack<T> { type Item = &'a T; type IntoIter = Rev<slice::Iter<'a, T>>; fn into_iter(self) -> Self::IntoIter }`,
`impl<T: fmt::Display> fmt::Display for Stack<T> { fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result }`.""", "O(1) amortised per push; O(n) to iterate", "O(n)"),
    "Why does `derive(Clone)` on `struct Wrapper<T>(Rc<T>)` require `T: Clone`, and what would you write instead?",
    ["Derives add a bound on every type parameter; hand-written impls don't have to.", "`IntoIterator` for `Stack<T>` and for `&'a Stack<T>`, with their associated types.", "`FromIterator` / `Extend` make `collect()` and `extend()` work."],
    source="W1", related=("L5", "S6", "L4"),
    wrong=dict(
        bottom_first=stack_solution(own_iter="self.items.into_iter()", own_ty="std::vec::IntoIter<T>", ref_iter="self.items.iter()", ref_ty="std::slice::Iter<'a, T>"),
        display_bottom_first=stack_solution(display_iter="self.items.iter()"),
        debug_display=stack_solution(display_bound="fmt::Debug", item_fmt='write!(f, "{x:?}")?;'),
    ),
))

VEC2_HEAD = """
use std::iter::Sum;
use std::ops::{Add, AddAssign, Mul, Neg, Sub};

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Vec2<T> {
    pub x: T,
    pub y: T,
}

impl<T> Vec2<T> {
    pub fn new(x: T, y: T) -> Self {
        Vec2 { x, y }
    }
}
"""


def vec2(trait_decl="pub trait Dot<Rhs> {", add="impl<T> Add for Vec2<T> {", sub="impl<T> Sub for Vec2<T> {", neg="impl<T> Neg for Vec2<T> {",
         mul="impl<T> Mul<T> for Vec2<T> {", mul_body="Vec2::new(self.x * k, self.y * k)", add_assign="impl<T> AddAssign for Vec2<T> {",
         sum="impl<T> Sum for Vec2<T> {", sum_body="iter.fold(Vec2::new(T::default(), T::default()), |acc, v| acc + v)",
         dot="impl<T> Dot for Vec2<T> {", dot_body="self.x * rhs.x + self.y * rhs.y"):
    return VEC2_HEAD + f"""
/// `a.dot(b)`: the dot product.
{trait_decl}
    type Output;
    fn dot(self, rhs: Rhs) -> Self::Output;
}}

{add}
    type Output = Vec2<T>;
    fn add(self, rhs: Self) -> Self::Output {{
        Vec2::new(self.x + rhs.x, self.y + rhs.y)
    }}
}}

{sub}
    type Output = Vec2<T>;
    fn sub(self, rhs: Self) -> Self::Output {{
        Vec2::new(self.x - rhs.x, self.y - rhs.y)
    }}
}}

{neg}
    type Output = Vec2<T>;
    fn neg(self) -> Self::Output {{
        Vec2::new(-self.x, -self.y)
    }}
}}

/// Scales both parts: `v * k`.
{mul}
    type Output = Vec2<T>;
    fn mul(self, k: T) -> Self::Output {{
        {mul_body}
    }}
}}

{add_assign}
    fn add_assign(&mut self, rhs: Self) {{
        self.x += rhs.x;
        self.y += rhs.y;
    }}
}}

/// The sum of no vectors is (0, 0).
{sum}
    fn sum<I: Iterator<Item = Self>>(iter: I) -> Self {{
        {sum_body}
    }}
}}

{dot}
    type Output = T;
    fn dot(self, rhs: Self) -> T {{
        {dot_body}
    }}
}}
"""


VEC2_OK = dict(trait_decl="pub trait Dot<Rhs = Self> {", add="impl<T: Add<Output = T>> Add for Vec2<T> {", sub="impl<T: Sub<Output = T>> Sub for Vec2<T> {",
               neg="impl<T: Neg<Output = T>> Neg for Vec2<T> {", mul="impl<T: Mul<Output = T> + Copy> Mul<T> for Vec2<T> {",
               add_assign="impl<T: AddAssign> AddAssign for Vec2<T> {", sum="impl<T: Add<Output = T> + Default> Sum for Vec2<T> {",
               dot="impl<T: Mul<Output = T> + Add<Output = T>> Dot for Vec2<T> {")

BIG = """
/// A number that is not Copy or Clone.
#[derive(Debug, PartialEq, Default)]
struct Big(i128);

impl std::ops::Add for Big {
    type Output = Big;
    fn add(self, o: Big) -> Big {
        Big(self.0 + o.0)
    }
}

impl std::ops::Sub for Big {
    type Output = Big;
    fn sub(self, o: Big) -> Big {
        Big(self.0 - o.0)
    }
}

impl std::ops::Neg for Big {
    type Output = Big;
    fn neg(self) -> Big {
        Big(-self.0)
    }
}

impl std::ops::AddAssign for Big {
    fn add_assign(&mut self, o: Big) {
        self.0 += o.0;
    }
}

impl std::ops::Mul for Big {
    type Output = Big;
    fn mul(self, o: Big) -> Big {
        Big(self.0 * o.0)
    }
}

/// Works for any type whose dot product is with itself: needs `Dot`'s default type parameter.
fn len_sq<V: Dot + Copy>(v: V) -> V::Output {
    v.dot(v)
}
"""

P.append(fix(
    "fix-vec2-operators", "Fix: operators on Vec2<T> (E0369)", "easy", "generic-code", ["E0369", "operator traits", "Output = T", "default type parameters"],
    """
        `Vec2<T>` implements `+`, `-`, unary `-`, `v * k`, `+=`, `.sum()` and `a.dot(b)`, but none of it compiles. Add the
        bounds each impl needs, and no more: the tests use a number type that is neither `Copy` nor `Clone`. The tests
        also write the bound `V: Dot`, with no type argument.
    """,
    vec2(),
    vec2(**VEC2_OK),
    [BIG,
     T("add", "(1, 2) + (3, 4)", "Vec2::new(1, 2) + Vec2::new(3, 4)", "Vec2::new(4, 6)"),
     T("scale", "(1.5, -2.0) * 2.0", "Vec2::new(1.5, -2.0) * 2.0", "Vec2::new(3.0, -4.0)"),
     T("neg_and_sub", "-(1, 2) - (3, 4)", "-Vec2::new(1, 2) - Vec2::new(3, 4)", "Vec2::new(-4, -6)"),
     T("sum", "[(1, 1), (2, 3), (-1, 0)].sum()", "vec![Vec2::new(1, 1), Vec2::new(2, 3), Vec2::new(-1, 0)].into_iter().sum::<Vec2<i32>>()", "Vec2::new(2, 4)"),
     T("dot_with_default_rhs", "len_sq((3, 4)), where len_sq takes V: Dot", "len_sq(Vec2::new(3, 4))", "25"),
     T("no_copy_needed", "Big values: (a + b - c), then += and neg", "-v",
       "Vec2::new(Big(-6), Big(-9))", setup="let mut v = Vec2::new(Big(1), Big(2)) + Vec2::new(Big(3), Big(4)) - Vec2::new(Big(0), Big(1));\nv += Vec2::new(Big(2), Big(4));")],
    [BIG,
     T("add_assign", "(1, 2) += (10, 20)", "v", "Vec2::new(11, 22)", setup="let mut v = Vec2::new(1, 2);\nv += Vec2::new(10, 20);"),
     T("empty_sum_is_zero", "an empty iterator of Vec2<f64>", "std::iter::empty::<Vec2<f64>>().sum::<Vec2<f64>>()", "Vec2::new(0.0, 0.0)"),
     T("dot_floats", "(0.5, 2.0) . (4.0, -1.0)", "Vec2::new(0.5, 2.0).dot(Vec2::new(4.0, -1.0))", "0.0"),
     T("wrapping", "Wrapping(250u8) + Wrapping(10u8) per part", "Vec2::new(Wrapping(250u8), Wrapping(1u8)) + Vec2::new(Wrapping(10u8), Wrapping(1u8))",
       "Vec2::new(Wrapping(4u8), Wrapping(2u8))", setup="use std::num::Wrapping;"),
     T("big_sum", "Big values summed", "vec![Vec2::new(Big(1), Big(2)), Vec2::new(Big(3), Big(4))].into_iter().sum::<Vec2<Big>>()", "Vec2::new(Big(4), Big(6))"),
     T("big_dot", "Big (2, 3) . (4, 5)", "Vec2::new(Big(2), Big(3)).dot(Vec2::new(Big(4), Big(5)))", "Big(23)"),
     T("scale_by_zero", "(7, -7) * 0", "Vec2::new(7, -7) * 0", "Vec2::new(0, 0)"),
     T("nested_vectors", "Vec2<Vec2<i32>> addition", "Vec2::new(Vec2::new(1, 2), Vec2::new(3, 4)) + Vec2::new(Vec2::new(10, 20), Vec2::new(30, 40))",
       "Vec2::new(Vec2::new(11, 22), Vec2::new(33, 44))"),
     T("dot_negative", "(-2, 3) . (4, 5)", "Vec2::new(-2, 3).dot(Vec2::new(4, 5))", "7"),
     T("i64_extremes", "(i64::MAX - 1, 0) + (1, i64::MIN)", "Vec2::new(i64::MAX - 1, 0) + Vec2::new(1, i64::MIN)", "Vec2::new(i64::MAX, i64::MIN)"),
     """
     #[test]
     fn random_vs_tuples() {
         let mut rng = anneal_prelude::Rng::new(4502);
         for _ in 0..300 {
             let (ax, ay, bx, by, k) = (rng.int(-99, 99), rng.int(-99, 99), rng.int(-99, 99), rng.int(-99, 99), rng.int(-9, 9));
             let (a, b) = (Vec2::new(ax, ay), Vec2::new(bx, by));
             let mut c = a;
             c += b;
             check!(format!("a = ({ax}, {ay}), b = ({bx}, {by}), k = {k}"),
                    (a + b, a - b, -a, a * k, c, vec![a, b, a].into_iter().sum::<Vec2<i64>>(), a.dot(b), len_sq(b)),
                    (Vec2::new(ax + bx, ay + by), Vec2::new(ax - bx, ay - by), Vec2::new(-ax, -ay), Vec2::new(ax * k, ay * k),
                     Vec2::new(ax + bx, ay + by), Vec2::new(2 * ax + bx, 2 * ay + by), ax * bx + ay * by, bx * bx + by * by));
         }
     }
     """],
    [("rust", "`T: Add` isn't enough: `x + y` then has type `<T as Add>::Output`, not `T`. Pin it with `T: Add<Output = T>`."),
     ("rust", "Only `v * k` uses a value twice (`k`), so only that impl needs `Copy`. `+=` needs `AddAssign`, `.sum()` needs a zero: `Default`."),
     ("rust", "`V: Dot` with no argument only works if the trait declares a default: `trait Dot<Rhs = Self>`.")],
    ("""Each impl asks for exactly what its body does. Syntax to remember: `impl<T: Add<Output = T>> Add for Vec2<T>` (associated-type binding in a bound); `trait Dot<Rhs = Self>` (default type parameter, as std's `Add<Rhs = Self>`); `impl<T: Mul<Output = T> + Copy> Mul<T> for Vec2<T>` (a non-default `Rhs`). Adding `Copy` everywhere would compile, but it would leak into every caller and shut out `Big`, `BigInt` and friends.""", "O(1) per operation", "O(1)"),
    "Why is `Add` declared as `trait Add<Rhs = Self>` with an associated `Output`, instead of `trait Add<Rhs, Output>`?",
    ["Operator traits: `Add<Output = T>` bindings.", "Default type parameters (`Rhs = Self`).", "The weakest bound per impl; don't make every caller pay for `Copy`."],
    related=("L5", "L4"),
    wrong=dict(
        cross_not_dot=vec2(**{**VEC2_OK, "dot_body": "self.x * rhs.y + self.y * rhs.x"}),
        scales_only_x=vec2(**{**VEC2_OK, "mul_body": "Vec2::new(self.x * k, self.y)"}),
        sum_without_zero=vec2(**{**VEC2_OK, "sum": "impl<T: Add<Output = T>> Sum for Vec2<T> {", "sum_body": "iter.reduce(|acc, v| acc + v).expect(\"empty sum\")"}),
    ),
))


def parse_list(generic=True, index="index", source_body="Some(source)", display_item='write!(f, "item {index}: {source}")'):
    if not generic:
        return """
use std::error::Error;
use std::fmt;
use std::num::ParseIntError;

#[derive(Debug, PartialEq)]
pub enum ParseListError {
    /// Nothing but whitespace.
    Empty,
    /// The item at `index` (0-based) didn't parse.
    Bad { index: usize, source: ParseIntError },
}

impl fmt::Display for ParseListError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            ParseListError::Empty => write!(f, "empty list"),
            ParseListError::Bad { index, source } => write!(f, "item {index}: {source}"),
        }
    }
}

impl Error for ParseListError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            ParseListError::Empty => None,
            ParseListError::Bad { source, .. } => Some(source),
        }
    }
}

/// Parses comma-separated items, trimming each one.
pub fn parse_list(s: &str) -> Result<Vec<i32>, ParseListError> {
    if s.trim().is_empty() {
        return Err(ParseListError::Empty);
    }
    s.split(',')
        .enumerate()
        .map(|(index, item)| item.trim().parse().map_err(|source| ParseListError::Bad { index, source }))
        .collect()
}
"""
    return f"""
use std::error::Error;
use std::fmt;
use std::str::FromStr;

#[derive(Debug, PartialEq)]
pub enum ParseListError<E> {{
    /// Nothing but whitespace.
    Empty,
    /// The item at `index` (0-based) didn't parse.
    Bad {{ index: usize, source: E }},
}}

impl<E: fmt::Display> fmt::Display for ParseListError<E> {{
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {{
        match self {{
            ParseListError::Empty => write!(f, "empty list"),
            ParseListError::Bad {{ index, source }} => {display_item},
        }}
    }}
}}

// `source` hands out `&(dyn Error + 'static)`, so E must be 'static too.
impl<E: Error + 'static> Error for ParseListError<E> {{
    fn source(&self) -> Option<&(dyn Error + 'static)> {{
        match self {{
            ParseListError::Empty => None,
            ParseListError::Bad {{ source, .. }} => {source_body},
        }}
    }}
}}

/// Parses comma-separated items, trimming each one.
pub fn parse_list<T: FromStr>(s: &str) -> Result<Vec<T>, ParseListError<T::Err>> {{
    if s.trim().is_empty() {{
        return Err(ParseListError::Empty);
    }}
    s.split(',')
        .enumerate()
        .map(|(index, item)| item.trim().parse().map_err(|source| ParseListError::Bad {{ index: {index}, source }}))
        .collect()
}}
"""


CSV_TYPES = """
/// A FromStr type whose error is a plain String (not an Error).
#[derive(Debug, PartialEq)]
struct Even(u32);

impl std::str::FromStr for Even {
    type Err = String;
    fn from_str(s: &str) -> Result<Even, String> {
        match s.parse::<u32>() {
            Ok(n) if n % 2 == 0 => Ok(Even(n)),
            _ => Err(format!("{s:?} is not even")),
        }
    }
}
"""

P.append(fix(
    "fix-generic-parse-list", "Fix: make parse_list generic", "easy", "generic-code", ["generic enums", "turbofish", "associated types", "Error"],
    """
        `parse_list` only parses `i32`. The tests call `parse_list::<T>(s)` for any `T: FromStr`, and expect
        `ParseListError<E>` to carry `T`'s own error type: `ParseListError<ParseIntError>`,
        `ParseListError<ParseBoolError>`, `ParseListError<String>`, and so on.

        Keep `Display` working whenever `E` is `Display`, and `Error` (with `source()`) whenever `E` is an `Error`, so
        `?` still converts it into `Box<dyn Error>`.
    """,
    parse_list(generic=False),
    parse_list(),
    [CSV_TYPES,
     T("integers", 'parse_list::<i32>("1, 2,3")', 'parse_list::<i32>("1, 2,3")', "Ok(vec![1, 2, 3])"),
     T("floats", 'parse_list::<f64>(" 0.5 ,-2")', 'parse_list::<f64>(" 0.5 ,-2")', "Ok(vec![0.5, -2.0])"),
     T("bad_bool", 'parse_list::<bool>("true, yes")', 'parse_list::<bool>("true, yes")', 'Err(ParseListError::Bad { index: 1, source: "yes".parse::<bool>().unwrap_err() })'),
     T("empty", 'parse_list::<u8>("  ")', 'parse_list::<u8>("  ")', "Err(ParseListError::Empty)"),
     T("error_that_is_not_an_error", 'parse_list::<Even>("2, 3"): E = String', 'parse_list::<Even>("2, 3").map_err(|e| e.to_string())', 'Err("item 1: \\"3\\" is not even".to_string())'),
     T("question_mark_into_box_dyn_error", 'sum parse_list::<i64>("4, x") through ?', "run().map_err(|e| (e.to_string(), e.source().map(|s| s.to_string())))",
       'Err(("item 1: invalid digit found in string".to_string(), Some("invalid digit found in string".to_string())))',
       setup='use std::error::Error;\nfn run() -> Result<i64, Box<dyn Error>> {\n    Ok(parse_list::<i64>("4, x")?.iter().sum())\n}')],
    [CSV_TYPES,
     T("single", 'parse_list::<u64>("18446744073709551615")', 'parse_list::<u64>("18446744073709551615")', "Ok(vec![u64::MAX])"),
     T("overflow", 'parse_list::<u8>("1,256")', 'parse_list::<u8>("1,256").map_err(|e| e.to_string())', 'Err("item 1: number too large to fit in target type".to_string())'),
     T("empty_item", 'parse_list::<i32>("1,,2")', 'parse_list::<i32>("1,,2").map_err(|e| e.to_string())', 'Err("item 1: cannot parse integer from empty string".to_string())'),
     T("first_bad_wins", 'parse_list::<i32>("a,b")', 'parse_list::<i32>("a,b").map_err(|e| e.to_string())', 'Err("item 0: invalid digit found in string".to_string())'),
     T("strings_never_fail", 'parse_list::<String>(" a , b ")', 'parse_list::<String>(" a , b ")', 'Ok(vec!["a".to_string(), "b".to_string()])'),
     T("chars", 'parse_list::<char>("é, x")', 'parse_list::<char>("é, x")', "Ok(vec!['é', 'x'])"),
     T("empty_string", 'parse_list::<i32>("")', 'parse_list::<i32>("")', "Err(ParseListError::Empty)"),
     T("even_ok", 'parse_list::<Even>("0,4")', 'parse_list::<Even>("0,4")', "Ok(vec![Even(0), Even(4)])"),
     T("empty_has_no_source", 'parse_list::<i32>(" ").source()', 'parse_list::<i32>(" ").unwrap_err().source().is_none()', "true", setup="use std::error::Error;"),
     T("source_is_the_item_error", 'parse_list::<std::net::Ipv4Addr>("1.2.3.4, 1.2.3")', 'parse_list::<std::net::Ipv4Addr>("1.2.3.4, 1.2.3").unwrap_err().source().map(|s| s.to_string())',
       'Some("invalid IPv4 address syntax".to_string())', setup="use std::error::Error;"),
     T("inferred_without_turbofish", 'let v: Vec<u16> = parse_list("7, 8")?', "v", "vec![7u16, 8]", setup='let v: Vec<u16> = parse_list("7, 8").unwrap();'),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(4503);
         for _ in 0..300 {
             let n = 1 + rng.below(4);
             let items: Vec<String> = (0..n).map(|_| if rng.below(5) == 0 { "x".to_string() } else { rng.int(-50, 50).to_string() }).collect();
             let s = items.join(" ,");
             let want = match items.iter().position(|x| x == "x") {
                 Some(i) => Err(format!("item {i}: invalid digit found in string")),
                 None => Ok(items.iter().map(|x| x.parse::<i8>().unwrap()).collect::<Vec<i8>>()),
             };
             check!(format!("s = {s:?}"), parse_list::<i8>(&s).map_err(|e| e.to_string()), want);
         }
     }
     """],
    [("rust", "Make the enum generic, `ParseListError<E>`, and return `ParseListError<T::Err>`: `T::Err` is `FromStr`'s associated error type."),
     ("rust", "Each impl gets its own bound: `impl<E: fmt::Display> fmt::Display for ParseListError<E>`, `impl<E: Error + 'static> Error for ParseListError<E>`."),
     ("edge", "`Even`'s error is a `String`, which isn't an `Error`. Don't require `T::Err: Error` on `parse_list` itself.")],
    ("""A generic error enum keeps the caller's error type instead of flattening it to a string. Syntax to remember: `pub enum ParseListError<E> { Empty, Bad { index: usize, source: E } }`; `pub fn parse_list<T: FromStr>(s: &str) -> Result<Vec<T>, ParseListError<T::Err>>`; calling with a turbofish, `parse_list::<i32>(s)`. `source()` returns `&(dyn Error + 'static)`, hence `E: Error + 'static` on that impl.""", "O(n)", "O(n)"),
    "Why does `Error::source` return `&(dyn Error + 'static)`? What would break for a borrowed error type like `E = &'a MyErr`?",
    ["Generic enums and per-impl bounds.", "Naming an associated type in a signature: `T::Err`.", "Turbofish: `parse_list::<T>(s)`."],
    related=("L5", "L8", "S1"),
    wrong=dict(
        one_based_index=parse_list(index="index + 1"),
        no_source=parse_list(source_body="{ let _ = source; None }"),
        display_hides_the_cause=parse_list(display_item='write!(f, "item {index}: bad value")'),
    ),
))


def max_by_key(bounds, body=None, doc="The item with the largest key; the first one on a tie. Calls `key` once per item."):
    body = body or """    let mut best = None;
    for item in items {
        let k = key(item);
        if best.as_ref().map_or(true, |(_, bk)| k > *bk) {
            best = Some((item, k));
        }
    }
    best.map(|(item, _)| item)"""
    return f"""
/// {doc}
pub fn max_by_key<T, K, F>(items: &[T], mut key: F) -> Option<&T>
where
{bounds}
{{
{body}
}}
"""


MBK_OK = "    F: FnMut(&T) -> &K,\n    K: Ord + ?Sized,"

PERSON = """
struct Person {
    name: String,
    age: u32,
    tags: Vec<i32>,
}

fn people() -> Vec<Person> {
    vec![
        Person { name: "ada".into(), age: 36, tags: vec![1, 5] },
        Person { name: "zed".into(), age: 31, tags: vec![1, 5, 0] },
        Person { name: "bob".into(), age: 36, tags: vec![2] },
    ]
}
"""

P.append(fix(
    "generic-max-by-key", "Generic max_by_key with borrowed keys", "medium", "generic-code", ["HRTB", "?Sized", "closures returning references"],
    """
        `max_by_key` returns the item with the largest key, the **first** one on a tie, calling `key` once per item.
        It's shaped like `Iterator::max_by_key`, so the key has to be an owned value. Callers want to compare by a
        field without cloning it: `max_by_key(&people, |p| p.name.as_str())`. Those calls don't compile.

        Change the signature so `key` returns a reference **into** the item, including to unsized data like `str`
        and `[i32]`. The body can stay as it is.
    """,
    max_by_key("    F: FnMut(&T) -> K,\n    K: Ord,"),
    max_by_key(MBK_OK),
    [PERSON,
     T("by_name", "people by name", "max_by_key(&v, |p| p.name.as_str()).map(|p| p.age)", "Some(31)", setup="let v = people();"),
     T("by_age_first_on_tie", "people by &age: ada and bob are both 36", "max_by_key(&v, |p| &p.age).map(|p| p.name.as_str())", 'Some("ada")', setup="let v = people();"),
     T("by_slice", "people by tags as &[i32] (lexicographic)", "max_by_key(&v, |p| p.tags.as_slice()).map(|p| p.name.as_str())", 'Some("bob")', setup="let v = people();"),
     T("empty", "no people", "max_by_key(&v, |p| p.name.as_str()).is_none()", "true", setup="let v: Vec<Person> = Vec::new();"),
     T("key_called_once_per_item", "count the calls over three people", "(best, calls)", '(Some("zed"), 3)',
       setup="let v = people();\nlet mut calls = 0;\nlet best = max_by_key(&v, |p| {\n    calls += 1;\n    p.name.as_str()\n}).map(|p| p.name.as_str());")],
    [PERSON,
     T("strings_by_str", '["pear", "Apple", "fig"] by as_str', 'max_by_key(&v, |s| s.as_str()).map(String::as_str)', 'Some("pear")',
       setup='let v = vec!["pear".to_string(), "Apple".to_string(), "fig".to_string()];'),
     T("tie_on_str_keys", '["b", "a", "b"] by as_str: which "b"?', "std::ptr::eq(max_by_key(&v, |s| s.as_str()).unwrap(), &v[0])", "true",
       setup='let v = vec!["b".to_string(), "a".to_string(), "b".to_string()];'),
     T("identity_on_integers", "[3, 9, 2] with |x| x", "max_by_key(&[3, 9, 2], |x| x)", "Some(&9)"),
     T("nested_field", "pairs by &pair.1", 'max_by_key(&v, |p| &p.1).map(|p| p.0)', "Some('b')", setup="let v = [('a', 1), ('b', 7), ('c', 7)];"),
     T("vec_of_vecs_by_slice", "[[1, 2], [1, 2, 0], [0, 9]] by as_slice", "max_by_key(&v, |x| x.as_slice())", "Some(&vec![1, 2, 0])",
       setup="let v = vec![vec![1, 2], vec![1, 2, 0], vec![0, 9]];"),
     T("single", "one person", "max_by_key(&v[..1], |p| p.name.as_str()).map(|p| p.age)", "Some(36)", setup="let v = people();"),
     T("unicode_str_keys", '["é", "z"] by as_str', 'max_by_key(&v, |s| s.as_str()).map(String::as_str)', 'Some("é")',
       setup='let v = vec!["é".to_string(), "z".to_string()];'),
     T("calls_on_empty", "no items: count the calls", "calls", "0",
       setup="let v: Vec<String> = Vec::new();\nlet mut calls = 0;\nlet _ = max_by_key(&v, |s| {\n    calls += 1;\n    s.as_str()\n});"),
     T("calls_with_ties", "five equal names: count the calls", "calls", "5",
       setup='let v = vec!["x".to_string(); 5];\nlet mut calls = 0;\nlet _ = max_by_key(&v, |s| {\n    calls += 1;\n    s.as_str()\n});'),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(4504);
         for _ in 0..300 {
             let n = rng.below(7);
             let words: Vec<String> = (0..n).map(|_| { let len = rng.below(3); rng.string(len, "ab") }).collect();
             let mut want: Option<usize> = None;
             for i in 0..n {
                 if want.map_or(true, |w| words[i] > words[w]) {
                     want = Some(i);
                 }
             }
             let mut calls = 0;
             let got = max_by_key(&words, |w| {
                 calls += 1;
                 w.as_str()
             });
             check!(format!("words = {words:?}"), (got.map(|r| r as *const String), calls), (want.map(|i| &words[i] as *const String), n));
         }
     }
     """],
    [("rust", "`F: FnMut(&T) -> K` means one `K` for every call, whatever the argument's lifetime, so `K` can't borrow from the argument. Tie the output to the input: `F: FnMut(&T) -> &K`."),
     ("rust", "Elided, `FnMut(&T) -> &K` is the higher-ranked `for<'a> FnMut(&'a T) -> &'a K`."),
     ("rust", "`K` is `str` or `[i32]` in the tests. Generic parameters are `Sized` unless you opt out: `K: Ord + ?Sized`.")],
    ("""The key closure must work for every borrow of an item, so its bound is higher-ranked: `for<'a> FnMut(&'a T) -> &'a K`, which the `Fn(&T) -> &K` sugar writes for you. `K: ?Sized` lets the key be `str` or `[T]` behind the reference. This is exactly why std's `max_by_key` can't return `p.name.as_str()`: its `B` is fixed before any item is borrowed.""", "O(n) key calls", "O(1)"),
    "Write the where clause with an explicit `for<'a>`. Why can't `Iterator::max_by_key` offer this signature?",
    ["Higher-ranked trait bounds: `for<'a> Fn(&'a T) -> &'a K`.", "`?Sized` for type parameters used only behind a reference."],
    rules=dict(lines=2),
    related=("L5", "L3", "L6"),
    wrong=dict(
        ties_go_last=max_by_key(MBK_OK, """    let mut best = None;
    for item in items {
        let k = key(item);
        if best.as_ref().map_or(true, |(_, bk)| k >= *bk) {
            best = Some((item, k));
        }
    }
    best.map(|(item, _)| item)"""),
        recomputes_best_key=max_by_key(MBK_OK, """    let mut best: Option<&T> = None;
    for item in items {
        if best.map_or(true, |b| key(item) > key(b)) {
            best = Some(item);
        }
    }
    best"""),
    ),
))

# ---------------------------------------------------------------- bounds & associated types (medium)


def report(fmt_body=None, generic=True):
    if not generic:
        return """
use std::fmt;

/// A titled list: the title, then one `- row` line per row.
pub struct Report<T> {
    title: String,
    rows: Vec<T>,
}

impl<T> Report<T> {
    pub fn new(title: &str, rows: Vec<T>) -> Self {
        Report { title: title.to_string(), rows }
    }

    pub fn rows(&self) -> &Vec<T> {
        &self.rows
    }
}

impl<T: fmt::Display> fmt::Display for Report<T> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.title)?;
        for row in &self.rows {
            write!(f, "\\n- {row}")?;
        }
        Ok(())
    }
}
"""
    fmt_body = fmt_body or """        write!(f, "{}", self.title)?;
        for row in &self.rows {
            write!(f, "\\n- {row}")?;
        }
        Ok(())"""
    return f"""
use std::fmt;

/// A titled list: the title, then one `- row` line per row.
pub struct Report<C> {{
    title: String,
    rows: C,
}}

impl<C> Report<C> {{
    pub fn new(title: &str, rows: C) -> Self {{
        Report {{ title: title.to_string(), rows }}
    }}

    pub fn rows(&self) -> &C {{
        &self.rows
    }}
}}

// `fmt` borrows `self` for a lifetime this impl can't name, so the bound must hold for every lifetime.
impl<C> fmt::Display for Report<C>
where
    for<'a> &'a C: IntoIterator,
    for<'a> <&'a C as IntoIterator>::Item: fmt::Display,
{{
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {{
{fmt_body}
    }}
}}
"""


EVENS = """
/// A collection that isn't Clone and whose by-reference items are owned u32s.
struct Evens(u32);

impl<'a> IntoIterator for &'a Evens {
    type Item = u32;
    type IntoIter = std::iter::StepBy<std::ops::Range<u32>>;
    fn into_iter(self) -> Self::IntoIter {
        (0..2 * self.0).step_by(2)
    }
}
"""

P.append(fix(
    "report-any-collection", "Fix: a Report over any collection (HRTB where clause)", "medium", "bounds-associated-types", ["where clauses", "HRTB", "IntoIterator"],
    """
        `Report` only holds a `Vec`. Make it hold any collection `C` (a `Vec`, an array, a `BTreeSet`, a `VecDeque`,
        an `Option`, or the tests' own `Evens`) and print whenever iterating `&C` yields printable items.

        Printing must not consume, clone or copy the rows: `rows()` still returns the collection afterwards, and
        `Evens` isn't `Clone`. The output format stays the same.
    """,
    report(generic=False),
    report(),
    [EVENS,
     T("vec", 'Report::new("Nums", vec![1, 2])', 'Report::new("Nums", vec![1, 2]).to_string()', '"Nums\\n- 1\\n- 2"'),
     T("empty_is_just_the_title", 'Report::new("None", Vec::<i32>::new())', 'Report::new("None", Vec::<i32>::new()).to_string()', '"None"'),
     T("btreeset_in_order", 'Report::new("Fruit", BTreeSet::from(["pear", "apple"]))', 'Report::new("Fruit", std::collections::BTreeSet::from(["pear", "apple"])).to_string()',
       '"Fruit\\n- apple\\n- pear"'),
     T("rows_still_there", "print a VecDeque report, then rows().len()", "(text, r.rows().len())", '("Q\\n- a\\n- b".to_string(), 2)',
       setup="let r = Report::new(\"Q\", std::collections::VecDeque::from(vec!['a', 'b']));\nlet text = r.to_string();"),
     T("own_collection", 'Report::new("Evens", Evens(3)): items are owned u32s', 'Report::new("Evens", Evens(3)).to_string()', '"Evens\\n- 0\\n- 2\\n- 4"')],
    [EVENS,
     T("array", 'Report::new("A", ["x", "y", "z"])', 'Report::new("A", ["x", "y", "z"]).to_string()', '"A\\n- x\\n- y\\n- z"'),
     T("option_some", 'Report::new("Maybe", Some(5))', 'Report::new("Maybe", Some(5)).to_string()', '"Maybe\\n- 5"'),
     T("option_none", 'Report::new("Maybe", None::<i32>)', 'Report::new("Maybe", None::<i32>).to_string()', '"Maybe"'),
     T("strings", 'Report::new("S", vec!["héllo".to_string()])', 'Report::new("S", vec!["héllo".to_string()]).to_string()', '"S\\n- héllo"'),
     T("nested_reports", "a Report of Reports", 'Report::new("outer", vec![Report::new("a", vec![1]), Report::new("b", vec![])]).to_string()', '"outer\\n- a\\n- 1\\n- b"'),
     T("empty_evens", 'Report::new("E", Evens(0))', 'Report::new("E", Evens(0)).to_string()', '"E"'),
     T("printed_twice", "print the same report twice", "(r.to_string(), r.to_string())", '("T\\n- 0".to_string(), "T\\n- 0".to_string())', setup='let r = Report::new("T", Evens(1));'),
     T("rows_returns_the_collection", "rows() of a BTreeSet report", "r.rows().iter().next().copied()", "Some(1)",
       setup='let r = Report::new("B", std::collections::BTreeSet::from([3, 1, 2]));\nlet _ = r.to_string();'),
     T("empty_title", 'Report::new("", vec![0])', 'Report::new("", vec![0]).to_string()', '"\\n- 0"'),
     """
     #[test]
     fn random_vs_format() {
         let mut rng = anneal_prelude::Rng::new(4505);
         for _ in 0..300 {
             let n = rng.below(5);
             let v: Vec<i32> = rng.vec(n, -99, 99);
             let mut want = String::from("R");
             for x in &v {
                 want.push_str(&format!("\\n- {x}"));
             }
             let r = Report::new("R", v.clone());
             check!(format!("rows = {v:?}"), (r.to_string(), r.rows().len()), (want, n));
         }
     }
     """],
    [("rust", "Store `rows: C`. The printing bound isn't on `C` but on `&C`: `&C: IntoIterator`, and its `Item: Display`."),
     ("rust", "Inside `fmt`, `&self.rows` has a lifetime the impl can't name. `impl<'a, C>` won't do; the bound has to hold for every lifetime: `where for<'a> &'a C: IntoIterator`."),
     ("rust", "Name the item type through the reference's impl: `for<'a> <&'a C as IntoIterator>::Item: fmt::Display`.")],
    ("""This is the classic use of a higher-ranked bound outside closures: 'iterating any borrow of `C` yields printable items'. Syntax to remember:
`impl<C> fmt::Display for Report<C> where for<'a> &'a C: IntoIterator, for<'a> <&'a C as IntoIterator>::Item: fmt::Display`.
Bounding `C: IntoIterator + Clone` would compile too, but it clones the whole collection on every print and shuts out `Evens`.""", "O(n) per print", "O(1)"),
    "Why doesn't `impl<'a, C> Display for Report<C> where &'a C: IntoIterator` work, even though a free function `fn show<'a, C>(c: &'a C)` could use that bound?",
    ["Higher-ranked bounds on a borrowed collection: `for<'a> &'a C: IntoIterator`.", "`where` clauses on projections: `<&'a C as IntoIterator>::Item`."],
    rules=dict(methods=["clone", "cloned", "to_vec", "to_owned"]),
    related=("L5", "L3", "S6"),
    wrong=dict(
        trailing_newline=report(fmt_body="""        writeln!(f, "{}", self.title)?;
        for row in &self.rows {
            writeln!(f, "- {row}")?;
        }
        Ok(())"""),
        comma_separated=report(fmt_body="""        write!(f, "{}", self.title)?;
        for (i, row) in (&self.rows).into_iter().enumerate() {
            write!(f, "{}{row}", if i == 0 { "\\n- " } else { ", " })?;
        }
        Ok(())"""),
    ),
))


def describe(fixed=True, none='"-"', sep='", "'):
    head = """
use std::fmt;

pub trait Describe {
    fn describe(&self) -> String;
}

/// A user name, shown in lowercase.
pub struct Name(pub String);

impl fmt::Display for Name {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.0.to_lowercase())
    }
}
"""
    if fixed:
        middle = """
// A blanket `impl<T: Display> Describe for T` would overlap the Vec and Option impls below (std may add
// `Display for Vec<_>` one day) and would stop other crates writing their own Describe for Display types.
macro_rules! describe_via_display {
    ($($t:ty),* $(,)?) => {
        $(
            impl Describe for $t {
                fn describe(&self) -> String {
                    self.to_string()
                }
            }
        )*
    };
}

describe_via_display!(i8, i16, i32, i64, i128, isize, u8, u16, u32, u64, u128, usize, f32, f64, bool, char, str, String, Name);

impl<T: Describe + ?Sized> Describe for &T {
    fn describe(&self) -> String {
        (**self).describe()
    }
}
"""
    else:
        middle = """
/// Anything printable describes itself with its Display text.
impl<T: fmt::Display> Describe for T {
    fn describe(&self) -> String {
        self.to_string()
    }
}
"""
    return head + middle + f"""
/// `[a, b, c]`
impl<T: Describe> Describe for Vec<T> {{
    fn describe(&self) -> String {{
        let parts: Vec<String> = self.iter().map(|x| x.describe()).collect();
        format!("[{{}}]", parts.join({sep}))
    }}
}}

/// The value, or `-` for None.
impl<T: Describe> Describe for Option<T> {{
    fn describe(&self) -> String {{
        match self {{
            Some(x) => x.describe(),
            None => {none}.to_string(),
        }}
    }}
}}
"""


CELSIUS = """
/// A type from "another crate" whose Describe differs from its Display.
struct Celsius(f64);

impl std::fmt::Display for Celsius {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl Describe for Celsius {
    fn describe(&self) -> String {
        format!("{}°C", self.0)
    }
}
"""

P.append(fix(
    "fix-conflicting-impls", "Fix: conflicting implementations (E0119)", "medium", "bounds-associated-types", ["E0119", "coherence", "blanket impls", "?Sized"],
    """
        `describe()` should work on the integer and float types, `bool`, `char`, `str`, `String`, `Name`, references to
        any of these, and `Vec<T>` / `Option<T>` of anything describable (nested too). Other crates must be able to
        implement `Describe` for their own types, even ones that already implement `Display`; the tests do.

        It doesn't compile. Keep every output format as it is.
    """,
    describe(fixed=False),
    describe(),
    [CELSIUS,
     T("scalars", "42i32, 2.5f64, true, 'x'", "(42i32.describe(), 2.5f64.describe(), true.describe(), 'x'.describe())",
       '("42".to_string(), "2.5".to_string(), "true".to_string(), "x".to_string())'),
     T("strings_and_name", '"hi", String "yo", Name("ADA")', '("hi".describe(), String::from("yo").describe(), Name("ADA".into()).describe())',
       '("hi".to_string(), "yo".to_string(), "ada".to_string())'),
     T("vec_and_option", "vec![1, 2], Some(3), None", "(vec![1, 2].describe(), Some(3).describe(), None::<i32>.describe())",
       '("[1, 2]".to_string(), "3".to_string(), "-".to_string())'),
     T("nested_with_refs", 'vec![Some("a"), None]', 'vec![Some("a"), None].describe()', '"[a, -]"'),
     T("your_own_impl", "Celsius(21.5): Display is 21.5, Describe is 21.5°C", "(Celsius(21.5).to_string(), vec![Celsius(21.5)].describe())",
       '("21.5".to_string(), "[21.5°C]".to_string())')],
    [CELSIUS,
     T("empty_vec", "Vec::<u8>::new()", "Vec::<u8>::new().describe()", '"[]"'),
     T("nested_vecs", "vec![vec![1], vec![], vec![2, 3]]", "vec![vec![1], vec![], vec![2, 3]].describe()", '"[[1], [], [2, 3]]"'),
     T("option_of_vec", "Some(vec![None, Some(1)])", "Some(vec![None, Some(1u64)]).describe()", '"[-, 1]"'),
     T("every_integer_width", "i8, i16, i64, i128, isize, u8, u16, u32, u128, usize", "vec![(-1i8).describe(), 2i16.describe(), (-3i64).describe(), 4i128.describe(), 5isize.describe(), 6u8.describe(), 7u16.describe(), 8u32.describe(), 9u128.describe(), 10usize.describe()].join(\" \")",
       '"-1 2 -3 4 5 6 7 8 9 10"'),
     T("f32", "0.5f32", "0.5f32.describe()", '"0.5"'),
     T("double_reference", '&&"x"', '(&&"x").describe()', '"x"'),
     T("vec_of_names", 'vec![Name("Bo"), Name("CY")]', 'vec![Name("Bo".into()), Name("CY".into())].describe()', '"[bo, cy]"'),
     T("option_of_celsius", "Some(Celsius(-4.0)), None", "(Some(Celsius(-4.0)).describe(), None::<Celsius>.describe())", '("-4°C".to_string(), "-".to_string())'),
     T("vec_of_strs_unicode", 'vec!["é", "ß"]', 'vec!["é", "ß"].describe()', '"[é, ß]"'),
     T("through_generic_fn", "a generic fn that takes T: Describe + ?Sized", 'show("str slice")', '"<str slice>"',
       setup="fn show<T: Describe + ?Sized>(x: &T) -> String {\n    format!(\"<{}>\", x.describe())\n}"),
     """
     #[test]
     fn random_vs_format() {
         let mut rng = anneal_prelude::Rng::new(4506);
         for _ in 0..300 {
             let n = rng.below(5);
             let v: Vec<Option<i64>> = (0..n).map(|_| if rng.bool() { Some(rng.int(-99, 99)) } else { None }).collect();
             let want = format!("[{}]", v.iter().map(|x| x.map_or("-".to_string(), |y| y.to_string())).collect::<Vec<_>>().join(", "));
             check!(format!("{v:?}"), v.describe(), want);
         }
     }
     """],
    [("rust", "Read the note on E0119: std may add `impl Display for Vec<_>` in a future version, and then your blanket impl and your `Vec` impl would both apply. Coherence rejects that now."),
     ("approach", "Drop the blanket impl. Implement `Describe` per concrete type instead: a small `macro_rules!` over a list of types avoids writing it out twenty times."),
     ("rust", "`\"a\"` inside a `Vec` is a `&str`, so add `impl<T: Describe + ?Sized> Describe for &T` (`?Sized` so `T` can be `str`).")],
    ("""A blanket impl claims every type that meets its bound, including types in other crates and types std might make `Display` later. Coherence must prove no two impls can ever overlap, so `impl<T: Display> Describe for T` rules out `impl<T> Describe for Vec<T>` and any downstream `impl Describe for Celsius`. Concrete impls (often macro-generated, as std does for integers) keep the trait open. Syntax to remember: `impl<T: Describe + ?Sized> Describe for &T`.""", "O(n) in the output size", "O(n)"),
    "Why does `impl<T: Display> Describe for T` conflict with `impl<T: Describe> Describe for Vec<T>` even though `Vec` isn't `Display` today?",
    ["Coherence and overlap: blanket impls vs specific impls (E0119).", "Macro-generated impls for a list of concrete types.", "`?Sized` on a forwarding impl for `&T`."],
    related=("L5", "L4", "L10"),
    wrong=dict(
        none_prints_none=describe(none='"None"'),
        no_space_after_comma=describe(sep='","'),
    ),
))

GRAPH_HEAD = """
use std::collections::{HashMap, HashSet, VecDeque};
use std::hash::Hash;

pub trait Graph {
    /// Each graph has one node type, so it's an associated type, not a parameter.
    type Node;

    fn neighbors(&self, node: &Self::Node) -> Vec<Self::Node>;
}

/// Nodes are 0..edges.len(); `edges[i]` lists the nodes `i` has an edge to. Edges are one-way.
pub struct AdjList {
    pub edges: Vec<Vec<usize>>,
}

/// Cells are `.` (open) or `#` (wall). Nodes are the (row, col) of open cells; moves go up, down, left or right.
pub struct Grid {
    cells: Vec<Vec<u8>>,
}
"""

GRAPH_STARTER = GRAPH_HEAD + """
impl Graph for AdjList {
    type Node = usize;

    fn neighbors(&self, node: &usize) -> Vec<usize> {
        todo!()
    }
}

impl Graph for Grid {
    type Node = (usize, usize);

    fn neighbors(&self, node: &(usize, usize)) -> Vec<(usize, usize)> {
        todo!()
    }
}

/// Rows separated by newlines.
impl From<&str> for Grid {
    fn from(text: &str) -> Self {
        todo!()
    }
}

/// One string per row.
impl From<Vec<&str>> for Grid {
    fn from(rows: Vec<&str>) -> Self {
        todo!()
    }
}

/// How many nodes can be reached from `start`, counting `start` itself.
pub fn reachable<G>(graph: &G, start: G::Node) -> usize
where
    G: Graph,
    G::Node: Eq + Hash + Clone,
{
    todo!()
}

/// The nodes on a shortest path from `from` to `to`, both included. None if `to` can't be reached.
pub fn shortest_path<G>(graph: &G, from: G::Node, to: G::Node) -> Option<Vec<G::Node>>
where
    G: Graph,
    G::Node: Eq + Hash + Clone,
{
    todo!()
}
"""


def graph_solution(grid_moves="[(0, 1), (1, 0), (0, -1), (-1, 0)]", visited="HashSet<G::Node> = HashSet::new()", count="seen.len()", adj="self.edges[*node].clone()", pop="queue.pop_front()"):
    return GRAPH_HEAD + f"""
impl Graph for AdjList {{
    type Node = usize;

    fn neighbors(&self, node: &usize) -> Vec<usize> {{
        {adj}
    }}
}}

impl Graph for Grid {{
    type Node = (usize, usize);

    fn neighbors(&self, node: &(usize, usize)) -> Vec<(usize, usize)> {{
        let (r, c) = *node;
        let mut out = Vec::new();
        for (dr, dc) in {grid_moves} {{
            let (nr, nc) = (r as isize + dr, c as isize + dc);
            if nr < 0 || nc < 0 {{
                continue;
            }}
            let (nr, nc) = (nr as usize, nc as usize);
            if self.cells.get(nr).and_then(|row| row.get(nc)) == Some(&b'.') {{
                out.push((nr, nc));
            }}
        }}
        out
    }}
}}

/// Rows separated by newlines.
impl From<&str> for Grid {{
    fn from(text: &str) -> Self {{
        Grid::from(text.lines().collect::<Vec<_>>())
    }}
}}

/// One string per row.
impl From<Vec<&str>> for Grid {{
    fn from(rows: Vec<&str>) -> Self {{
        Grid {{ cells: rows.iter().map(|r| r.as_bytes().to_vec()).collect() }}
    }}
}}

/// How many nodes can be reached from `start`, counting `start` itself.
pub fn reachable<G>(graph: &G, start: G::Node) -> usize
where
    G: Graph,
    G::Node: Eq + Hash + Clone,
{{
    let mut seen: {visited};
    seen.insert(start.clone());
    let mut stack = vec![start];
    while let Some(node) = stack.pop() {{
        for next in graph.neighbors(&node) {{
            if !seen.contains(&next) {{
                seen.insert(next.clone());
                stack.push(next);
            }}
        }}
    }}
    {count}
}}

/// The nodes on a shortest path from `from` to `to`, both included. None if `to` can't be reached.
pub fn shortest_path<G>(graph: &G, from: G::Node, to: G::Node) -> Option<Vec<G::Node>>
where
    G: Graph,
    G::Node: Eq + Hash + Clone,
{{
    // BFS; `parent` doubles as the seen set. The start maps to itself.
    let mut parent: HashMap<G::Node, G::Node> = HashMap::new();
    parent.insert(from.clone(), from.clone());
    let mut queue = VecDeque::from([from.clone()]);
    while let Some(node) = {pop} {{
        if node == to {{
            let mut path = vec![node];
            while *path.last().unwrap() != from {{
                let prev = parent[path.last().unwrap()].clone();
                path.push(prev);
            }}
            path.reverse();
            return Some(path);
        }}
        for next in graph.neighbors(&node) {{
            if !parent.contains_key(&next) {{
                parent.insert(next.clone(), node.clone());
                queue.push_back(next);
            }}
        }}
    }}
    None
}}
"""


GRAPH_SOLUTION = graph_solution()

LADDER = """
/// A word ladder: nodes are borrowed words, edges join words that differ in one letter.
struct Ladder<'w> {
    words: &'w [&'w str],
}

impl<'w> Graph for Ladder<'w> {
    type Node = &'w str;
    fn neighbors(&self, w: &&'w str) -> Vec<&'w str> {
        self.words
            .iter()
            .copied()
            .filter(|x| x.len() == w.len() && x.chars().zip(w.chars()).filter(|(a, b)| a != b).count() == 1)
            .collect()
    }
}

const WORDS: [&str; 10] = ["cold", "cord", "card", "ward", "warm", "worm", "word", "wore", "core", "bore"];
"""


P.append(write(
    "associated-type-vs-parameter", "Associated type vs type parameter", "medium", "bounds-associated-types", ["associated types", "From", "graph traversal"],
    """
        `Graph` has an **associated type** `Node`: a graph has exactly one node type, so callers never have to name
        it. `From<T>` has a **type parameter**: `Grid` implements it twice, once for `&str` and once for `Vec<&str>`.

        Implement both graphs and both conversions, then two functions that work on *any* `Graph` whose nodes are
        `Eq + Hash + Clone` (the tests define graphs of their own, including one whose nodes are borrowed `&str`s):

        - `reachable` counts the nodes reachable from `start`, including `start`;
        - `shortest_path` returns the nodes on a shortest path, both ends included (any shortest path will do).

        - `AdjList`: `edges[i]` lists the nodes `i` has a one-way edge to.
        - `Grid`: `.` is open, `#` is a wall. From an open cell you can move up, down, left or right onto an open
          cell. Rows may have different lengths; `start` is always an open cell.
    """,
    GRAPH_STARTER,
    GRAPH_SOLUTION,
    [LADDER,
     T("shortest_in_grid", '"...\\n.#.\\n..." from (0, 0) to (2, 2): length and ends', 'shortest_path(&Grid::from("...\\n.#.\\n..."), (0, 0), (2, 2)).map(|p| (p.len(), p[0], p[p.len() - 1]))',
       "Some((5, (0, 0), (2, 2)))"),
     T("unreachable_is_none", "edges [[1], [2], [], [0]], from 2 to 0", "shortest_path(&AdjList { edges: vec![vec![1], vec![2], vec![], vec![0]] }, 2, 0)", "None"),
     T("adj_list", "edges [[1], [2], [], [0]], start 0", "reachable(&AdjList { edges: vec![vec![1], vec![2], vec![], vec![0]] }, 0)", "3"),
     T("edges_are_one_way", "edges [[1], [2], [], [0]], start 2", "reachable(&AdjList { edges: vec![vec![1], vec![2], vec![], vec![0]] }, 2)", "1"),
     T("grid_from_str", '"..#\\n#..\\n##." from (0, 0)', 'reachable(&Grid::from("..#\\n#..\\n##."), (0, 0))', "5"),
     T("grid_from_rows", '["..", "#."] from (1, 1)', 'reachable(&Grid::from(vec!["..", "#."]), (1, 1))', "3"),
     T("your_graph_too", "a Collatz graph defined in the test, start 6", "reachable(&Collatz, 6)", "9",
       setup="struct Collatz;\nimpl Graph for Collatz {\n    type Node = u64;\n    fn neighbors(&self, n: &u64) -> Vec<u64> {\n        match *n {\n            1 => vec![],\n            n if n % 2 == 0 => vec![n / 2],\n            n => vec![3 * n + 1],\n        }\n    }\n}")],
    [LADDER,
     T("path_to_itself", "from 1 to 1", "shortest_path(&AdjList { edges: vec![vec![0], vec![0]] }, 1, 1)", "Some(vec![1])"),
     T("unique_path", "edges [[1], [2], [0, 3], []], from 0 to 3", "shortest_path(&AdjList { edges: vec![vec![1], vec![2], vec![0, 3], vec![]] }, 0, 3)", "Some(vec![0, 1, 2, 3])"),
     T("borrowed_nodes", "word ladder cold -> warm", 'shortest_path(&Ladder { words: &WORDS }, "cold", "warm").map(|p| (p.len(), p[0], p[p.len() - 1]))',
       'Some((5, "cold", "warm"))'),
     T("borrowed_nodes_reachable", "word ladder from bore", 'reachable(&Ladder { words: &WORDS }, "bore")', "10"),
     T("single_node", "edges [[]], start 0", "reachable(&AdjList { edges: vec![vec![]] }, 0)", "1"),
     T("self_loop_and_duplicates", "edges [[0, 1, 1], [0]]", "reachable(&AdjList { edges: vec![vec![0, 1, 1], vec![0]] }, 0)", "2"),
     T("cycle", "edges [[1], [2], [0]], start 1", "reachable(&AdjList { edges: vec![vec![1], vec![2], vec![0]] }, 1)", "3"),
     T("walled_in", '"###\\n#.#\\n###" from (1, 1)', 'reachable(&Grid::from("###\\n#.#\\n###"), (1, 1))', "1"),
     T("no_diagonal_moves", '".#\\n#." from (0, 0)', 'reachable(&Grid::from(".#\\n#."), (0, 0))', "1"),
     T("ragged_rows", '["...", ".", "..."] from (0, 2)', 'reachable(&Grid::from(vec!["...", ".", "..."]), (0, 2))', "7"),
     T("grid_neighbors", '"...\\n...\\n..." neighbors of (0, 0) and (1, 1)', "(g.neighbors(&(0, 0)).len(), g.neighbors(&(1, 1)).len())", "(2, 4)",
       setup='let g = Grid::from("...\\n...\\n...");'),
     T("adj_neighbors", "edges [[2, 1]] neighbors of 0", "AdjList { edges: vec![vec![2, 1], vec![], vec![]] }.neighbors(&0)", "vec![2, 1]"),
     T("node_without_copy_or_ord", "a graph whose nodes are Strings in a newtype with no Copy/Ord/Debug", 'reachable(&Words, Name("a".to_string()))', "3",
       setup='#[derive(Clone, PartialEq, Eq, Hash)]\nstruct Name(String);\nstruct Words;\nimpl Graph for Words {\n    type Node = Name;\n    fn neighbors(&self, n: &Name) -> Vec<Name> {\n        if n.0.len() < 3 { vec![Name(format!("{}a", n.0))] } else { vec![] }\n    }\n}'),
     """
     fn closure_count(edges: &[Vec<usize>], start: usize) -> usize {
         let n = edges.len();
         let mut reach = vec![vec![false; n]; n];
         for i in 0..n {
             reach[i][i] = true;
             for &j in &edges[i] {
                 reach[i][j] = true;
             }
         }
         for k in 0..n {
             for i in 0..n {
                 for j in 0..n {
                     if reach[i][k] && reach[k][j] {
                         reach[i][j] = true;
                     }
                 }
             }
         }
         reach[start].iter().filter(|&&b| b).count()
     }

     fn distance(edges: &[Vec<usize>], from: usize, to: usize) -> Option<usize> {
         let n = edges.len();
         let mut dist = vec![usize::MAX; n];
         dist[from] = 0;
         for _ in 0..n {
             for u in 0..n {
                 if dist[u] == usize::MAX {
                     continue;
                 }
                 for &v in &edges[u] {
                     dist[v] = dist[v].min(dist[u] + 1);
                 }
             }
         }
         (dist[to] != usize::MAX).then_some(dist[to])
     }

     fn flood(rows: &[String], r: usize, c: usize, seen: &mut Vec<Vec<bool>>) {
         if seen[r][c] {
             return;
         }
         seen[r][c] = true;
         let open = |r: usize, c: usize| rows.get(r).and_then(|row| row.as_bytes().get(c)) == Some(&b'.');
         if r > 0 && open(r - 1, c) {
             flood(rows, r - 1, c, seen);
         }
         if open(r + 1, c) {
             flood(rows, r + 1, c, seen);
         }
         if c > 0 && open(r, c - 1) {
             flood(rows, r, c - 1, seen);
         }
         if open(r, c + 1) {
             flood(rows, r, c + 1, seen);
         }
     }

     #[test]
     fn random_adj_lists_vs_closure() {
         let mut rng = anneal_prelude::Rng::new(4507);
         for _ in 0..300 {
             let n = 1 + rng.below(7);
             let mut edges = Vec::new();
             for _ in 0..n {
                 let k = rng.below(3);
                 let list: Vec<usize> = rng.vec(k, 0, n as i64 - 1);
                 edges.push(list);
             }
             let start = rng.below(n);
             check!(format!("edges = {edges:?}, start = {start}"), reachable(&AdjList { edges: edges.clone() }, start), closure_count(&edges, start));
             let to = rng.below(n);
             let got = shortest_path(&AdjList { edges: edges.clone() }, start, to);
             let valid = got.as_ref().map(|p| p[0] == start && p[p.len() - 1] == to && p.windows(2).all(|w| edges[w[0]].contains(&w[1])));
             check!(format!("edges = {edges:?}, from {start} to {to}"), (got.as_ref().map(|p| p.len() - 1), valid), (distance(&edges, start, to), valid.map(|_| true)));
         }
     }

     #[test]
     fn random_grids_vs_flood_fill() {
         let mut rng = anneal_prelude::Rng::new(4508);
         for _ in 0..300 {
             let h = 1 + rng.below(5);
             let rows: Vec<String> = (0..h).map(|_| { let w = 1 + rng.below(5); rng.string(w, "..#") }).collect();
             let r = rng.below(h);
             let c = rng.below(rows[r].len());
             let mut row = rows[r].clone().into_bytes();
             row[c] = b'.';
             let mut rows = rows;
             rows[r] = String::from_utf8(row).unwrap();
             let mut seen: Vec<Vec<bool>> = rows.iter().map(|row| vec![false; row.len() + 1]).collect();
             seen.push(Vec::new());
             flood(&rows, r, c, &mut seen);
             let want = seen.iter().flatten().filter(|&&b| b).count();
             let refs: Vec<&str> = rows.iter().map(String::as_str).collect();
             check!(format!("rows = {rows:?}, start = ({r}, {c})"), reachable(&Grid::from(refs), (r, c)), want);
         }
     }

     #[test]
     fn scale_open_grid() {
         let row = ".".repeat(600);
         let rows: Vec<&str> = (0..600).map(|_| row.as_str()).collect();
         let g = Grid::from(rows);
         check!("600 x 600 open grid from the corner", reachable(&g, (599, 599)), 360_000);
         check!("600 x 600 open grid, corner to corner", shortest_path(&g, (0, 0), (599, 599)).map(|p| p.len()), Some(1199));
     }

     #[test]
     fn scale_long_chain() {
         let n = 200_000;
         let edges: Vec<Vec<usize>> = (0..n).map(|i| if i + 1 < n { vec![i + 1] } else { vec![] }).collect();
         check!("a chain of 200000 nodes", reachable(&AdjList { edges }, 0), 200_000);
     }
     """],
    [("approach", "`reachable`: DFS with a `HashSet<G::Node>`. `shortest_path`: BFS with a `VecDeque` and a `HashMap<G::Node, G::Node>` of parents, which also marks nodes as seen; walk the parents back from `to`."),
     ("rust", "`G::Node` is the graph's own node type. Because it's associated, `reachable<G>` needs no second type parameter, and `reachable(&grid, (0, 0))` needs no annotation."),
     ("edge", "In `Grid::neighbors`, compute moves in `isize` (or check `r > 0`) so row 0 doesn't underflow, and use `.get()` for ragged rows.")],
    ("""Syntax to remember: `trait Graph { type Node; fn neighbors(&self, node: &Self::Node) -> Vec<Self::Node>; }`, `impl Graph for Grid { type Node = (usize, usize); ... }`, and in generic code `G::Node` (or `<G as Graph>::Node`). Associated type: one implementation per type, chosen by the implementor (`Iterator::Item`, `Deref::Target`). Type parameter: many implementations per type, chosen by the caller (`From<T>`, `Add<Rhs>`). With `trait Graph<N>`, a type could be a graph over several node types and every caller would have to say which.""", "O(V + E)", "O(V)"),
    "Rewrite `Graph` as `trait Graph<N>`. What changes in `reachable`'s signature, and when would that design be the right one?",
    ["Associated types: one impl per type, picked by the implementor.", "Type parameters: many impls per type, picked by the caller (`From<T>`)."],
    related=("L5", "L4", "D9"),
    wrong=dict(
        diagonal_moves=graph_solution(grid_moves="[(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]"),
        vec_as_visited_set=graph_solution(visited="Vec<G::Node> = Vec::new();\n    let mut seen = VecSet(seen)").replace(
            "/// How many nodes", "struct VecSet<T>(Vec<T>);\n\nimpl<T: PartialEq> VecSet<T> {\n    fn insert(&mut self, x: T) {\n        self.0.push(x);\n    }\n\n    fn contains(&self, x: &T) -> bool {\n        self.0.contains(x)\n    }\n\n    fn len(&self) -> usize {\n        self.0.len()\n    }\n}\n\n/// How many nodes"),
        dfs_path=graph_solution(pop="queue.pop_back()"),
        undirected_edges=graph_solution(adj="let mut out = self.edges[*node].clone();\n        for (i, list) in self.edges.iter().enumerate() {\n            if list.contains(node) {\n                out.push(i);\n            }\n        }\n        out"),
    ),
))

BUILDER_HEAD = """
use std::marker::PhantomData;

#[derive(Debug, PartialEq)]
pub struct Request {
    pub url: String,
    pub headers: Vec<(String, String)>,
    pub timeout_ms: u64,
}

#[derive(Debug, PartialEq)]
pub enum UrlError {
    Empty,
    NoScheme,
}

/// The builder's states: before and after it has a URL.
pub struct NoUrl;
pub struct HasUrl;

pub struct RequestBuilder<S> {
    url: String,
    headers: Vec<(String, String)>,
    timeout_ms: u64,
    state: PhantomData<S>,
}
"""

BUILDER_STARTER = BUILDER_HEAD + """
impl RequestBuilder<NoUrl> {
    /// No URL, no headers, a 30 000 ms timeout.
    pub fn new() -> Self {
        todo!()
    }

    /// The only way to get a builder that can `build`.
    pub fn url(self, url: &str) -> Result<RequestBuilder<HasUrl>, UrlError> {
        todo!()
    }
}

impl<S> RequestBuilder<S> {
    pub fn header(self, key: &str, value: &str) -> Self {
        todo!()
    }

    pub fn timeout_ms(self, ms: u64) -> Self {
        todo!()
    }
}

impl RequestBuilder<HasUrl> {
    pub fn build(self) -> Request {
        todo!()
    }
}
"""


def builder_solution(new_headers="self.headers", header_body="self.headers.push((key.to_string(), value.to_string()));", scheme='url.starts_with("http://") || url.starts_with("https://")'):
    return BUILDER_HEAD + f"""
impl RequestBuilder<NoUrl> {{
    /// No URL, no headers, a 30 000 ms timeout.
    pub fn new() -> Self {{
        RequestBuilder {{ url: String::new(), headers: Vec::new(), timeout_ms: 30_000, state: PhantomData }}
    }}

    /// The only way to get a builder that can `build`.
    pub fn url(self, url: &str) -> Result<RequestBuilder<HasUrl>, UrlError> {{
        let url = url.trim();
        if url.is_empty() {{
            return Err(UrlError::Empty);
        }}
        if !({scheme}) {{
            return Err(UrlError::NoScheme);
        }}
        // A different type parameter means a new value: move each field across.
        Ok(RequestBuilder {{ url: url.to_string(), headers: {new_headers}, timeout_ms: self.timeout_ms, state: PhantomData }})
    }}
}}

impl<S> RequestBuilder<S> {{
    pub fn header(mut self, key: &str, value: &str) -> Self {{
        {header_body}
        self
    }}

    pub fn timeout_ms(mut self, ms: u64) -> Self {{
        self.timeout_ms = ms;
        self
    }}
}}

impl RequestBuilder<HasUrl> {{
    pub fn build(self) -> Request {{
        Request {{ url: self.url, headers: self.headers, timeout_ms: self.timeout_ms }}
    }}
}}
"""


def req(url, headers=(), timeout=30000):
    hs = ", ".join(f'("{k}".to_string(), "{v}".to_string())' for k, v in headers)
    return f'Request {{ url: "{url}".to_string(), headers: vec![{hs}], timeout_ms: {timeout} }}'


P.append(write(
    "typestate-http-builder", "Typestate HTTP builder", "medium", "bounds-associated-types", ["typestate", "builder", "PhantomData"],
    """
        Build HTTP requests with a builder whose **type** says whether it has a URL yet. `RequestBuilder<NoUrl>`
        has no `build` method, so "forgot the URL" is a compile error instead of a runtime one.

        - `new()` starts with no headers and a 30 000 ms timeout.
        - `url(u)` trims `u`. It fails with `UrlError::Empty` if nothing is left, and with `UrlError::NoScheme` unless
          it starts with `http://` or `https://`. On success it moves everything set so far into a
          `RequestBuilder<HasUrl>`.
        - `header` and `timeout_ms` work in either state. Headers accumulate in call order (a repeated key is
          kept twice); the last `timeout_ms` wins.
        - `build()` exists only on `RequestBuilder<HasUrl>` and can't fail.
    """,
    BUILDER_STARTER,
    builder_solution(),
    [T("minimal", 'new().url("https://a.io")?.build()', 'RequestBuilder::new().url("https://a.io").unwrap().build()', req("https://a.io")),
     T("full_chain", "headers and a timeout after the URL", 'b.header("Accept", "json").timeout_ms(500).header("X-Id", "7").build()',
       req("https://a.io/x", [("Accept", "json"), ("X-Id", "7")], 500),
       setup='let b: RequestBuilder<HasUrl> = RequestBuilder::new().url("https://a.io/x").unwrap();'),
     T("settings_before_the_url_are_kept", "header and timeout before url()", 'b.url("http://b.io").unwrap().build()',
       req("http://b.io", [("K", "v")], 10),
       setup='let b: RequestBuilder<NoUrl> = RequestBuilder::new().header("K", "v").timeout_ms(10);'),
     T("empty_url", 'url("  ")', 'RequestBuilder::new().url("  ").err()', "Some(UrlError::Empty)"),
     T("no_scheme", 'url("a.io")', 'RequestBuilder::new().url("a.io").err()', "Some(UrlError::NoScheme)")],
    [T("url_is_trimmed", 'url("  https://t.io \\n")', 'RequestBuilder::new().url("  https://t.io \\n").unwrap().build().url', '"https://t.io"'),
     T("empty_string", 'url("")', 'RequestBuilder::new().url("").err()', "Some(UrlError::Empty)"),
     T("ftp_is_rejected", 'url("ftp://x")', 'RequestBuilder::new().url("ftp://x").err()', "Some(UrlError::NoScheme)"),
     T("scheme_is_case_sensitive", 'url("HTTPS://x")', 'RequestBuilder::new().url("HTTPS://x").err()', "Some(UrlError::NoScheme)"),
     T("scheme_must_be_at_the_start", 'url("see https://x")', 'RequestBuilder::new().url("see https://x").err()', "Some(UrlError::NoScheme)"),
     T("repeated_header_kept_twice", 'header("A", "1").header("A", "2")', 'RequestBuilder::new().header("A", "1").url("https://x").unwrap().header("A", "2").build().headers',
       'vec![("A".to_string(), "1".to_string()), ("A".to_string(), "2".to_string())]'),
     T("last_timeout_wins", "timeout_ms(1) before url, timeout_ms(2) after", 'RequestBuilder::new().timeout_ms(1).url("https://x").unwrap().timeout_ms(2).build().timeout_ms', "2"),
     T("zero_timeout", "timeout_ms(0)", 'RequestBuilder::new().url("https://x").unwrap().timeout_ms(0).build().timeout_ms', "0"),
     T("unicode_header", 'header("X-Name", "Zoë")', 'RequestBuilder::new().url("https://x").unwrap().header("X-Name", "Zoë").build()',
       req("https://x", [("X-Name", "Zoë")])),
     T("scheme_only", 'url("http://")', 'RequestBuilder::new().url("http://").unwrap().build().url', '"http://"'),
     """
     #[test]
     fn random_vs_model() {
         let mut rng = anneal_prelude::Rng::new(4509);
         for _ in 0..300 {
             let mut log = Vec::new();
             let mut headers = Vec::new();
             let mut timeout = 30_000u64;
             let mut b = RequestBuilder::new();
             let before = rng.below(4);
             for _ in 0..before {
                 if rng.bool() {
                     let k = rng.string(1, "AB");
                     let v = rng.below(10).to_string();
                     log.push(format!("header({k:?}, {v:?})"));
                     b = b.header(&k, &v);
                     headers.push((k, v));
                 } else {
                     let t = rng.below(1000) as u64;
                     log.push(format!("timeout_ms({t})"));
                     b = b.timeout_ms(t);
                     timeout = t;
                 }
             }
             let url = format!("https://h{}.io", rng.below(10));
             log.push(format!("url({url:?})"));
             let mut b = b.url(&url).unwrap();
             let after = rng.below(4);
             for _ in 0..after {
                 if rng.bool() {
                     let k = rng.string(1, "AB");
                     let v = rng.below(10).to_string();
                     log.push(format!("header({k:?}, {v:?})"));
                     b = b.header(&k, &v);
                     headers.push((k, v));
                 } else {
                     let t = rng.below(1000) as u64;
                     log.push(format!("timeout_ms({t})"));
                     b = b.timeout_ms(t);
                     timeout = t;
                 }
             }
             check!(log.join("."), b.build(), Request { url, headers, timeout_ms: timeout });
         }
     }
     """],
    [("rust", "`PhantomData<S>` makes `S` part of the type at zero size. Split the methods into `impl RequestBuilder<NoUrl>`, `impl<S> RequestBuilder<S>` and `impl RequestBuilder<HasUrl>`."),
     ("rust", "`url` can't return `self` with a new state: `RequestBuilder<HasUrl>` is a different type. Build a new struct, moving each field across (`..self` doesn't work when the type parameter changes)."),
     ("edge", "Carry the headers and timeout across the transition; settings made before `url()` must survive.")],
    ("Typestate moves a runtime check (\"is there a URL?\") into the type system: `build` simply doesn't exist until `url` has succeeded, so `build` can return `Request` instead of `Result`. The states are zero-sized, so this costs nothing at run time.", "O(1) per call", "O(headers)"),
    "How would you require at least one `header` call before `build`, also at compile time? What does each extra state cost the API?",
    ["Typestate: marker types plus `PhantomData` pick which methods exist.", "Consuming builders (`self` in, `Self` out) and moving fields across a state change."],
    source="W11", related=("L5", "M1"),
    wrong=dict(
        drops_early_headers=builder_solution(new_headers="Vec::new()"),
        headers_overwrite=builder_solution(header_body="self.headers.retain(|(k, _)| k != key);\n        self.headers.push((key.to_string(), value.to_string()));"),
        scheme_anywhere=builder_solution(scheme='url.contains("://")'),
    ),
))

STAGES = [
    ("generic-code", "Generic code", "easy"),
    ("bounds-associated-types", "Bounds & associated types", "medium"),
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
