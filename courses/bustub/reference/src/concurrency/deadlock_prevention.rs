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
    // @begin 4d-c1
    let requester_is_older = requester_ts < holder_ts;
    match (policy, requester_is_older) {
        (Policy::WaitDie, true) => Decision::Wait,
        (Policy::WaitDie, false) => Decision::AbortRequester,
        (Policy::WoundWait, true) => Decision::AbortHolder,
        (Policy::WoundWait, false) => Decision::Wait,
    }
    //~ todo!("4d-c1: compare the ages and apply the policy")
    // @end
}
