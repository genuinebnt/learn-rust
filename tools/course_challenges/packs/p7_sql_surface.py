from _c import C
M3I = "19-sql-surface"
CH = []

CH.append(C("3i-c1", M3I, "90-challenge-in-through-a-hash-set", "build", "Challenge: IN through a hash set", "easy", "stages_3i::s3i_c1",
  ["answering `x IN (constants)` in constant time per row","keeping SQL's third answer when the list contains a NULL"],
  ["sql-types-and-three-valued-logic","hash-aggregation","property-testing-and-fuzzing"],
  "`InSet` in `src/execution/in_set.rs`: built once from a list of constants (some of which may be NULL), it answers `contains(x)` for a value that may be NULL with TRUE, FALSE or NULL, as `x IN (list)` does, and `not_in(x)` as `x NOT IN (list)` does, without scanning the list for every row.",
  "A parser rewrite turns `a IN (1, 2, 3)` into a chain of ORs, which costs a comparison per item per row. A long list of constants (a thousand ids from an application) makes that the slowest part of the query. A hash set answers in one probe, and the part to get right is not the set but the answers around it: a NULL in the list changes what a miss means.",
  ["`new(list)` takes the constants as `Option<i64>`; duplicates and NULLs are allowed.","`contains(x)`: TRUE if `x` is not NULL and is in the list; otherwise NULL if `x` is NULL and the list is not empty, or if the list contains a NULL; otherwise FALSE.","`not_in(x)` is the three-valued negation of `contains(x)`.","`len()` is the number of distinct non-NULL values."],
  ["`contains` agrees with the OR chain `x = v1 OR x = v2 ...` evaluated in three-valued logic.","`not_in(x) == not contains(x)` for every `x`."],
  ["Adding a value that is already there changes nothing.","Adding a NULL to a list turns every FALSE of `contains` into NULL and changes no TRUE.","An empty list answers FALSE for every `x`, a NULL `x` included."],
  ["list [1, 2]: contains(Some(2)) = TRUE, contains(Some(3)) = FALSE, contains(None) = NULL","list [1, NULL]: contains(Some(3)) = NULL, not_in(Some(1)) = FALSE"],
  ["Hits, misses and NULL on the left.","A NULL in the list.","The empty list and duplicates.","A property against the OR chain."],
  src=("src/execution/in_set.rs", '''
//! `x IN (constants)` through a hash set.

use std::collections::HashSet;

pub struct InSet {
    // @begin 3i-c1
    values: HashSet<i64>,
    has_null: bool,
    //~ _in_set: (),
    // @end
}

impl InSet {
    pub fn new(list: &[Option<i64>]) -> InSet {
        // @begin 3i-c1
        InSet { values: list.iter().flatten().copied().collect(), has_null: list.iter().any(|v| v.is_none()) }
        //~ todo!("3i-c1: remember the non-NULL values, and whether the list had a NULL")
        // @end
    }

    /// The number of distinct non-NULL values.
    pub fn len(&self) -> usize {
        // @begin 3i-c1
        self.values.len()
        //~ todo!("3i-c1: distinct non-NULL values")
        // @end
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0 && !self.has_null_entry()
    }

    fn has_null_entry(&self) -> bool {
        // @begin 3i-c1
        self.has_null
        //~ todo!("3i-c1: did the list have a NULL")
        // @end
    }

    /// `x IN (list)`: `Some(true)`, `Some(false)` or `None` (NULL).
    pub fn contains(&self, x: Option<i64>) -> Option<bool> {
        // @begin 3i-c1
        if self.is_empty() {
            return Some(false);
        }
        match x {
            Some(v) if self.values.contains(&v) => Some(true),
            _ if x.is_none() || self.has_null => None,
            _ => Some(false),
        }
        //~ todo!("3i-c1: TRUE on a hit; NULL for a NULL x (list not empty) or a miss with a NULL in the list; FALSE otherwise")
        // @end
    }

    /// `x NOT IN (list)`.
    pub fn not_in(&self, x: Option<i64>) -> Option<bool> {
        // @begin 3i-c1
        self.contains(x).map(|b| !b)
        //~ todo!("3i-c1: the three-valued negation of contains")
        // @end
    }
}
'''),
  test=("tests/stages_3i.rs", '''
use super::*;
use bustub::execution::in_set::InSet;

/// The definition: an OR chain of equalities in three-valued logic.
fn chain(x: Option<i64>, list: &[Option<i64>]) -> Option<bool> {
    let cmp: Vec<Option<bool>> = list.iter().map(|v| match (x, v) { (Some(a), Some(b)) => Some(a == *b), _ => None }).collect();
    if cmp.contains(&Some(true)) {
        Some(true)
    } else if cmp.contains(&None) {
        None
    } else {
        Some(false)
    }
}

#[test]
fn s3i_c1_hits_misses_and_a_null_on_the_left() {
    let s = InSet::new(&[Some(1), Some(2)]);
    assert_eq!((s.contains(Some(2)), s.contains(Some(3)), s.contains(None)), (Some(true), Some(false), None));
    assert_eq!((s.not_in(Some(2)), s.not_in(Some(3)), s.not_in(None)), (Some(false), Some(true), None));
}

#[test]
fn s3i_c1_a_null_in_the_list_turns_misses_into_unknown() {
    let s = InSet::new(&[Some(1), None]);
    assert_eq!(s.contains(Some(1)), Some(true), "a hit is still a hit");
    assert_eq!(s.contains(Some(3)), None, "a miss might have been equal to the NULL");
    assert_eq!(s.not_in(Some(1)), Some(false));
    assert_eq!(s.not_in(Some(3)), None, "NOT IN with a NULL in the list is never TRUE");
}

#[test]
fn s3i_c1_the_empty_list_and_duplicates() {
    let e = InSet::new(&[]);
    assert_eq!((e.contains(Some(1)), e.contains(None), e.not_in(None)), (Some(false), Some(false), Some(true)), "nothing equals anything");
    let d = InSet::new(&[Some(5), Some(5), None, None]);
    assert_eq!(d.len(), 1, "distinct non-NULL values");
    assert_eq!(d.contains(Some(5)), Some(true));
}

#[test]
fn s3i_c1_only_a_null_in_the_list() {
    let n = InSet::new(&[None]);
    assert_eq!((n.contains(Some(1)), n.contains(None)), (None, None), "everything is unknown");
    assert_eq!(n.len(), 0, "no non-NULL values");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: agrees with the OR chain for every list and value; NOT IN is the negation.
    #[test]
    fn s3i_c1_property_agrees_with_the_or_chain(list in proptest::collection::vec(proptest::option::of(0i64..6), 0..8), x in proptest::option::of(0i64..8)) {
        let s = InSet::new(&list);
        prop_assert_eq!(s.contains(x), chain(x, &list));
        prop_assert_eq!(s.not_in(x), chain(x, &list).map(|b| !b));
    }
}
''')))

CH.append(C("3i-c2", M3I, "91-challenge-the-not-in-that-lost-its-null", "debug", "Challenge: the NOT IN that lost its NULL", "easy", "stages_3i::s3i_c2",
  ["spotting an optimisation that changes the answer","what a NULL in a list does to NOT IN, and why `NOT EXISTS` is the safe spelling"],
  ["sql-types-and-three-valued-logic","property-testing-and-fuzzing","errors-3d"],
  "`not_in` in `src/execution/not_in.rs` evaluates `x NOT IN (list)` for a value and a list that may contain NULLs. A well-meant simplification, \"NULLs can never match, so drop them first\", makes it return TRUE where SQL says unknown. Find the bug and fix it.",
  "This is the most common wrong answer a hand-written NOT IN produces, and it is wrong in the direction that looks right: the NULL cannot equal anything, so ignoring it seems harmless. What it throws away is the *possibility* that the value equals something unknown, which is exactly what makes SQL return no rows. A query that is wrong only when a list happens to contain a NULL is the kind that works for years.",
  ["`not_in(x, list)` is TRUE if `x` is not NULL, differs from every item and the list has no NULL (or is empty); FALSE if `x` equals some item; NULL otherwise.","`x` NULL with an empty list is TRUE: there is nothing it could equal."],
  ["`not_in` is never TRUE for a non-empty list containing a NULL.","`not_in(x, list)` is the three-valued negation of `x IN list`."],
  ["Removing a non-NULL item from a list can only move the answer towards TRUE.","Adding a NULL to any list never makes the answer TRUE."],
  ["x = 3, list [1, 2]: TRUE","x = 3, list [1, NULL]: unknown (NULL)","x = 1, list [1, NULL]: FALSE"],
  ["The textbook cases.","A NULL in the list.","A NULL on the left.","The empty list.","A property against the definition."],
  src=("src/execution/not_in.rs", '''
//! `x NOT IN (list)` in three-valued logic.

/// `Some(true)`, `Some(false)` or `None` (NULL).
pub fn not_in(x: Option<i64>, list: &[Option<i64>]) -> Option<bool> {
    // @begin 3i-c2
    if list.iter().any(|v| matches!((x, v), (Some(a), Some(b)) if a == *b)) {
        return Some(false);
    }
    let unknown = (x.is_none() && !list.is_empty()) || list.iter().any(|v| v.is_none());
    if unknown {
        None
    } else {
        Some(true)
    }
    //~ // "a NULL can never match, so leave NULLs out of the list"
    //~ let known: Vec<i64> = list.iter().flatten().copied().collect();
    //~ match x {
    //~     Some(a) => Some(!known.contains(&a)),
    //~     None => None,
    //~ }
    // @end
}
'''),
  test=("tests/stages_3i.rs", '''
use super::*;
use bustub::execution::not_in::not_in;

#[test]
fn s3i_c2_the_textbook_cases() {
    assert_eq!(not_in(Some(3), &[Some(1), Some(2)]), Some(true), "not in the list");
    assert_eq!(not_in(Some(1), &[Some(1), Some(2)]), Some(false), "in the list");
}

#[test]
fn s3i_c2_a_null_in_the_list_makes_a_miss_unknown() {
    assert_eq!(not_in(Some(3), &[Some(1), None]), None, "3 might equal the NULL: unknown");
    assert_eq!(not_in(Some(1), &[Some(1), None]), Some(false), "a hit is decided whatever else is in the list");
}

#[test]
fn s3i_c2_a_null_on_the_left_is_unknown_for_a_non_empty_list() {
    assert_eq!(not_in(None, &[Some(1)]), None, "NULL NOT IN (1) is NULL");
    assert_eq!(not_in(None, &[None]), None, "NULL NOT IN (NULL) is NULL");
}

#[test]
fn s3i_c2_the_empty_list_has_nothing_to_equal() {
    assert_eq!(not_in(Some(1), &[]), Some(true), "1 NOT IN () is TRUE");
    assert_eq!(not_in(None, &[]), Some(true), "and so is NULL NOT IN ()");
}

#[test]
fn s3i_c2_only_nulls_in_the_list() {
    assert_eq!(not_in(Some(7), &[None, None]), None, "every comparison is unknown");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the definition `NOT (x = v1 OR x = v2 ...)`, evaluated in three-valued logic.
    #[test]
    fn s3i_c2_property_agrees_with_not_of_the_or_chain(x in proptest::option::of(0i64..5), list in proptest::collection::vec(proptest::option::of(0i64..5), 0..6)) {
        let cmp: Vec<Option<bool>> = list.iter().map(|v| match (x, v) { (Some(a), Some(b)) => Some(a == *b), _ => None }).collect();
        let or = if cmp.contains(&Some(true)) { Some(true) } else if cmp.contains(&None) { None } else { Some(false) };
        prop_assert_eq!(not_in(x, &list), or.map(|b| !b));
    }
}
''')))

CH.append(C("3i-c3", M3I, "92-challenge-simplifying-a-case", "build", "Challenge: simplifying a CASE", "medium", "stages_3i::s3i_c3",
  ["constant folding that must not change meaning","finding the branches of a CASE that can never be taken"],
  ["case-expressions-and-lazy-evaluation","rule-based-query-optimization","property-testing-and-fuzzing"],
  "`fold_case` in `src/optimizer/case_fold.rs`: given a CASE whose conditions are either known (TRUE, FALSE, NULL) or unknown until a row arrives, return a simpler CASE that means exactly the same, or the result outright when it is already decided. Results are opaque ids so the tests can tell them apart.",
  "ORM-generated queries and rewritten views are full of `CASE WHEN 1 = 1 THEN ...` and `CASE WHEN false THEN ...`. An optimizer that folds them makes the plan smaller, lets predicates inside become index lookups, and avoids evaluating dead branches. The skill is the one every optimizer rule needs: change the shape, prove the meaning is the same, and remember that the *order* of branches is part of the meaning.",
  ["A branch whose condition is FALSE or NULL can never be taken and is removed.","The first branch whose condition is TRUE always wins when reached: it becomes the ELSE, and every branch after it is removed.","If no branch is left, the CASE is its ELSE (or NULL when there is none): `Folded::Result`. If the first remaining branch is TRUE, the result is its result.","Otherwise the result is `Folded::Case` with the remaining branches, in their original order."],
  ["Folding preserves meaning for every assignment of the unknown conditions.","Folding is idempotent."],
  ["Folding a folded CASE changes nothing.","The number of branches never increases.","A CASE of only unknown conditions is returned unchanged."],
  ["[(False, 1), (Unknown(0), 2)] else 3 -> CASE [(Unknown(0), 2)] else 3","[(Unknown(0), 1), (True, 2), (Unknown(1), 3)] else 4 -> CASE [(Unknown(0), 1)] else 2","[(False, 1)] -> NULL"],
  ["Dead branches removed.","A TRUE branch decides everything after it.","Fully decided CASEs.","Idempotence and meaning by property."],
  src=("src/optimizer/case_fold.rs", '''
//! Folding the constant conditions of a CASE.

/// A condition: a literal, or something that depends on the row (named by a number).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cond {
    True,
    False,
    Null,
    Unknown(u32),
}

/// `CASE WHEN c1 THEN r1 ... [ELSE e] END`; results are opaque ids, `otherwise: None` is no ELSE (NULL).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Case {
    pub branches: Vec<(Cond, u32)>,
    pub otherwise: Option<u32>,
}

#[derive(Debug, PartialEq, Eq)]
pub enum Folded {
    /// Decided: the id of the result, `None` for NULL.
    Result(Option<u32>),
    /// Still depends on the row.
    Case(Case),
}

pub fn fold_case(case: &Case) -> Folded {
    // @begin 3i-c3
    let mut kept: Vec<(Cond, u32)> = Vec::new();
    let mut otherwise = case.otherwise;
    for &(cond, result) in &case.branches {
        match cond {
            Cond::False | Cond::Null => continue,
            Cond::True => {
                // this branch is taken whenever it is reached: it is the ELSE, and nothing after it matters
                otherwise = Some(result);
                break;
            }
            Cond::Unknown(_) => kept.push((cond, result)),
        }
    }
    if kept.is_empty() {
        return Folded::Result(otherwise);
    }
    Folded::Case(Case { branches: kept, otherwise })
    //~ todo!("3i-c3: drop FALSE and NULL branches; a TRUE branch ends the list and becomes the ELSE; nothing left means the ELSE")
    // @end
}
'''),
  test=("tests/stages_3i.rs", '''
use super::*;
use bustub::optimizer::case_fold::{fold_case, Case, Cond, Cond::*, Folded};

fn case(branches: &[(Cond, u32)], otherwise: Option<u32>) -> Case {
    Case { branches: branches.to_vec(), otherwise }
}

/// What the CASE gives when the unknown conditions take the values in `env` (index = Unknown number).
fn eval(c: &Case, env: &[Option<bool>]) -> Option<u32> {
    for &(cond, r) in &c.branches {
        let v = match cond {
            True => Some(true),
            False => Some(false),
            Null => None,
            Unknown(i) => env[i as usize],
        };
        if v == Some(true) {
            return Some(r);
        }
    }
    c.otherwise
}

fn eval_folded(f: &Folded, env: &[Option<bool>]) -> Option<u32> {
    match f {
        Folded::Result(r) => *r,
        Folded::Case(c) => eval(c, env),
    }
}

#[test]
fn s3i_c3_branches_that_can_never_be_taken_are_removed() {
    let c = case(&[(False, 1), (Unknown(0), 2), (Null, 3), (Unknown(1), 4)], Some(9));
    assert_eq!(fold_case(&c), Folded::Case(case(&[(Unknown(0), 2), (Unknown(1), 4)], Some(9))), "FALSE and NULL conditions are never TRUE");
}

#[test]
fn s3i_c3_a_true_branch_ends_the_case_and_becomes_the_else() {
    let c = case(&[(Unknown(0), 1), (True, 2), (Unknown(1), 3)], Some(4));
    assert_eq!(fold_case(&c), Folded::Case(case(&[(Unknown(0), 1)], Some(2))), "what follows a TRUE branch is unreachable");
}

#[test]
fn s3i_c3_a_case_with_nothing_left_is_decided() {
    assert_eq!(fold_case(&case(&[(False, 1)], None)), Folded::Result(None), "no branch and no ELSE: NULL");
    assert_eq!(fold_case(&case(&[(Null, 1), (False, 2)], Some(5))), Folded::Result(Some(5)), "the ELSE");
    assert_eq!(fold_case(&case(&[(True, 7), (Unknown(0), 8)], Some(5))), Folded::Result(Some(7)), "a leading TRUE");
}

#[test]
fn s3i_c3_a_case_of_unknown_conditions_is_left_alone() {
    let c = case(&[(Unknown(0), 1), (Unknown(1), 2)], None);
    assert_eq!(fold_case(&c), Folded::Case(c.clone()), "nothing to fold");
}

#[test]
fn s3i_c3_branch_order_is_kept() {
    let c = case(&[(Unknown(2), 1), (False, 9), (Unknown(0), 2), (Unknown(1), 3)], Some(0));
    match fold_case(&c) {
        Folded::Case(f) => assert_eq!(f.branches, vec![(Unknown(2), 1), (Unknown(0), 2), (Unknown(1), 3)], "first match wins: the order is the meaning"),
        other => panic!("{other:?}"),
    }
}

fn arb_cond() -> impl Strategy<Value = Cond> {
    prop_oneof![Just(True), Just(False), Just(Null), (0u32..3).prop_map(Unknown)]
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 400, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the folded CASE gives the same result for every assignment of the unknowns; folding is idempotent and never adds branches.
    #[test]
    fn s3i_c3_property_folding_preserves_meaning(branches in proptest::collection::vec((arb_cond(), 0u32..5), 0..6), otherwise in proptest::option::of(5u32..9)) {
        let c = Case { branches, otherwise };
        let f = fold_case(&c);
        for bits in 0..27u32 {
            let env: Vec<Option<bool>> = (0..3).map(|i| match (bits / 3u32.pow(i)) % 3 { 0 => Some(true), 1 => Some(false), _ => None }).collect();
            prop_assert_eq!(eval_folded(&f, &env), eval(&c, &env), "env {:?}", env);
        }
        if let Folded::Case(inner) = &f {
            prop_assert!(inner.branches.len() <= c.branches.len());
            prop_assert_eq!(fold_case(inner), Folded::Case(inner.clone()), "idempotent");
        }
    }
}
''')))

CH.append(C("3i-c4", M3I, "93-challenge-a-like-prefix-becomes-a-range", "build", "Challenge: a LIKE prefix becomes a range", "medium", "stages_3i::s3i_c4",
  ["the literal prefix of a LIKE pattern as an index range","computing the smallest string above every string with a given prefix"],
  ["like-matching-without-backtracking","range-scans-and-the-leaf-chain","unicode-and-case-mapping"],
  "`prefix_range` in `src/optimizer/like_prefix.rs`: given a LIKE pattern, return what an optimizer can use: nothing (the pattern starts with a wildcard), an exact string (no wildcards at all), or a range `[prefix, upper)` that contains every string the pattern can match, together with whether the matches still have to be checked against the pattern afterwards.",
  "`name LIKE 'abc%'` is not a scan in a good engine: it is the range `name >= 'abc' AND name < 'abd'` on a B+ tree, plus nothing to check. `LIKE '%abc'` is a full scan whatever you do. Telling the two apart, and computing `'abd'`, is a small exercise with two traps: escapes (`\\\\%` is a literal) and the last character (what comes after `z`, and after the largest character there is).",
  ["`Everything`: the pattern starts with `%` or `_` (or is empty after escapes are resolved to nothing): no usable prefix.","`Exact(s)`: the pattern has no wildcard: `s` is the pattern with escapes resolved.","`Range { prefix, upper, recheck }`: the literal prefix before the first wildcard; `upper` is the smallest string greater than every string that starts with `prefix` (increase the last character; a character that cannot be increased is dropped and the one before it is increased; `None` if nothing is left to increase); `recheck` is false only when the pattern is exactly the prefix followed by one `%`.","A backslash makes the next character literal, also inside the prefix."],
  ["Every string that matches the pattern is `>= prefix` and `< upper` (when there is one).","`upper` has no string between it and the strings that start with `prefix`."],
  ["`abc%` and `abc%%` have the same range; `abc%d` has the same range and `recheck` true.","The range of `a\\\\%b%` is the prefix `a%b`.","A longer prefix gives a range inside the shorter one's."],
  ["`abc%` -> Range { prefix: \"abc\", upper: Some(\"abd\"), recheck: false }","`%abc` -> Everything","`abc` -> Exact(\"abc\")","`ab_` -> Range { prefix: \"ab\", upper: Some(\"ac\"), recheck: true }"],
  ["Prefix, exact and no-prefix patterns.","Escapes in the prefix.","The upper bound at the end of the alphabet.","A property against the matcher."],
  src=("src/optimizer/like_prefix.rs", '''
//! What a LIKE pattern says about the *range* of strings it can match.

#[derive(Debug, PartialEq, Eq)]
pub enum LikeRange {
    /// The pattern starts with a wildcard: no usable prefix.
    Everything,
    /// No wildcard at all: only this string matches.
    Exact(String),
    /// Every match starts with `prefix`; all of them are `< upper` (if there is one). `recheck`: the matches of the range still have to
    /// be tested against the pattern.
    Range { prefix: String, upper: Option<String>, recheck: bool },
}

/// The smallest string greater than every string that starts with `prefix`, if there is one.
pub fn successor(prefix: &str) -> Option<String> {
    // @begin 3i-c4
    let mut chars: Vec<char> = prefix.chars().collect();
    while let Some(last) = chars.pop() {
        let mut next = last as u32 + 1;
        if (0xD800..=0xDFFF).contains(&next) {
            next = 0xE000;
        }
        if let Some(c) = char::from_u32(next) {
            chars.push(c);
            return Some(chars.into_iter().collect());
        }
        // the largest character: drop it and increase the one before
    }
    None
    //~ todo!("3i-c4: increase the last character; if it cannot be increased, drop it and increase the previous one; None when nothing is left")
    // @end
}

pub fn prefix_range(pattern: &str) -> LikeRange {
    // @begin 3i-c4
    let mut prefix = String::new();
    let mut chars = pattern.chars().peekable();
    let mut wildcard_at: Option<(char, String)> = None;
    while let Some(c) = chars.next() {
        match c {
            '%' | '_' => {
                wildcard_at = Some((c, chars.collect()));
                break;
            }
            '\\\\' => prefix.push(chars.next().unwrap_or('\\\\')),
            c => prefix.push(c),
        }
    }
    let Some((wildcard, rest)) = wildcard_at else {
        return LikeRange::Exact(prefix);
    };
    if prefix.is_empty() {
        return LikeRange::Everything;
    }
    // only "prefix%" (and "prefix%%...") is exactly the range
    let recheck = !(wildcard == '%' && rest.chars().all(|c| c == '%'));
    let upper = successor(&prefix);
    LikeRange::Range { prefix, upper, recheck }
    //~ todo!("3i-c4: the literal prefix (escapes resolved), then Everything / Exact / Range")
    // @end
}
'''),
  test=("tests/stages_3i.rs", '''
use super::*;
use bustub::execution::expressions::like_expression::like_matches;
use bustub::optimizer::like_prefix::{prefix_range, successor, LikeRange};

fn range(prefix: &str, upper: Option<&str>, recheck: bool) -> LikeRange {
    LikeRange::Range { prefix: prefix.to_string(), upper: upper.map(String::from), recheck }
}

#[test]
fn s3i_c4_a_prefix_followed_by_percent_is_a_range_with_nothing_to_recheck() {
    assert_eq!(prefix_range("abc%"), range("abc", Some("abd"), false), "abc% is [abc, abd)");
    assert_eq!(prefix_range("abc%%"), range("abc", Some("abd"), false), "extra percents change nothing");
}

#[test]
fn s3i_c4_anything_after_the_prefix_means_the_matches_are_rechecked() {
    assert_eq!(prefix_range("abc%d"), range("abc", Some("abd"), true), "a suffix");
    assert_eq!(prefix_range("ab_"), range("ab", Some("ac"), true), "an underscore");
    assert_eq!(prefix_range("ab_%"), range("ab", Some("ac"), true), "an underscore then a percent");
}

#[test]
fn s3i_c4_a_leading_wildcard_has_no_prefix_and_no_wildcard_is_exact() {
    assert_eq!(prefix_range("%abc"), LikeRange::Everything);
    assert_eq!(prefix_range("_abc"), LikeRange::Everything);
    assert_eq!(prefix_range("%"), LikeRange::Everything);
    assert_eq!(prefix_range("abc"), LikeRange::Exact("abc".into()));
    assert_eq!(prefix_range(""), LikeRange::Exact(String::new()), "the empty pattern matches only the empty string");
}

#[test]
fn s3i_c4_escapes_are_part_of_the_prefix() {
    assert_eq!(prefix_range("a\\\\%b%"), range("a%b", Some("a%c"), false), "an escaped percent is a letter");
    assert_eq!(prefix_range("100\\\\%"), LikeRange::Exact("100%".into()), "an escaped percent at the end: no wildcard");
}

#[test]
fn s3i_c4_the_upper_bound_at_the_end_of_the_alphabet() {
    assert_eq!(successor("az"), Some("a{".into()), "z + 1");
    assert_eq!(successor(&format!("a{}", char::MAX)), Some("b".into()), "the largest character is dropped and the one before increased");
    assert_eq!(successor(&char::MAX.to_string()), None, "nothing is above it");
    assert_eq!(successor("a\\u{D7FF}"), Some("a\\u{E000}".into()), "surrogates are not characters: skip them");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 400, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: every string the pattern matches lies in [prefix, upper); an Exact pattern matches only its string.
    #[test]
    fn s3i_c4_property_matches_stay_inside_the_range(pattern in "[ab%_]{0,5}", text in "[abc]{0,6}") {
        match prefix_range(&pattern) {
            LikeRange::Everything => {}
            LikeRange::Exact(s) => prop_assert_eq!(like_matches(&text, &pattern), text == s),
            LikeRange::Range { prefix, upper, recheck } => {
                if like_matches(&text, &pattern) {
                    prop_assert!(text.starts_with(&prefix), "{:?} matches {:?} but does not start with {:?}", text, pattern, prefix);
                    prop_assert!(text >= prefix);
                    if let Some(u) = &upper { prop_assert!(&text < u, "{:?} is not below {:?}", text, u); }
                }
                if !recheck && text.starts_with(&prefix) {
                    prop_assert!(like_matches(&text, &pattern), "no recheck needed, so every string with the prefix must match");
                }
            }
        }
    }
}
''')))

CH.append(C("3i-c5", M3I, "94-challenge-who-is-slow", "build", "Challenge: who is slow", "medium", "stages_3i::s3i_c5",
  ["exclusive time from inclusive time in a tree","reading the output of your own EXPLAIN ANALYZE"],
  ["explain-analyze-and-operator-statistics","performance-tests-and-measuring","the-iterator-model"],
  "`exclusive_times` in `src/execution/analyze_times.rs`: parse the text your `EXPLAIN ANALYZE` prints (one line per operator, children indented by two spaces, each ending in `(rows=R, batches=B, loops=L, time=T.TTTms)` or `(never executed)`) and give, for every operator in order, its depth, its inclusive time and its **exclusive** time: its own, without its children's. `slowest` names the operator with the largest exclusive time.",
  "The time next to an operator is *inclusive*: a Limit \"took\" as long as the scan under it, so the root always looks the slowest and is never the problem. The question a person asks is which operator spent the time *itself*. The subtraction is trivial and the parsing is where the care goes; doing it on your own output closes the loop: the tool that measures and the tool that reads the measurement.",
  ["Lines that are blank or start with `===` are skipped.","Depth is the indentation in units of two spaces.","`inclusive_ms` is the number before `ms`; `(never executed)` is 0.0.","`exclusive_ms` is `inclusive - sum of the children's inclusive`, but never below 0 (clock jitter).","`slowest` returns the operator text (the line without its depth indent and its statistics) of the largest exclusive time; the first of equals; `None` for no operators."],
  ["Exclusive times are non-negative.","The exclusive times of a tree whose children never exceed their parents add up to the root's inclusive time."],
  ["A leaf's exclusive time is its inclusive time.","Making one operator slower by `d` raises its exclusive time by `d` and its ancestors' inclusive times, not their exclusive ones."],
  ["Limit 0.9ms over Sort 0.8ms over Scan 0.5ms -> exclusive 0.1, 0.3, 0.5; slowest is the Scan"],
  ["Parsing indentation and statistics.","Never executed nodes.","Exclusive time as a difference.","A property over random trees."],
  src=("src/execution/analyze_times.rs", '''
//! Reading an `EXPLAIN ANALYZE` back: which operator spent the time itself?

#[derive(Debug, Clone, PartialEq)]
pub struct OpTime {
    pub op: String,
    pub depth: usize,
    pub inclusive_ms: f64,
    pub exclusive_ms: f64,
}

pub fn exclusive_times(analysis: &str) -> Vec<OpTime> {
    // @begin 3i-c5
    let mut ops: Vec<OpTime> = Vec::new();
    for line in analysis.lines() {
        if line.trim().is_empty() || line.starts_with("===") {
            continue;
        }
        let depth = (line.len() - line.trim_start().len()) / 2;
        let body = line.trim();
        let (op, inclusive) = if let Some(at) = body.rfind(" (rows=") {
            let stats = &body[at..];
            let ms = stats
                .find("time=")
                .map(|i| &stats[i + 5..])
                .and_then(|t| t.split("ms").next())
                .and_then(|t| t.parse::<f64>().ok())
                .unwrap_or(0.0);
            (body[..at].to_string(), ms)
        } else {
            (body.trim_end_matches(" (never executed)").to_string(), 0.0)
        };
        ops.push(OpTime { op, depth, inclusive_ms: inclusive, exclusive_ms: inclusive });
    }
    // subtract each node's children (the nodes after it that are exactly one level deeper, until the depth comes back)
    for i in 0..ops.len() {
        let mut children = 0.0;
        for j in i + 1..ops.len() {
            if ops[j].depth <= ops[i].depth {
                break;
            }
            if ops[j].depth == ops[i].depth + 1 {
                children += ops[j].inclusive_ms;
            }
        }
        ops[i].exclusive_ms = (ops[i].inclusive_ms - children).max(0.0);
    }
    ops
    //~ todo!("3i-c5: parse each line (indent, text, time); exclusive = inclusive minus the inclusive of the direct children, at least 0")
    // @end
}

/// The operator with the largest exclusive time (the first when equal), `None` when there are no operators.
pub fn slowest(analysis: &str) -> Option<String> {
    // @begin 3i-c5
    let mut best: Option<OpTime> = None;
    for op in exclusive_times(analysis) {
        if best.as_ref().is_none_or(|b| op.exclusive_ms > b.exclusive_ms) {
            best = Some(op);
        }
    }
    best.map(|b| b.op)
    //~ todo!("3i-c5: the operator with the largest exclusive time")
    // @end
}
'''),
  test=("tests/stages_3i.rs", '''
use super::*;
use bustub::execution::analyze_times::{exclusive_times, slowest};

fn lines(l: &[&str]) -> String {
    l.iter().map(|x| format!("{x}\\n")).collect()
}

fn sample() -> String {
    lines(&[
        "=== ANALYZE ===",
        "Limit { limit=5 } (rows=5, batches=1, loops=1, time=0.900ms)",
        "  ExternalMergeSort { order_bys=[(Default, Default, #0.0)] } (rows=5, batches=1, loops=1, time=0.800ms)",
        "    SeqScan { table=t } (rows=100, batches=5, loops=1, time=0.500ms)",
    ])
}

#[test]
fn s3i_c5_each_line_gives_its_depth_text_and_inclusive_time() {
    let ops = exclusive_times(&sample());
    assert_eq!(ops.len(), 3, "one entry per operator, the header skipped");
    assert_eq!(ops.iter().map(|o| o.depth).collect::<Vec<_>>(), [0, 1, 2], "indentation is depth");
    assert_eq!(ops[0].op, "Limit { limit=5 }", "the text without the statistics");
    assert_eq!(ops.iter().map(|o| o.inclusive_ms).collect::<Vec<_>>(), [0.9, 0.8, 0.5]);
}

#[test]
fn s3i_c5_exclusive_time_is_what_is_left_after_the_children() {
    let ops = exclusive_times(&sample());
    let ex: Vec<f64> = ops.iter().map(|o| (o.exclusive_ms * 1000.0).round() / 1000.0).collect();
    assert_eq!(ex, [0.1, 0.3, 0.5], "0.9 - 0.8, 0.8 - 0.5, and a leaf keeps its own");
    assert_eq!(slowest(&sample()).as_deref(), Some("SeqScan { table=t }"), "the scan did the work: not the root");
}

#[test]
fn s3i_c5_siblings_are_subtracted_from_their_common_parent_only() {
    let text = lines(&[
        "NestedLoopJoin { type=Inner } (rows=4, batches=1, loops=1, time=3.000ms)",
        "  SeqScan { table=l } (rows=2, batches=1, loops=1, time=0.500ms)",
        "  Filter { x } (rows=2, batches=1, loops=3, time=2.000ms)",
        "    SeqScan { table=r } (rows=6, batches=2, loops=3, time=1.500ms)",
    ]);
    let ops = exclusive_times(&text);
    let ex: Vec<f64> = ops.iter().map(|o| (o.exclusive_ms * 1000.0).round() / 1000.0).collect();
    assert_eq!(ex, [0.5, 0.5, 0.5, 1.5], "3.0 - 0.5 - 2.0; 0.5; 2.0 - 1.5; 1.5");
}

#[test]
fn s3i_c5_a_node_that_never_ran_costs_nothing_and_negatives_are_clamped() {
    let text = lines(&["Projection { exprs=[#0.0] } (rows=0, batches=0, loops=1, time=0.100ms)", "  SeqScan { table=t } (never executed)"]);
    let ops = exclusive_times(&text);
    assert_eq!(ops[1].inclusive_ms, 0.0, "(never executed) is zero");
    assert!((ops[0].exclusive_ms - 0.1).abs() < 1e-9);
    let jitter = "A (rows=1, batches=1, loops=1, time=1.000ms)\\n  B (rows=1, batches=1, loops=1, time=1.200ms)\\n";
    assert_eq!(exclusive_times(jitter)[0].exclusive_ms, 0.0, "a child that measured longer than its parent: never below zero");
}

#[test]
fn s3i_c5_no_operators_no_slowest() {
    assert!(exclusive_times("").is_empty());
    assert_eq!(slowest("=== ANALYZE ===\\n"), None);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 200, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: for a tree where every child is shorter than its parent, the exclusive times are non-negative and add up to the root's.
    #[test]
    fn s3i_c5_property_exclusive_times_add_up_to_the_root(shape in proptest::collection::vec((0usize..3, 1u32..50), 1..8)) {
        // build a valid tree text: the node's depth is at most one more than the previous node's
        let mut depth_prev = 0usize;
        let mut lines: Vec<(usize, u32)> = vec![];
        for (i, (d, self_cost)) in shape.iter().enumerate() {
            let depth = if i == 0 { 0 } else { (*d).min(depth_prev + 1) };
            let depth = if i > 0 && depth == 0 { 1 } else { depth };
            lines.push((depth, *self_cost));
            depth_prev = depth;
        }
        // inclusive = own + children's inclusive, computed bottom-up in tenths of a millisecond
        let n = lines.len();
        let mut inclusive = vec![0u32; n];
        for i in (0..n).rev() {
            let mut total = lines[i].1;
            let mut j = i + 1;
            while j < n && lines[j].0 > lines[i].0 {
                if lines[j].0 == lines[i].0 + 1 { total += inclusive[j]; }
                j += 1;
            }
            inclusive[i] = total;
        }
        let text: String = lines.iter().enumerate().map(|(i, (d, _))| format!("{}Op{} (rows=1, batches=1, loops=1, time={:.3}ms)\\n", "  ".repeat(*d), i, inclusive[i] as f64 / 10.0)).collect();
        let ops = exclusive_times(&text);
        prop_assert_eq!(ops.len(), n);
        prop_assert!(ops.iter().all(|o| o.exclusive_ms >= 0.0));
        let roots_total: f64 = ops.iter().filter(|o| o.depth == 0).map(|o| o.inclusive_ms).sum();
        let exclusive_total: f64 = ops.iter().map(|o| o.exclusive_ms).sum();
        prop_assert!((roots_total - exclusive_total).abs() < 1e-6, "{} vs {}", roots_total, exclusive_total);
    }
}
''')))

CH.append(C("3i-c6", M3I, "95-challenge-coalesce-evaluates-once", "build", "Challenge: COALESCE that evaluates each argument once", "medium", "stages_3i::s3i_c6",
  ["an expression node of your own in the planner's tree","evaluating arguments lazily and exactly once"],
  ["case-expressions-and-lazy-evaluation","expression-trees","sql-types-and-three-valued-logic"],
  "`CoalesceExpression` in `src/execution/expressions/coalesce_expression.rs`: an expression with one or more children that returns the first child value that is not NULL, **evaluating each child at most once and stopping at the first non-NULL**. The binder's rewrite of COALESCE into a CASE evaluates an argument twice (once to ask whether it is NULL, once to use it); this node does not.",
  "For a column reference the second evaluation costs nothing. For an expensive argument (a function, a subquery, a user-defined function with a side effect) it doubles the work, and for a volatile one (`random()`, `nextval()`) it gives two different answers inside one expression. A dedicated node is also what PostgreSQL has, for the same reasons.",
  ["`new(args)` needs at least one argument and one type shared by all (a bare NULL constant adopts it): else `MismatchType`.","`evaluate` and `evaluate_join` return the first non-NULL value among the children, evaluated in order, each at most once; NULL of the result type if all are NULL.","`return_type` is the shared type; `children` returns the arguments in order."],
  ["No child is evaluated after a non-NULL one has been found.","No child is evaluated more than once per call."],
  ["`coalesce(a)` is `a`.","`coalesce(NULL, NULL)` is NULL of the shared type.","The result of `coalesce(a, b)` is `a` whenever `a` is not NULL, whatever `b` would have done (even an error)."],
  ["children evaluate to [NULL, 7, 9]: result 7, the third child is never evaluated","children [3, error]: result 3, the error is never reached"],
  ["First non-NULL wins.","Later children are not evaluated.","Each child once.","Types and arity."],
  src=("src/execution/expressions/coalesce_expression.rs", '''
//! `COALESCE(a, b, ...)` as a node of its own.

use std::any::Any;
use std::sync::Arc;

use super::abstract_expression::{ExprRef, Expression};
use crate::catalog::column::Column;
use crate::catalog::schema::Schema;
use crate::common::exception::{Exception, ExceptionType, Result};
use crate::storage::table::tuple::Tuple;
use crate::types::value::Value;

#[derive(Clone, Debug)]
pub struct CoalesceExpression {
    children: Vec<ExprRef>,
    ret_type: Column,
}

impl CoalesceExpression {
    /// At least one argument; all of one type (the engine types a bare NULL constant INTEGER: it takes the type of the others).
    pub fn new(args: Vec<ExprRef>) -> Result<CoalesceExpression> {
        // @begin 3i-c6
        use super::constant_value_expression::ConstantValueExpression;
        if args.is_empty() {
            return Err(Exception::new(ExceptionType::Invalid, "COALESCE needs at least one argument"));
        }
        let is_null_literal = |e: &ExprRef| e.as_any().downcast_ref::<ConstantValueExpression>().is_some_and(|c| c.val.is_null());
        let ret = args.iter().find(|a| !is_null_literal(a)).unwrap_or(&args[0]).return_type().with_column_name("<val>");
        let mut children = Vec::new();
        for a in args {
            if is_null_literal(&a) {
                children.push(Arc::new(ConstantValueExpression::new(Value::null(ret.type_id()))) as ExprRef);
            } else if a.return_type().type_id() != ret.type_id() {
                return Err(Exception::new(ExceptionType::MismatchType, "COALESCE types cannot be matched"));
            } else {
                children.push(a);
            }
        }
        Ok(CoalesceExpression { children, ret_type: ret })
        //~ todo!("3i-c6: at least one argument; one shared type, a NULL constant adopting it; else MismatchType")
        // @end
    }
}

impl Expression for CoalesceExpression {
    fn evaluate(&self, tuple: &Tuple, schema: &Schema) -> Result<Value> {
        // @begin 3i-c6
        for child in &self.children {
            let v = child.evaluate(tuple, schema)?;
            if !v.is_null() {
                return Ok(v);
            }
        }
        Ok(Value::null(self.ret_type.type_id()))
        //~ todo!("3i-c6: the first non-NULL child value; evaluate no child after it and none twice")
        // @end
    }

    fn evaluate_join(&self, left_tuple: &Tuple, left_schema: &Schema, right_tuple: &Tuple, right_schema: &Schema) -> Result<Value> {
        // @begin 3i-c6
        for child in &self.children {
            let v = child.evaluate_join(left_tuple, left_schema, right_tuple, right_schema)?;
            if !v.is_null() {
                return Ok(v);
            }
        }
        Ok(Value::null(self.ret_type.type_id()))
        //~ todo!("3i-c6: the same with evaluate_join")
        // @end
    }

    fn children(&self) -> &[ExprRef] {
        &self.children
    }

    fn return_type(&self) -> &Column {
        &self.ret_type
    }

    fn to_string(&self) -> String {
        format!("coalesce({})", self.children.iter().map(|c| c.to_string()).collect::<Vec<_>>().join(", "))
    }

    fn clone_with_children(&self, children: Vec<ExprRef>) -> ExprRef {
        Arc::new(CoalesceExpression { children, ..self.clone() })
    }

    fn as_any(&self) -> &dyn Any {
        self
    }
}
'''),
  test=("tests/stages_3i.rs", '''
use super::*;
use std::any::Any;
use std::sync::atomic::{AtomicUsize, Ordering};

use bustub::catalog::column::Column;
use bustub::execution::expressions::coalesce_expression::CoalesceExpression;

/// A child that says how often it was evaluated, and can be made to fail.
#[derive(Debug)]
struct Probe {
    value: Value,
    calls: Arc<AtomicUsize>,
    fails: bool,
    ret: Column,
}

fn probe(value: Value, fails: bool) -> (ExprRef, Arc<AtomicUsize>) {
    let calls = Arc::new(AtomicUsize::new(0));
    let ret = if value.type_id() == TypeId::Varchar { Column::new_varchar("<probe>", 64) } else { Column::new("<probe>", value.type_id()) };
    (Arc::new(Probe { value, calls: calls.clone(), fails, ret }), calls)
}

impl Expression for Probe {
    fn evaluate(&self, _: &Tuple, _: &Schema) -> bustub::common::exception::Result<Value> {
        self.calls.fetch_add(1, Ordering::SeqCst);
        if self.fails {
            return Err(Exception::new(ExceptionType::Execution, "evaluated a child that should not have been"));
        }
        Ok(self.value.clone())
    }
    fn evaluate_join(&self, l: &Tuple, ls: &Schema, _: &Tuple, _: &Schema) -> bustub::common::exception::Result<Value> {
        self.evaluate(l, ls)
    }
    fn children(&self) -> &[ExprRef] {
        &[]
    }
    fn return_type(&self) -> &Column {
        &self.ret
    }
    fn to_string(&self) -> String {
        "probe".into()
    }
    fn clone_with_children(&self, _: Vec<ExprRef>) -> ExprRef {
        unreachable!("a probe has no children")
    }
    fn as_any(&self) -> &dyn Any {
        self
    }
}

fn eval_c(c: &CoalesceExpression) -> bustub::common::exception::Result<Value> {
    c.evaluate(&Tuple::new(&[], &Schema::new(vec![])), &Schema::new(vec![]))
}

fn null() -> Value {
    Value::null(TypeId::Integer)
}

#[test]
fn s3i_c6_the_first_non_null_wins_and_later_children_are_not_evaluated() {
    let (a, ca) = probe(null(), false);
    let (b, cb) = probe(Value::integer(7), false);
    let (c, cc) = probe(Value::integer(9), true);
    let e = CoalesceExpression::new(vec![a, b, c]).unwrap();
    assert_eq!(eval_c(&e).unwrap(), Value::integer(7), "the second child");
    assert_eq!((ca.load(Ordering::SeqCst), cb.load(Ordering::SeqCst), cc.load(Ordering::SeqCst)), (1, 1, 0), "each earlier child once, the third never");
}

#[test]
fn s3i_c6_a_set_first_child_is_the_only_one_evaluated() {
    let (a, ca) = probe(Value::integer(3), false);
    let (b, cb) = probe(Value::integer(1), true);
    let e = CoalesceExpression::new(vec![a, b]).unwrap();
    assert_eq!(eval_c(&e).unwrap(), Value::integer(3), "a is set");
    assert_eq!((ca.load(Ordering::SeqCst), cb.load(Ordering::SeqCst)), (1, 0), "b would have failed: it is never reached");
}

#[test]
fn s3i_c6_all_null_gives_null_of_the_shared_type_and_one_argument_is_itself() {
    let (a, _) = probe(null(), false);
    let (b, _) = probe(null(), false);
    let e = CoalesceExpression::new(vec![a, b]).unwrap();
    assert!(eval_c(&e).unwrap().is_null(), "every argument NULL");
    assert_eq!(e.return_type().type_id(), TypeId::Integer);
    let (only, calls) = probe(Value::integer(5), false);
    assert_eq!(eval_c(&CoalesceExpression::new(vec![only]).unwrap()).unwrap(), Value::integer(5), "coalesce(a) is a");
    assert_eq!(calls.load(Ordering::SeqCst), 1, "evaluated once");
}

#[test]
fn s3i_c6_types_must_agree_and_a_bare_null_adopts_them() {
    let (i, _) = probe(Value::integer(1), false);
    let (s, _) = probe(Value::varchar("x"), false);
    assert!(CoalesceExpression::new(vec![i, s]).is_err(), "an integer and a string do not coalesce");
    assert!(CoalesceExpression::new(vec![]).is_err(), "at least one argument");
    let (s2, _) = probe(Value::varchar("y"), false);
    let nul: ExprRef = Arc::new(ConstantValueExpression::new(null()));
    let e = CoalesceExpression::new(vec![nul, s2]).unwrap();
    assert_eq!(e.return_type().type_id(), TypeId::Varchar, "a bare NULL takes the string type");
    assert_eq!(eval_c(&e).unwrap(), Value::varchar("y"), "and is skipped");
}

#[test]
fn s3i_c6_an_error_in_a_reached_child_is_passed_on() {
    let (a, _) = probe(null(), false);
    let (b, _) = probe(Value::integer(1), true);
    let e = CoalesceExpression::new(vec![a, b]).unwrap();
    assert!(eval_c(&e).is_err(), "the failing child was needed: its error is the result");
}
''')))
