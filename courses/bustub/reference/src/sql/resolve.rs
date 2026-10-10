//! Which table and column does a name refer to?

#[derive(Debug, PartialEq, Eq)]
pub enum ResolveError {
    UnknownTable,
    UnknownColumn,
    Ambiguous(Vec<usize>),
}

/// `tables[i] = (alias, column names)`.
pub fn resolve_column(tables: &[(&str, Vec<&str>)], qualifier: Option<&str>, name: &str) -> Result<(usize, usize), ResolveError> {
    // @begin 3d-c5
    let name = name.to_ascii_lowercase();
    let find_in = |t: usize| -> Vec<usize> {
        tables[t].1.iter().enumerate().filter(|(_, c)| c.to_ascii_lowercase() == name).map(|(i, _)| i).collect()
    };
    match qualifier {
        Some(q) => {
            let q = q.to_ascii_lowercase();
            let t = tables.iter().position(|(a, _)| a.to_ascii_lowercase() == q).ok_or(ResolveError::UnknownTable)?;
            let cols = find_in(t);
            match cols.len() {
                0 => Err(ResolveError::UnknownColumn),
                1 => Ok((t, cols[0])),
                _ => Err(ResolveError::Ambiguous(vec![t; cols.len()])),
            }
        }
        None => {
            let mut hits: Vec<(usize, usize)> = Vec::new();
            for t in 0..tables.len() {
                hits.extend(find_in(t).into_iter().map(|c| (t, c)));
            }
            match hits.len() {
                0 => Err(ResolveError::UnknownColumn),
                1 => Ok(hits[0]),
                _ => Err(ResolveError::Ambiguous(hits.into_iter().map(|(t, _)| t).collect())),
            }
        }
    }
    //~ todo!("3d-c5: find the column in the named table, or in every table when unqualified")
    // @end
}
