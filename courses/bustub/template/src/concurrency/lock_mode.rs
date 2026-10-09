//! The five lock modes of a table-and-row hierarchy, and which of them can be held together.

/// A lock mode. The intention modes (IS, IX, SIX) are taken on a table to say "I am about to lock rows of it in this way"; S and X lock
/// whatever they are taken on, a table or a row.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum LockMode {
    IntentionShared,
    IntentionExclusive,
    Shared,
    SharedIntentionExclusive,
    Exclusive,
}

/// Can two different transactions hold `a` and `b` on the same thing at the same time?
pub fn compatible(a: LockMode, b: LockMode) -> bool {
    use LockMode::*;
    todo!("4d-01: the compatibility of two lock modes")
}

/// May a transaction that holds `from` ask for `to` on the same thing, to replace it? Only a stronger mode, never the same one.
pub fn can_upgrade(from: LockMode, to: LockMode) -> bool {
    use LockMode::*;
    todo!("4d-01: which modes may be replaced by which")
}
