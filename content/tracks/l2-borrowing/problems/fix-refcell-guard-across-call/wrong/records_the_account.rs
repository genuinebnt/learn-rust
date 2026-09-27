use std::cell::RefCell;

pub struct Bank {
    balances: RefCell<Vec<i64>>,
    audit: RefCell<Vec<String>>,
}

impl Bank {
    pub fn new(accounts: usize) -> Self {
        Bank { balances: RefCell::new(vec![0; accounts]), audit: RefCell::new(Vec::new()) }
    }

    fn total(&self) -> i64 {
        self.balances.borrow().iter().sum()
    }

    /// Adds `amount` to account `i` and records the new total.
    pub fn deposit(&self, i: usize, amount: i64) {
        let balance = {
            let mut balances = self.balances.borrow_mut();
            balances[i] += amount;
            balances[i]
        };
        self.audit.borrow_mut().push(format!("total {balance}"));
    }

    pub fn audit(&self) -> Vec<String> {
        self.audit.borrow().to_vec()
    }
}
