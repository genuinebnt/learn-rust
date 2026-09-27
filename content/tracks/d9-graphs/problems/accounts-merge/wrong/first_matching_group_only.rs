use std::collections::BTreeSet;

pub fn accounts_merge(accounts: &[Vec<&str>]) -> Vec<Vec<String>> {
    let mut groups: Vec<(String, BTreeSet<String>)> = Vec::new();
    for account in accounts {
        let emails = account[1..].iter().map(|e| e.to_string());
        match groups.iter_mut().find(|(_, g)| account[1..].iter().any(|e| g.contains(*e))) {
            Some((_, g)) => g.extend(emails),
            None => groups.push((account[0].to_string(), emails.collect())),
        }
    }
    let mut out: Vec<Vec<String>> = groups.into_iter().map(|(n, e)| std::iter::once(n).chain(e).collect()).collect();
    out.sort_unstable();
    out
}
