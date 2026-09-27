pub fn transfer(balances: &mut [i64], from: usize, to: usize, amount: i64) -> Result<(), &'static str> {
    if from >= balances.len() || to >= balances.len() {
        return Err("no such account");
    }
    if balances[from] < amount {
        return Err("insufficient funds");
    }
    if from == to {
        return Err("same account");
    }
    balances[from] -= amount;
    balances[to] += amount;
    Ok(())
}
