//! Pushing NOT down to the variables of a boolean expression.

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum B {
    Var(usize),
    Not(Box<B>),
    And(Box<B>, Box<B>),
    Or(Box<B>, Box<B>),
}

pub fn eval(e: &B, vars: &[bool]) -> bool {
    match e {
        B::Var(i) => vars[*i],
        B::Not(a) => !eval(a, vars),
        B::And(a, b) => eval(a, vars) && eval(b, vars),
        B::Or(a, b) => eval(a, vars) || eval(b, vars),
    }
}

pub fn push_not(e: &B) -> B {
    go(e, false)
}

/// `negate` says that an odd number of NOTs are being pushed through this subtree.
fn go(e: &B, negate: bool) -> B {
    match e {
        B::Var(i) => {
            if negate {
                B::Not(Box::new(B::Var(*i)))
            } else {
                B::Var(*i)
            }
        }
        B::Not(a) => go(a, !negate),
        B::And(a, b) => {
            let (l, r) = (Box::new(go(a, negate)), Box::new(go(b, negate)));
            B::And(l, r)
        }
        B::Or(a, b) => {
            let (l, r) = (Box::new(go(a, negate)), Box::new(go(b, negate)));
            if negate {
                B::And(l, r)
            } else {
                B::Or(l, r)
            }
        }
    }
}
