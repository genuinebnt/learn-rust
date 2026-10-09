//! Deadlock prevention by age.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Policy {
    WaitDie,
    WoundWait,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Decision {
    Wait,
    AbortRequester,
    AbortHolder,
}

/// A smaller timestamp is an older transaction.
pub fn decide(policy: Policy, requester_ts: u64, holder_ts: u64) -> Decision {
    todo!("4d-c1: compare the ages and apply the policy")
}
