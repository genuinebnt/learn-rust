//! The states of a SQL session and what each input does in each state.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum State {
    Idle,
    InTxn,
    Failed,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Input {
    Begin,
    Statement { ok: bool },
    Commit,
    Rollback,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Reply {
    Tag(&'static str),
    Warning,
    Refused,
    Done,
    Error,
}

pub fn step(state: State, input: Input) -> (State, Reply) {
    use Input::*;
    use State::*;
    match (state, input) {
        (Idle, Begin) => (InTxn, Reply::Tag("BEGIN")),
        (InTxn, Begin) => (InTxn, Reply::Warning),
        (Failed, Begin) => (Failed, Reply::Refused),
        (Idle, Statement { ok }) => (Idle, if ok { Reply::Done } else { Reply::Error }),
        (InTxn, Statement { ok: true }) => (InTxn, Reply::Done),
        (InTxn, Statement { ok: false }) => (Failed, Reply::Error),
        (Failed, Statement { .. }) => (Failed, Reply::Refused),
        (Idle, Commit) | (Idle, Rollback) => (Idle, Reply::Warning),
        (InTxn, Commit) => (Idle, Reply::Tag("COMMIT")),
        (InTxn, Rollback) => (Idle, Reply::Tag("ROLLBACK")),
        (Failed, Commit) => (Idle, Reply::Tag("COMMIT")),
        (Failed, Rollback) => (Idle, Reply::Tag("ROLLBACK")),
    }
}
