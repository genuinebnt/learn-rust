//! What to do with a node that has too few keys after a delete.

#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub enum Action {
    Nothing,
    BorrowLeft,
    BorrowRight,
    MergeLeft,
    MergeRight,
    /// No sibling can help (the node is the only child).
    Underfull,
}

pub fn after_delete(node: usize, min: usize, max: usize, left: Option<usize>, right: Option<usize>) -> Action {
    if node >= min {
        return Action::Nothing;
    }
    if left.is_some_and(|l| l + node <= max) {
        return Action::MergeLeft;
    }
    if right.is_some_and(|r| r + node <= max) {
        return Action::MergeRight;
    }
    if left.is_some_and(|l| l > min) {
        return Action::BorrowLeft;
    }
    if right.is_some_and(|r| r > min) {
        return Action::BorrowRight;
    }
    Action::Underfull
}
