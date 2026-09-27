pub struct Account {
    pub balance: i64,
}

/// Adds `amount` to every account.
pub fn deposit_all(accounts: &mut [Account], amount: i64) {
    for a in accounts {
        a.balance += amount;
    }
}
