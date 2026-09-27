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


# ---------------------------------------------------------------- define & implement (easy)
# The easy band is recall: the starter is the code that *uses* the traits, and the solver writes the trait layer
# from memory. Those starters can't compile until it's written, so these problems use fix mode.

SHAPE_HEAD = r"""
use std::f64::consts::PI;

pub struct Circle {
    pub r: f64,
}

pub struct Rect {
    pub w: f64,
    pub h: f64,
}

/// Another trait with a `name` method. Don't change it.
pub trait Label {
    fn name(&self) -> String;
}

impl Label for Rect {
    fn name(&self) -> String {
        "box".to_string()
    }
}
"""

SHAPE_TRAITS = r"""
pub trait Named {
    fn name(&self) -> String;
}

pub trait Shape: Named {
    /// Number of straight sides (0 for a circle).
    const SIDES: u32;

    fn area(&self) -> f64;
    fn perimeter(&self) -> f64;

    /// "<name>, <SIDES> sides, area <area to 2 decimals>".
    fn describe(&self) -> String {
        format!("{}, {} sides, area {:.2}", self.name(), Self::SIDES, self.area())
    }
}

impl Named for Circle {
    fn name(&self) -> String {
        "circle".to_string()
    }
}

impl Shape for Circle {
    const SIDES: u32 = 0;

    fn area(&self) -> f64 {
        PI * self.r * self.r
    }

    fn perimeter(&self) -> f64 {
        2.0 * PI * self.r
    }
}

impl Named for Rect {
    fn name(&self) -> String {
        "rect".to_string()
    }
}

impl Shape for Rect {
    const SIDES: u32 = 4;

    fn area(&self) -> f64 {
        self.w * self.h
    }

    fn perimeter(&self) -> f64 {
        2.0 * (self.w + self.h)
    }
}
"""

SHAPE_TAIL = r"""
/// Total number of sides across the shapes.
pub fn total_sides<S: Shape>(shapes: &[S]) -> u32 {
    S::SIDES * shapes.len() as u32
}

/// "<Named name>/<Label name>" for a rect: "rect/box".
pub fn both_names(r: &Rect) -> String {
    BODY
}
"""

SHAPE_SOLUTION = SHAPE_HEAD + SHAPE_TRAITS + SHAPE_TAIL.replace("BODY", 'format!("{}/{}", Named::name(r), <Rect as Label>::name(r))')

P.append(fix(
    "shape-trait", "A Shape trait", "easy", "define-implement", ["supertraits", "associated consts", "default methods", "fully qualified syntax"],
    """
        The code at the bottom uses two traits that don't exist yet. Write them and implement both for `Circle`
        and `Rect`:

        - `Named`: `fn name(&self) -> String`, giving `"circle"` and `"rect"`.
        - `Shape`, which requires `Named`: an associated const `SIDES: u32` (0 for a circle, 4 for a rect),
          `area` and `perimeter` returning `f64`, and a default `describe` returning
          `"<name>, <SIDES> sides, area <area to 2 decimals>"`.

        Then finish `both_names`. `Rect` also implements `Label`, which has its own `name`.
    """,
    SHAPE_HEAD + "\n// TODO: the Named and Shape traits, and their impls for Circle and Rect.\n" + SHAPE_TAIL.replace("BODY", "todo!()"),
    SHAPE_SOLUTION,
    [T("describe_circle", "Circle { r: 1.0 }.describe()", "Circle { r: 1.0 }.describe()", '"circle, 0 sides, area 3.14"'),
     T("describe_uses_named", "Rect { w: 2.0, h: 3.0 }.describe()", "Rect { w: 2.0, h: 3.0 }.describe()", '"rect, 4 sides, area 6.00"'),
     T("sides_const", "<Rect as Shape>::SIDES, Circle::SIDES", "(<Rect as Shape>::SIDES, Circle::SIDES)", "(4, 0)"),
     T("both_names_rect", "both_names(&Rect { w: 1.0, h: 1.0 })", "both_names(&Rect { w: 1.0, h: 1.0 })", '"rect/box"'),
     """
     #[test]
     fn a_new_shape() {
         // Implemented outside your crate: it only needs Named, the const, area and perimeter.
         struct Tri(f64);
         impl Named for Tri {
             fn name(&self) -> String {
                 "tri".to_string()
             }
         }
         impl Shape for Tri {
             const SIDES: u32 = 3;
             fn area(&self) -> f64 {
                 self.0 * self.0 * 3f64.sqrt() / 4.0
             }
             fn perimeter(&self) -> f64 {
                 3.0 * self.0
             }
         }
         check!("Tri(2.0).describe()", Tri(2.0).describe(), "tri, 3 sides, area 1.73");
         check!("total_sides(&[Tri(1.0), Tri(2.0)])", total_sides(&[Tri(1.0), Tri(2.0)]), 6);
     }
     """],
    [T("circle_perimeter", "Circle { r: 2.5 }.perimeter(), 4 decimals", 'format!("{:.4}", Circle { r: 2.5 }.perimeter())', '"15.7080"'),
     T("rect_perimeter", "Rect { w: 2.0, h: 3.5 }.perimeter()", "Rect { w: 2.0, h: 3.5 }.perimeter()", "11.0"),
     T("describe_rounds", "Circle { r: 2.0 }.describe()", "Circle { r: 2.0 }.describe()", '"circle, 0 sides, area 12.57"'),
     T("describe_zero_rect", "Rect { w: 0.0, h: 9.0 }.describe()", "Rect { w: 0.0, h: 9.0 }.describe()", '"rect, 4 sides, area 0.00"'),
     T("total_sides_empty", "total_sides::<Rect>(&[])", "total_sides::<Rect>(&[])", "0"),
     T("total_sides_rects", "three rects", "total_sides(&[Rect { w: 1.0, h: 1.0 }, Rect { w: 2.0, h: 1.0 }, Rect { w: 3.0, h: 1.0 }])", "12"),
     T("total_sides_circles", "two circles", "total_sides(&[Circle { r: 1.0 }, Circle { r: 2.0 }])", "0"),
     T("label_untouched", "<Rect as Label>::name", "<Rect as Label>::name(&Rect { w: 1.0, h: 1.0 })", '"box"'),
     T("named_on_circle", "Named::name(&Circle { r: 1.0 })", "Named::name(&Circle { r: 1.0 })", '"circle"'),
     """
     #[test]
     fn supertrait_gives_name() {
         // With only `S: Shape` in scope, `name` must come from the supertrait.
         fn via_shape<S: Shape>(s: &S) -> String {
             s.name()
         }
         check!("via_shape(&Rect { w: 1.0, h: 1.0 })", via_shape(&Rect { w: 1.0, h: 1.0 }), "rect");
         check!("via_shape(&Circle { r: 1.0 })", via_shape(&Circle { r: 1.0 }), "circle");
     }
     """,
     r"""
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(4401);
         for _ in 0..300 {
             let (w, h) = (rng.int(0, 40) as f64 / 4.0, rng.int(0, 40) as f64 / 4.0);
             let r = Rect { w, h };
             check!(format!("Rect {{ w: {w}, h: {h} }}.describe()"), r.describe(), format!("rect, 4 sides, area {:.2}", w * h));
             check!(format!("Rect {{ w: {w}, h: {h} }}.perimeter()"), r.perimeter(), 2.0 * (w + h));
             let rad = rng.int(0, 40) as f64 / 8.0;
             check!(format!("Circle {{ r: {rad} }}.describe()"), Circle { r: rad }.describe(), format!("circle, 0 sides, area {:.2}", std::f64::consts::PI * rad * rad));
         }
     }
     """],
    [("rust", "A supertrait goes after a colon: `trait Shape: Named { ... }`. An associated const is declared `const SIDES: u32;` in the trait and given a value in each impl."),
     ("rust", "Inside `describe`, read the const through `Self::SIDES`. In `both_names`, `r.name()` is ambiguous because `Rect` has two `name` methods; name the trait: `Named::name(r)` or `<Rect as Label>::name(r)`.")],
    ("""A supertrait `Shape: Named` means every `Shape` is also `Named`, so `Shape`'s defaults (and any `S: Shape` code) can call `name`. An associated const is per type, read as `Self::SIDES` or `<Rect as Shape>::SIDES`. When two traits give a type methods with the same name, call one with fully qualified syntax.

Syntax: `trait Shape: Named { const SIDES: u32; fn describe(&self) -> String { ... } }` · `impl Shape for Rect { const SIDES: u32 = 4; ... }` · `<Rect as Label>::name(r)`.

A trait with an associated const is not dyn-compatible: `dyn Shape` has no single value for `SIDES`.""", "O(1)", "O(1)"),
    "Why can't `Vec<Box<dyn Shape>>` exist here, and how would you change `Shape` so it can?",
    ["Supertraits: `trait Shape: Named`.", "Associated consts are declared in the trait and set per impl.", "Fully qualified syntax picks between same-named methods."],
    related=("L5", "S8"),
    wrong=dict(
        both_names_reversed=SHAPE_HEAD + SHAPE_TRAITS + SHAPE_TAIL.replace("BODY", 'format!("{}/{}", <Rect as Label>::name(r), Named::name(r))'),
        circle_one_side=SHAPE_HEAD + SHAPE_TRAITS.replace("const SIDES: u32 = 0;", "const SIDES: u32 = 1;") + SHAPE_TAIL.replace("BODY", 'format!("{}/{}", Named::name(r), <Rect as Label>::name(r))'),
    ),
))

METRIC_HEAD = r"""
pub struct Latency {
    pub samples: Vec<f64>,
}

/// Requests per second, one value per second. Idle seconds (0.0) don't count toward the mean.
pub struct Throughput {
    pub rps: Vec<f64>,
}
"""

METRIC_TRAIT = r"""
pub trait Metric {
    fn name(&self) -> &str;
    fn values(&self) -> &[f64];

    /// The mean of the values, or None when there are none.
    fn mean(&self) -> Option<f64> {
        let v = self.values();
        if v.is_empty() {
            None
        } else {
            Some(v.iter().sum::<f64>() / v.len() as f64)
        }
    }

    /// "<name>: n=<number of values> mean=<mean, 2 decimals>", or "<name>: no data" when `mean` is None.
    fn report(&self) -> String {
        match self.mean() {
            Some(m) => format!("{}: n={} mean={:.2}", self.name(), self.values().len(), m),
            None => format!("{}: no data", self.name()),
        }
    }

    /// How many values `pred` accepts.
    fn count_where<F: Fn(f64) -> bool>(&self, pred: F) -> usize
    where
        Self: Sized,
    {
        self.values().iter().filter(|&&v| pred(v)).count()
    }
}

impl Metric for Latency {
    fn name(&self) -> &str {
        "latency"
    }

    fn values(&self) -> &[f64] {
        &self.samples
    }
}

impl Metric for Throughput {
    fn name(&self) -> &str {
        "throughput"
    }

    fn values(&self) -> &[f64] {
        &self.rps
    }

    fn mean(&self) -> Option<f64> {
        let busy: Vec<f64> = self.rps.iter().copied().filter(|&v| v != 0.0).collect();
        if busy.is_empty() {
            None
        } else {
            Some(busy.iter().sum::<f64>() / busy.len() as f64)
        }
    }
}
"""

METRIC_TAIL = r"""
/// Every metric's report, in order.
pub fn reports(metrics: &[Box<dyn Metric>]) -> Vec<String> {
    metrics.iter().map(|m| m.report()).collect()
}
"""

P.append(fix(
    "default-methods", "Default methods", "easy", "define-implement", ["default methods", "generic methods", "where Self: Sized"],
    """
        Write the `Metric` trait that `reports` uses, and implement it for `Latency` (name `"latency"`) and
        `Throughput` (name `"throughput"`).

        - Required: `fn name(&self) -> &str` and `fn values(&self) -> &[f64]`.
        - Default `mean(&self) -> Option<f64>`: the mean of the values, `None` when there are none.
          `Throughput` overrides it to ignore idle (`0.0`) seconds.
        - Default `report(&self) -> String`: `"<name>: n=<number of values> mean=<mean, 2 decimals>"`, or
          `"<name>: no data"` when `mean` is `None`.
        - Default generic `count_where<F: Fn(f64) -> bool>(&self, pred: F) -> usize`.
    """,
    METRIC_HEAD + "\n// TODO: the Metric trait and its impls for Latency and Throughput.\n" + METRIC_TAIL,
    METRIC_HEAD + METRIC_TRAIT + METRIC_TAIL,
    [T("latency_report", "Latency { samples: [10, 20, 30] }.report()", "Latency { samples: vec![10.0, 20.0, 30.0] }.report()", '"latency: n=3 mean=20.00"'),
     T("no_data", "Latency { samples: [] }.report()", "Latency { samples: vec![] }.report()", '"latency: no data"'),
     T("report_uses_the_override", "Throughput { rps: [0, 100, 0, 200] }.report()", "Throughput { rps: vec![0.0, 100.0, 0.0, 200.0] }.report()", '"throughput: n=4 mean=150.00"'),
     T("reports_through_dyn", "reports([Latency [5], Throughput [0]])", "reports(&ms)", 'vec!["latency: n=1 mean=5.00", "throughput: no data"]',
       setup="let ms: Vec<Box<dyn Metric>> = vec![Box::new(Latency { samples: vec![5.0] }), Box::new(Throughput { rps: vec![0.0] })];"),
     T("count_where_closure", "Latency [120, 80, 300], count values > limit (100)", "Latency { samples: vec![120.0, 80.0, 300.0] }.count_where(|v| v > limit)", "2",
       setup="let limit = 100.0;"),
     """
     #[test]
     fn defaults_for_a_new_type() {
         struct Temps(Vec<f64>);
         impl Metric for Temps {
             fn name(&self) -> &str {
                 "temps"
             }
             fn values(&self) -> &[f64] {
                 &self.0
             }
         }
         check!("Temps([21.5, 22.5, 23.0, 25.0]).report()", Temps(vec![21.5, 22.5, 23.0, 25.0]).report(), "temps: n=4 mean=23.00");
     }
     """],
    [T("empty_mean", "Latency { samples: [] }.mean()", "Latency { samples: vec![] }.mean()", "None"),
     T("throughput_mean", "Throughput { rps: [0, 100, 0, 200] }.mean()", "Throughput { rps: vec![0.0, 100.0, 0.0, 200.0] }.mean()", "Some(150.0)"),
     T("throughput_all_idle", "Throughput { rps: [0, 0] }.report()", "Throughput { rps: vec![0.0, 0.0] }.report()", '"throughput: no data"'),
     T("throughput_empty", "Throughput { rps: [] }.mean()", "Throughput { rps: vec![] }.mean()", "None"),
     T("rounding", "Latency { samples: [1, 2, 2] }.report()", "Latency { samples: vec![1.0, 2.0, 2.0] }.report()", '"latency: n=3 mean=1.67"'),
     T("negatives", "Latency { samples: [-4, 1] }.mean()", "Latency { samples: vec![-4.0, 1.0] }.mean()", "Some(-1.5)"),
     T("count_where_counts_idle", "Throughput [0, 5, 0], count zeros", "Throughput { rps: vec![0.0, 5.0, 0.0] }.count_where(|v| v == 0.0)", "2"),
     T("count_where_none", "Latency [], anything", "Latency { samples: vec![] }.count_where(|_| true)", "0"),
     T("reports_empty", "reports(&[])", "reports(&[])", "Vec::<String>::new()"),
     """
     #[test]
     fn override_seen_through_dyn() {
         // An override of `mean` must change what the default `report` prints, even through `dyn Metric`.
         struct Median(Vec<f64>);
         impl Metric for Median {
             fn name(&self) -> &str {
                 "median"
             }
             fn values(&self) -> &[f64] {
                 &self.0
             }
             fn mean(&self) -> Option<f64> {
                 let mut v = self.0.clone();
                 v.sort_by(f64::total_cmp);
                 v.get(v.len() / 2).copied()
             }
         }
         let ms: Vec<Box<dyn Metric>> = vec![Box::new(Median(vec![1.0, 100.0, 3.0]))];
         check!("reports([Median [1, 100, 3]])", reports(&ms), vec!["median: n=3 mean=3.00".to_string()]);
     }
     """,
     r"""
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(4402);
         for _ in 0..300 {
             let n = rng.below(6);
             let v: Vec<f64> = rng.vec::<i64>(n, 0, 3).into_iter().map(|x| x as f64 * 10.0).collect();
             let busy: Vec<f64> = v.iter().copied().filter(|&x| x != 0.0).collect();
             let want = if busy.is_empty() {
                 "throughput: no data".to_string()
             } else {
                 format!("throughput: n={} mean={:.2}", n, busy.iter().sum::<f64>() / busy.len() as f64)
             };
             check!(format!("Throughput {v:?}"), Throughput { rps: v.clone() }.report(), want);
             let want = if n == 0 { "latency: no data".to_string() } else { format!("latency: n={} mean={:.2}", n, v.iter().sum::<f64>() / n as f64) };
             check!(format!("Latency {v:?}"), Latency { samples: v.clone() }.report(), want);
         }
     }
     """],
    [("approach", "`report` must call `self.mean()`, not recompute the mean, or `Throughput`'s override never shows."),
     ("rust", "A generic method can't go in a vtable, so `dyn Metric` is rejected (E0038) while `count_where` is generic. Add `where Self: Sized` to that one method: it stays callable on concrete types and is left out of `dyn Metric`.")],
    ("""Default methods are written once in the trait and may call the required ones; an impl can override any of them, and the other defaults then call the override (dispatch goes through `self`). A generic method has one copy per type argument, which a vtable can't hold, so it needs `where Self: Sized` for the trait to stay dyn-compatible.

Syntax: `fn count_where<F: Fn(f64) -> bool>(&self, pred: F) -> usize where Self: Sized { ... }` (the `where` goes after the return type, before the body).""", "O(n) per call", "O(1)"),
    "How else could `count_where` stay callable on `dyn Metric`? What does each option cost?",
    ["Defaults call required methods through `self`, so overrides are seen.", "Generic methods need `where Self: Sized` in a dyn-compatible trait."],
    related=("L5",),
    wrong=dict(
        report_recomputes_mean=METRIC_HEAD + METRIC_TRAIT.replace(
            "        match self.mean() {\n            Some(m) => format!(\"{}: n={} mean={:.2}\", self.name(), self.values().len(), m),",
            "        let v = self.values();\n        match (!v.is_empty()).then(|| v.iter().sum::<f64>() / v.len() as f64) {\n            Some(m) => format!(\"{}: n={} mean={:.2}\", self.name(), v.len(), m),") + METRIC_TAIL,
        no_override=METRIC_HEAD + METRIC_TRAIT.split("\n    fn mean(&self) -> Option<f64> {\n        let busy")[0] + "\n}\n" + METRIC_TAIL,
    ),
))

MONEY_DISPLAY = r"""
impl fmt::Display for Money {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let abs = self.cents.unsigned_abs();
        let digits = (abs / 100).to_string();
        let mut grouped = String::new();
        for (i, c) in digits.chars().enumerate() {
            if i > 0 && (digits.len() - i) % 3 == 0 {
                grouped.push(',');
            }
            grouped.push(c);
        }
        let sign = if self.cents < 0 { "-" } else { "" };
        f.pad(&format!("{sign}${grouped}.{:02}", abs % 100))
    }
}
"""

CRED_DEBUG = r"""
impl fmt::Debug for Credentials {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.debug_struct("Credentials").field("user", &self.user).field("password", &"***").finish()
    }
}
"""


def money_types(cred_derive):
    return r"""
use std::fmt;

/// An amount of money in cents.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Money {
    pub cents: i64,
}

/// Login details. They get logged with {:?}.
#[derive(""" + cred_derive + r""")]
pub struct Credentials {
    pub user: String,
    pub password: String,
}
"""


MONEY_SOLUTION = money_types("Clone, PartialEq, Eq") + MONEY_DISPLAY + CRED_DEBUG

P.append(fix(
    "impl-display", "impl Display, and a Debug that hides secrets", "easy", "define-implement", ["Display", "Debug", "derive vs manual impls", "Formatter"],
    """
        Two problems:

        - `Money` has no `Display`. Print dollars with a comma every three digits and two decimals: `123456` →
          `$1,234.56`, `-50` → `-$0.50`. Any `i64` is allowed. Width and alignment must work: `{:>10}`.
        - The derived `Debug` on `Credentials` writes the password into the logs. Write `Debug` by hand so the
          password shows as `"***"` and everything else, including `{:#?}`, looks exactly as derived.

        Keep the other derives.
    """,
    money_types("Debug, Clone, PartialEq, Eq") + "\n// TODO: Display for Money.\n",
    MONEY_SOLUTION,
    [T("thousands", "Money { cents: 123456 }", "Money { cents: 123456 }.to_string()", '"$1,234.56"'),
     T("negative_under_a_dollar", "Money { cents: -50 }", "Money { cents: -50 }.to_string()", '"-$0.50"'),
     T("width", "format!(\"[{:>10}]\", Money { cents: 5 })", 'format!("[{:>10}]", Money { cents: 5 })', '"[     $0.05]"'),
     T("password_hidden", "format!(\"{:?}\", Credentials { user: \"bob\", password: \"hunter2\" })", 'format!("{:?}", c)', r'r#"Credentials { user: "bob", password: "***" }"#',
       setup='let c = Credentials { user: "bob".into(), password: "hunter2".into() };'),
     T("pretty_debug", "format!(\"{:#?}\", Credentials { user: \"bob\", .. })", 'format!("{:#?}", c)', r'"Credentials {\n    user: \"bob\",\n    password: \"***\",\n}"',
       setup='let c = Credentials { user: "bob".into(), password: "hunter2".into() };')],
    [T("zero", "Money { cents: 0 }", "Money { cents: 0 }.to_string()", '"$0.00"'),
     T("no_comma_below_1000", "Money { cents: 99999 }", "Money { cents: 99999 }.to_string()", '"$999.99"'),
     T("exactly_1000", "Money { cents: 100000 }", "Money { cents: 100000 }.to_string()", '"$1,000.00"'),
     T("i64_min", "Money { cents: i64::MIN }", "Money { cents: i64::MIN }.to_string()", '"-$92,233,720,368,547,758.08"'),
     T("i64_max", "Money { cents: i64::MAX }", "Money { cents: i64::MAX }.to_string()", '"$92,233,720,368,547,758.07"'),
     T("centered_fill", "format!(\"{:*^11}\", Money { cents: -123 })", 'format!("{:*^11}", Money { cents: -123 })', '"**-$1.23***"'),
     T("money_debug_still_derived", "format!(\"{:?}\", Money { cents: 5 })", 'format!("{:?}", Money { cents: 5 })', '"Money { cents: 5 }"'),
     T("user_is_escaped", "user with a quote: bo\"b", 'format!("{:?}", c)', r'r#"Credentials { user: "bo\"b", password: "***" }"#',
       setup='let c = Credentials { user: "bo\\"b".into(), password: "x".into() };'),
     T("empty_password_still_hidden", "password \"\"", 'format!("{:?}", c)', r'r#"Credentials { user: "", password: "***" }"#',
       setup='let c = Credentials { user: String::new(), password: String::new() };'),
     T("other_derives_kept", "c.clone() == c", "c.clone() == c", "true",
       setup='let c = Credentials { user: "a".into(), password: "b".into() };'),
     T("nested_pretty", "format!(\"{:#?}\", vec![Credentials])", 'format!("{:#?}", vec![c])', r'"[\n    Credentials {\n        user: \"é\",\n        password: \"***\",\n    },\n]"',
       setup='let c = Credentials { user: "é".into(), password: "p".into() };'),
     r"""
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(4403);
         for _ in 0..400 {
             let digits = rng.below(13) as u32;
             let cents = rng.int(-(10i64.pow(digits)), 10i64.pow(digits));
             let abs = cents.unsigned_abs();
             let mut parts = Vec::new();
             let mut d = abs / 100;
             loop {
                 parts.push(d % 1000);
                 d /= 1000;
                 if d == 0 {
                     break;
                 }
             }
             let mut body = parts.pop().unwrap().to_string();
             while let Some(p) = parts.pop() {
                 body.push_str(&format!(",{p:03}"));
             }
             let want = format!("{}${}.{:02}", if cents < 0 { "-" } else { "" }, body, abs % 100);
             check!(format!("cents = {cents}"), Money { cents }.to_string(), want);
         }
     }
     """],
    [("rust", "`write!(f, ...)` ignores the caller's width; build the text, then `f.pad(&text)`. `i64::MIN.abs()` overflows, `unsigned_abs()` doesn't, and `-50 / 100` is 0, so keep the sign apart."),
     ("rust", "Remove `Debug` from the derive list, then use `f.debug_struct(\"Credentials\").field(..).finish()`. It handles `{:#?}` and escaping; a hand-written `write!` doesn't.")],
    ("""`#[derive(Debug)]` prints every field, secrets included. A manual impl with the `debug_*` builders keeps the derived look, pretty-printing and escaping. For `Display`, `Formatter::pad` applies width, fill and alignment.

Syntax: `impl fmt::Display for Money { fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result { ... } }` · `f.debug_struct("Name").field("a", &self.a).finish()` · `finish_non_exhaustive()` prints `..` for hidden fields.""", "O(digits)", "O(digits)"),
    "Which derives are safe to keep on a type holding a secret, and which would you also write by hand?",
    ["Derive when the generated impl is right; write it by hand when it isn't (secrets, ignored fields).", "`f.pad` for width; `debug_struct` for Debug."],
    related=("S2", "S8"),
    wrong=dict(
        write_ignores_width=MONEY_SOLUTION.replace('f.pad(&format!("{sign}${grouped}.{:02}", abs % 100))', 'write!(f, "{sign}${grouped}.{:02}", abs % 100)'),
        debug_by_hand_with_write=money_types("Clone, PartialEq, Eq") + MONEY_DISPLAY + r"""
impl fmt::Debug for Credentials {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Credentials {{ user: {:?}, password: \"***\" }}", self.user)
    }
}
""",
        sign_from_division=MONEY_SOLUTION.replace(
            "        let abs = self.cents.unsigned_abs();\n        let digits = (abs / 100).to_string();",
            "        let dollars = self.cents / 100;\n        let abs = (self.cents % 100).unsigned_abs();\n        let digits = dollars.unsigned_abs().to_string();").replace(
            'let sign = if self.cents < 0 { "-" } else { "" };', 'let sign = if dollars < 0 { "-" } else { "" };').replace("abs % 100))", "abs))"),
    ),
))

ASSOC_HEAD = r"""
use std::fmt::Debug;

pub struct Celsius(pub f64);
pub struct Fahrenheit(pub f64);
pub struct Kelvin(pub f64);

/// Decodes "1, 2, 3" into integers.
pub struct CsvInts;
/// Decodes "key=value" into a pair.
pub struct KeyValue;
"""

ASSOC_TRAITS = r"""
pub trait Convert<T> {
    fn convert(&self) -> T;
}

impl Convert<Fahrenheit> for Celsius {
    fn convert(&self) -> Fahrenheit {
        Fahrenheit(self.0 * 9.0 / 5.0 + 32.0)
    }
}

impl Convert<Kelvin> for Celsius {
    fn convert(&self) -> Kelvin {
        Kelvin(self.0 + 273.15)
    }
}

pub trait Decoder {
    type Output;
    const NAME: &'static str;

    fn decode(&self, input: &str) -> Option<Self::Output>;
}

impl Decoder for CsvInts {
    type Output = Vec<i64>;
    const NAME: &'static str = "csv";

    fn decode(&self, input: &str) -> Option<Vec<i64>> {
        if input.trim().is_empty() {
            return Some(Vec::new());
        }
        input.split(',').map(|p| p.trim().parse().ok()).collect()
    }
}

impl Decoder for KeyValue {
    type Output = (String, String);
    const NAME: &'static str = "kv";

    fn decode(&self, input: &str) -> Option<(String, String)> {
        let (k, v) = input.split_once('=')?;
        Some((k.trim().to_string(), v.trim().to_string()))
    }
}
"""

ASSOC_TAIL = r"""
/// Decodes every item, skipping the ones that fail.
pub fn decode_all<D: Decoder>(d: &D, items: &[&str]) -> Vec<D::Output> {
    items.iter().filter_map(|s| d.decode(s)).collect()
}

/// "<NAME>: <first item that decodes, in Debug form>", or "<NAME>: none".
pub fn first_decoded<D>(d: &D, items: &[&str]) -> String
WHERE
{
    FIRST
}

/// The temperature in the two other scales.
pub fn to_both(c: &Celsius) -> (Fahrenheit, Kelvin) {
    BOTH
}
"""

ASSOC_FILLED = ASSOC_TAIL.replace("WHERE", "where\n    D: Decoder,\n    D::Output: Debug,").replace(
    "FIRST", 'match items.iter().find_map(|s| d.decode(s)) {\n        Some(out) => format!("{}: {:?}", D::NAME, out),\n        None => format!("{}: none", D::NAME),\n    }').replace(
    "BOTH", "(c.convert(), <Celsius as Convert<Kelvin>>::convert(c))")

P.append(fix(
    "associated-types", "Associated types, consts and generic traits", "easy", "define-implement", ["associated types", "associated consts", "generic traits", "fully qualified syntax"],
    """
        Write the two traits the code at the bottom uses, then finish `first_decoded` (its `where` clause too)
        and `to_both`.

        - `Convert<T>` with `fn convert(&self) -> T`. `Celsius` converts to `Fahrenheit` (×9/5 + 32) and to
          `Kelvin` (+273.15).
        - `Decoder` with an associated type `Output`, an associated const `NAME: &'static str`, and
          `fn decode(&self, input: &str) -> Option<Self::Output>`.
          - `CsvInts` (`"csv"`) gives `Vec<i64>`. Parts are split on `,` and trimmed; a blank input is an empty
            list; any part that isn't an integer makes the whole input fail.
          - `KeyValue` (`"kv"`) gives `(String, String)`, split at the first `=`, both sides trimmed. No `=` fails.
    """,
    ASSOC_HEAD + "\n// TODO: the Convert<T> and Decoder traits, and their impls.\n" + ASSOC_TAIL.replace("WHERE", "// TODO: the where clause").replace("FIRST", "todo!()").replace("BOTH", "todo!()"),
    ASSOC_HEAD + ASSOC_TRAITS + ASSOC_FILLED,
    [T("decode_csv", "decode_all(&CsvInts, [\"1, 2\", \"x\", \"\"])", 'decode_all(&CsvInts, &["1, 2", "x", ""])', "vec![vec![1, 2], vec![]]"),
     T("decode_kv", "KeyValue.decode(\" a = b=c \")", 'KeyValue.decode(" a = b=c ")', 'Some(("a".to_string(), "b=c".to_string()))'),
     T("first_decoded_csv", "first_decoded(&CsvInts, [\"x\", \"3,4\"])", 'first_decoded(&CsvInts, &["x", "3,4"])', '"csv: [3, 4]"'),
     T("both_scales", "to_both(&Celsius(100.0))", 'format!("{:.2} {:.2}", f.0, k.0)', '"212.00 373.15"', setup="let (f, k) = to_both(&Celsius(100.0));"),
     """
     #[test]
     fn a_new_decoder() {
         struct Flag;
         impl Decoder for Flag {
             type Output = bool;
             const NAME: &'static str = "flag";
             fn decode(&self, input: &str) -> Option<bool> {
                 match input {
                     "on" => Some(true),
                     "off" => Some(false),
                     _ => None,
                 }
             }
         }
         check!("decode_all(&Flag, [\\"on\\", \\"?\\", \\"off\\"])", decode_all(&Flag, &["on", "?", "off"]), vec![true, false]);
         check!("first_decoded(&Flag, [\\"?\\"])", first_decoded(&Flag, &["?"]), "flag: none");
         check!("<Flag as Decoder>::NAME", <Flag as Decoder>::NAME, "flag");
     }
     """],
    [T("csv_bad_part_fails", "CsvInts.decode(\"1,,2\")", 'CsvInts.decode("1,,2")', "None"),
     T("csv_blank", "CsvInts.decode(\"   \")", 'CsvInts.decode("   ")', "Some(vec![])"),
     T("csv_negative", "CsvInts.decode(\"-5, 7\")", 'CsvInts.decode("-5, 7")', "Some(vec![-5, 7])"),
     T("csv_overflow_fails", "CsvInts.decode(\"99999999999999999999\")", 'CsvInts.decode("99999999999999999999")', "None"),
     T("kv_no_equals", "KeyValue.decode(\"abc\")", 'KeyValue.decode("abc")', "None"),
     T("kv_empty_sides", "KeyValue.decode(\"=\")", 'KeyValue.decode("=")', "Some((String::new(), String::new()))"),
     T("names", "CsvInts::NAME, KeyValue::NAME", "(<CsvInts as Decoder>::NAME, <KeyValue as Decoder>::NAME)", '("csv", "kv")'),
     T("first_decoded_kv", "first_decoded(&KeyValue, [\"k=v\"])", 'first_decoded(&KeyValue, &["k=v"])', r'r#"kv: ("k", "v")"#'),
     T("first_decoded_empty", "first_decoded(&CsvInts, [])", "first_decoded(&CsvInts, &[])", '"csv: none"'),
     T("convert_by_annotation", "let f: Fahrenheit = Celsius(-40.0).convert()", 'format!("{:.2}", f.0)', '"-40.00"', setup="let f: Fahrenheit = Celsius(-40.0).convert();"),
     T("absolute_zero", "<Celsius as Convert<Kelvin>>::convert(&Celsius(-273.15))", 'format!("{:.2}", <Celsius as Convert<Kelvin>>::convert(&Celsius(-273.15)).0)', '"0.00"'),
     r"""
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(4404);
         for _ in 0..300 {
             let n = rng.below(4);
             let parts: Vec<String> = (0..n).map(|_| if rng.below(8) == 0 { "x".to_string() } else { rng.int(-99, 99).to_string() }).collect();
             let input = parts.join(",");
             let want: Option<Vec<i64>> = if input.is_empty() { Some(vec![]) } else { parts.iter().map(|p| p.parse().ok()).collect() };
             check!(format!("CsvInts.decode({input:?})"), CsvInts.decode(&input), want);
             let c = rng.int(-500, 500) as f64 / 2.0;
             let (f, k) = to_both(&Celsius(c));
             check!(format!("to_both(&Celsius({c}))"), format!("{:.3} {:.3}", f.0, k.0), format!("{:.3} {:.3}", c * 1.8 + 32.0, c + 273.15));
         }
     }
     """],
    [("rust", "Declare `type Output;` and `const NAME: &'static str;` in the trait; each impl writes `type Output = Vec<i64>;` and `const NAME: &'static str = \"csv\";`."),
     ("rust", "`first_decoded` needs `where D: Decoder, D::Output: Debug`. In `to_both`, `c.convert()` has two candidates: let the expected type choose, or write `<Celsius as Convert<Kelvin>>::convert(c)`."),
     ("edge case", "Collecting an iterator of `Option<i64>` into `Option<Vec<i64>>` stops at the first `None`.")],
    ("""Use an associated type when each implementor has exactly one natural output (`Decoder::Output`); use a generic trait `Convert<T>` when one type can implement it several times. With several impls, the caller picks one by the expected type or with fully qualified syntax.

Syntax: `trait Decoder { type Output; const NAME: &'static str; fn decode(&self, input: &str) -> Option<Self::Output>; }` · bounds on an associated type: `where D: Decoder, D::Output: Debug` · `<Celsius as Convert<Kelvin>>::convert(c)`.""", "O(n) per decode", "O(n)"),
    "`Iterator` uses an associated `Item`; `From<T>` is generic. Why did std choose differently for each?",
    ["Associated types: one output per implementing type.", "Generic traits: many impls per type, picked by type annotation or fully qualified syntax.", "Bounds can constrain associated types: `D::Output: Debug`."],
    related=("L5",),
    wrong=dict(
        kv_splits_at_last=ASSOC_HEAD + ASSOC_TRAITS.replace("input.split_once('=')?", "input.rsplit_once('=')?") + ASSOC_FILLED,
        csv_skips_bad_parts=ASSOC_HEAD + ASSOC_TRAITS.replace("input.split(',').map(|p| p.trim().parse().ok()).collect()", "Some(input.split(',').filter_map(|p| p.trim().parse().ok()).collect())") + ASSOC_FILLED,
    ),
))

ITER_ARGS_STARTER = r"""
use std::fmt::Display;

/// Total number of characters (not bytes) across the words.
pub fn total_chars(words: &[String]) -> usize {
    words.iter().map(|w| w.chars().count()).sum()
}

/// The items formatted with Display, joined with `sep`.
pub fn join_display(items: &[i32], sep: &str) -> String {
    items.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(sep)
}

/// How many words `keep` accepts.
pub fn count_where(words: &[String], keep: fn(&str) -> bool) -> usize {
    words.iter().filter(|w| keep(w)).count()
}

/// `f`, then `g`.
pub fn compose(f: fn(i64) -> i64, g: fn(i64) -> i64) -> Box<dyn Fn(i64) -> i64> {
    Box::new(move |x| g(f(x)))
}

/// The even numbers from 0 up to `limit`, inclusive.
pub fn evens(limit: u64) -> std::vec::IntoIter<u64> {
    (0..=limit).filter(|n| n % 2 == 0).collect::<Vec<_>>().into_iter()
}

/// The items in order, or in reverse when `descending`.
pub fn ordered(v: &[i32], descending: bool) -> impl Iterator<Item = &i32> {
    if descending {
        v.iter().rev()
    } else {
        v.iter()
    }
}
"""

ITER_ARGS_SOLUTION = r"""
use std::fmt::Display;

/// Total number of characters (not bytes) across the words.
pub fn total_chars(words: impl IntoIterator<Item = impl AsRef<str>>) -> usize {
    words.into_iter().map(|w| w.as_ref().chars().count()).sum()
}

/// The items formatted with Display, joined with `sep`.
pub fn join_display(items: impl IntoIterator<Item = impl Display>, sep: &str) -> String {
    items.into_iter().map(|x| x.to_string()).collect::<Vec<_>>().join(sep)
}

/// How many words `keep` accepts.
pub fn count_where(words: impl IntoIterator<Item = impl AsRef<str>>, keep: impl Fn(&str) -> bool) -> usize {
    words.into_iter().filter(|w| keep(w.as_ref())).count()
}

/// `f`, then `g`.
pub fn compose(f: impl Fn(i64) -> i64, g: impl Fn(i64) -> i64) -> impl Fn(i64) -> i64 {
    move |x| g(f(x))
}

/// The even numbers from 0 up to `limit`, inclusive.
pub fn evens(limit: u64) -> impl Iterator<Item = u64> + Clone {
    (0..=limit).step_by(2)
}

/// The items in order, or in reverse when `descending`.
pub fn ordered(v: &[i32], descending: bool) -> Box<dyn Iterator<Item = &i32> + '_> {
    if descending {
        Box::new(v.iter().rev())
    } else {
        Box::new(v.iter())
    }
}
"""

P.append(fix(
    "impl-trait-arguments", "impl Trait in argument and return position", "easy", "define-implement", ["impl Trait", "IntoIterator", "AsRef", "Box<dyn Iterator>"],
    """
        These functions take and return types that are too specific. The tests call them with arrays of `&str`,
        `Vec`s, ranges, `split` iterators and capturing closures, clone what `evens` returns, and call
        `evens(u64::MAX)`, so it must be lazy. `ordered` doesn't compile at all.

        Change the signatures (and bodies where needed) so every call works. Keep what each function computes.
    """,
    ITER_ARGS_STARTER,
    ITER_ARGS_SOLUTION,
    [T("owned_vec_of_strings", "vec![\"héllo\", \"ab\"] as Strings", 'total_chars(vec!["héllo".to_string(), "ab".to_string()])', "7"),
     T("join_a_range", "1..=3, \", \"", 'join_display(1..=3, ", ")', '"1, 2, 3"'),
     T("closure_captures", "words longer than min = 3", "count_where(&words, |w| w.len() > min)", "2",
       setup='let min = 3;\nlet words = vec!["tree".to_string(), "sky".to_string(), "forest".to_string()];'),
     T("compose_closures", "compose(x + k, x * 2)(1) with k = 3", "h(1)", "8", setup="let k = 3;\nlet h = compose(move |x| x + k, |x| x * 2);"),
     T("evens_is_lazy_and_clone", "evens(u64::MAX).take(3), cloned", "(e.clone().collect::<Vec<_>>(), e.count())", "(vec![0, 2, 4], 3)",
       setup="let e = evens(u64::MAX).take(3);"),
     T("ordered_both_ways", "ordered(&[1, 2, 3], true / false)", "(ordered(&v, true).copied().collect::<Vec<_>>(), ordered(&v, false).copied().collect::<Vec<_>>())", "(vec![3, 2, 1], vec![1, 2, 3])",
       setup="let v = [1, 2, 3];")],
    [T("array_of_str", "[\"a\", \"bc\"]", 'total_chars(["a", "bc"])', "3"),
     T("split_iterator", "\"one two\".split(' ')", "total_chars(\"one two\".split(' '))", "6"),
     T("empty_iter", "std::iter::empty::<&str>()", "total_chars(std::iter::empty::<&str>())", "0"),
     T("borrowed_vec_still_usable", "&v, then v.len()", "(total_chars(&v), v.len())", "(5, 2)",
       setup='let v = vec!["abc".to_string(), "de".to_string()];'),
     T("join_floats_by_ref", "&[1.5, 2.0], \"|\"", 'join_display(&[1.5, 2.0], "|")', '"1.5|2"'),
     T("join_empty", "Vec::<i32>::new()", 'join_display(Vec::<i32>::new(), ",")', "String::new()"),
     T("fn_item_still_works", "[\"\", \"a\"], str::is_empty", 'count_where(["", "a"], str::is_empty)', "1"),
     T("compose_order", "compose(x * 10, x + 1)(2)", "compose(|x| x * 10, |x| x + 1)(2)", "21"),
     T("compose_nested", "compose(compose(+1, *2), -3)(5)", "compose(compose(|x| x + 1, |x| x * 2), |x| x - 3)(5)", "9"),
     T("evens_inclusive", "evens(6)", "evens(6).collect::<Vec<_>>()", "vec![0, 2, 4, 6]"),
     T("evens_zero", "evens(0)", "evens(0).collect::<Vec<_>>()", "vec![0]"),
     T("ordered_empty", "ordered(&[], true)", "ordered(&[], true).count()", "0"),
     r"""
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(4405);
         for _ in 0..300 {
             let n = rng.below(5);
             let words: Vec<String> = (0..n).map(|_| { let len = rng.below(4); rng.string(len, "aé") }).collect();
             let chars: usize = words.iter().map(|w| w.chars().count()).sum();
             check!(format!("total_chars({words:?})"), total_chars(&words), chars);
             check!(format!("join_display({words:?}, \"/\")"), join_display(&words, "/"), words.join("/"));
             let limit = rng.below(20) as u64;
             check!(format!("evens({limit})"), evens(limit).collect::<Vec<_>>(), (0..=limit).filter(|x| x % 2 == 0).collect::<Vec<_>>());
             let v: Vec<i32> = rng.vec(n, -9, 9);
             let desc = rng.bool();
             let mut want = v.clone();
             if desc {
                 want.reverse();
             }
             check!(format!("ordered({v:?}, {desc})"), ordered(&v, desc).copied().collect::<Vec<_>>(), want);
         }
     }
     """],
    [("rust", "Arguments: `impl IntoIterator<Item = impl AsRef<str>>`, `impl Display` items, `impl Fn(&str) -> bool` (a `fn` pointer can't capture). Returns: `impl Fn(i64) -> i64` and `impl Iterator<Item = u64> + Clone`: callers may only use what the signature promises."),
     ("rust", "`impl Trait` in return position is one concrete type, so `if`/`else` returning `Rev<Iter>` and `Iter` fails (E0308). Box both branches as `Box<dyn Iterator<Item = &i32> + '_>`.")],
    ("""In argument position `impl Trait` is an anonymous generic: the caller picks the type and each call site is monomorphised. In return position it's one hidden type the function picks, and callers see only the listed traits (so `+ Clone` must be written to be usable). Two different types need `Box<dyn Trait + '_>` (or an enum like `Either`).

Syntax: `fn f(xs: impl IntoIterator<Item = impl AsRef<str>>)` · `fn g() -> impl Iterator<Item = u64> + Clone` · `-> Box<dyn Iterator<Item = &i32> + '_>` (`'_` ties the box to the borrowed input).""", "O(n)", "O(1) extra (evens is lazy)"),
    "Why can't a caller write `compose::<SomeType, _>(...)` with `impl Trait` arguments, and when does that matter?",
    ["`impl Trait` arguments: caller-chosen generic.", "`impl Trait` returns: one callee-chosen type; list every trait callers need.", "Different types per branch → `Box<dyn Trait + '_>`."],
    related=("L5", "S6"),
    wrong=dict(
        bytes_not_chars=ITER_ARGS_SOLUTION.replace("w.as_ref().chars().count()", "w.as_ref().len()"),
        compose_backwards=ITER_ARGS_SOLUTION.replace("move |x| g(f(x))", "move |x| f(g(x))"),
        evens_exclusive=ITER_ARGS_SOLUTION.replace("(0..=limit).step_by(2)", "(0..limit).step_by(2)"),
    ),
))

STAGES = [
    ("define-implement", "Define & implement", "easy"),
    ("static-vs-dynamic", "Static vs dynamic", "medium"),
    ("object-safety", "Object safety", "medium"),
    ("operator-traits", "Operator traits", "medium"),
    ("coherence-extension", "Coherence & extension", "hard"),
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
    n = write_track("l4-traits-dispatch", "L4", "Traits & dispatch", "L", "core", 4,
                    "Traits say what a type can do. Generics pick the code at compile time; trait objects pick it at run time.",
                    STAGES, P)
    print("L4", n)
