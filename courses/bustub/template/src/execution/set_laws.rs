//! The six set operations on lists of integers; the results are sorted.

use std::collections::BTreeMap;

fn counts(rows: &[i64]) -> BTreeMap<i64, usize> {
    let mut m = BTreeMap::new();
    for r in rows {
        *m.entry(*r).or_insert(0) += 1;
    }
    m
}

fn combine(l: &[i64], r: &[i64], f: impl Fn(usize, usize) -> usize) -> Vec<i64> {
    let (a, b) = (counts(l), counts(r));
    let keys: std::collections::BTreeSet<i64> = a.keys().chain(b.keys()).copied().collect();
    let mut out = Vec::new();
    for k in keys {
        let n = f(a.get(&k).copied().unwrap_or(0), b.get(&k).copied().unwrap_or(0));
        out.extend(std::iter::repeat(k).take(n));
    }
    out
}

pub fn union_all(l: &[i64], r: &[i64]) -> Vec<i64> {
    let mut v: Vec<i64> = l.iter().chain(r).copied().collect();
    v.sort();
    v
}

pub fn union(l: &[i64], r: &[i64]) -> Vec<i64> {
    let mut v: Vec<i64> = l.iter().chain(r).copied().collect();
    v.dedup();
    v.sort();
    v
}

pub fn intersect_all(l: &[i64], r: &[i64]) -> Vec<i64> {
    combine(l, r, |a, b| a.min(b))
}

pub fn intersect(l: &[i64], r: &[i64]) -> Vec<i64> {
    combine(l, r, |a, b| usize::from(a > 0 && b > 0))
}

pub fn except_all(l: &[i64], r: &[i64]) -> Vec<i64> {
    combine(l, r, |a, b| a.saturating_sub(b))
}

pub fn except(l: &[i64], r: &[i64]) -> Vec<i64> {
    combine(l, r, |a, b| usize::from(a > 0 && b == 0))
}
