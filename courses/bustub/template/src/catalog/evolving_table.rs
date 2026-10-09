//! A table whose columns can be added and dropped without rewriting its rows.

pub struct EvolvingTable {
    _evolving: (),
}

impl EvolvingTable {
    pub fn new(columns: usize) -> EvolvingTable {
        todo!("3c-c5: an empty table with `columns` columns")
    }

    pub fn columns(&self) -> usize {
        todo!("3c-c5: the number of columns now")
    }

    pub fn insert(&mut self, row: &[i64]) -> Option<usize> {
        todo!("3c-c5: store the row in the stored layout")
    }

    pub fn add_column(&mut self, default: i64) {
        todo!("3c-c5: a new column that old rows read as the default")
    }

    pub fn drop_column(&mut self, i: usize) -> bool {
        todo!("3c-c5: hide the column from every row")
    }

    pub fn get(&self, rid: usize) -> Option<Vec<i64>> {
        todo!("3c-c5: the row as the current schema sees it")
    }
}
