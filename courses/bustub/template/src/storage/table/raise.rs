//! The Halloween problem in an append-only heap.

/// A heap slot: `Some((employee id, salary))` while live, `None` once the version is dead.
pub type Slot = Option<(u32, i64)>;

/// Multiplies the salary of every live row below `limit` by `factor`, once. Returns how many rows changed.
pub fn give_raise(rows: &mut Vec<Slot>, limit: i64, factor: i64) -> usize {
    let mut updated = 0;
    let mut i = 0;
    while i < rows.len() {
        if let Some((id, salary)) = rows[i] {
            if salary < limit {
                rows[i] = None;
                rows.push(Some((id, salary * factor)));
                updated += 1;
            }
        }
        i += 1;
    }
    updated
}
