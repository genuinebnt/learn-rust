//! Does a condition fail on a row that an outer join padded with NULLs?

/// An integer-valued expression.
#[derive(Debug, Clone, PartialEq)]
pub enum S {
    Col(usize),
    Lit(i64),
    Coalesce(Box<S>, Box<S>),
}

/// A condition.
#[derive(Debug, Clone, PartialEq)]
pub enum B {
    Gt(S, S),
    Eq(S, S),
    IsNull(S),
    IsNotNull(S),
    And(Box<B>, Box<B>),
    Or(Box<B>, Box<B>),
    Not(Box<B>),
}

pub fn eval_s(s: &S, row: &[Option<i64>]) -> Option<i64> {
    match s {
        S::Col(i) => row[*i],
        S::Lit(v) => Some(*v),
        S::Coalesce(a, b) => eval_s(a, row).or_else(|| eval_s(b, row)),
    }
}

/// Three-valued evaluation: `None` is unknown.
pub fn eval(b: &B, row: &[Option<i64>]) -> Option<bool> {
    match b {
        B::Gt(x, y) => Some(eval_s(x, row)? > eval_s(y, row)?),
        B::Eq(x, y) => Some(eval_s(x, row)? == eval_s(y, row)?),
        B::IsNull(x) => Some(eval_s(x, row).is_none()),
        B::IsNotNull(x) => Some(eval_s(x, row).is_some()),
        B::And(x, y) => match (eval(x, row), eval(y, row)) {
            (Some(false), _) | (_, Some(false)) => Some(false),
            (Some(true), Some(true)) => Some(true),
            _ => None,
        },
        B::Or(x, y) => match (eval(x, row), eval(y, row)) {
            (Some(true), _) | (_, Some(true)) => Some(true),
            (Some(false), Some(false)) => Some(false),
            _ => None,
        },
        B::Not(x) => eval(x, row).map(|v| !v),
    }
}

/// Is `cond` certainly not TRUE when the columns in `nulls` are NULL, whatever the other columns hold?
pub fn rejects_nulls(cond: &B, nulls: &[usize]) -> bool {
    let _ = (cond, nulls);
    false
}
