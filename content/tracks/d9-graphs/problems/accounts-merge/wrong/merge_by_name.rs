use std::collections::{BTreeMap, BTreeSet};

pub fn accounts_merge(accounts: &[Vec<&str>]) -> Vec<Vec<String>> {
    let mut by_name: BTreeMap<&str, BTreeSet<&str>> = BTreeMap::new();
    for account in accounts {
        by_name.entry(account[0]).or_default().extend(account[1..].iter().copied());
    }
    by_name.into_iter().map(|(n, e)| std::iter::once(n).chain(e).map(String::from).collect()).collect()
}
