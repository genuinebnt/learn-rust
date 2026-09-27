use std::slice::GetDisjointMutError;

pub fn transfer(balances: &mut [i64], from: usize, to: usize, amount: i64) -> Result<(), &'static str> {
    let [a, b] = balances.get_disjoint_mut([from, to]).map_err(|e| match e {
        GetDisjointMutError::OverlappingIndices => "same account",
        GetDisjointMutError::IndexOutOfBounds => "no such account",
    })?;
    if *a <= amount {
        return Err("insufficient funds");
    }
    *a -= amount;
    *b += amount;
    Ok(())
}
