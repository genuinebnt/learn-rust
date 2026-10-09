//! A table of balances with one lock per slot.

use std::sync::Mutex;

#[derive(Debug, PartialEq, Eq)]
pub enum TransferError {
    NoSuchSlot(usize),
    Insufficient,
}

pub struct Slots {
    _slots: (),
}

impl Slots {
    pub fn new(balances: &[i64]) -> Slots {
        todo!("1g-c5: one lock per slot")
    }

    pub fn balance(&self, i: usize) -> Option<i64> {
        todo!("1g-c5: the balance of one slot")
    }

    pub fn total(&self) -> i64 {
        todo!("1g-c5: every balance at one instant")
    }

    pub fn transfer(&self, from: usize, to: usize, amount: i64) -> Result<(), TransferError> {
        todo!("1g-c5: both locks, in an order every thread agrees on; then the move")
    }
}
