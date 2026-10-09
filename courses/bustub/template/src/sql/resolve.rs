//! Which table and column does a name refer to?

#[derive(Debug, PartialEq, Eq)]
pub enum ResolveError {
    UnknownTable,
    UnknownColumn,
    Ambiguous(Vec<usize>),
}

/// `tables[i] = (alias, column names)`.
pub fn resolve_column(tables: &[(&str, Vec<&str>)], qualifier: Option<&str>, name: &str) -> Result<(usize, usize), ResolveError> {
    todo!("3d-c5: find the column in the named table, or in every table when unqualified")
}
