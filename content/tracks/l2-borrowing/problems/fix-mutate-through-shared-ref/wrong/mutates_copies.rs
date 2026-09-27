pub struct Account {
    pub balance: i64,
}

/// Adds `amount` to every account.
pub fn deposit_all(accounts: &[Account], amount: i64) {
    for mut a in accounts.iter().map(|a| Account { balance: a.balance }) {
        a.balance += amount;
    }
}
